"""Especificação do modelo semântico (tabelas, Power Query, medidas DAX) usada por gerar_pbip.py.

Cada medida tem um comentário (vira a descrição da medida no Power BI, via `///` no TMDL).
As definições numéricas batem 1:1 com etl/kpis.py (usado para gerar docs/valores_referencia.md).

Nomes visíveis ao usuário em português correto, com acento (coluna do modelo pode ter nome diferente da coluna
do CSV: o TMDL guarda `sourceColumn` com o nome ASCII do arquivo).
"""
from __future__ import annotations

CAMINHO_PADRAO = r"C:\projetos\raio-x-portuario\data\processed" + "\\"
COR_SUAPE = "#C9A96E"      # dourado do portfólio — Suape em todas as páginas
COR_PADRAO = "#8FB4D9"     # azul frio — demais portos
COR_ANO_ANTERIOR = "#6B7380"  # cinza — ano anterior / referência
COR_TEXTO = "#FFFFFF"
COR_TEXTO_SUAVE = "#C9CDD3"
ANO_INICIAL, ANO_FINAL = 2021, 2025
MENOS = "\u2212"           # sinal de menos tipográfico (−)

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


def col(nome, tipo, oculto=False, fmt=None, sort=None, categoria=None, resumo="none", chave=False, rotulo=None):
    """`nome` = coluna do CSV (sourceColumn); `rotulo` = nome no modelo (visível, com acento)."""
    return dict(nome=nome, tipo=tipo, oculto=oculto, fmt=fmt, sort=sort, categoria=categoria, resumo=resumo,
                chave=chave, rotulo=rotulo or nome)


def tipos(cols):
    return [(c["nome"], T[c["tipo"]]) for c in cols if c["nome"] != "__calc__"]


TABELAS: list[dict] = []

# --- fatos --------------------------------------------------------------------
FCARGA = [col("DataRef", "date", True, "dd/mm/yyyy"), col("IDInstalacao", "text", True),
          col("CodMercadoria", "text", True), col("CodNatureza", "int", True, "0"),
          col("CodNavegacao", "int", True, "0"), col("CodSentido", "int", True, "0"),
          col("Toneladas", "num", True, "#,0", resumo="sum"), col("TEU", "num", True, "#,0", resumo="sum"),
          col("NumRegistros", "int", True, "#,0", resumo="sum")]
TABELAS.append(dict(
    nome="fCarga", descricao="Movimentação de carga (FlagMCOperacaoCarga = 1) por mês x instalação x mercadoria "
    "x natureza x navegação x sentido.", colunas=FCARGA, m=m_csv("fCarga.csv", tipos(FCARGA))))

FATR_TIPOS = [("IDAtracacao", "int"), ("IDInstalacao", "text"), ("IDBerco", "text"), ("DataChegada", "datetime"),
              ("DataAtracacao", "datetime"), ("DataDesatracacao", "datetime"), ("CodNavegacao", "int"),
              ("CodNatureza", "int"), ("EsperaAtracacao_h", "num"), ("Operacao_h", "num"), ("Atracado_h", "num"),
              ("Estadia_h", "num"), ("Toneladas", "num"), ("TEU", "num")]
FATR = [col("IDAtracacao", "int", True, "0"), col("IDInstalacao", "text", True), col("IDBerco", "text", True),
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
    "limpos) e toneladas. Arquivos anuais combinados da pasta fAtracacao.", colunas=FATR,
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

FPAR = [col("DataRef", "date", True, "dd/mm/yyyy"), col("IDInstalacao", "text", True),
        col("MotivoCurto", "text", rotulo="Motivo da Paralisação"),
        col("MotivoParalisacao", "text", rotulo="Motivo da Paralisação (texto ANTAQ)"),
        col("HorasParalisadas", "num", True, "#,0.0", resumo="sum"),
        col("NumOcorrencias", "int", True, "#,0", resumo="sum")]
TABELAS.append(dict(
    nome="fParalisacao", descricao="Horas paralisadas por mês x instalação x motivo (eventos de "
    "TemposAtracacaoParalisacao, já limpos).", colunas=FPAR, m=m_csv("fParalisacao.csv", tipos(FPAR))))

# --- dimensões ------------------------------------------------------------------
DINST = [col("IDInstalacao", "text", True, chave=True), col("Instalacao", "text", rotulo="Instalação"),
         col("ComplexoPortuario", "text", rotulo="Complexo Portuário"),
         col("ComplexoPortuarioANTAQ", "text", rotulo="Complexo Portuário (ANTAQ)"),
         col("TipoInstalacao", "text", rotulo="Tipo de Instalação"),
         col("Municipio", "text", categoria="City", rotulo="Município"),
         col("UF", "text", categoria="StateOrProvince"), col("UFNome", "text", rotulo="Nome da UF"),
         col("Regiao", "text", rotulo="Região"),
         col("Latitude", "num", fmt="0.000000", categoria="Latitude"),
         col("Longitude", "num", fmt="0.000000", categoria="Longitude"),
         col("PortoBenchmarkNE", "text", sort="OrdemBenchmark", rotulo="Porto (benchmark NE)"),
         col("EhSuape", "int", True, "0"), col("OrdemBenchmark", "int", True, "0"),
         col("GrupoBenchmark", "text", rotulo="Grupo do Benchmark"),
         col("LatitudeComplexo", "num", fmt="0.000000", categoria="Latitude", rotulo="Latitude do Complexo"),
         col("LongitudeComplexo", "num", fmt="0.000000", categoria="Longitude", rotulo="Longitude do Complexo"),
         col("LatitudeRotulo", "num", True, "0.000000", rotulo="Latitude do Rótulo"),
         col("LongitudeRotulo", "num", True, "0.000000", rotulo="Longitude do Rótulo")]
TABELAS.append(dict(
    nome="dInstalacao", descricao="Instalações portuárias (porto organizado ou TUP), complexo, UF, região, "
    "coordenadas oficiais (e do complexo, ponderadas por toneladas) e marcação do benchmark Nordeste.",
    colunas=DINST, m=m_csv("dInstalacao.csv", tipos(DINST))))

DMERC = [col("CodMercadoria", "text", True, chave=True), col("Mercadoria", "text"),
         col("DescricaoSH4", "text", rotulo="Descrição SH4"), col("CapituloSH2", "text", rotulo="Capítulo SH2"),
         col("DescricaoCapituloSH2", "text", rotulo="Descrição do Capítulo SH2"),
         col("GrupoMercadoria", "text", sort="OrdemGrupo", rotulo="Grupo de Mercadoria"),
         col("OrdemGrupo", "int", True, "0"), col("FonteDescricao", "text", rotulo="Fonte da Descrição")]
TABELAS.append(dict(nome="dMercadoria", descricao="Mercadorias: SH4 com descrição oficial do Comex Stat "
                    "(MDIC), nome curto e grupo simplificado do projeto.", colunas=DMERC,
                    m=m_csv("dMercadoria.csv", tipos(DMERC))))

DNAV = [col("CodNavegacao", "int", True, "0", chave=True),
        col("Navegacao", "text", sort="OrdemNavegacao", rotulo="Navegação"),
        col("GrupoNavegacao", "text", rotulo="Grupo de Navegação"), col("OrdemNavegacao", "int", True, "0")]
TABELAS.append(dict(nome="dNavegacao", descricao="Tipo de navegação (ordem de exibição).", colunas=DNAV,
                    m=m_csv("dNavegacao.csv", tipos(DNAV))))
DNAT = [col("CodNatureza", "int", True, "0", chave=True),
        col("NaturezaCarga", "text", sort="OrdemNatureza", rotulo="Natureza da Carga"),
        col("NaturezaCargaANTAQ", "text", rotulo="Natureza da Carga (ANTAQ)"),
        col("OrdemNatureza", "int", True, "0")]
TABELAS.append(dict(nome="dNaturezaCarga", descricao="Natureza da carga (ordem de exibição).", colunas=DNAT,
                    m=m_csv("dNaturezaCarga.csv", tipos(DNAT))))
DSEN = [col("CodSentido", "int", True, "0", chave=True), col("Sentido", "text", sort="OrdemSentido"),
        col("SentidoANTAQ", "text", rotulo="Sentido (ANTAQ)"), col("OrdemSentido", "int", True, "0")]
TABELAS.append(dict(nome="dSentido", descricao="Sentido da movimentação (embarque/desembarque).", colunas=DSEN,
                    m=m_csv("dSentido.csv", tipos(DSEN))))

META = [col("DataProcessamento", "datetime", fmt="dd/mm/yyyy hh:nn", rotulo="Data de Processamento"),
        col("UltimoMesDisponivel", "date", fmt="mm/yyyy", rotulo="Último Mês Disponível"),
        col("AnoInicial", "int", fmt="0", rotulo="Ano Inicial"), col("AnoFinal", "int", fmt="0", rotulo="Ano Final"),
        col("OrigemDados", "text", rotulo="Origem dos Dados")]
TABELAS.append(dict(nome="Meta", oculta=True, descricao="Metadados do processamento.", colunas=META,
                    m=m_csv("meta.csv", tipos(META))))

DCAL = [col("Data", "date", fmt="dd/mm/yyyy", chave=True), col("Ano", "int", fmt="0"),
        col("Trimestre", "text"), col("MesNum", "int", True, "0"),
        col("MesNome", "text", sort="MesNum", rotulo="Mês"),
        col("MesAbrev", "text", sort="MesNum", rotulo="Mês (abrev.)"),
        col("AnoMes", "text", sort="AnoMesNum", rotulo="Mês/Ano"),
        col("AnoMesNum", "int", True, "0"), col("InicioMes", "date", fmt="mm/yyyy", rotulo="Início do Mês"),
        col("MesComDado", "bool", rotulo="Mês com Dado")]
TABELAS.append(dict(
    nome="dCalendario", data=True,
    descricao=f"Calendário diário de 01/01/{ANO_INICIAL} a 31/12/{ANO_FINAL} (Power Query), marcado como tabela de "
    "datas. Mês com Dado = mês até o último mês disponível na base.", colunas=DCAL,
    m="\n".join([
        "let",
        '    MetaCsv = Table.PromoteHeaders(Csv.Document(File.Contents(CaminhoDados & "meta.csv"), '
        "[Delimiter = \",\", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]), [PromoteAllScalars = true]),",
        '    UltimoMes = Date.FromText(MetaCsv{0}[UltimoMesDisponivel], [Format = "yyyy-MM-dd", Culture = "en-US"]),',
        f"    Inicio = #date({ANO_INICIAL}, 1, 1),",
        f"    Fim = #date({ANO_FINAL}, 12, 31),",
        "    Datas = List.Dates(Inicio, Duration.Days(Fim - Inicio) + 1, #duration(1, 0, 0, 0)),",
        "    Base = Table.FromList(Datas, Splitter.SplitByNothing(), type table [Data = date]),",
        '    Abrev = {"jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"},',
        '    Nomes = {"janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", '
        '"outubro", "novembro", "dezembro"},',
        '    C1 = Table.AddColumn(Base, "Ano", each Date.Year([Data]), Int64.Type),',
        '    C2 = Table.AddColumn(C1, "Trimestre", each Text.From(Date.QuarterOfYear([Data])) & "º tri", type text),',
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
# Formatos (format strings no padrão do Power BI; a cultura do modelo é pt-BR)
# ---------------------------------------------------------------------------
F_T = "#,0"                                    # toneladas cheias
F_MI = '#,0.0" Mi t"'                          # milhões de toneladas
F_H = '#,0.0" h"'                              # horas
F_P = "0.0%"
F_VAR = f'+0.0%;"{MENOS}"0.0%;0.0%'            # percentual com sinal
F_TH = '#,0" t/h"'
F_INT = "#,0"
F_TEU = '#,0" TEU"'
F_GRAU = "0.000"


def rotulo(expr: str, fmt: str, sufixo: str = "") -> str:
    """Medida de texto para cartões (mostra exatamente o que queremos, sem 'Mi'/'Bi' automáticos)."""
    return f'VAR v = {expr}\nRETURN\n    IF ( NOT ISBLANK ( v ), FORMAT ( v, "{fmt}" ){(" & " + chr(34) + sufixo + chr(34)) if sufixo else ""} )'


def rotulo_var(expr: str) -> str:
    return (f"VAR v = {expr}\nRETURN\n    IF (\n        NOT ISBLANK ( v ),\n"
            f'        IF ( v >= 0, "+", "{MENOS}" ) & FORMAT ( ABS ( v ), "0.0%" )\n    )')


PER = "[Título Dinâmico Período]"

MEDIDAS: list[tuple[str, str, str | None, str, str]] = [
    # ---------------- Volume ----------------
    ("Volume", "Toneladas", F_T,
     "Toneladas movimentadas (peso bruto) — soma de VLPesoCargaBruta com FlagMCOperacaoCarga = 1 (regra ANTAQ).",
     "SUM ( fCarga[Toneladas] )"),
    ("Volume", "Toneladas (Mi t)", F_MI, "Toneladas em milhões, para eixos e rótulos de gráfico.",
     "DIVIDE ( [Toneladas], 1000000 )"),
    ("Volume", "Toneladas AA", F_T,
     "Toneladas do mesmo período do ano anterior, só nos meses que têm dado no período atual.",
     """// meses do contexto atual que têm dado publicado
VAR DatasComDado =
    CALCULATETABLE ( VALUES ( dCalendario[Data] ), dCalendario[Mês com Dado] = TRUE () )
RETURN
    IF (
        NOT ISEMPTY ( DatasComDado ),
        CALCULATE ( [Toneladas], SAMEPERIODLASTYEAR ( DatasComDado ) )
    )"""),
    ("Volume", "Toneladas AA (Mi t)", F_MI, "Toneladas do ano anterior em milhões.",
     "DIVIDE ( [Toneladas AA], 1000000 )"),
    ("Volume", "Var % Toneladas AA", F_VAR,
     "Variação percentual das toneladas contra o mesmo período do ano anterior.",
     """VAR Atual = [Toneladas]
VAR AnoAnterior = [Toneladas AA]
RETURN
    IF ( NOT ISBLANK ( AnoAnterior ), DIVIDE ( Atual - AnoAnterior, AnoAnterior ) )"""),
    ("Volume", "TEU", F_INT, "Contêineres movimentados em TEU (unidade equivalente a um contêiner de 20 pés).",
     "SUM ( fCarga[TEU] )"),
    ("Volume", "Nº Atracações", F_INT,
     "Número de atracações com movimentação de carga no período (mês da desatracação).",
     "COUNTROWS ( fAtracacao )"),
    ("Volume", "Toneladas por Atracação", F_INT,
     "Toneladas médias por atracação = soma das toneladas das atracações ÷ nº de atracações (razão de somas).",
     "DIVIDE ( SUM ( fAtracacao[Toneladas] ), [Nº Atracações] )"),
    # ---------------- Participação ----------------
    ("Participação", "% do Total Brasil", F_P,
     "Participação das toneladas no total do Brasil do mesmo período (ignora filtros de instalação/região).",
     "DIVIDE ( [Toneladas], CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ) ) )"),
    ("Participação", "% Cabotagem", F_P,
     "Fatia das toneladas movimentada em navegação de cabotagem (entre portos brasileiros).",
     """DIVIDE (
    CALCULATE ( [Toneladas], dNavegacao[Navegação] = "Cabotagem" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)"""),
    ("Participação", "% Longo Curso", F_P,
     "Fatia das toneladas movimentada em navegação de longo curso (comércio exterior).",
     """DIVIDE (
    CALCULATE ( [Toneladas], dNavegacao[Navegação] = "Longo Curso" ),
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dNavegacao ) )
)"""),
    ("Participação", "% Contêiner", F_P, "Fatia das toneladas movimentada em contêiner (0% quando o porto não movimenta contêiner).",
     """IF (
    NOT ISBLANK ( [Toneladas] ),
    DIVIDE (
        CALCULATE ( [Toneladas], dNaturezaCarga[Natureza da Carga] = "Contêiner" ),
        CALCULATE ( [Toneladas], REMOVEFILTERS ( dNaturezaCarga ) )
    ) + 0
)"""),
    ("Participação", "Ranking Porto", F_INT,
     "Posição por toneladas entre as instalações (ou complexos) visíveis no visual — 1 = maior.",
     """VAR T = [Toneladas]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( T ), BLANK (),
        // a coluna Porto é ordenada por OrdemBenchmark: o visual agrupa pelas duas, então o RANKX itera o par
        ISINSCOPE ( dInstalacao[Porto (benchmark NE)] ),
            RANKX (
                ALLSELECTED ( dInstalacao[Porto (benchmark NE)], dInstalacao[OrdemBenchmark] ),
                [Toneladas], , DESC, DENSE
            ),
        ISINSCOPE ( dInstalacao[Instalação] ),
            RANKX ( ALLSELECTED ( dInstalacao[Instalação] ), [Toneladas], , DESC, DENSE ),
        ISINSCOPE ( dInstalacao[Complexo Portuário] ),
            RANKX ( ALLSELECTED ( dInstalacao[Complexo Portuário] ), [Toneladas], , DESC, DENSE )
    )"""),
    ("Participação", "Ranking Suape Brasil", F_INT,
     "Posição de Suape entre todas as instalações do Brasil por toneladas no período.",
     """VAR ToneladasSuape =
    CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )
VAR Todas =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[Instalação] ), "@t", [Toneladas] ),
        REMOVEFILTERS ( dInstalacao )
    )
RETURN
    IF ( NOT ISBLANK ( ToneladasSuape ), COUNTROWS ( FILTER ( Todas, [@t] > ToneladasSuape ) ) + 1 )"""),
    # ---------------- Eficiência ----------------
    ("Eficiência", "Espera Média (h)", F_H,
     "Média das horas entre a chegada do navio e a atracação. Sensível a filas longas.",
     "AVERAGE ( fAtracacao[EsperaAtracacao_h] )"),
    ("Eficiência", "Espera Mediana (h)", F_H,
     "Mediana das horas entre chegada e atracação: a espera do navio típico, sem distorção das filas extremas.",
     "MEDIAN ( fAtracacao[EsperaAtracacao_h] )"),
    ("Eficiência", "Tempo Atracado Médio (h)", F_H,
     "Média das horas entre atracação e desatracação (ocupação do berço por navio).",
     "AVERAGE ( fAtracacao[Atracado_h] )"),
    ("Eficiência", "Tempo de Operação Médio (h)", F_H,
     "Média das horas entre o início e o fim da operação de carga/descarga.",
     "AVERAGE ( fAtracacao[Operacao_h] )"),
    ("Eficiência", "% Atracado em Operação", F_P,
     "Horas de operação ÷ horas atracado (só atracações com os dois tempos): quanto do tempo no berço é operação.",
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
    ("Eficiência", "Horas Paralisadas", '#,0" h"',
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
        VALUES ( dInstalacao[Porto (benchmark NE)] ),
        REMOVEFILTERS ( dInstalacao ),
        dInstalacao[Grupo do Benchmark] = "Pares do Nordeste"
    )
RETURN
    AVERAGEX (
        Pares,
        VAR Porto = dInstalacao[Porto (benchmark NE)]
        RETURN
            CALCULATE (
                [Espera Mediana (h)],
                REMOVEFILTERS ( dInstalacao ),
                dInstalacao[Porto (benchmark NE)] = Porto
            )
    )"""),
    ("Eficiência\\Benchmark Nordeste", "Diferença Espera Suape vs Pares (h)", f'+#,0.0" h";"{MENOS}"#,0.0" h";0.0" h"',
     "Espera mediana de Suape menos a média dos pares (negativo = Suape espera menos).",
     "[Espera Mediana Suape (h)] - [Espera Mediana Média Pares (h)]"),
    ("Volume\\Suape", "Toneladas Suape", F_T, "Toneladas de Suape no período.",
     "CALCULATE ( [Toneladas], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Volume\\Suape", "TEU Suape", F_INT, "TEU movimentados em Suape no período.",
     "CALCULATE ( [TEU], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Volume\\Suape", "Var % Toneladas Suape AA", F_VAR, "Variação de toneladas de Suape vs. ano anterior.",
     "CALCULATE ( [Var % Toneladas AA], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    ("Participação", "% Contêiner Suape", F_P, "Fatia de contêiner nas toneladas de Suape.",
     "CALCULATE ( [% Contêiner], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 )"),
    # ---------------- Mapa ----------------
    ("Auxiliares\\Mapa", "Latitude do Complexo", F_GRAU,
     "Latitude do complexo portuário (média das coordenadas oficiais ponderada por toneladas).",
     "MAX ( dInstalacao[Latitude do Complexo] )"),
    ("Auxiliares\\Mapa", "Longitude do Complexo", F_GRAU,
     "Longitude do complexo portuário (média das coordenadas oficiais ponderada por toneladas).",
     "MAX ( dInstalacao[Longitude do Complexo] )"),
    ("Auxiliares\\Mapa", "Destaque no Mapa", F_INT,
     "1 para Suape e para os 5 complexos com mais toneladas no contexto (os que recebem rótulo no mapa).",
     """VAR Posicao =
    IF (
        ISINSCOPE ( dInstalacao[Complexo Portuário] ),
        RANKX ( ALLSELECTED ( dInstalacao[Complexo Portuário] ), [Toneladas], , DESC, DENSE )
    )
RETURN
    IF ( NOT ISBLANK ( [Toneladas] ) && ( Posicao <= 5 || MAX ( dInstalacao[EhSuape] ) = 1 ), 1 )"""),
    ("Auxiliares\\Mapa", "Latitude (rótulo)", F_GRAU, "Latitude só dos complexos destacados (camada de rótulos).",
     "IF ( [Destaque no Mapa] = 1, MAX ( dInstalacao[Latitude do Rótulo] ) )"),
    ("Auxiliares\\Mapa", "Longitude (rótulo)", F_GRAU, "Longitude só dos complexos destacados (camada de rótulos).",
     "IF ( [Destaque no Mapa] = 1, MAX ( dInstalacao[Longitude do Rótulo] ) )"),
    ("Auxiliares\\Mapa", "UF do Complexo", None, "UF(s) do complexo portuário (dica de ferramenta).",
     'CONCATENATEX ( VALUES ( dInstalacao[UF] ), dInstalacao[UF], "/" )'),
    # ---------------- Rótulos de cartão (texto) ----------------
    ("Auxiliares\\Rótulos", "Rótulo Toneladas", None, "Toneladas em milhões com unidade (cartão).",
     rotulo("[Toneladas (Mi t)]", "#,0.0", " Mi t")),
    ("Auxiliares\\Rótulos", "Rótulo Var % AA", None, "Variação vs. ano anterior com sinal (cartão).",
     rotulo_var("[Var % Toneladas AA]")),
    ("Auxiliares\\Rótulos", "Rótulo Atracações", None, "Nº de atracações com separador de milhar (cartão).",
     rotulo("[Nº Atracações]", "#,0")),
    ("Auxiliares\\Rótulos", "Rótulo Espera Mediana", None, "Espera mediana com 1 casa e unidade (cartão).",
     rotulo("[Espera Mediana (h)]", "#,0.0", " h")),
    ("Auxiliares\\Rótulos", "Rótulo Prancha Operacional", None, "Prancha operacional inteira com unidade (cartão).",
     rotulo("[Prancha Média Operacional (t/h)]", "#,0", " t/h")),
    ("Auxiliares\\Rótulos", "Rótulo Tempo Atracado", None, "Tempo atracado médio (cartão).",
     rotulo("[Tempo Atracado Médio (h)]", "#,0.0", " h")),
    ("Auxiliares\\Rótulos", "Rótulo % Atracado em Operação", None, "% do tempo atracado em operação (cartão).",
     rotulo("[% Atracado em Operação]", "0.0%")),
    ("Auxiliares\\Rótulos", "Rótulo Horas Paralisadas", None, "Horas paralisadas em milhares (cartão).",
     rotulo("DIVIDE ( [Horas Paralisadas], 1000 )", "#,0.0", " mil h")),
    ("Auxiliares\\Rótulos", "Rótulo TEU", None, "TEU em milhares (cartão).",
     rotulo("DIVIDE ( [TEU], 1000 )", "#,0", " mil TEU")),
    ("Auxiliares\\Rótulos", "Rótulo % Contêiner", None, "% contêiner (cartão).", rotulo("[% Contêiner]", "0.0%")),
    ("Auxiliares\\Rótulos", "Rótulo % Longo Curso", None, "% longo curso (cartão).", rotulo("[% Longo Curso]", "0.0%")),
    ("Auxiliares\\Rótulos", "Rótulo % Cabotagem", None, "% cabotagem (cartão).", rotulo("[% Cabotagem]", "0.0%")),
    ("Auxiliares\\Rótulos", "Rótulo Toneladas Suape", None, "Toneladas de Suape em milhões (cartão).",
     rotulo("DIVIDE ( [Toneladas Suape], 1000000 )", "#,0.0", " Mi t")),
    ("Auxiliares\\Rótulos", "Rótulo Var % Suape", None, "Variação de Suape vs. ano anterior (cartão).",
     rotulo_var("[Var % Toneladas Suape AA]")),
    ("Auxiliares\\Rótulos", "Rótulo TEU Suape", None, "TEU de Suape em milhares (cartão).",
     rotulo("DIVIDE ( [TEU Suape], 1000 )", "#,0", " mil TEU")),
    ("Auxiliares\\Rótulos", "Rótulo % Contêiner Suape", None, "% contêiner de Suape (cartão).",
     rotulo("[% Contêiner Suape]", "0.0%")),
    ("Auxiliares\\Rótulos", "Rótulo Ranking Suape", None, "Posição de Suape no Brasil (cartão).",
     'VAR r = [Ranking Suape Brasil]\nRETURN\n    IF ( NOT ISBLANK ( r ), r & "ª do Brasil" )'),
    # ---------------- Auxiliares ----------------
    ("Auxiliares", "Última Atualização", None,
     "Texto com o recorte e a data de processamento do pipeline.",
     f""""Dados ANTAQ {ANO_INICIAL}–{ANO_FINAL} (anos completos) · processado em "
    & FORMAT ( MAX ( Meta[Data de Processamento] ), "dd/mm/yyyy" )"""),
    ("Auxiliares", "Título Dinâmico Período", None,
     "Texto do período filtrado (ex.: 'em 2025', 'de 2021 a 2025').",
     """VAR DataIni = CALCULATE ( MIN ( dCalendario[Data] ), dCalendario[Mês com Dado] = TRUE () )
VAR DataFim = CALCULATE ( MAX ( dCalendario[Data] ), dCalendario[Mês com Dado] = TRUE () )
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
        "de " & AnoIni & " a " & AnoFim
    )"""),
    ("Auxiliares", "Toneladas (Top 10) (Mi t)", F_MI,
     "Toneladas (Mi t) só das 10 maiores instalações visíveis (ranking sem barra de rolagem).",
     "IF ( [Ranking Porto] <= 10, [Toneladas (Mi t)] )"),
    ("Auxiliares", "Toneladas (Top 10 mercadorias) (Mi t)", F_MI,
     "Toneladas (Mi t) só das 10 maiores mercadorias visíveis.",
     """VAR Posicao =
    IF (
        ISINSCOPE ( dMercadoria[Mercadoria] ),
        RANKX ( ALLSELECTED ( dMercadoria[Mercadoria] ), [Toneladas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 10, [Toneladas (Mi t)] )"""),
    ("Auxiliares", "Horas Paralisadas (Top 8 motivos)", '#,0" h"',
     "Horas paralisadas só dos 8 motivos com mais horas no contexto (cabe sem rolagem em qualquer zoom).",
     """VAR Posicao =
    IF (
        ISINSCOPE ( fParalisacao[Motivo da Paralisação] ),
        RANKX ( ALLSELECTED ( fParalisacao[Motivo da Paralisação] ), [Horas Paralisadas], , DESC, DENSE )
    )
RETURN
    IF ( Posicao <= 8, [Horas Paralisadas] )"""),
    ("Auxiliares", "Cor Destaque Suape", None,
     "Cor das barras/pontos: dourado para Suape (ou o complexo que contém Suape), azul para as demais.",
     f'IF ( MAX ( dInstalacao[EhSuape] ) = 1, "{COR_SUAPE}", "{COR_PADRAO}" )'),
    ("Auxiliares", "Cor Texto Suape", None, "Cor do texto: dourado na linha de Suape, branco nas demais.",
     f'IF ( MAX ( dInstalacao[EhSuape] ) = 1, "{COR_SUAPE}", "{COR_TEXTO}" )'),
    ("Auxiliares", "Cor Calor Espera", None,
     "Cor do mapa de calor da espera mediana: até 2 h, 6 h, 24 h, 72 h e acima de 72 h.",
     """VAR Espera = [Espera Mediana (h)]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( Espera ), BLANK (),
        Espera <= 2, "#1E3A2F",
        Espera <= 6, "#2F5D46",
        Espera <= 24, "#6E5F33",
        Espera <= 72, "#8F4A28",
        "#7A1C2A"
    )"""),
    ("Auxiliares", "Cor Benchmark Espera", None,
     "Verde se a espera mediana do porto é menor ou igual à média dos pares; vermelho se maior.",
     """VAR Espera = [Espera Mediana (h)]
RETURN
    IF (
        NOT ISBLANK ( Espera ),
        IF ( Espera <= [Espera Mediana Média Pares (h)], "#1E3A2F", "#5A2318" )
    )"""),
    # ---------------- Títulos (uma linha, sem truncar) ----------------
    ("Auxiliares\\Títulos", "Título KPI Brasil", None, "Manchete da página Visão Geral.",
     f"""VAR Mt = [Toneladas] / 1000000
VAR Variacao = [Var % Toneladas AA]
RETURN
    "Portos brasileiros movimentaram " & FORMAT ( Mt, "#,0.0" ) & " Mi t " & {PER}
        & IF (
            NOT ISBLANK ( Variacao ),
            " (" & IF ( Variacao >= 0, "+", "{MENOS}" ) & FORMAT ( ABS ( Variacao ), "0.0%" ) & " vs. ano anterior)"
        )"""),
    ("Auxiliares\\Títulos", "Título Linha Mensal", None, "Título do gráfico de linha mensal.",
     f'"Toneladas por mês " & {PER} & " (cinza = ano anterior)"'),
    ("Auxiliares\\Títulos", "Título Região", None, "Título do gráfico por região.",
     """VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Região] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    MAXX ( Lider, dInstalacao[Região] ) & " concentra " & FORMAT ( DIVIDE ( MAXX ( Lider, [@t] ), [Toneladas] ), "0%" )
        & " da carga\""""),
    ("Auxiliares\\Títulos", "Título Top 10", None, "Título do ranking de instalações.",
     f"""VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dInstalacao[Instalação] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    "Top 10 instalações: " & MAXX ( Lider, dInstalacao[Instalação] ) & " lidera com "
        & FORMAT ( MAXX ( Lider, [@t] ) / 1000000, "#,0.0" ) & " Mi t " & {PER}"""),
    ("Auxiliares\\Títulos", "Título Mapa", None, "Título do mapa.",
     f'"Complexos portuários " & {PER} & " (tamanho = toneladas)"'),
    ("Auxiliares\\Títulos", "Título Benchmark Espera", None,
     "Manchete da página Nordeste & Suape: espera de Suape vs. pares.",
     f"""VAR Dif = [Diferença Espera Suape vs Pares (h)]
RETURN
    IF (
        ISBLANK ( Dif ), "Espera mediana: Suape x média dos pares",
        "Suape opera com espera mediana " & FORMAT ( ABS ( Dif ), "#,0.0" ) & " h "
            & IF ( Dif <= 0, "menor", "maior" ) & " que a média dos pares " & {PER}
    )"""),
    ("Auxiliares\\Títulos", "Título Tabela Benchmark", None, "Título da tabela de benchmark.",
     f'"Suape x pares " & {PER} & " · verde = espera mediana até a média dos pares"'),
    ("Auxiliares\\Títulos", "Título Crescimento Pares", None, "Título das barras de crescimento.",
     f"""VAR Pares =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( dInstalacao[Porto (benchmark NE)] ), "@v", [Var % Toneladas AA] ),
        NOT ISBLANK ( dInstalacao[Porto (benchmark NE)] )
    )
VAR Lider = TOPN ( 1, FILTER ( Pares, NOT ISBLANK ( [@v] ) ), [@v], DESC )
VAR v = MAXX ( Lider, [@v] )
RETURN
    IF (
        ISEMPTY ( Lider ), "Crescimento vs. ano anterior",
        "Maior alta " & {PER} & ": " & MAXX ( Lider, dInstalacao[Porto (benchmark NE)] )
            & " (" & IF ( v >= 0, "+", "{MENOS}" ) & FORMAT ( ABS ( v ), "0.0%" ) & ")"
    )"""),
    ("Auxiliares\\Títulos", "Título Linha Suape Pares", None, "Título da linha Suape x pares.",
     f'"Espera mediana por mês " & {PER} & ": Suape (dourado) x média dos pares (cinza)"'),
    ("Auxiliares\\Títulos", "Título Eficiência", None, "Manchete da página Eficiência e Gargalos.",
     f""""Navio típico esperou " & FORMAT ( [Espera Mediana (h)], "#,0.0" ) & " h para atracar " & {PER}
    & "; prancha operacional de " & FORMAT ( [Prancha Média Operacional (t/h)], "#,0" ) & " t/h\""""),
    ("Auxiliares\\Títulos", "Título Mapa de Calor", None, "Título do mapa de calor.",
     f"""VAR Lider =
    TOPN (
        1,
        CALCULATETABLE (
            ADDCOLUMNS ( VALUES ( dInstalacao[Porto (benchmark NE)] ), "@e", [Espera Mediana (h)] ),
            NOT ISBLANK ( dInstalacao[Porto (benchmark NE)] )
        ),
        [@e], DESC
    )
RETURN
    "Espera mediana (h) por mês " & {PER} & " · maior: " & MAXX ( Lider, dInstalacao[Porto (benchmark NE)] )
        & " (" & FORMAT ( MAXX ( Lider, [@e] ), "#,0" ) & " h)\""""),
    ("Auxiliares\\Títulos", "Título Operação", None, "Título das barras de % atracado em operação.",
     f""""Suape opera " & FORMAT ( CALCULATE ( [% Atracado em Operação], REMOVEFILTERS ( dInstalacao ), dInstalacao[EhSuape] = 1 ), "0%" )
    & " do tempo atracado " & {PER}"""),
    ("Auxiliares\\Títulos", "Título Paralisação", None, "Título das horas paralisadas por motivo.",
     """VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( fParalisacao[Motivo da Paralisação] ), "@h", [Horas Paralisadas] ), [@h], DESC )
RETURN
    IF (
        ISEMPTY ( Lider ), "Horas paralisadas por motivo",
        "Top 8 motivos de paralisação · maior: " & MAXX ( Lider, fParalisacao[Motivo da Paralisação] ) & " ("
            & FORMAT ( DIVIDE ( MAXX ( Lider, [@h] ), [Horas Paralisadas] ), "0%" ) & ")"
    )"""),
    ("Auxiliares\\Títulos", "Título Dispersão", None, "Título da dispersão espera x prancha.",
     f'"Portos públicos " & {PER} & ": espera (h) x prancha (t/h)"'),
    ("Auxiliares\\Títulos", "Título Perfil", None, "Manchete da página Perfil de Carga.",
     f"""VAR Selecao =
    IF (
        HASONEVALUE ( dInstalacao[Instalação] ), SELECTEDVALUE ( dInstalacao[Instalação] ),
        IF ( ISFILTERED ( dInstalacao ), "Instalações selecionadas", "Brasil" )
    )
RETURN
    Selecao & " " & {PER} & ": " & FORMAT ( [Toneladas] / 1000000, "#,0.0" ) & " Mi t movimentadas\""""),
    ("Auxiliares\\Títulos", "Título Natureza", None, "Título da composição por natureza de carga.",
     """VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dNaturezaCarga[Natureza da Carga] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    "Por mês · " & MAXX ( Lider, dNaturezaCarga[Natureza da Carga] ) & " responde por "
        & FORMAT ( DIVIDE ( MAXX ( Lider, [@t] ), [Toneladas] ), "0%" ) & " da carga\""""),
    ("Auxiliares\\Títulos", "Título Mercadorias", None, "Título do top mercadorias.",
     """VAR Lider =
    TOPN ( 1, ADDCOLUMNS ( VALUES ( dMercadoria[Mercadoria] ), "@t", [Toneladas] ), [@t], DESC )
RETURN
    "Top 10 mercadorias · " & MAXX ( Lider, dMercadoria[Mercadoria] ) & ": "
        & FORMAT ( DIVIDE ( MAXX ( Lider, [@t] ), [Toneladas] ), "0%" ) & " das toneladas\""""),
    ("Auxiliares\\Títulos", "Título Sentido", None, "Título do embarque x desembarque.",
     """VAR Emb = CALCULATE ( [Toneladas], dSentido[Sentido] = "Embarque" )
RETURN
    FORMAT ( DIVIDE ( Emb, CALCULATE ( [Toneladas], REMOVEFILTERS ( dSentido ) ) ), "0%" ) & " das toneladas são embarque\""""),
    ("Auxiliares\\Títulos", "Título Navegação", None, "Título da movimentação por navegação.",
     """"Por navegação · longo curso " & FORMAT ( [% Longo Curso], "0%" ) & ", cabotagem " & FORMAT ( [% Cabotagem], "0%" )"""),
]
