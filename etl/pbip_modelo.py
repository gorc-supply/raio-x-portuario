"""Especificação do modelo semântico (tabelas, Power Query, medidas DAX) usada por gerar_pbip.py.

Cada medida tem um comentário (vira a descrição da medida no Power BI, via `///` no TMDL).
As definições batem 1:1 com etl/kpis.py (usado para gerar docs/valores_referencia.md).
"""
from __future__ import annotations

CAMINHO_PADRAO = r"C:\projetos\raio-x-portuario\data\processed" + "\\"
COR_SUAPE = "#C9A96E"      # dourado do portfólio — Suape em todas as páginas
COR_PADRAO = "#8FB4D9"     # azul frio
COR_NEUTRA = "#5B6470"

# ---------------------------------------------------------------------------
# Power Query
# ---------------------------------------------------------------------------
def m_csv(arquivo: str, tipos: list[tuple[str, str]], extra: str = "") -> str:
    tipos_m = ", ".join(f'{{"{c}", {t}}}' for c, t in tipos)
    passos = [
        "let",
        f'    Fonte = Csv.Document(File.Contents(CaminhoDados & "{arquivo}"), '
        "[Delimiter = \",\", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),",
        "    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),",
        "    SemVazios = Table.TransformColumns(Cabecalhos, {}, each if _ = \"\" then null else _),",
        f'    Tipos = Table.TransformColumnTypes(SemVazios, {{{tipos_m}}}, "en-US")' + ("," if extra else ""),
    ]
    if extra:
        passos.append(extra)
    passos += ["in", "    " + ("Final" if extra else "Tipos")]
    return "\n".join(passos)


T = {"text": "type text", "int": "Int64.Type", "num": "type number", "date": "type date",
     "datetime": "type datetime", "bool": "type logical"}
DT = {"text": "string", "int": "int64", "num": "double", "date": "dateTime", "datetime": "dateTime",
      "bool": "boolean"}


def col(nome, tipo, oculto=False, fmt=None, sort=None, categoria=None, resumo="none", chave=False):
    return dict(nome=nome, tipo=tipo, oculto=oculto, fmt=fmt, sort=sort, categoria=categoria, resumo=resumo,
                chave=chave)


TABELAS: list[dict] = []

# --- fatos --------------------------------------------------------------------
FCARGA_COLS = [col("DataRef", "date", True, "dd/mm/yyyy"), col("IDInstalacao", "text", True),
               col("CodMercadoria", "text", True), col("CodNatureza", "int", True, "0"),
               col("CodNavegacao", "int", True, "0"), col("CodSentido", "int", True, "0"),
               col("Toneladas", "num", True, "#,0", resumo="sum"), col("TEU", "num", True, "#,0", resumo="sum"),
               col("NumRegistros", "int", True, "#,0", resumo="sum")]
TABELAS.append(dict(
    nome="fCarga", descricao="Movimentação de carga (FlagMCOperacaoCarga = 1) por mês x instalação x mercadoria "
    "x natureza x navegação x sentido.", colunas=FCARGA_COLS,
    m=m_csv("fCarga.csv", [(c["nome"], T[c["tipo"]]) for c in FCARGA_COLS])))

FATR_TIPOS = [("IDAtracacao", "int"), ("IDInstalacao", "text"), ("IDBerco", "text"), ("DataChegada", "datetime"),
              ("DataAtracacao", "datetime"), ("DataDesatracacao", "datetime"), ("CodNavegacao", "int"),
              ("CodNatureza", "int"), ("EsperaAtracacao_h", "num"), ("Operacao_h", "num"), ("Atracado_h", "num"),
              ("Estadia_h", "num"), ("Toneladas", "num"), ("TEU", "num")]
FATR_COLS = [col("IDAtracacao", "int", True, "0"), col("IDInstalacao", "text", True), col("IDBerco", "text", True),
             col("DataChegada", "datetime", True, "dd/mm/yyyy hh:nn"),
             col("DataAtracacao", "datetime", True, "dd/mm/yyyy hh:nn"),
             col("DataDesatracacao", "datetime", True, "dd/mm/yyyy hh:nn"),
             col("CodNavegacao", "int", True, "0"), col("CodNatureza", "int", True, "0"),
             col("EsperaAtracacao_h", "num", True, "#,0.0"), col("Operacao_h", "num", True, "#,0.0"),
             col("Atracado_h", "num", True, "#,0.0"), col("Estadia_h", "num", True, "#,0.0"),
             col("Toneladas", "num", True, "#,0", resumo="sum"), col("TEU", "num", True, "#,0", resumo="sum"),
             col("DataRef", "date", True, "dd/mm/yyyy")]
_tipos_atr = ", ".join(f'{{"{c}", {T[t]}}}' for c, t in FATR_TIPOS)
TABELAS.append(dict(
    nome="fAtracacao", descricao="Uma linha por atracação com movimentação de carga: datas, tempos (h, já "
    "limpos) e toneladas. Arquivos anuais combinados da pasta fAtracacao.", colunas=FATR_COLS,
    m="\n".join([
        "let",
        '    Arquivos = Folder.Files(CaminhoDados & "fAtracacao"),',
        '    SoCsv = Table.SelectRows(Arquivos, each Text.StartsWith([Name], "fAtracacao_") and [Extension] = ".csv"),',
        "    Tabelas = List.Transform(SoCsv[Content], each Table.PromoteHeaders(Csv.Document(_, "
        "[Delimiter = \",\", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]), [PromoteAllScalars = true])),",
        "    Combinado = Table.Combine(Tabelas),",
        "    SemVazios = Table.TransformColumns(Combinado, {}, each if _ = \"\" then null else _),",
        f'    Tipos = Table.TransformColumnTypes(SemVazios, {{{_tipos_atr}}}, "en-US"),',
        '    Final = Table.AddColumn(Tipos, "DataRef", each Date.StartOfMonth(DateTime.Date([DataDesatracacao])), type date)',
        "in",
        "    Final"])))

FPAR_COLS = [col("DataRef", "date", True, "dd/mm/yyyy"), col("IDInstalacao", "text", True),
             col("MotivoParalisacao", "text"), col("HorasParalisadas", "num", True, "#,0.0", resumo="sum"),
             col("NumOcorrencias", "int", True, "#,0", resumo="sum")]
TABELAS.append(dict(
    nome="fParalisacao", descricao="Horas paralisadas por mês x instalação x motivo (eventos de "
    "TemposAtracacaoParalisacao, já limpos).", colunas=FPAR_COLS,
    m=m_csv("fParalisacao.csv", [(c["nome"], T[c["tipo"]]) for c in FPAR_COLS])))

# --- dimensões ------------------------------------------------------------------
DINST_CSV = [col("IDInstalacao", "text", True, chave=True), col("Instalacao", "text"), col("ComplexoPortuario", "text"),
             col("ComplexoPortuarioANTAQ", "text"), col("TipoInstalacao", "text"),
             col("Municipio", "text", categoria="City"), col("UF", "text", categoria="StateOrProvince"),
             col("UFNome", "text"), col("Regiao", "text"),
             col("Latitude", "num", fmt="0.000000", categoria="Latitude"),
             col("Longitude", "num", fmt="0.000000", categoria="Longitude"),
             col("PortoBenchmarkNE", "text", sort="OrdemBenchmark"), col("EhSuape", "int", True, "0"),
             col("OrdemBenchmark", "int", True, "0"), col("GrupoBenchmark", "text")]
TABELAS.append(dict(
    nome="dInstalacao", descricao="Instalações portuárias (porto organizado ou TUP), complexo, UF, região, "
    "coordenadas e marcação do benchmark Nordeste.",
    colunas=DINST_CSV + [col("LocalMapa", "text", categoria="Place")],
    m=m_csv("dInstalacao.csv", [(c["nome"], T[c["tipo"]]) for c in DINST_CSV],
            extra='    Final = Table.AddColumn(Tipos, "LocalMapa", each [Municipio] & " - " & [UF] & ", Brasil", type text)')))

DMERC = [col("CodMercadoria", "text", True, chave=True), col("Mercadoria", "text"), col("DescricaoSH4", "text"),
         col("CapituloSH2", "text"), col("DescricaoCapituloSH2", "text"),
         col("GrupoMercadoria", "text", sort="OrdemGrupo"), col("OrdemGrupo", "int", True, "0"),
         col("FonteDescricao", "text")]
TABELAS.append(dict(nome="dMercadoria", descricao="Mercadorias: SH4 com descrição oficial do Comex Stat "
                    "(MDIC), nome curto e grupo simplificado do projeto.", colunas=DMERC,
                    m=m_csv("dMercadoria.csv", [(c["nome"], T[c["tipo"]]) for c in DMERC])))

DNAV = [col("CodNavegacao", "int", True, "0", chave=True), col("Navegacao", "text", sort="OrdemNavegacao"),
        col("GrupoNavegacao", "text"), col("OrdemNavegacao", "int", True, "0")]
TABELAS.append(dict(nome="dNavegacao", descricao="Tipo de navegação (ordem de exibição).", colunas=DNAV,
                    m=m_csv("dNavegacao.csv", [(c["nome"], T[c["tipo"]]) for c in DNAV])))
DNAT = [col("CodNatureza", "int", True, "0", chave=True), col("NaturezaCarga", "text", sort="OrdemNatureza"),
        col("NaturezaCargaANTAQ", "text"), col("OrdemNatureza", "int", True, "0")]
TABELAS.append(dict(nome="dNaturezaCarga", descricao="Natureza da carga (ordem de exibição).", colunas=DNAT,
                    m=m_csv("dNaturezaCarga.csv", [(c["nome"], T[c["tipo"]]) for c in DNAT])))
DSEN = [col("CodSentido", "int", True, "0", chave=True), col("Sentido", "text", sort="OrdemSentido"),
        col("SentidoANTAQ", "text"), col("OrdemSentido", "int", True, "0")]
TABELAS.append(dict(nome="dSentido", descricao="Sentido da movimentação (embarque/desembarque).", colunas=DSEN,
                    m=m_csv("dSentido.csv", [(c["nome"], T[c["tipo"]]) for c in DSEN])))

META = [col("DataProcessamento", "datetime", fmt="dd/mm/yyyy hh:nn"), col("UltimoMesDisponivel", "date", fmt="mm/yyyy"),
        col("AnoInicial", "int", fmt="0"), col("AnoFinal", "int", fmt="0"), col("OrigemDados", "text")]
TABELAS.append(dict(nome="Meta", oculta=True, descricao="Metadados do processamento (data e último mês com dado).",
                    colunas=META, m=m_csv("meta.csv", [(c["nome"], T[c["tipo"]]) for c in META])))

DCAL = [col("Data", "date", fmt="dd/mm/yyyy", chave=True), col("Ano", "int", fmt="0"),
        col("Trimestre", "text"), col("MesNum", "int", True, "0"), col("MesNome", "text", sort="MesNum"),
        col("MesAbrev", "text", sort="MesNum"), col("AnoMes", "text", sort="AnoMesNum"),
        col("AnoMesNum", "int", True, "0"), col("InicioMes", "date", fmt="mm/yyyy"),
        col("MesComDado", "bool")]
TABELAS.append(dict(
    nome="dCalendario", data=True,
    descricao="Calendário diário de 01/01/2021 a 31/12/2026 (Power Query), marcado como tabela de datas. "
    "MesComDado = mês até o último mês disponível na base.", colunas=DCAL,
    m="\n".join([
        "let",
        '    MetaCsv = Table.PromoteHeaders(Csv.Document(File.Contents(CaminhoDados & "meta.csv"), '
        "[Delimiter = \",\", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]), [PromoteAllScalars = true]),",
        '    UltimoMes = Date.FromText(MetaCsv{0}[UltimoMesDisponivel], [Format = "yyyy-MM-dd", Culture = "en-US"]),',
        "    Inicio = #date(2021, 1, 1),",
        "    Fim = #date(2026, 12, 31),",
        "    Datas = List.Dates(Inicio, Duration.Days(Fim - Inicio) + 1, #duration(1, 0, 0, 0)),",
        "    Base = Table.FromList(Datas, Splitter.SplitByNothing(), type table [Data = date]),",
        '    Abrev = {"jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"},',
        '    Nomes = {"janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", '
        '"outubro", "novembro", "dezembro"},',
        '    C1 = Table.AddColumn(Base, "Ano", each Date.Year([Data]), Int64.Type),',
        '    C2 = Table.AddColumn(C1, "Trimestre", each "T" & Text.From(Date.QuarterOfYear([Data])), type text),',
        '    C3 = Table.AddColumn(C2, "MesNum", each Date.Month([Data]), Int64.Type),',
        '    C4 = Table.AddColumn(C3, "MesNome", each Nomes{[MesNum] - 1}, type text),',
        '    C5 = Table.AddColumn(C4, "MesAbrev", each Abrev{[MesNum] - 1}, type text),',
        '    C6 = Table.AddColumn(C5, "AnoMes", each Abrev{[MesNum] - 1} & "/" & Text.End(Text.From([Ano]), 2), type text),',
        '    C7 = Table.AddColumn(C6, "AnoMesNum", each [Ano] * 100 + [MesNum], Int64.Type),',
        '    C8 = Table.AddColumn(C7, "InicioMes", each Date.StartOfMonth([Data]), type date),',
        '    Final = Table.AddColumn(C8, "MesComDado", each [Data] <= Date.EndOfMonth(UltimoMes), type logical)',
        "in",
        "    Final"])))

TABELAS.append(dict(nome="_Medidas", descricao="Tabela só de medidas, organizadas em pastas.",
                    colunas=[col("Medidas", "text", True)],
                    m='let\n    Fonte = #table(type table [Medidas = text], {})\nin\n    Fonte'))

RELACOES = [
    ("fCarga", "DataRef", "dCalendario", "Data"), ("fAtracacao", "DataRef", "dCalendario", "Data"),
    ("fParalisacao", "DataRef", "dCalendario", "Data"),
    ("fCarga", "IDInstalacao", "dInstalacao", "IDInstalacao"),
    ("fAtracacao", "IDInstalacao", "dInstalacao", "IDInstalacao"),
    ("fParalisacao", "IDInstalacao", "dInstalacao", "IDInstalacao"),
    ("fCarga", "CodMercadoria", "dMercadoria", "CodMercadoria"),
    ("fCarga", "CodNavegacao", "dNavegacao", "CodNavegacao"),
    ("fAtracacao", "CodNavegacao", "dNavegacao", "CodNavegacao"),
    ("fCarga", "CodNatureza", "dNaturezaCarga", "CodNatureza"),
    ("fAtracacao", "CodNatureza", "dNaturezaCarga", "CodNatureza"),
    ("fCarga", "CodSentido", "dSentido", "CodSentido"),
]

# ---------------------------------------------------------------------------
# Medidas (pasta, nome, formato, descrição, DAX)
# ---------------------------------------------------------------------------
F_T, F_H, F_P, F_VAR, F_TH, F_INT = "#,0", "#,0.0", "0.0%", "+0.0%;-0.0%;0.0%", "#,0", "0"

MEDIDAS: list[tuple[str, str, str | None, str, str]] = [
    # ---------------- Volume ----------------
    ("Volume", "Toneladas", F_T,
     "Toneladas movimentadas (peso bruto) — soma de VLPesoCargaBruta com FlagMCOperacaoCarga = 1 (regra ANTAQ).",
     "SUM ( fCarga[Toneladas] )"),
    ("Volume", "Toneladas AA", F_T,
     "Toneladas do mesmo período do ano anterior, considerando só os meses que têm dado no período atual "
     "(ex.: 2026 parcial compara jan/2026 com jan/2025).",
     """// meses do contexto atual que já têm dado publicado
VAR DatasComDado =
    CALCULATETABLE ( VALUES ( dCalendario[Data] ), dCalendario[MesComDado] = TRUE () )
RETURN
    IF (
        NOT ISEMPTY ( DatasComDado ),
        CALCULATE ( [Toneladas], SAMEPERIODLASTYEAR ( DatasComDado ) )
    )"""),
    ("Volume", "Var % Toneladas AA", F_VAR,
     "Variação percentual das toneladas contra o mesmo período do ano anterior.",
     """VAR Atual = [Toneladas]
VAR AnoAnterior = [Toneladas AA]
RETURN
    IF ( NOT ISBLANK ( AnoAnterior ), DIVIDE ( Atual - AnoAnterior, AnoAnterior ) )"""),
    ("Volume", "TEU", F_T, "Contêineres movimentados em TEU (unidade equivalente a um contêiner de 20 pés).",
     "SUM ( fCarga[TEU] )"),
    ("Volume", "Nº Atracações", F_T,
     "Número de atracações com movimentação de carga no período (mês da desatracação).",
     "COUNTROWS ( fAtracacao )"),
    ("Volume", "Toneladas por Atracação", F_T,
     "Toneladas médias por atracação = soma das toneladas das atracações ÷ nº de atracações (razão de somas).",
     "DIVIDE ( SUM ( fAtracacao[Toneladas] ), [Nº Atracações] )"),
    # ---------------- Participação ----------------
    ("Participação", "% do Total Brasil", F_P,
     "Participação das toneladas no total do Brasil do mesmo período (ignora filtros de instalação/região).",
     "DIVIDE ( [Toneladas], CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ) ) )"),
    ("Participação", "% Cabotagem", F_P,
     "Fatia das toneladas movimentada em navegação de cabotagem (entre portos brasileiros).",
     """DIVIDE (
    CALCULATE ( [Toneladas], dNavegacao[Navegacao] = "Cabotagem" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)"""),
    ("Participação", "% Longo Curso", F_P,
     "Fatia das toneladas movimentada em navegação de longo curso (comércio exterior).",
     """DIVIDE (
    CALCULATE ( [Toneladas], dNavegacao[Navegacao] = "Longo Curso" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)"""),
    ("Participação", "% Contêiner", F_P,
     "Fatia das toneladas movimentada em contêiner.",
     """DIVIDE (
    CALCULATE ( [Toneladas], dNaturezaCarga[NaturezaCarga] = "Contêiner" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNaturezaCarga ) )
)"""),
    ("Participação", "Ranking Porto", F_INT,
     "Posição por toneladas entre as instalações (ou complexos) visíveis no visual — 1 = maior.",
     """VAR T = [Toneladas]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( T ), BLANK (),
        ISINSCOPE ( dInstalacao[Instalacao] ) || ISINSCOPE ( dInstalacao[PortoBenchmarkNE] ),
            RANKX (
                ALLSELECTED ( dInstalacao[Instalacao], dInstalacao[PortoBenchmarkNE] ),
                [Toneladas], , DESC, DENSE
            ),
        ISINSCOPE ( dInstalacao[ComplexoPortuario] ),
            RANKX ( ALLSELECTED ( dInstalacao[ComplexoPortuario] ), [Toneladas], , DESC, DENSE )
    )"""),
    ("Participação", "Ranking Suape Brasil", F_INT,
     "Posição de Suape entre todas as instalações do Brasil por toneladas no período.",
     """VAR ToneladasSuape =
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
VAR Todas =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[Instalacao] ), "@t", [Toneladas] ),
        REMOVEFILTERS ( dInstalacao )
    )
RETURN
    IF ( NOT ISBLANK ( ToneladasSuape ), COUNTROWS ( FILTER ( Todas, [@t] > ToneladasSuape ) ) + 1 )"""),
    # ---------------- Eficiência ----------------
    ("Eficiência", "Espera Média (h)", F_H,
     "Média das horas entre a chegada do navio e a atracação. Sensível a filas longas.",
     "AVERAGE ( fAtracacao[EsperaAtracacao_h] )"),
    ("Eficiência", "Espera Mediana (h)", F_H,
     "Mediana das horas entre chegada e atracação: a espera do navio 'típico', sem distorção das filas extremas.",
     "MEDIAN ( fAtracacao[EsperaAtracacao_h] )"),
    ("Eficiência", "Tempo Atracado Médio (h)", F_H,
     "Média das horas entre atracação e desatracação (ocupação do berço por navio).",
     "AVERAGE ( fAtracacao[Atracado_h] )"),
    ("Eficiência", "Tempo de Operação Médio (h)", F_H,
     "Média das horas entre o início e o fim da operação de carga/descarga.",
     "AVERAGE ( fAtracacao[Operacao_h] )"),
    ("Eficiência", "% Atracado em Operação", F_P,
     "Horas de operação ÷ horas atracado (só atracações com os dois tempos). Quanto do tempo no berço é "
     "operação de fato.",
     """VAR HorasOperacao =
    CALCULATE (
        SUM ( fAtracacao[Operacao_h] ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Operacao_h] ) ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Atracado_h] ) )
    )
VAR HorasAtracado =
    CALCULATE (
        SUM ( fAtracacao[Atracado_h] ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Operacao_h] ) ),
        KEEPFILTERS ( NOT ISBLANK ( fAtracacao[Atracado_h] ) )
    )
RETURN
    DIVIDE ( HorasOperacao, HorasAtracado )"""),
    ("Eficiência", "Prancha Média Operacional (t/h)", F_TH,
     "Toneladas ÷ horas de operação (razão de somas, só atracações com tempo de operação > 0).",
     """DIVIDE (
    CALCULATE ( SUM ( fAtracacao[Toneladas] ), KEEPFILTERS ( fAtracacao[Operacao_h] > 0 ) ),
    CALCULATE ( SUM ( fAtracacao[Operacao_h] ), KEEPFILTERS ( fAtracacao[Operacao_h] > 0 ) )
)"""),
    ("Eficiência", "Prancha Média Geral (t/h)", F_TH,
     "Toneladas ÷ horas atracado (razão de somas): produtividade considerando todo o tempo no berço.",
     """DIVIDE (
    CALCULATE ( SUM ( fAtracacao[Toneladas] ), KEEPFILTERS ( fAtracacao[Atracado_h] > 0 ) ),
    CALCULATE ( SUM ( fAtracacao[Atracado_h] ), KEEPFILTERS ( fAtracacao[Atracado_h] > 0 ) )
)"""),
    ("Eficiência", "Horas Paralisadas", F_T,
     "Soma das horas de paralisação registradas durante as atracações (chuva, quebra, espera de carga etc.).",
     "SUM ( fParalisacao[HorasParalisadas] )"),
    # ---------------- Benchmark Nordeste ----------------
    ("Eficiência\\Benchmark Nordeste", "Espera Mediana Suape (h)", F_H,
     "Espera mediana de Suape no período, independentemente do porto filtrado.",
     "CALCULATE ( [Espera Mediana (h)], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Eficiência\\Benchmark Nordeste", "Espera Mediana Média Pares (h)", F_H,
     "Média simples das esperas medianas dos 8 pares do Nordeste (Pecém, Itaqui, Salvador, Aratu, Recife, "
     "Natal, Cabedelo, Maceió).",
     """VAR Pares =
    CALCULATETABLE (
        VALUES ( dInstalacao[PortoBenchmarkNE] ),
        REMOVEFILTERS ( dInstalacao ),
        dInstalacao[GrupoBenchmark] = "Pares do Nordeste"
    )
RETURN
    AVERAGEX (
        Pares,
        VAR Porto = dInstalacao[PortoBenchmarkNE]
        RETURN
            CALCULATE (
                [Espera Mediana (h)],
                REMOVEFILTERS ( dInstalacao ),
                dInstalacao[PortoBenchmarkNE] = Porto
            )
    )"""),
    ("Eficiência\\Benchmark Nordeste", "Diferença Espera Suape vs Pares (h)", "+#,0.0;-#,0.0;0.0",
     "Espera mediana de Suape menos a média dos pares (negativo = Suape espera menos).",
     "[Espera Mediana Suape (h)] - [Espera Mediana Média Pares (h)]"),
    ("Volume\\Suape", "Toneladas Suape", F_T, "Toneladas de Suape no período.",
     "CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Volume\\Suape", "TEU Suape", F_T, "TEU movimentados em Suape no período.",
     "CALCULATE ( [TEU], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Volume\\Suape", "Var % Toneladas Suape AA", F_VAR, "Variação de toneladas de Suape vs. ano anterior.",
     "CALCULATE ( [Var % Toneladas AA], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Participação", "% Contêiner Suape", F_P, "Fatia de contêiner nas toneladas de Suape.",
     "CALCULATE ( [% Contêiner], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    # ---------------- Auxiliares ----------------
    ("Auxiliares", "Última Atualização", None,
     "Texto com o último mês de dado da ANTAQ e a data de processamento do pipeline.",
     """"Dados ANTAQ até " & FORMAT ( MAX ( Meta[UltimoMesDisponivel] ), "mm/yyyy" )
    & " · processado em " & FORMAT ( MAX ( Meta[DataProcessamento] ), "dd/mm/yyyy" )"""),
    ("Auxiliares", "Título Dinâmico Período", None,
     "Texto do período filtrado com dado (ex.: 'em 2025', 'de 2021 a 2025', 'em jan/2026').",
     """VAR DataIni = CALCULATE ( MIN ( dCalendario[Data] ), dCalendario[MesComDado] = TRUE () )
VAR DataFim = CALCULATE ( MAX ( dCalendario[Data] ), dCalendario[MesComDado] = TRUE () )
VAR AnoIni = YEAR ( DataIni )
VAR AnoFim = YEAR ( DataFim )
VAR AnoCompleto = MONTH ( DataIni ) = 1 && MONTH ( DataFim ) = 12
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( DataIni ), "no período sem dados",
        AnoIni = AnoFim && AnoCompleto, "em " & AnoIni,
        AnoIni = AnoFim && MONTH ( DataIni ) = MONTH ( DataFim ), "em " & FORMAT ( DataFim, "mmm/yyyy" ),
        AnoIni = AnoFim, "de " & FORMAT ( DataIni, "mmm" ) & " a " & FORMAT ( DataFim, "mmm/yyyy" ),
        "de " & AnoIni & " a " & FORMAT ( DataFim, IF ( MONTH ( DataFim ) = 12, "yyyy", "mmm/yyyy" ) )
    )"""),
    ("Auxiliares", "Toneladas (Top 10)", F_T,
     "Toneladas só das 10 maiores instalações visíveis (para o gráfico de ranking).",
     "IF ( [Ranking Porto] <= 10, [Toneladas] )"),
    ("Auxiliares", "Toneladas (Top 10 mercadorias)", F_T,
     "Toneladas só das 10 maiores mercadorias visíveis.",
     """VAR Posicao =
    IF (
        ISINSCOPE ( dMercadoria[Mercadoria] ),
        RANKX ( ALLSELECTED ( dMercadoria[Mercadoria] ), [Toneladas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 10, [Toneladas] )"""),
    ("Auxiliares", "Horas Paralisadas (Top 10 motivos)", F_T,
     "Horas paralisadas só dos 10 motivos com mais horas no contexto.",
     """VAR Posicao =
    IF (
        ISINSCOPE ( fParalisacao[MotivoParalisacao] ),
        RANKX ( ALLSELECTED ( fParalisacao[MotivoParalisacao] ), [Horas Paralisadas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 10, [Horas Paralisadas] )"""),
    ("Auxiliares", "Cor Destaque Suape", None,
     "Cor das barras/pontos: dourado para Suape, azul para as demais (formatação condicional por valor de campo).",
     f'IF ( SELECTEDVALUE ( dInstalacao[EhSuape], 0 ) = 1, "{COR_SUAPE}", "{COR_PADRAO}" )'),
    ("Auxiliares", "Cor Texto Suape", None, "Cor do texto: dourado na linha de Suape, branco nas demais.",
     f'IF ( SELECTEDVALUE ( dInstalacao[EhSuape], 0 ) = 1, "{COR_SUAPE}", "#FFFFFF" )'),
    ("Auxiliares", "Cor Calor Espera", None,
     "Cor do mapa de calor da espera mediana: até 2 h, 6 h, 24 h, 72 h e acima de 72 h.",
     """VAR Espera = [Espera Mediana (h)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( Espera ), BLANK (),
        Espera <= 2, "#1E3A2F",
        Espera <= 6, "#2F5D46",
        Espera <= 24, "#7A6A3A",
        Espera <= 72, "#A0522D",
        "#8B1E2D"
    )"""),
    ("Auxiliares", "Cor Benchmark Espera", None,
     "Verde se a espera mediana do porto é menor ou igual à média dos pares; vermelho se maior.",
     """VAR Espera = [Espera Mediana (h)]
RETURN
    IF (
        NOT ISBLANK ( Espera ),
        IF ( Espera <= [Espera Mediana Média Pares (h)], "#1E3A2F", "#4A1C14" )
    )"""),
    # ---------------- Títulos (Auxiliares\\Títulos) ----------------
    ("Auxiliares\\Títulos", "Título KPI Brasil", None, "Título da página Visão Geral.",
     """VAR Mt = [Toneladas] / 1000000
VAR Variacao = [Var % Toneladas AA]
RETURN
    "Portos brasileiros movimentaram " & FORMAT ( Mt, "#,0.0" ) & " milhões de t " & [Título Dinâmico Período]
        & IF ( NOT ISBLANK ( Variacao ), " (" & FORMAT ( Variacao, "+0.0%;-0.0%" ) & " vs. ano anterior)" )"""),
    ("Auxiliares\\Títulos", "Título Linha Mensal", None, "Título do gráfico de linha mensal.",
     """"Toneladas por mês " & [Título Dinâmico Período] & " x mesmo mês do ano anterior\""""),
    ("Auxiliares\\Títulos", "Título Região", None, "Título do gráfico por região.",
     """VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Regiao] ), "@t", [Toneladas] ), [@t], DESC )
VAR Nome = MAXX ( Top, dInstalacao[Regiao] )
VAR Fatia = DIVIDE ( MAXX ( Top, [@t] ), [Toneladas] )
RETURN
    Nome & " concentra " & FORMAT ( Fatia, "0%" ) & " da carga " & [Título Dinâmico Período]"""),
    ("Auxiliares\\Títulos", "Título Top 10", None, "Título do ranking de instalações.",
     """VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Instalacao] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Top, dInstalacao[Instalacao] ) & " lidera com " & FORMAT ( MAXX ( Top, [@t] ) / 1000000, "#,0.0" )
        & " milhões de t " & [Título Dinâmico Período]"""),
    ("Auxiliares\\Títulos", "Título Benchmark Espera", None,
     "Título da página Nordeste & Suape: conclusão sobre a espera de Suape vs. pares.",
     """VAR Dif = [Diferença Espera Suape vs Pares (h)]
RETURN
    IF (
        ISBLANK ( Dif ), "Espera mediana: Suape x média dos pares",
        "Suape opera com espera mediana " & FORMAT ( ABS ( Dif ), "#,0.0" ) & " h "
            & IF ( Dif <= 0, "menor", "maior" ) & " que a média dos pares " & [Título Dinâmico Período]
    )"""),
    ("Auxiliares\\Títulos", "Título Crescimento Pares", None, "Título das barras de crescimento.",
     """VAR Pares =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[PortoBenchmarkNE] ), "@v", [Var % Toneladas AA] ),
        NOT ISBLANK ( dInstalacao[PortoBenchmarkNE] )
    )
VAR Top = TOPN ( 1, FILTER ( Pares, NOT ISBLANK ( [@v] ) ), [@v], DESC )
RETURN
    IF (
        ISEMPTY ( Top ), "Crescimento vs. ano anterior",
        "Maior crescimento " & [Título Dinâmico Período] & ": " & MAXX ( Top, dInstalacao[PortoBenchmarkNE] )
            & " (" & FORMAT ( MAXX ( Top, [@v] ), "+0.0%;-0.0%" ) & ")"
    )"""),
    ("Auxiliares\\Títulos", "Título Ranking Suape", None, "Texto do cartão de ranking de Suape.",
     """"Suape é a " & [Ranking Suape Brasil] & "ª maior instalação do Brasil " & [Título Dinâmico Período]"""),
    ("Auxiliares\\Títulos", "Título Mapa de Calor", None, "Título do mapa de calor.",
     """VAR Top =
    TOPN (
        1,
        CALCULATETABLE (
            ADDCOLUMNS ( VALUES ( dInstalacao[PortoBenchmarkNE] ), "@e", [Espera Mediana (h)] ),
            NOT ISBLANK ( dInstalacao[PortoBenchmarkNE] )
        ),
        [@e], DESC
    )
RETURN
    "Maior espera mediana entre os pares " & [Título Dinâmico Período] & ": " & MAXX ( Top, dInstalacao[PortoBenchmarkNE] )
        & " (" & FORMAT ( MAXX ( Top, [@e] ), "#,0" ) & " h)\""""),
    ("Auxiliares\\Títulos", "Título Operação", None, "Título das barras de % atracado em operação.",
     """"Suape usa " & FORMAT ( CALCULATE ( [% Atracado em Operação], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 ), "0%" )
    & " do tempo atracado operando " & [Título Dinâmico Período]"""),
    ("Auxiliares\\Títulos", "Título Paralisação", None, "Título das horas paralisadas por motivo.",
     """VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( fParalisacao[MotivoParalisacao] ), "@h", [Horas Paralisadas] ), [@h], DESC )
RETURN
    IF (
        ISEMPTY ( Top ), "Horas paralisadas por motivo",
        "Principal causa de paralisação: " & MAXX ( Top, fParalisacao[MotivoParalisacao] ) & " ("
            & FORMAT ( DIVIDE ( MAXX ( Top, [@h] ), [Horas Paralisadas] ), "0%" ) & " das horas)"
    )"""),
    ("Auxiliares\\Títulos", "Título Dispersão", None, "Título da dispersão espera x prancha.",
     """"Portos públicos " & [Título Dinâmico Período] & ": espera mediana (h) x prancha operacional (t/h)\""""),
    ("Auxiliares\\Títulos", "Título Natureza", None, "Título da composição por natureza de carga.",
     """VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dNaturezaCarga[NaturezaCarga] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Top, dNaturezaCarga[NaturezaCarga] ) & " responde por " & FORMAT ( DIVIDE ( MAXX ( Top, [@t] ), [Toneladas] ), "0%" )
        & " da carga " & [Título Dinâmico Período]"""),
    ("Auxiliares\\Títulos", "Título Mercadorias", None, "Título do top mercadorias.",
     """VAR Top =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dMercadoria[Mercadoria] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Top, dMercadoria[Mercadoria] ) & " é a principal mercadoria: " & FORMAT ( DIVIDE ( MAXX ( Top, [@t] ), [Toneladas] ), "0%" )
        & " das toneladas\""""),
    ("Auxiliares\\Títulos", "Título Sentido", None, "Título do embarque x desembarque.",
     """VAR Emb = CALCULATE ( [Toneladas], dSentido[Sentido] = "Embarque" )
RETURN
    FORMAT ( DIVIDE ( Emb, CALCULATE ( [Toneladas], REMOVEFILTERS ( dSentido ) ) ), "0%" ) & " das toneladas são embarque\""""),
    ("Auxiliares\\Títulos", "Título Navegação", None, "Título da movimentação por navegação.",
     """"Longo curso: " & FORMAT ( [% Longo Curso], "0%" ) & " · cabotagem: " & FORMAT ( [% Cabotagem], "0%" )
    & " das toneladas\""""),
]
