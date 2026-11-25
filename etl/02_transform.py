"""Etapa 2 — tratamento.

Lê os dados brutos (zips oficiais da ANTAQ se existirem, senão o espelho de contingência),
padroniza tipos, aplica a regra oficial de contagem de movimentação, limpa os tempos e
grava as tabelas finais num banco DuckDB intermediário (data/raw/staging.duckdb).

Regras (detalhes e justificativas em docs/DECISOES.md):
  * Movimentação = soma de VLPesoCargaBruta das linhas de Carga com FlagMCOperacaoCarga = 1
    (inclui transbordo/baldeação, como a ANTAQ; exclui safamento, remoção a bordo,
    transferência interna, operação intermediária e abastecimento).
  * Período de referência = mês/ano da DATA DE DESATRACAÇÃO (convenção da ANTAQ; confere
    com a coluna Ano da base em 100% das linhas).
  * Tempos = os já calculados pela ANTAQ (TemposAtracacao, em horas). Negativos -> descartados.
    Outliers acima do percentil 99,5 por natureza de carga -> limitados ao percentil (só tempo).
  * Tonelagem nunca é limitada nem descartada.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

DB_PATH = C.RAW_DIR / "staging.duckdb"


# ---------------------------------------------------------------------------
# Leitura das fontes
# ---------------------------------------------------------------------------
def _zips_oficiais() -> dict[tuple[int, str], tuple[Path, str]]:
    achados = {}
    for z in sorted(C.RAW_OFICIAL_DIR.glob("*.zip")) if C.RAW_OFICIAL_DIR.exists() else []:
        try:
            nomes = zipfile.ZipFile(z).namelist()
        except zipfile.BadZipFile:
            continue
        for nome in nomes:
            m = re.match(r"^(\d{4})(Atracacao|Carga|TemposAtracacao|TemposAtracacaoParalisacao)\.txt$",
                         Path(nome).name)
            if m and int(m.group(1)) in C.ANOS:
                achados[(int(m.group(1)), m.group(2))] = (z, nome)
    return achados


def _sql_txt_oficial(z: Path, membro: str) -> str:
    """Extrai o TXT oficial e devolve o SQL de leitura (tudo como texto).

    Layout do Estatístico Aquaviário: separador ';', cabeçalho na 1ª linha, decimal com vírgula.
    Encoding: tenta UTF-8 e, se falhar, Latin-1. (Ver docs/exploracao.md.)
    """
    destino = C.RAW_OFICIAL_DIR / "_extraido" / Path(membro).name
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z) as zf, zf.open(membro) as src, destino.open("wb") as dst:
            dst.write(src.read())
    try:
        destino.read_bytes()[:1_000_000].decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        enc = "latin-1"
    p = destino.as_posix()
    return (f"SELECT * FROM read_csv('{p}', delim=';', header=true, all_varchar=true, "
            f"quote='\"', encoding='{enc}')")


def fonte(con: duckdb.DuckDBPyConnection, tabela: str) -> tuple[str, dict]:
    """Cria a view bruta `raw_<tabela>` (todas as colunas como VARCHAR, nomes oficiais)."""
    oficiais = _zips_oficiais()
    partes, origem = [], {}
    espelho = []
    for ano in C.ANOS:
        if (ano, tabela) in oficiais:
            z, membro = oficiais[(ano, tabela)]
            partes.append(f"SELECT CAST(COLUMNS(*) AS VARCHAR) FROM ({_sql_txt_oficial(z, membro)})")
            origem[ano] = f"ANTAQ oficial ({z.name})"
        else:
            arq = C.RAW_ESPELHO_DIR / tabela / f"{ano}.parquet"
            if arq.exists():
                espelho.append(arq.as_posix())
                origem[ano] = "espelho de contingência"
    if espelho:
        lista = ", ".join(f"'{p}'" for p in espelho)
        partes.append(f"SELECT CAST(COLUMNS(*) AS VARCHAR) FROM read_parquet([{lista}], union_by_name=true)")
    if not partes:
        raise FileNotFoundError(f"Nenhum dado bruto para {tabela}. Rode etl/01_download.py.")
    nome = f"raw_{tabela.lower()}"
    con.sql(f"CREATE OR REPLACE VIEW {nome} AS " + " UNION ALL BY NAME ".join(partes))
    return nome, origem


# ---------------------------------------------------------------------------
# Utilitários SQL
# ---------------------------------------------------------------------------
NUM = "try_cast(replace(trim({c}), ',', '.') AS DOUBLE)"
ID = "try_cast(try_cast(replace(trim({c}), ',', '.') AS DOUBLE) AS BIGINT)"
DT = ("coalesce(try_strptime(trim({c}), '%d/%m/%Y %H:%M:%S'), try_strptime(trim({c}), '%d/%m/%Y %H:%M'), "
      "try_strptime(trim({c}), '%Y-%m-%d %H:%M:%S.%f'), try_strptime(trim({c}), '%Y-%m-%d %H:%M:%S'))")


def q(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def corrigir_mojibake(texto):
    """Corrige texto UTF-8 que foi lido como Latin-1 (ex.: 'BaldeaÃ§Ã£o' -> 'Baldeação')."""
    if texto is None or not isinstance(texto, str):
        return texto
    if "Ã" in texto or "Â" in texto:
        try:
            return texto.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return texto
    return texto


def corrigir_texto(con, tabela: str, colunas: list[str], log: list) -> None:
    """Aplica corrigir_mojibake só nos valores distintos e atualiza via junção (rápido)."""
    for col in colunas:
        dist = con.sql(f"SELECT DISTINCT {q(col)} AS v FROM {tabela} WHERE {q(col)} IS NOT NULL").df()
        dist["novo"] = dist["v"].map(corrigir_mojibake)
        mud = dist[dist["v"] != dist["novo"]]
        if mud.empty:
            continue
        con.register("_mapa", mud)
        n = con.sql(f"SELECT count(*) FROM {tabela} t JOIN _mapa m ON t.{q(col)} = m.v").fetchall()[0][0]
        con.sql(f"UPDATE {tabela} SET {q(col)} = m.novo FROM _mapa m WHERE {tabela}.{q(col)} = m.v")
        con.unregister("_mapa")
        log.append({"regra": "R7 texto com encoding corrompido corrigido", "tabela": tabela, "coluna": col,
                    "valores_distintos": len(mud), "linhas": int(n)})


# ---------------------------------------------------------------------------
# Staging
# ---------------------------------------------------------------------------
def staging(con, log: list) -> dict:
    origens = {}
    v, origens["Atracacao"] = fonte(con, "Atracacao")
    con.sql(f"""
        CREATE OR REPLACE TABLE stg_atracacao AS
        SELECT {ID.format(c=q('IDAtracacao'))} AS id_atracacao,
               trim("CDTUP") AS cdtup,
               trim("IDBerco") AS id_berco,
               trim("Berço") AS berco,
               trim("Porto Atracação") AS porto_atracacao,
               trim("Coordenadas") AS coordenadas,
               trim("Complexo Portuário") AS complexo_portuario,
               trim("Tipo da Autoridade Portuária") AS tipo_autoridade,
               {DT.format(c=q('Data Chegada'))} AS dt_chegada,
               {DT.format(c=q('Data Atracação'))} AS dt_atracacao,
               {DT.format(c=q('Data Início Operação'))} AS dt_inicio_op,
               {DT.format(c=q('Data Término Operação'))} AS dt_termino_op,
               {DT.format(c=q('Data Desatracação'))} AS dt_desatracacao,
               {ID.format(c=q('Ano'))} AS ano_base,
               trim("Tipo de Operação") AS tipo_operacao,
               trim("Tipo de Navegação da Atracação") AS navegacao_atracacao,
               trim("Município") AS municipio,
               trim("UF") AS uf_nome,
               trim("SGUF") AS sguf,
               trim("Região Geográfica") AS regiao
        FROM {v}
    """)
    corrigir_texto(con, "stg_atracacao", ["berco", "porto_atracacao", "complexo_portuario", "tipo_autoridade",
                                          "tipo_operacao", "navegacao_atracacao", "municipio", "uf_nome", "regiao"], log)

    v, origens["TemposAtracacao"] = fonte(con, "TemposAtracacao")
    con.sql(f"""
        CREATE OR REPLACE TABLE stg_tempos AS
        SELECT {ID.format(c=q('IDAtracacao'))} AS id_atracacao,
               {NUM.format(c=q('TEsperaAtracacao'))} AS t_espera_atracacao,
               {NUM.format(c=q('TEsperaInicioOp'))} AS t_espera_inicio_op,
               {NUM.format(c=q('TOperacao'))} AS t_operacao,
               {NUM.format(c=q('TEsperaDesatracacao'))} AS t_espera_desatracacao,
               {NUM.format(c=q('TAtracado'))} AS t_atracado,
               {NUM.format(c=q('TEstadia'))} AS t_estadia
        FROM {v}
    """)

    v, origens["Carga"] = fonte(con, "Carga")
    con.sql(f"""
        CREATE OR REPLACE TABLE stg_carga AS
        SELECT {ID.format(c=q('IDCarga'))} AS id_carga,
               {ID.format(c=q('IDAtracacao'))} AS id_atracacao,
               -- códigos numéricos que viraram float em alguns anos ('2601.0', '201.0') voltam a SH4 com 4 dígitos
               CASE WHEN regexp_matches(trim("CDMercadoria"), '^[0-9]+\\.0$')
                    THEN lpad(regexp_replace(trim("CDMercadoria"), '\\.0$', ''), 4, '0')
                    ELSE nullif(trim("CDMercadoria"), '') END AS cd_mercadoria_orig,
               trim("Tipo Operação da Carga") AS tipo_operacao_carga,
               trim("Tipo Navegação") AS navegacao,
               {ID.format(c=q('FlagMCOperacaoCarga'))} AS flag_mc,
               trim("Natureza da Carga") AS natureza_orig,
               trim("Sentido") AS sentido_orig,
               coalesce({NUM.format(c=q('TEU'))}, 0) AS teu,
               coalesce({NUM.format(c=q('VLPesoCargaBruta'))}, 0) AS peso
        FROM {v}
    """)
    corrigir_texto(con, "stg_carga", ["tipo_operacao_carga", "navegacao", "natureza_orig", "sentido_orig"], log)

    v, origens["TemposAtracacaoParalisacao"] = fonte(con, "TemposAtracacaoParalisacao")
    con.sql(f"""
        CREATE OR REPLACE TABLE stg_paralisacao AS
        SELECT {ID.format(c=q('IDTemposDescontos'))} AS id_paralisacao,
               {ID.format(c=q('IDAtracacao'))} AS id_atracacao,
               trim("DescricaoTempoDesconto") AS motivo,
               {DT.format(c=q('DTInicio'))} AS dt_inicio,
               {DT.format(c=q('DTTermino'))} AS dt_termino
        FROM {v}
    """)
    corrigir_texto(con, "stg_paralisacao", ["motivo"], log)
    return origens


# ---------------------------------------------------------------------------
# Dimensões
# ---------------------------------------------------------------------------
def dim_instalacao(con) -> None:
    bench = pd.read_csv(C.REF_DIR / "benchmark_nordeste.csv", dtype=str)
    con.register("_bench", bench)
    con.sql("""
        CREATE OR REPLACE TABLE dInstalacao AS
        WITH base AS (
            SELECT cdtup,
                   mode(porto_atracacao) AS porto,
                   regexp_replace(trim(mode(complexo_portuario)), ' {2,}', ' ', 'g') AS complexo,
                   mode(tipo_autoridade) AS tipo, mode(municipio) AS municipio, mode(uf_nome) AS uf_nome,
                   mode(sguf) AS sguf, mode(regiao) AS regiao, mode(coordenadas) AS coord,
                   count(*) AS n
            FROM stg_atracacao GROUP BY cdtup
        ), coord AS (
            SELECT *, try_cast(split_part(coord, ',', 1) AS DOUBLE) AS lon,
                      try_cast(split_part(coord, ',', 2) AS DOUBLE) AS lat
            FROM base
        ), nomes AS (
            SELECT *,
                   CASE WHEN cdtup = 'BR' OR porto IS NULL THEN 'Instalação não identificada' ELSE porto END AS nome0
            FROM coord
        ), unicos AS (
            SELECT *, CASE WHEN count(*) OVER (PARTITION BY nome0) > 1
                           THEN nome0 || ' (' || coalesce(sguf, cdtup) || ')' ELSE nome0 END AS instalacao
            FROM nomes
        )
        SELECT u.cdtup AS IDInstalacao,
               u.instalacao AS Instalacao,
               CASE WHEN u.cdtup = 'BR' THEN u.instalacao
                    WHEN u.complexo IS NULL OR u.complexo ILIKE 'Sem complexo%' OR u.complexo ILIKE '%(Instalação Isolada)%'
                    THEN u.instalacao ELSE u.complexo END AS ComplexoPortuario,
               coalesce(u.complexo, 'Não informado') AS ComplexoPortuarioANTAQ,
               CASE WHEN u.cdtup = 'BR' THEN 'Não informado'
                    WHEN u.tipo = 'Porto Organizado' THEN 'Porto Organizado'
                    WHEN u.tipo = 'Terminal Autorizado' THEN 'TUP (Terminal Autorizado)'
                    ELSE 'Não informado' END AS TipoInstalacao,
               coalesce(u.municipio, 'Não informado') AS Municipio,
               coalesce(u.sguf, 'ND') AS UF,
               coalesce(u.uf_nome, 'Não informado') AS UFNome,
               coalesce(u.regiao, 'Não informada') AS Regiao,
               CASE WHEN u.lat BETWEEN -34 AND 6 AND u.lon BETWEEN -75 AND -28 THEN round(u.lat, 6) END AS Latitude,
               CASE WHEN u.lat BETWEEN -34 AND 6 AND u.lon BETWEEN -75 AND -28 THEN round(u.lon, 6) END AS Longitude,
               b.PortoBenchmark AS PortoBenchmarkNE,
               coalesce(try_cast(b.EhSuape AS INTEGER), 0) AS EhSuape,
               try_cast(b.OrdemBenchmark AS INTEGER) AS OrdemBenchmark,
               CASE WHEN b.EhSuape = '1' THEN 'Suape' WHEN b.PortoBenchmark IS NOT NULL THEN 'Pares do Nordeste'
                    ELSE 'Demais instalações' END AS GrupoBenchmark
        FROM unicos u LEFT JOIN _bench b ON b.IDInstalacao = u.cdtup
        ORDER BY 1
    """)
    con.unregister("_bench")
    # Coordenada do COMPLEXO = média das coordenadas oficiais das instalações do complexo, ponderada pelas
    # toneladas de todo o recorte (o ponto cai perto do terminal que mais movimenta). Ver DECISOES D21.
    con.sql("""
        CREATE OR REPLACE TABLE _coord_cx AS
        SELECT d.ComplexoPortuario,
               round(sum(d.Latitude * t.ton) / sum(t.ton), 6) AS lat_cx,
               round(sum(d.Longitude * t.ton) / sum(t.ton), 6) AS lon_cx
        FROM dInstalacao d
        JOIN (SELECT cdtup, sum(peso) AS ton FROM carga_mov GROUP BY 1) t ON t.cdtup = d.IDInstalacao
        WHERE d.Latitude IS NOT NULL AND t.ton > 0
        GROUP BY 1
    """)
    con.sql("ALTER TABLE dInstalacao ADD COLUMN LatitudeComplexo DOUBLE")
    con.sql("ALTER TABLE dInstalacao ADD COLUMN LongitudeComplexo DOUBLE")
    con.sql("""UPDATE dInstalacao SET LatitudeComplexo = c.lat_cx, LongitudeComplexo = c.lon_cx
                FROM _coord_cx c WHERE dInstalacao.ComplexoPortuario = c.ComplexoPortuario""")
    # Posição do rótulo no mapa: o ponto do complexo + deslocamento fixo para os complexos do litoral
    # Sudeste/Sul/Suape, onde os nomes se sobrepõem (etl/referencias/rotulos_mapa.csv).
    desloc = pd.read_csv(C.REF_DIR / "rotulos_mapa.csv")
    con.register("_desloc", desloc)
    con.sql("ALTER TABLE dInstalacao ADD COLUMN LatitudeRotulo DOUBLE")
    con.sql("ALTER TABLE dInstalacao ADD COLUMN LongitudeRotulo DOUBLE")
    con.sql("""UPDATE dInstalacao SET LatitudeRotulo = round(LatitudeComplexo + coalesce(d.dLat, 0), 6),
                                      LongitudeRotulo = round(LongitudeComplexo + coalesce(d.dLon, 0), 6)
                FROM (SELECT DISTINCT i.ComplexoPortuario, x.dLat, x.dLon FROM dInstalacao i
                      LEFT JOIN _desloc x ON x.ComplexoPortuario = i.ComplexoPortuario) d
                WHERE dInstalacao.ComplexoPortuario = d.ComplexoPortuario""")
    con.unregister("_desloc")


def dim_mercadoria(con) -> None:
    sh = json.loads(C.RAW_SH_FILE.read_text(encoding="utf-8"))["data"]["list"]
    sh4 = (pd.DataFrame(sh)[["headingCode", "heading", "chapterCode", "chapter"]]
           .drop_duplicates("headingCode").rename(columns={"headingCode": "cod", "heading": "desc_sh4",
                                                          "chapterCode": "cap", "chapter": "desc_cap"}))
    apel = pd.read_csv(C.REF_DIR / "apelidos_mercadoria.csv", dtype=str)
    grupos = pd.read_csv(C.REF_DIR / "grupos_sh2.csv", dtype=str)
    con.register("_sh4", sh4)
    con.register("_apel", apel)
    con.register("_grupos", grupos)
    con.sql("""
        CREATE OR REPLACE TABLE dMercadoria AS
        WITH usados AS (SELECT DISTINCT cd_mercadoria FROM carga_mov)
        SELECT u.cd_mercadoria AS CodMercadoria,
               CASE WHEN u.cd_mercadoria = 'CONTEINER' THEN 'Contêineres'
                    WHEN u.cd_mercadoria = 'NAO_INFORMADO' THEN 'Não informado'
                    WHEN a.Mercadoria IS NOT NULL THEN a.Mercadoria
                    WHEN s.desc_sh4 IS NOT NULL THEN
                         CASE WHEN length(s.desc_sh4) > 60 THEN left(s.desc_sh4, 57) || '...' ELSE s.desc_sh4 END
                         || ' [' || u.cd_mercadoria || ']'
                    ELSE 'Código ANTAQ ' || u.cd_mercadoria || ' (sem descrição)' END AS Mercadoria,
               CASE WHEN u.cd_mercadoria = 'CONTEINER' THEN 'Carga conteinerizada (todas as mercadorias em contêiner)'
                    ELSE coalesce(s.desc_sh4, 'Sem descrição na nomenclatura SH') END AS DescricaoSH4,
               coalesce(s.cap, '--') AS CapituloSH2,
               coalesce(s.desc_cap, CASE WHEN u.cd_mercadoria = 'CONTEINER' THEN 'Contêineres' ELSE 'Não classificado' END)
                   AS DescricaoCapituloSH2,
               CASE WHEN u.cd_mercadoria = 'CONTEINER' THEN 'Contêineres'
                    WHEN g.GrupoMercadoria IS NOT NULL THEN g.GrupoMercadoria
                    ELSE 'Outros' END AS GrupoMercadoria,
               CASE WHEN u.cd_mercadoria = 'CONTEINER' THEN 10
                    ELSE coalesce(try_cast(g.OrdemGrupo AS INTEGER), 11) END AS OrdemGrupo,
               CASE WHEN u.cd_mercadoria IN ('CONTEINER', 'NAO_INFORMADO') THEN 'Agrupamento do projeto'
                    WHEN s.desc_sh4 IS NOT NULL THEN 'Nomenclatura SH (Comex Stat/MDIC)'
                    ELSE 'Código especial ANTAQ sem tabela oficial disponível' END AS FonteDescricao
        FROM usados u
        LEFT JOIN _sh4 s ON s.cod = u.cd_mercadoria
        LEFT JOIN _apel a ON a.CodMercadoria = u.cd_mercadoria
        LEFT JOIN _grupos g ON s.cap BETWEEN g.CapituloIni AND g.CapituloFim
        ORDER BY 1
    """)
    for n in ("_sh4", "_apel", "_grupos"):
        con.unregister(n)


def dims_pequenas(con) -> None:
    con.sql("""
        CREATE OR REPLACE TABLE dNavegacao AS
        SELECT * FROM (VALUES
            (1, 'Longo Curso', 'Longo Curso', 1),
            (2, 'Cabotagem', 'Cabotagem', 2),
            (3, 'Interior', 'Interior', 3),
            (4, 'Apoio Marítimo', 'Apoio', 4),
            (5, 'Apoio Portuário', 'Apoio', 5),
            (9, 'Não informado', 'Não informado', 9)
        ) t(CodNavegacao, Navegacao, GrupoNavegacao, OrdemNavegacao)
    """)
    con.sql("""
        CREATE OR REPLACE TABLE dNaturezaCarga AS
        SELECT * FROM (VALUES
            (1, 'Granel Sólido', 'Granel Sólido', 1),
            (2, 'Granel Líquido e Gasoso', 'Granel Líquido e Gasoso', 2),
            (3, 'Carga Geral', 'Carga Geral', 3),
            (4, 'Contêiner', 'Carga Conteinerizada', 4)
        ) t(CodNatureza, NaturezaCarga, NaturezaCargaANTAQ, OrdemNatureza)
    """)
    con.sql("""
        CREATE OR REPLACE TABLE dSentido AS
        SELECT * FROM (VALUES
            (1, 'Embarque', 'Embarcados', 1),
            (2, 'Desembarque', 'Desembarcados', 2),
            (9, 'Não informado', 'Não Informado', 9)
        ) t(CodSentido, Sentido, SentidoANTAQ, OrdemSentido)
    """)


# ---------------------------------------------------------------------------
# Fatos
# ---------------------------------------------------------------------------
def fatos(con, log: list) -> None:
    ano_ini, ano_fim = C.ANO_INICIAL, C.ANO_FINAL
    # Atracações do recorte (por data de desatracação)
    con.sql(f"""
        CREATE OR REPLACE TABLE atrac AS
        SELECT a.*, year(dt_desatracacao) AS ano, date_trunc('month', dt_desatracacao)::DATE AS data_ref
        FROM stg_atracacao a
        WHERE year(dt_desatracacao) BETWEEN {ano_ini} AND {ano_fim}
    """)
    fora = con.sql(f"SELECT count(*) FROM stg_atracacao WHERE dt_desatracacao IS NULL "
                   f"OR year(dt_desatracacao) NOT BETWEEN {ano_ini} AND {ano_fim}").fetchall()[0][0]
    log.append({"regra": "R2 atracação fora do recorte ou sem data de desatracação (excluída)", "linhas": int(fora)})

    # Carga: regra oficial de movimentação
    con.sql("""
        CREATE OR REPLACE TABLE carga_rec AS
        SELECT c.*, a.ano, a.data_ref, a.cdtup
        FROM stg_carga c JOIN atrac a USING (id_atracacao)
    """)
    for r in con.sql("""SELECT ano, count(*) n, sum(peso) t FROM carga_rec WHERE coalesce(flag_mc, 0) <> 1
                         GROUP BY ano ORDER BY ano""").fetchall():
        log.append({"regra": "R1 carga sem movimentação (FlagMCOperacaoCarga<>1) fora da tonelagem",
                    "ano": r[0], "linhas": int(r[1]), "toneladas": round(r[2] or 0, 1)})
    orf = con.sql("SELECT count(*) FROM stg_carga WHERE id_atracacao NOT IN (SELECT id_atracacao FROM stg_atracacao)"
                  ).fetchall()[0][0]
    log.append({"regra": "R9 carga sem atracação correspondente (órfã, excluída)", "linhas": int(orf)})

    con.sql("""
        CREATE OR REPLACE TABLE carga_mov AS
        SELECT c.id_carga, c.id_atracacao, c.ano, c.data_ref, c.cdtup,
               CASE WHEN c.natureza_orig = 'Carga Conteinerizada' THEN 'CONTEINER'
                    WHEN c.cd_mercadoria_orig IS NULL THEN 'NAO_INFORMADO'
                    ELSE c.cd_mercadoria_orig END AS cd_mercadoria,
               coalesce(n.CodNatureza, 3) AS natureza,
               coalesce(nv.CodNavegacao, 9) AS navegacao,
               coalesce(s.CodSentido, 9) AS sentido,
               c.tipo_operacao_carga, c.teu, c.peso
        FROM carga_rec c
        LEFT JOIN dNaturezaCarga n ON n.NaturezaCargaANTAQ = c.natureza_orig
        LEFT JOIN dSentido s ON s.SentidoANTAQ = c.sentido_orig
        LEFT JOIN dNavegacao nv ON nv.Navegacao = c.navegacao
        WHERE c.flag_mc = 1
    """)
    n_cont = con.sql("SELECT count(*) FROM carga_mov WHERE cd_mercadoria = 'CONTEINER'").fetchall()[0][0]
    log.append({"regra": "R8 carga conteinerizada agrupada na mercadoria 'Contêineres'", "linhas": int(n_cont)})

    # Toneladas e natureza predominante por atracação
    con.sql("""
        CREATE OR REPLACE TABLE carga_atrac AS
        -- somas em DECIMAL (resultado idêntico entre execuções) e desempate explícito da natureza predominante
        WITH por_nat AS (
            SELECT id_atracacao, natureza, sum(peso::DECIMAL(24, 6)) AS peso_nat, sum(teu::DECIMAL(18, 2)) AS teu_nat
            FROM carga_mov GROUP BY 1, 2
        ), ordenado AS (
            SELECT *, row_number() OVER (PARTITION BY id_atracacao ORDER BY peso_nat DESC, natureza) AS ordem
            FROM por_nat
        )
        SELECT id_atracacao, sum(peso_nat)::DOUBLE AS toneladas, sum(teu_nat)::DOUBLE AS teu,
               max(natureza) FILTER (WHERE ordem = 1) AS natureza_predominante
        FROM ordenado GROUP BY 1
    """)

    # Tempos oficiais da ANTAQ (horas) + limpeza
    con.sql("""
        CREATE OR REPLACE TABLE atrac_t AS
        SELECT a.id_atracacao, a.ano, a.data_ref, a.cdtup, a.id_berco,
               a.dt_chegada, a.dt_atracacao, a.dt_desatracacao,
               coalesce(nv.CodNavegacao, 9) AS navegacao,
               coalesce(a.tipo_operacao, 'Não informado') AS tipo_operacao,
               coalesce(ca.toneladas, 0) AS toneladas, coalesce(ca.teu, 0) AS teu,
               CASE WHEN coalesce(ca.toneladas, 0) > 0 THEN 1 ELSE 0 END AS com_carga,
               coalesce(ca.natureza_predominante, 0) AS natureza,
               t.t_espera_atracacao AS espera, t.t_operacao AS operacao,
               t.t_atracado AS atracado, t.t_estadia AS estadia
        FROM atrac a
        LEFT JOIN stg_tempos t USING (id_atracacao)
        LEFT JOIN carga_atrac ca USING (id_atracacao)
        LEFT JOIN dNavegacao nv ON nv.Navegacao = a.navegacao_atracacao
    """)
    n_sem = con.sql("SELECT ano, count(*) FROM atrac_t WHERE com_carga = 0 GROUP BY 1 ORDER BY 1").fetchall()
    for r in n_sem:
        log.append({"regra": "R11 atracação sem movimentação de carga (fora de fAtracacao)", "ano": r[0],
                    "linhas": int(r[1])})
    con.sql("DELETE FROM atrac_t WHERE com_carga = 0")
    metricas = ["espera", "operacao", "atracado", "estadia"]
    for m in metricas:
        for r in con.sql(f"SELECT ano, count(*) FROM atrac_t WHERE {m} < 0 GROUP BY 1 ORDER BY 1").fetchall():
            log.append({"regra": "R3 tempo negativo descartado", "metrica": m, "ano": r[0], "linhas": int(r[1])})
        con.sql(f"UPDATE atrac_t SET {m} = NULL WHERE {m} < 0")
        for r in con.sql(f"SELECT ano, count(*) FROM atrac_t WHERE {m} IS NULL GROUP BY 1 ORDER BY 1").fetchall():
            log.append({"regra": "R4 tempo ausente (sem a data correspondente)", "metrica": m, "ano": r[0],
                        "linhas": int(r[1])})
    # operação maior que o tempo atracado é inconsistente -> operação descartada
    for r in con.sql("SELECT ano, count(*) FROM atrac_t WHERE operacao > atracado GROUP BY 1 ORDER BY 1").fetchall():
        log.append({"regra": "R10 tempo de operação maior que o tempo atracado (operação descartada)",
                    "ano": r[0], "linhas": int(r[1])})
    con.sql("UPDATE atrac_t SET operacao = NULL WHERE operacao > atracado")

    # Limites de outlier (P99,5 por natureza de carga predominante), só tempos
    p = C.PERCENTIL_OUTLIER_TEMPO
    con.sql(f"""
        CREATE OR REPLACE TABLE limites_tempo AS
        SELECT natureza, {", ".join(f"quantile_cont({m}, {p}) AS lim_{m}" for m in metricas)}
        FROM atrac_t GROUP BY natureza
    """)
    for m in metricas:
        for r in con.sql(f"""SELECT a.ano, count(*) FROM atrac_t a JOIN limites_tempo l USING (natureza)
                             WHERE a.{m} > l.lim_{m} GROUP BY 1 ORDER BY 1""").fetchall():
            log.append({"regra": f"R5 tempo acima do P{p*100:g} da natureza de carga (limitado ao percentil)",
                        "metrica": m, "ano": r[0], "linhas": int(r[1])})
        con.sql(f"""UPDATE atrac_t SET {m} = l.lim_{m} FROM limites_tempo l
                    WHERE atrac_t.natureza = l.natureza AND atrac_t.{m} > l.lim_{m}""")

    con.sql("""
        CREATE OR REPLACE TABLE fAtracacao AS
        SELECT id_atracacao AS IDAtracacao, cdtup AS IDInstalacao, id_berco AS IDBerco,
               dt_chegada AS DataChegada, dt_atracacao AS DataAtracacao, dt_desatracacao AS DataDesatracacao,
               navegacao AS CodNavegacao, natureza AS CodNatureza,
               round(espera, 2) AS EsperaAtracacao_h, round(operacao, 2) AS Operacao_h,
               round(atracado, 2) AS Atracado_h, round(estadia, 2) AS Estadia_h,
               round(toneladas, 3) AS Toneladas, round(teu, 1) AS TEU
        FROM atrac_t ORDER BY DataDesatracacao, IDAtracacao
    """)

    con.sql("""
        CREATE OR REPLACE TABLE fCarga AS
        SELECT data_ref AS DataRef, cdtup AS IDInstalacao, cd_mercadoria AS CodMercadoria,
               natureza AS CodNatureza, navegacao AS CodNavegacao, sentido AS CodSentido,
               round(sum(peso::DECIMAL(24, 6)), 3)::DOUBLE AS Toneladas, round(sum(teu::DECIMAL(18, 2)), 1)::DOUBLE AS TEU,
               count(*) AS NumRegistros
        FROM carga_mov GROUP BY ALL ORDER BY 1, 2, 3, 4, 5, 6
    """)

    # Paralisações: horas por evento, limpas
    con.sql("""
        CREATE OR REPLACE TABLE paral AS
        SELECT p.id_paralisacao, p.id_atracacao, a.ano, a.data_ref, a.cdtup,
               coalesce(p.motivo, 'Não informado') AS motivo, coalesce(ca.natureza_predominante, 0) AS natureza,
               date_diff('second', p.dt_inicio, p.dt_termino) / 3600.0 AS horas
        FROM stg_paralisacao p JOIN atrac a USING (id_atracacao)
        LEFT JOIN carga_atrac ca USING (id_atracacao)
    """)
    for r in con.sql("SELECT ano, count(*) FROM paral WHERE horas IS NULL OR horas < 0 GROUP BY 1 ORDER BY 1").fetchall():
        log.append({"regra": "R6 paralisação com duração negativa ou sem data (descartada)", "ano": r[0],
                    "linhas": int(r[1])})
    con.sql("DELETE FROM paral WHERE horas IS NULL OR horas < 0")
    con.sql(f"""CREATE OR REPLACE TABLE limites_paral AS
                SELECT natureza, quantile_cont(horas, {p}) AS lim FROM paral GROUP BY 1""")
    for r in con.sql("""SELECT ano, count(*) FROM paral JOIN limites_paral l USING (natureza)
                        WHERE horas > l.lim GROUP BY 1 ORDER BY 1""").fetchall():
        log.append({"regra": f"R6b paralisação acima do P{p*100:g} da natureza de carga (limitada)", "ano": r[0],
                    "linhas": int(r[1])})
    con.sql("UPDATE paral SET horas = l.lim FROM limites_paral l WHERE paral.natureza = l.natureza AND horas > l.lim")
    con.sql("""
        CREATE OR REPLACE TABLE fParalisacao AS
        SELECT data_ref AS DataRef, cdtup AS IDInstalacao, motivo AS MotivoParalisacao,
               round(sum(horas::DECIMAL(24, 6)), 3)::DOUBLE AS HorasParalisadas, count(*) AS NumOcorrencias
        FROM paral GROUP BY ALL ORDER BY 1, 2, 3
    """)
    # nome curto do motivo (rótulo de eixo legível); motivo sem nome curto mantém o texto da ANTAQ
    curtos = pd.read_csv(C.REF_DIR / "motivos_paralisacao_curto.csv", dtype=str)
    con.register("_curtos", curtos)
    con.sql("""
        CREATE OR REPLACE TABLE fParalisacao AS
        SELECT p.DataRef, p.IDInstalacao, coalesce(c.MotivoCurto, p.MotivoParalisacao) AS MotivoCurto,
               p.MotivoParalisacao, p.HorasParalisadas, p.NumOcorrencias
        FROM fParalisacao p LEFT JOIN _curtos c USING (MotivoParalisacao)
        ORDER BY 1, 2, 4
    """)
    con.unregister("_curtos")


def main() -> int:
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    log: list[dict] = []
    origens = staging(con, log)
    dims_pequenas(con)
    fatos(con, log)
    dim_instalacao(con)
    dim_mercadoria(con)
    meta = {"origens": origens, "log": log}
    (C.RAW_DIR / "transform_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str),
                                                   encoding="utf-8")
    for t in ["fAtracacao", "fCarga", "fParalisacao", "dInstalacao", "dMercadoria", "dNavegacao",
              "dNaturezaCarga", "dSentido"]:
        print(f"{t:16s} {con.sql(f'SELECT count(*) FROM {t}').fetchall()[0][0]:>10,} linhas")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
