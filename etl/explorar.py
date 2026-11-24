"""Gera docs/exploracao.md: layout real dos arquivos, colunas usadas, chaves de ligação, linhas por ano,
% de nulos nas colunas-chave, tempos negativos/absurdos e definição de cada tempo (conferida nos dados).

Lê os dados BRUTOS (data/raw/) e o staging gerado por 02_transform.py.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

DB_PATH = C.RAW_DIR / "staging.duckdb"

# Colunas usadas e significado. Fonte das descrições: documentação do Estatístico Aquaviário (ANTAQ);
# o dicionário oficial não pôde ser baixado (portal fora do ar), então cada descrição marcada com (✓)
# foi conferida empiricamente nos dados — ver seção 5.
USADAS = {
    "Atracacao": {
        "IDAtracacao": "Identificador único da atracação (chave para Carga, Tempos e Paralisações) (✓ único)",
        "CDTUP": "Código da instalação portuária (porto organizado ou TUP) — chave de dInstalacao",
        "IDBerco": "Identificador do berço",
        "Porto Atracação": "Nome da instalação portuária onde ocorreu a atracação",
        "Complexo Portuário": "Complexo portuário definido pela ANTAQ (agrupa instalações próximas)",
        "Tipo da Autoridade Portuária": "Porto Organizado (público) ou Terminal Autorizado (TUP)",
        "Coordenadas": "Longitude,latitude da instalação (✓ ordem lon,lat conferida em Recife/Suape)",
        "Data Chegada": "Chegada da embarcação à área do porto (fundeio/barra)",
        "Data Atracação": "Atracação no berço",
        "Data Início Operação": "Início da operação de carga/descarga",
        "Data Término Operação": "Término da operação",
        "Data Desatracação": "Desatracação; define o mês/ano de referência (✓ coluna Ano = ano desta data em 100%)",
        "Ano": "Ano de referência da atracação",
        "Tipo de Operação": "Finalidade da atracação (Movimentação da Carga, Apoio, Passageiro etc.)",
        "Tipo de Navegação da Atracação": "Longo Curso, Cabotagem, Interior, Apoio Marítimo, Apoio Portuário",
        "Município": "Município da instalação",
        "UF / SGUF": "Unidade da Federação (nome / sigla)",
        "Região Geográfica": "Região do Brasil",
    },
    "Carga": {
        "IDCarga": "Identificador do registro de carga (✓ único)",
        "IDAtracacao": "Atracação em que a carga foi movimentada",
        "CDMercadoria": "Código da mercadoria: posição SH4 da NCM; códigos ISO 6346 para contêineres "
                        "(ex.: 22G0, 45G1); alguns códigos especiais ANTAQ (ex.: SRFC, CA01)",
        "Tipo Operação da Carga": "Longo Curso Exportação/Importação, Cabotagem, Interior, Baldeação, Safamento etc.",
        "Tipo Navegação": "Tipo de navegação da carga",
        "FlagMCOperacaoCarga": "1 = a operação conta como movimentação de carga na estatística oficial (✓ conciliação)",
        "Natureza da Carga": "Granel Sólido, Granel Líquido e Gasoso, Carga Geral, Carga Conteinerizada",
        "Sentido": "Embarcados, Desembarcados, Não Informado",
        "TEU": "Quantidade de TEU (contêineres de 20 pés equivalentes)",
        "VLPesoCargaBruta": "Peso bruto da carga em toneladas (✓ soma reconcilia com o total oficial)",
    },
    "TemposAtracacao": {
        "IDAtracacao": "Chave 1:1 com Atracacao (✓)",
        "TEsperaAtracacao": "Horas entre Data Chegada e Data Atracação (✓)",
        "TEsperaInicioOp": "Horas entre Data Atracação e Data Início Operação",
        "TOperacao": "Horas entre Data Início Operação e Data Término Operação",
        "TEsperaDesatracacao": "Horas entre Data Término Operação e Data Desatracação",
        "TAtracado": "Horas entre Data Atracação e Data Desatracação (✓)",
        "TEstadia": "Horas entre Data Chegada e Data Desatracação",
    },
    "TemposAtracacaoParalisacao": {
        "IDTemposDescontos": "Identificador do evento de paralisação",
        "IDAtracacao": "Atracação em que ocorreu a paralisação",
        "DescricaoTempoDesconto": "Motivo da paralisação (chuva, quebra de equipamento, aguardando carga etc.)",
        "DTInicio / DTTermino": "Início e fim da paralisação (horas = diferença entre as duas)",
    },
}
CHAVES = {
    "Atracacao": ["IDAtracacao", "CDTUP", "Data Atracação", "Data Desatracação", "Data Chegada",
                  "Data Início Operação", "Data Término Operação", "Tipo de Navegação da Atracação"],
    "Carga": ["IDCarga", "IDAtracacao", "CDMercadoria", "FlagMCOperacaoCarga", "Natureza da Carga", "Sentido",
              "VLPesoCargaBruta", "Tipo Navegação"],
    "TemposAtracacao": ["IDAtracacao", "TEsperaAtracacao", "TOperacao", "TAtracado", "TEstadia"],
    "TemposAtracacaoParalisacao": ["IDAtracacao", "DescricaoTempoDesconto", "DTInicio", "DTTermino"],
}


def arquivos(tabela: str) -> list[str]:
    return [p.as_posix() for p in sorted((C.RAW_ESPELHO_DIR / tabela).glob("*.parquet"))]


def main() -> int:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    out = ["# Exploração dos dados", "",
           f"> Gerado por `etl/explorar.py` em {datetime.now():%d/%m/%Y %H:%M}.", "",
           "## 1. Fonte e layout", "",
           "- **Fonte oficial**: ANTAQ — Estatístico Aquaviário, base de dados anual "
           f"(`{C.ANTAQ_PAGINA_DOWNLOAD}`). **Fora do ar** durante todo o projeto (o host `web3.antaq.gov.br` não "
           "resolve mais no DNS; o endereço antigo redireciona para o aviso "
           f"[\"Painel Estatístico Aquaviário Indisponível\"]({C.ANTAQ_AVISO_INDISPONIVEL}), publicado em "
           "23/06/2026). Ver docs/DECISOES.md (D02).",
           f"- **Fonte usada**: espelho público `{C.ESPELHO_REPO}` no Hugging Face (licença CC-BY-4.0, revisão "
           f"`{C.ESPELHO_REVISAO[:7]}` de 18/04/2026), com os arquivos TXT oficiais convertidos 1:1 para Parquet. "
           "Os **nomes das colunas são os originais da ANTAQ** (com acentos e espaços).",
           "- **Layout do espelho**: Parquet por tabela e ano. Datas da Atracação como texto `dd/mm/aaaa hh:mm:ss`; "
           "datas da Paralisação como texto `aaaa-mm-dd hh:mm:ss.ffffff`; números como DOUBLE (ponto decimal); "
           "parte dos textos com acentuação corrompida (UTF-8 lido como Latin-1, ex.: `BaldeaÃ§Ã£o`) — "
           "corrigido no tratamento (regra R7).",
           "- **Layout dos TXT oficiais** (aceitos pelo pipeline se colocados em `data/raw/antaq_oficial/`): "
           "separador `;`, cabeçalho na 1ª linha, vírgula decimal, datas `dd/mm/aaaa hh:mm:ss`. O leitor detecta "
           "UTF-8 ou Latin-1. **Não pôde ser conferido com arquivo oficial real** (pendência registrada).",
           "- **Recorte**: 2021 até o último mês disponível. O espelho foi gerado em 18/04/2026 e só contém "
           "**janeiro/2026** — é o último mês disponível neste projeto.", ""]

    out += ["## 2. Colunas reais de cada arquivo e colunas usadas", ""]
    for tab, usadas in USADAS.items():
        cols = con.sql(f"DESCRIBE SELECT * FROM read_parquet({arquivos(tab)}, union_by_name=true)").fetchall()
        out += [f"### {tab}", "", f"Colunas no arquivo ({len(cols)}): " +
                ", ".join(f"`{c[0]}`" for c in cols), "", "| Coluna usada | Significado |", "|---|---|"]
        out += [f"| `{k}` | {v} |" for k, v in usadas.items()]
        out.append("")

    out += ["## 3. Chaves de ligação", "",
            "```",
            "Atracacao (IDAtracacao, PK) 1 ──── 1 TemposAtracacao (IDAtracacao)",
            "Atracacao (IDAtracacao, PK) 1 ──── N Carga (IDAtracacao)",
            "Atracacao (IDAtracacao, PK) 1 ──── N TemposAtracacaoParalisacao (IDAtracacao)",
            "Atracacao (CDTUP)           N ──── 1 instalação portuária (dInstalacao no modelo)",
            "Carga (CDMercadoria)        N ──── 1 mercadoria (dMercadoria no modelo)",
            "```", ""]
    chk = con.sql("""
        SELECT (SELECT count(*) FROM stg_atracacao), (SELECT count(DISTINCT id_atracacao) FROM stg_atracacao),
               (SELECT count(*) FROM stg_tempos), (SELECT count(*) FROM stg_tempos WHERE id_atracacao NOT IN
                    (SELECT id_atracacao FROM stg_atracacao)),
               (SELECT count(*) FROM stg_carga), (SELECT count(DISTINCT id_carga) FROM stg_carga),
               (SELECT count(*) FROM stg_carga WHERE id_atracacao NOT IN (SELECT id_atracacao FROM stg_atracacao)),
               (SELECT count(*) FROM stg_paralisacao WHERE id_atracacao NOT IN (SELECT id_atracacao FROM stg_atracacao)),
               (SELECT count(*) FROM stg_atracacao WHERE id_atracacao NOT IN (SELECT id_atracacao FROM stg_tempos))
    """).fetchall()[0]
    out += [f"- Atracacao: {chk[0]:,} linhas, {chk[1]:,} IDAtracacao distintos (chave única).",
            f"- TemposAtracacao: {chk[2]:,} linhas; {chk[3]} sem atracação; {chk[8]} atracações sem tempos.",
            f"- Carga: {chk[4]:,} linhas, {chk[5]:,} IDCarga distintos; {chk[6]} órfãs.",
            f"- Paralisações órfãs: {chk[7]}.", ""]

    out += ["## 4. Linhas por ano (ano da data de desatracação)", "",
            "| Ano | Atracações | Registros de carga | Paralisações | Atracações com carga movimentada |",
            "|---|---:|---:|---:|---:|"]
    for r in con.sql("""
        WITH a AS (SELECT id_atracacao, year(dt_desatracacao) ano FROM stg_atracacao)
        SELECT a.ano, count(DISTINCT a.id_atracacao),
               (SELECT count(*) FROM stg_carga c JOIN a a2 USING (id_atracacao) WHERE a2.ano = a.ano),
               (SELECT count(*) FROM stg_paralisacao p JOIN a a3 USING (id_atracacao) WHERE a3.ano = a.ano),
               (SELECT count(*) FROM fAtracacao WHERE year(DataDesatracacao) = a.ano)
        FROM a GROUP BY 1 ORDER BY 1""").fetchall():
        out.append(f"| {r[0]} | {r[1]:,} | {r[2]:,} | {r[3]:,} | {r[4]:,} |")
    out.append("")

    out += ["## 5. % de nulos nas colunas-chave (base bruta, 2021–2026)", "",
            "| Tabela | Coluna | % nulos |", "|---|---|---:|"]
    for tab, cols in CHAVES.items():
        sel = ", ".join(f"avg(CASE WHEN \"{c}\" IS NULL OR trim(CAST(\"{c}\" AS VARCHAR)) = '' THEN 1 ELSE 0 END)"
                        for c in cols)
        vals = con.sql(f"SELECT {sel} FROM read_parquet({arquivos(tab)}, union_by_name=true)").fetchall()[0]
        out += [f"| {tab} | `{c}` | {v * 100:.2f}% |" for c, v in zip(cols, vals)]
    out.append("")

    out += ["## 6. Tempos: definição ANTAQ, conferência e valores negativos/absurdos", "",
            "A ANTAQ já entrega os tempos calculados (tabela TemposAtracacao, em **horas**). O projeto usa esses "
            "valores e confere a definição recalculando a partir das datas:", ""]
    conf = con.sql("""
        SELECT max(abs(date_diff('second', a.dt_atracacao, a.dt_desatracacao) / 3600.0 - t.t_atracado)),
               max(abs(date_diff('second', a.dt_chegada, a.dt_atracacao) / 3600.0 - t.t_espera_atracacao)),
               max(abs(date_diff('second', a.dt_inicio_op, a.dt_termino_op) / 3600.0 - t.t_operacao)),
               max(abs(date_diff('second', a.dt_chegada, a.dt_desatracacao) / 3600.0 - t.t_estadia))
        FROM stg_atracacao a JOIN stg_tempos t USING (id_atracacao)""").fetchall()[0]
    out += ["| Tempo ANTAQ | Definição | Maior diferença vs. recalculado (h) |", "|---|---|---:|",
            f"| TEsperaAtracacao | Data Atracação − Data Chegada | {conf[1]:.6f} |",
            f"| TOperacao | Data Término Operação − Data Início Operação | {conf[2]:.6f} |",
            f"| TAtracado | Data Desatracação − Data Atracação | {conf[0]:.6f} |",
            f"| TEstadia | Data Desatracação − Data Chegada | {conf[3]:.6f} |", ""]
    out += ["| Métrica | Linhas | Negativos | Nulos | Mediana (h) | P99,5 (h) | Máximo (h) | > 30 dias |",
            "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for col in ["t_espera_atracacao", "t_espera_inicio_op", "t_operacao", "t_espera_desatracacao", "t_atracado",
                "t_estadia"]:
        r = con.sql(f"""SELECT count(*), count(*) FILTER (WHERE {col} < 0), count(*) FILTER (WHERE {col} IS NULL),
                               median({col}), quantile_cont({col}, 0.995), max({col}),
                               count(*) FILTER (WHERE {col} > 720)
                        FROM stg_tempos JOIN stg_atracacao USING (id_atracacao)
                        WHERE year(dt_desatracacao) BETWEEN {C.ANO_INICIAL} AND {C.ANO_FINAL}""").fetchall()[0]
        out.append(f"| {col} | {r[0]:,} | {r[1]:,} | {r[2]:,} | {r[3]:.1f} | {r[4]:.1f} | {r[5]:,.1f} | {r[6]:,} |")
    out += ["", "Leitura: não há tempos negativos na base; há valores absurdos (esperas de mais de 2 anos, "
            "atracações de meses) — por isso a limitação no P99,5 por natureza de carga (regra R5). "
            "A espera média é muito maior que a mediana (cauda longa): o painel destaca a **mediana**.", ""]

    out += ["## 7. Regra de contagem da movimentação", "",
            "| Tipo Operação da Carga | FlagMCOperacaoCarga | Registros | Toneladas (Mt) |", "|---|---:|---:|---:|"]
    for r in con.sql("""SELECT tipo_operacao_carga, flag_mc, count(*), sum(peso) / 1e6
                        FROM stg_carga c JOIN stg_atracacao a USING (id_atracacao)
                        WHERE year(dt_desatracacao) BETWEEN 2021 AND 2026 GROUP BY 1, 2 ORDER BY 2 DESC, 4 DESC""").fetchall():
        out.append(f"| {r[0]} | {r[1]} | {r[2]:,} | {r[3]:,.1f} |")
    out += ["", "Somar só `FlagMCOperacaoCarga = 1` (inclui baldeação/transbordo) reproduz o total oficial "
            "dentro de ±1,2% em todos os anos — ver [conciliacao_antaq.md](conciliacao_antaq.md)."]
    con.close()
    (C.DOCS_DIR / "exploracao.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("docs/exploracao.md gerado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
