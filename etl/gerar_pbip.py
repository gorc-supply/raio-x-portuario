"""Gera o projeto Power BI (PBIP) em powerbi/: modelo semântico em TMDL, relatório em PBIR e tema JSON.

    .venv\\Scripts\\python etl\\gerar_pbip.py

Versões de formato (as mesmas de um PBIP público salvo pelo Power BI Desktop 2.144 / jun-2025, que o Desktop
atual abre): report 1.3.0, page 1.4.0, visualContainer 2.0.0, pagesMetadata/versionMetadata 1.0.0,
definition.pbir 4.0, definition.pbism 4.1, TMDL compatibilityLevel 1601.
"""
from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pbip_modelo as M  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PBI = RAIZ / "powerbi"
NOME = "RaioXPortuario"
SM = PBI / f"{NOME}.SemanticModel"
RP = PBI / f"{NOME}.Report"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
NS = uuid.UUID("6f1c2d4e-8a9b-4c3d-9e2f-1a2b3c4d5e6f")


def guid(*partes: str) -> str:
    """GUID determinístico (diffs estáveis entre execuções)."""
    return str(uuid.uuid5(NS, "/".join(partes)))


def nome_tmdl(n: str) -> str:
    simples = n.replace("_", "").isalnum() and n.isascii() and n[0].isalpha()
    return n if simples else "'" + n.replace("'", "''") + "'"


def escrever(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def escrever_json(caminho: Path, obj) -> None:
    escrever(caminho, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# ===========================================================================
# MODELO SEMÂNTICO (TMDL)
# ===========================================================================
def bloco(texto: str, tabs: int) -> str:
    return "\n".join(("\t" * tabs + linha) if linha.strip() else "" for linha in texto.split("\n"))


def tmdl_tabela(t: dict) -> str:
    L = [f"/// {t['descricao']}", f"table {nome_tmdl(t['nome'])}"]
    if t.get("oculta"):
        L.append("\tisHidden")
    if t.get("data"):
        L.append("\tdataCategory: Time")
    L += [f"\tlineageTag: {guid('tabela', t['nome'])}", ""]
    if t["nome"] == "_Medidas":
        for pasta, nome, fmt, desc, dax in M.MEDIDAS:
            L.append(f"\t/// {desc}")
            if "\n" in dax:
                L.append(f"\tmeasure {nome_tmdl(nome)} =")
                L.append(bloco(dax, 3))
            else:
                L.append(f"\tmeasure {nome_tmdl(nome)} = {dax}")
            if fmt:
                L.append(f"\t\tformatString: {fmt}")
            L.append(f"\t\tdisplayFolder: {pasta}")
            L.append(f"\t\tlineageTag: {guid('medida', nome)}")
            L.append("")
    for c in t["colunas"]:
        L.append(f"\tcolumn {nome_tmdl(c['nome'])}")
        L.append(f"\t\tdataType: {M.DT[c['tipo']]}")
        if c["oculto"]:
            L.append("\t\tisHidden")
        if c["chave"] and t.get("data"):
            L.append("\t\tisKey")
        if c["fmt"]:
            L.append(f"\t\tformatString: {c['fmt']}")
        L.append(f"\t\tlineageTag: {guid('coluna', t['nome'], c['nome'])}")
        if c["categoria"]:
            L.append(f"\t\tdataCategory: {c['categoria']}")
        L.append(f"\t\tsummarizeBy: {c['resumo']}")
        L.append(f"\t\tsourceColumn: {c['nome']}")
        if c["sort"]:
            L.append(f"\t\tsortByColumn: {nome_tmdl(c['sort'])}")
        L.append("")
        L.append("\t\tannotation SummarizationSetBy = Automatic")
        if c["tipo"] == "date":
            L.append("")
            L.append("\t\tannotation UnderlyingDateTimeDataType = Date")
        L.append("")
    L.append(f"\tpartition {nome_tmdl(t['nome'])} = m")
    L.append("\t\tmode: import")
    L.append("\t\tsource =")
    L.append(bloco(t["m"], 4))
    L += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(L)


def gerar_modelo() -> None:
    d = SM / "definition"
    escrever(d / "database.tmdl", "database\n\tcompatibilityLevel: 1601\n\n")
    ordem = ["CaminhoDados"] + [t["nome"] for t in M.TABELAS]
    model = [
        "model Model",
        "\tculture: pt-BR",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tdiscourageImplicitMeasures",
        "\tsourceQueryCulture: pt-BR",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        f"annotation PBI_QueryOrder = {json.dumps(ordem, ensure_ascii=False)}",
        "",
    ] + [f"ref table {nome_tmdl(t['nome'])}" for t in M.TABELAS] + [""]
    escrever(d / "model.tmdl", "\n".join(model) + "\n")
    escrever(d / "expressions.tmdl", "\n".join([
        "/// Pasta com os CSV gerados pelo pipeline (etl/run_all.py). Troque aqui se clonar o projeto em outro lugar.",
        f'expression CaminhoDados = "{M.CAMINHO_PADRAO}" meta [IsParameterQuery = true, Type = "Text", '
        "IsParameterQueryRequired = true]",
        f"\tlineageTag: {guid('expressao', 'CaminhoDados')}",
        "",
        "\tannotation PBI_ResultType = Text",
        "", ""]))
    rel = []
    for ft, fc, dt, dc in M.RELACOES:
        rel += [f"relationship {guid('rel', ft, fc, dt, dc)}", f"\tfromColumn: {ft}.{nome_tmdl(fc)}",
                f"\ttoColumn: {dt}.{nome_tmdl(dc)}", ""]
    escrever(d / "relationships.tmdl", "\n".join(rel) + "\n")
    for t in M.TABELAS:
        escrever(d / "tables" / f"{t['nome']}.tmdl", tmdl_tabela(t))
    escrever_json(SM / "definition.pbism", {
        "$schema": f"{SCHEMA}/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.1", "settings": {}})
    escrever_json(SM / ".platform", {
        "$schema": f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NOME},
        "config": {"version": "2.0", "logicalId": guid("item", "semanticModel")}})


# ===========================================================================
# RELATÓRIO (PBIR)
# ===========================================================================
MED = "_Medidas"


def lit(v) -> dict:
    return {"expr": {"Literal": {"Value": v}}}


def txt(s: str) -> dict:
    return lit("'" + s.replace("'", "''") + "'")


def cor(hexa: str) -> dict:
    return {"solid": {"color": txt(hexa)}}


def cor_medida(medida: str) -> dict:
    return {"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": MED}},
                                                      "Property": medida}}}}}


def campo_col(ent: str, prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}


def campo_med(prop: str, ent: str = MED) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}


def proj(campo: dict, ativo: bool | None = None, nome: str | None = None) -> dict:
    k = "Column" if "Column" in campo else "Measure"
    ent = campo[k]["Expression"]["SourceRef"]["Entity"]
    prop = campo[k]["Property"]
    p = {"field": campo, "queryRef": f"{ent}.{prop}", "nativeQueryRef": prop}
    if ativo is not None:
        p["active"] = ativo
    if nome:
        p["displayName"] = nome
    return p


def C(ent, prop, **kw):
    return proj(campo_col(ent, prop), **kw)


def Me(prop, **kw):
    return proj(campo_med(prop), **kw)


def titulo(texto: str | None = None, medida: str | None = None, tamanho: int = 12) -> dict:
    props = {"show": lit("true"), "fontSize": lit(f"{tamanho}D"), "fontColor": cor("#FFFFFF"),
             "titleWrap": lit("true")}
    props["text"] = {"expr": {"Measure": campo_med(medida)["Measure"]}} if medida else txt(texto)
    return {"title": [{"properties": props}]}


def ordenar(campo: dict, desc: bool = True) -> dict:
    return {"sort": [{"field": campo, "direction": "Descending" if desc else "Ascending"}]}


def filtro_in(nome: str, ent: str, prop: str, valores: list) -> dict:
    vals = [[{"Literal": {"Value": v if isinstance(v, str) and v.endswith("L") and v[:-1].isdigit()
                          else "'" + str(v).replace("'", "''") + "'"}}] for v in valores]
    return {"name": nome, "field": campo_col(ent, prop), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "f", "Entity": ent, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [
                           {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": prop}}],
                           "Values": vals}}}]},
            "howCreated": "User"}


FILTRO_BENCH = ("dInstalacao", "GrupoBenchmark", ["Suape", "Pares do Nordeste"])


class Pagina:
    def __init__(self, nome: str, exibicao: str):
        self.nome, self.exibicao = nome, exibicao
        self.visuais: list[dict] = []
        self.filtros: list[dict] = []
        self.z = 1000

    def add(self, nome: str, x, y, w, h, visual: dict | None = None, filtros=None, **extra) -> dict:
        self.z += 100
        v = {"$schema": f"{SCHEMA}/item/report/definition/visualContainer/2.0.0/schema.json",
             "name": nome, "position": {"x": x, "y": y, "z": self.z, "height": h, "width": w, "tabOrder": self.z}}
        if visual is not None:
            visual.setdefault("drillFilterOtherVisuals", True)
            v["visual"] = visual
        if filtros:
            v["filterConfig"] = {"filters": filtros}
        v.update(extra)
        self.visuais.append(v)
        return v


def vis(tipo: str, papeis: dict | None = None, objetos: dict | None = None, container: dict | None = None,
        sort: dict | None = None, **extra) -> dict:
    v = {"visualType": tipo}
    if papeis:
        v["query"] = {"queryState": {k: {"projections": p} for k, p in papeis.items()}}
        if sort:
            v["query"]["sortDefinition"] = sort
    if objetos:
        v["objects"] = objetos
    if container:
        v["visualContainerObjects"] = container
    v.update(extra)
    return v


def rotulos_dados(cor_txt="#C9CDD3") -> dict:
    return {"labels": [{"properties": {"show": lit("true"), "color": cor(cor_txt), "fontSize": lit("9D")}}]}


def barras(categoria: dict, valor: dict, titulo_med: str | None = None, titulo_txt: str | None = None,
           cor_suape: bool = False, ordem_desc: bool = True, sort_campo: dict | None = None) -> dict:
    obj = rotulos_dados()
    obj["categoryAxis"] = [{"properties": {"show": lit("true"), "fontSize": lit("9D")}}]
    obj["valueAxis"] = [{"properties": {"show": lit("false")}}]
    if cor_suape:
        obj["dataPoint"] = [{"properties": {"fill": cor_medida("Cor Destaque Suape")},
                             "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}]
    else:
        obj["dataPoint"] = [{"properties": {"fill": cor(M.COR_PADRAO)}}]
    return vis("clusteredBarChart", {"Category": [categoria], "Y": [valor]}, obj,
               titulo(titulo_txt, titulo_med), sort=ordenar(sort_campo or valor["field"], ordem_desc))


def cartao(medida: str, rotulo: str, tamanho: int = 22) -> dict:
    return vis("card", {"Values": [Me(medida, nome=rotulo)]},
               {"labels": [{"properties": {"fontSize": lit(f"{tamanho}D"), "color": cor("#FFFFFF")}}],
                "categoryLabels": [{"properties": {"show": lit("true"), "fontSize": lit("10D"),
                                                   "color": cor("#8A8F98")}}]},
               {"title": [{"properties": {"show": lit("false")}}]})


def textbox(paragrafos: list[list[dict]]) -> dict:
    return vis("textbox", objetos={"general": [{"properties": {"paragraphs": [
        {"textRuns": runs} for runs in paragrafos]}}]})


def run(texto: str, tam=11, cor_hex="#C9CDD3", negrito=False, url: str | None = None) -> dict:
    estilo = {"fontFamily": "Segoe UI", "fontSize": f"{tam}pt", "color": cor_hex}
    if negrito:
        estilo["fontWeight"] = "bold"
    r = {"value": texto, "textStyle": estilo}
    if url:
        r["url"] = url
    return r


PAGINAS = [("visao_geral", "Visão Geral Brasil"), ("nordeste_suape", "Nordeste & Suape"),
           ("eficiencia", "Eficiência e Gargalos"), ("perfil_carga", "Perfil de Carga"), ("sobre", "Sobre")]
ROTULO_BOTAO = {"visao_geral": "Visão Geral", "nordeste_suape": "Nordeste & Suape",
                "eficiencia": "Eficiência", "perfil_carga": "Perfil de Carga", "sobre": "Sobre"}


def cabecalho(p: Pagina, subtitulo: str) -> None:
    p.add("cab_titulo", 16, 6, 400, 48, textbox([[run("Raio-X Portuário", 18, "#FFFFFF", True)],
                                                 [run(subtitulo, 10, "#C9A96E")]]))
    x = 432
    for i, (pag, _) in enumerate(PAGINAS):
        atual = pag == p.nome
        p.add(f"nav_{pag}", x + i * 166, 12, 160, 34, vis(
            "actionButton",
            objetos={
                "icon": [{"properties": {"show": lit("false")}}],
                "text": [{"properties": {"show": lit("true")}},
                         {"properties": {"text": txt(ROTULO_BOTAO[pag]), "fontColor": cor("#000000" if atual else "#FFFFFF"),
                                         "fontSize": lit("11D"), "bold": lit("true")},
                          "selector": {"id": "default"}}],
                "fill": [{"properties": {"show": lit("true")}},
                         {"properties": {"fillColor": cor(M.COR_SUAPE if atual else "#1D2127"),
                                         "transparency": lit("0D")}, "selector": {"id": "default"}}],
                "outline": [{"properties": {"show": lit("false")}}]},
            container={"visualLink": [{"properties": {"show": lit("true"), "type": txt("PageNavigation"),
                                                      "navigationSection": txt(pag)}}]}),
            howCreated="InsertVisualButton")
    # segmentações sincronizadas entre as páginas
    ano = vis("slicer", {"Values": [C("dCalendario", "Ano", ativo=True)]},
              {"data": [{"properties": {"mode": txt("Dropdown")}}],
               "header": [{"properties": {"show": lit("true"), "text": txt("Ano"), "fontColor": cor("#C9CDD3")}}],
               "general": [{"properties": {"filter": {"filter": {
                   "Version": 2, "From": [{"Name": "c", "Entity": "dCalendario", "Type": 0}],
                   "Where": [{"Condition": {"In": {"Expressions": [
                       {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Ano"}}],
                       "Values": [[{"Literal": {"Value": "2025L"}}]]}}}]}}}}]},
              sort=ordenar(campo_col("dCalendario", "Ano"), False),
              syncGroup={"groupName": "Ano", "fieldChanges": True, "filterChanges": True})
    p.add("seg_ano", 16, 58, 150, 46, ano)
    reg = vis("slicer", {"Values": [C("dInstalacao", "Regiao", ativo=True)]},
              {"data": [{"properties": {"mode": txt("Dropdown")}}],
               "header": [{"properties": {"show": lit("true"), "text": txt("Região"), "fontColor": cor("#C9CDD3")}}]},
              sort=ordenar(campo_col("dInstalacao", "Regiao"), False),
              syncGroup={"groupName": "Regiao", "fieldChanges": True, "filterChanges": True})
    p.add("seg_regiao", 174, 58, 190, 46, reg)
    p.add("cab_atualizacao", 896, 58, 368, 46, vis(
        "card", {"Values": [Me("Última Atualização")]},
        {"labels": [{"properties": {"fontSize": lit("10D"), "color": cor("#8A8F98")}}],
         "categoryLabels": [{"properties": {"show": lit("false")}}]},
        {"title": [{"properties": {"show": lit("false")}}],
         "background": [{"properties": {"show": lit("false")}}],
         "border": [{"properties": {"show": lit("false")}}]}))


def pagina_visao_geral() -> Pagina:
    p = Pagina("visao_geral", "Visão Geral Brasil")
    cabecalho(p, "Visão geral do Brasil")
    p.add("titulo_pagina", 16, 108, 1248, 30, vis(
        "card", {"Values": [Me("Título KPI Brasil")]},
        {"labels": [{"properties": {"fontSize": lit("14D"), "color": cor("#FFFFFF")}}],
         "categoryLabels": [{"properties": {"show": lit("false")}}]},
        {"title": [{"properties": {"show": lit("false")}}], "background": [{"properties": {"show": lit("false")}}],
         "border": [{"properties": {"show": lit("false")}}]}))
    kpis = [("Toneladas", "Toneladas"), ("Var % Toneladas AA", "Var. vs. ano anterior"),
            ("Nº Atracações", "Atracações com carga"), ("Espera Mediana (h)", "Espera mediana p/ atracar (h)"),
            ("Prancha Média Operacional (t/h)", "Prancha operacional (t/h)")]
    w = (1248 - 4 * 8) / 5
    for i, (m, r) in enumerate(kpis):
        p.add(f"kpi_{i + 1}", 16 + i * (w + 8), 142, w, 84, cartao(m, r))
    linha = vis("lineChart", {"Category": [C("dCalendario", "AnoMes", ativo=True)],
                              "Y": [Me("Toneladas"), Me("Toneladas AA", nome="Ano anterior")]},
                {"dataPoint": [{"properties": {"fill": cor(M.COR_PADRAO)}, "selector": {"metadata": f"{MED}.Toneladas"}},
                               {"properties": {"fill": cor("#5B6470")}, "selector": {"metadata": f"{MED}.Toneladas AA"}}],
                 "legend": [{"properties": {"show": lit("true"), "position": txt("Top")}}],
                 "valueAxis": [{"properties": {"show": lit("true"), "fontSize": lit("9D")}}],
                 "categoryAxis": [{"properties": {"show": lit("true"), "fontSize": lit("9D")}}]},
                titulo(medida="Título Linha Mensal"),
                sort=ordenar(campo_col("dCalendario", "AnoMes"), False))
    p.add("linha_mensal", 16, 234, 620, 236, linha)
    p.add("barras_regiao", 644, 234, 300, 236,
          barras(C("dInstalacao", "Regiao"), Me("Toneladas"), titulo_med="Título Região"))
    mapa = vis("azureMap", {"Category": [C("dInstalacao", "LocalMapa", ativo=True)], "Size": [Me("Toneladas")]},
               {"bubbleLayer": [{"properties": {"bubbleColor": cor(M.COR_PADRAO)}}]},
               titulo("Onde a carga passa: bolhas por município portuário (tamanho = toneladas)"),
               sort=ordenar(campo_med("Toneladas")))
    p.add("mapa_bolhas", 952, 234, 312, 478, mapa)
    p.add("top10_instalacoes", 16, 478, 928, 234,
          barras(C("dInstalacao", "Instalacao"), Me("Toneladas (Top 10)", nome="Toneladas"),
                 titulo_med="Título Top 10", cor_suape=True))
    return p


def pagina_nordeste() -> Pagina:
    p = Pagina("nordeste_suape", "Nordeste & Suape")
    p.filtros.append(filtro_in("FiltroBenchmarkNE", *FILTRO_BENCH))
    cabecalho(p, "Suape x pares do Nordeste")
    tabela = vis("tableEx", {"Values": [
        C("dInstalacao", "PortoBenchmarkNE", nome="Porto"), Me("Toneladas"), Me("Var % Toneladas AA", nome="Var. % AA"),
        Me("Espera Mediana (h)", nome="Espera mediana (h)"),
        Me("Prancha Média Operacional (t/h)", nome="Prancha op. (t/h)"), Me("% Contêiner"),
        Me("Ranking Porto", nome="Ranking")]},
        {"values": [
            {"properties": {"backColor": cor_medida("Cor Benchmark Espera")},
             "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}],
                          "metadata": f"{MED}.Espera Mediana (h)"}},
            {"properties": {"fontColor": cor_medida("Cor Texto Suape")},
             "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}],
                          "metadata": "dInstalacao.PortoBenchmarkNE"}}],
         "columnHeaders": [{"properties": {"fontSize": lit("10D")}}],
         "total": [{"properties": {"totals": lit("false")}}]},
        titulo("Benchmark: Suape x pares do Nordeste (verde = espera menor ou igual à média dos pares)"),
        sort=ordenar(campo_med("Toneladas")))
    p.add("tabela_benchmark", 16, 110, 760, 300, tabela)
    p.add("barras_crescimento", 784, 110, 480, 300,
          barras(C("dInstalacao", "PortoBenchmarkNE"), Me("Var % Toneladas AA", nome="Var. % AA"),
                 titulo_med="Título Crescimento Pares", cor_suape=True))
    linha = vis("lineChart", {"Category": [C("dCalendario", "AnoMes", ativo=True)],
                              "Y": [Me("Espera Mediana Suape (h)", nome="Suape"),
                                    Me("Espera Mediana Média Pares (h)", nome="Média dos pares")]},
                {"dataPoint": [{"properties": {"fill": cor(M.COR_SUAPE)},
                                "selector": {"metadata": f"{MED}.Espera Mediana Suape (h)"}},
                               {"properties": {"fill": cor("#8A8F98")},
                                "selector": {"metadata": f"{MED}.Espera Mediana Média Pares (h)"}}],
                 "legend": [{"properties": {"show": lit("true"), "position": txt("Top")}}],
                 "labels": [{"properties": {"show": lit("true"), "fontSize": lit("8D")}}]},
                titulo(medida="Título Benchmark Espera"),
                sort=ordenar(campo_col("dCalendario", "AnoMes"), False))
    p.add("linha_suape_pares", 16, 418, 760, 294, linha)
    cards = [("Toneladas Suape", "Toneladas de Suape"), ("TEU Suape", "TEU de Suape"),
             ("% Contêiner Suape", "% contêiner em Suape"), ("Ranking Suape Brasil", "Posição de Suape no Brasil")]
    for i, (m, r) in enumerate(cards):
        p.add(f"card_suape_{i + 1}", 784 + (i % 2) * 244, 418 + (i // 2) * 100, 236, 92, cartao(m, r, 20))
    p.add("card_ranking_texto", 784, 618, 480, 94, vis(
        "card", {"Values": [Me("Título Ranking Suape")]},
        {"labels": [{"properties": {"fontSize": lit("12D"), "color": cor(M.COR_SUAPE)}}],
         "categoryLabels": [{"properties": {"show": lit("false")}}]},
        {"title": [{"properties": {"show": lit("false")}}]}))
    return p


def pagina_eficiencia() -> Pagina:
    p = Pagina("eficiencia", "Eficiência e Gargalos")
    cabecalho(p, "Onde estão os gargalos")
    disp = vis("scatterChart", {"Category": [C("dInstalacao", "Instalacao", ativo=True)],
                                "X": [Me("Espera Mediana (h)")], "Y": [Me("Prancha Média Operacional (t/h)")],
                                "Size": [Me("Toneladas")]},
               {"dataPoint": [{"properties": {"fill": cor_medida("Cor Destaque Suape")},
                               "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                "categoryLabels": [{"properties": {"show": lit("false")}}],
                "categoryAxis": [{"properties": {"show": lit("true"), "showAxisTitle": lit("true")}}],
                "valueAxis": [{"properties": {"show": lit("true"), "showAxisTitle": lit("true")}}]},
               titulo(medida="Título Dispersão"))
    p.add("dispersao_espera_prancha", 16, 110, 620, 300, disp,
          filtros=[filtro_in("FiltroPortoOrganizado", "dInstalacao", "TipoInstalacao", ["Porto Organizado"])])
    calor = vis("pivotTable", {"Rows": [C("dInstalacao", "PortoBenchmarkNE", ativo=True, nome="Porto")],
                               "Columns": [C("dCalendario", "MesAbrev", ativo=True, nome="Mês")],
                               "Values": [Me("Espera Mediana (h)", nome="Espera mediana (h)")]},
                {"values": [{"properties": {"backColor": cor_medida("Cor Calor Espera")},
                             "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}],
                                          "metadata": f"{MED}.Espera Mediana (h)"}}],
                 "subTotals": [{"properties": {"rowSubtotals": lit("false"), "columnSubtotals": lit("false")}}],
                 "columnHeaders": [{"properties": {"fontSize": lit("9D")}}]},
                titulo(medida="Título Mapa de Calor"))
    p.add("mapa_calor_espera", 644, 110, 620, 300, calor, filtros=[filtro_in("FiltroBenchmarkNE", *FILTRO_BENCH)])
    p.add("barras_pct_operacao", 16, 418, 620, 294,
          barras(C("dInstalacao", "PortoBenchmarkNE"), Me("% Atracado em Operação"),
                 titulo_med="Título Operação", cor_suape=True),
          filtros=[filtro_in("FiltroBenchmarkNE", *FILTRO_BENCH)])
    p.add("barras_paralisacao", 644, 418, 620, 294,
          barras(C("fParalisacao", "MotivoParalisacao"), Me("Horas Paralisadas (Top 10 motivos)", nome="Horas"),
                 titulo_med="Título Paralisação"))
    return p


def pagina_perfil() -> Pagina:
    p = Pagina("perfil_carga", "Perfil de Carga")
    cabecalho(p, "O que cada porto movimenta")
    porto = vis("slicer", {"Values": [C("dInstalacao", "Instalacao", ativo=True)]},
                {"data": [{"properties": {"mode": txt("Dropdown")}}],
                 "header": [{"properties": {"show": lit("true"), "text": txt("Porto / terminal"),
                                            "fontColor": cor("#C9CDD3")}}],
                 "selection": [{"properties": {"singleSelect": lit("false")}}]},
                sort=ordenar(campo_col("dInstalacao", "Instalacao"), False))
    p.add("seg_porto", 372, 58, 300, 46, porto)
    empilhado = vis("columnChart", {"Category": [C("dCalendario", "AnoMes", ativo=True)],
                                    "Series": [C("dNaturezaCarga", "NaturezaCarga")], "Y": [Me("Toneladas")]},
                    {"legend": [{"properties": {"show": lit("true"), "position": txt("Top")}}],
                     "valueAxis": [{"properties": {"show": lit("true"), "fontSize": lit("9D")}}]},
                    titulo(medida="Título Natureza"), sort=ordenar(campo_col("dCalendario", "AnoMes"), False))
    p.add("empilhado_natureza", 16, 110, 620, 300, empilhado)
    p.add("top_mercadorias", 644, 110, 620, 300,
          barras(C("dMercadoria", "Mercadoria"), Me("Toneladas (Top 10 mercadorias)", nome="Toneladas"),
                 titulo_med="Título Mercadorias"))
    p.add("barras_navegacao", 16, 418, 620, 294,
          barras(C("dNavegacao", "Navegacao"), Me("Toneladas"), titulo_med="Título Navegação"))
    rosca = vis("donutChart", {"Category": [C("dSentido", "Sentido")], "Y": [Me("Toneladas")]},
                {"legend": [{"properties": {"show": lit("true"), "position": txt("Right")}}],
                 "labels": [{"properties": {"show": lit("true"), "labelStyle": txt("Percent of total")}}]},
                titulo(medida="Título Sentido"), sort=ordenar(campo_med("Toneladas")))
    p.add("rosca_sentido", 644, 418, 620, 294, rosca)
    return p


def pagina_sobre() -> Pagina:
    p = Pagina("sobre", "Sobre")
    cabecalho(p, "Sobre o painel")
    h = lambda s: [run(s, 13, M.COR_SUAPE, True)]  # noqa: E731
    t = lambda s: [run(s, 10)]  # noqa: E731
    esquerda = [
        h("O que é"),
        t("Painel sobre o desempenho dos portos brasileiros, com foco em Suape e nos pares do Nordeste: "
          "quanto se movimenta, onde estão os gargalos e o que cada porto movimenta."),
        h("Fonte"),
        [run("ANTAQ — Estatístico Aquaviário (dados abertos), tabelas Atracação, Carga, Tempos de Atracação e "
             "Paralisações. ", 10),
         run("gov.br/antaq", 10, "#8FB4D9", url="https://www.gov.br/antaq/pt-br/assuntos/estatistica")],
        t("Com o portal de download da ANTAQ fora do ar desde jun/2026, os arquivos oficiais vieram de um espelho "
          "público (Hugging Face, CC-BY-4.0). O total anual bate com o publicado pela ANTAQ (diferença de −0,1% a "
          "+1,2% entre 2021 e 2025)."),
        h("Recorte"),
        t("2021 até o último mês disponível (jan/2026). Período = mês da desatracação, como na ANTAQ. "
          "Suape = porto organizado de Suape; pares = Pecém, Itaqui, Salvador, Aratu, Recife, Natal, Cabedelo e Maceió."),
        h("Regras de limpeza"),
        t("Toneladas = peso bruto das cargas marcadas como movimentação (FlagMCOperacaoCarga = 1), com transbordo. "
          "Tempos: os calculados pela ANTAQ; negativos descartados; acima do percentil 99,5 da natureza de carga, "
          "limitados ao percentil. Tonelagem nunca é cortada."),
    ]
    direita = [
        h("Como ler as métricas"),
        t("Espera = chegada até atracação. A mediana mostra o navio típico; a média é puxada por filas longas."),
        t("Tempo atracado = atracação até desatracação. Tempo de operação = início ao fim da carga/descarga."),
        t("% atracado em operação = horas operando ÷ horas no berço."),
        t("Prancha operacional = toneladas ÷ horas de operação; prancha geral = toneladas ÷ horas atracado "
          "(sempre razão de somas)."),
        h("Projeto"),
        [run("Código, dados tratados e documentação: ", 10),
         run("github.com/gorc-supply/raio-x-portuario", 10, "#8FB4D9",
             url="https://github.com/gorc-supply/raio-x-portuario")],
        [run("Portfólio: ", 10), run("gorc-supply.github.io", 10, "#8FB4D9", url="https://gorc-supply.github.io")],
        [run("Gabriel Cunha · Supply Chain & Operations · Recife/PE · ", 10, "#FFFFFF", True),
         run("LinkedIn", 10, "#8FB4D9", url="https://www.linkedin.com/in/gabriel-cunha-xp")],
    ]
    p.add("texto_sobre_esq", 16, 112, 616, 600, textbox(esquerda))
    p.add("texto_sobre_dir", 648, 112, 616, 520, textbox(direita))
    p.add("card_atualizacao_sobre", 648, 640, 616, 72, vis(
        "card", {"Values": [Me("Última Atualização")]},
        {"labels": [{"properties": {"fontSize": lit("12D"), "color": cor(M.COR_SUAPE)}}],
         "categoryLabels": [{"properties": {"show": lit("false")}}]},
        {"title": [{"properties": {"show": lit("false")}}]}))
    return p


def tema() -> dict:
    fundo, painel, linha, texto, suave = "#000000", "#0C0D10", "#1D2127", "#FFFFFF", "#C9CDD3"
    return {
        "name": "Raio-X Portuário (identidade gorc-supply)",
        "dataColors": ["#8FB4D9", "#C9A96E", "#7DB592", "#D98A86", "#D9A87A", "#8A8F98", "#5B7A99", "#E0C48F"],
        "background": painel, "foreground": texto, "tableAccent": M.COR_SUAPE,
        "good": "#7DB592", "neutral": "#D9A87A", "bad": "#D98A86",
        "maximum": "#8B1E2D", "center": "#7A6A3A", "minimum": "#1E3A2F",
        "textClasses": {
            "callout": {"fontSize": 22, "fontFace": "Segoe UI Semibold", "color": texto},
            "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": texto},
            "header": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": texto},
            "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": suave},
        },
        "visualStyles": {
            "page": {"*": {
                "background": [{"color": {"solid": {"color": fundo}}, "transparency": 0}],
                "outspace": [{"color": {"solid": {"color": fundo}}, "transparency": 0}]}},
            "*": {"*": {
                "background": [{"show": True, "color": {"solid": {"color": painel}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": linha}}, "radius": 8}],
                "title": [{"show": True, "fontColor": {"solid": {"color": texto}}, "fontSize": 12}],
                "categoryAxis": [{"labelColor": {"solid": {"color": suave}}, "titleColor": {"solid": {"color": suave}},
                                  "gridlineColor": {"solid": {"color": linha}}}],
                "valueAxis": [{"labelColor": {"solid": {"color": suave}}, "titleColor": {"solid": {"color": suave}},
                               "gridlineColor": {"solid": {"color": linha}}}],
                "legend": [{"labelColor": {"solid": {"color": suave}}}],
                "labels": [{"color": {"solid": {"color": suave}}}],
                "visualTooltip": [{"titleFontColor": {"solid": {"color": texto}},
                                   "valueFontColor": {"solid": {"color": texto}},
                                   "background": {"solid": {"color": "#121419"}}}]}},
            "tableEx": {"*": {
                "columnHeaders": [{"fontColor": {"solid": {"color": texto}}, "backColor": {"solid": {"color": "#121419"}}}],
                "values": [{"fontColorPrimary": {"solid": {"color": suave}}, "backColorPrimary": {"solid": {"color": painel}},
                            "fontColorSecondary": {"solid": {"color": suave}},
                            "backColorSecondary": {"solid": {"color": "#07080A"}}}],
                "grid": [{"gridHorizontalColor": {"solid": {"color": linha}}}]}},
            "pivotTable": {"*": {
                "columnHeaders": [{"fontColor": {"solid": {"color": texto}}, "backColor": {"solid": {"color": "#121419"}}}],
                "rowHeaders": [{"fontColor": {"solid": {"color": texto}}, "backColor": {"solid": {"color": painel}}}],
                "values": [{"fontColorPrimary": {"solid": {"color": texto}}, "backColorPrimary": {"solid": {"color": painel}},
                            "fontColorSecondary": {"solid": {"color": texto}},
                            "backColorSecondary": {"solid": {"color": painel}}}]}},
            "slicer": {"*": {
                "items": [{"fontColor": {"solid": {"color": texto}}, "background": {"solid": {"color": "#121419"}}}],
                "header": [{"fontColor": {"solid": {"color": suave}}}]}},
            "textbox": {"*": {"background": [{"show": False}], "border": [{"show": False}]}},
            "actionButton": {"*": {"background": [{"show": False}], "border": [{"show": False}]}},
        },
    }


def gerar_relatorio() -> None:
    d = RP / "definition"
    if d.exists():
        shutil.rmtree(d)
    paginas = [pagina_visao_geral(), pagina_nordeste(), pagina_eficiencia(), pagina_perfil(), pagina_sobre()]
    escrever_json(RP / "definition.pbir", {
        "$schema": f"{SCHEMA}/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{NOME}.SemanticModel"}}})
    escrever_json(RP / ".platform", {
        "$schema": f"{SCHEMA}/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": NOME},
        "config": {"version": "2.0", "logicalId": guid("item", "report")}})
    escrever_json(d / "version.json", {"$schema": f"{SCHEMA}/item/report/definition/versionMetadata/1.0.0/schema.json",
                                       "version": "2.0.0"})
    escrever_json(d / "report.json", {
        "$schema": f"{SCHEMA}/item/report/definition/report/1.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.61", "type": "SharedResources"},
            "customTheme": {"name": "tema-raio-x.json", "reportVersionAtImport": "5.61",
                            "type": "RegisteredResources"}},
        "layoutOptimization": "None",
        "objects": {"outspacePane": [{"properties": {"expanded": lit("false"), "visible": lit("false")}}]},
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": "tema-raio-x.json", "path": "tema-raio-x.json", "type": "CustomTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
                     "useEnhancedTooltips": True}})
    escrever_json(d / "pages" / "pages.json", {
        "$schema": f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p.nome for p in paginas], "activePageName": paginas[0].nome})
    for p in paginas:
        pg = {"$schema": f"{SCHEMA}/item/report/definition/page/1.4.0/schema.json", "name": p.nome,
              "displayName": p.exibicao, "displayOption": "FitToPage", "height": 720, "width": 1280}
        if p.filtros:
            pg["filterConfig"] = {"filters": p.filtros}
        escrever_json(d / "pages" / p.nome / "page.json", pg)
        for v in p.visuais:
            escrever_json(d / "pages" / p.nome / "visuals" / v["name"] / "visual.json", v)
    t = tema()
    escrever_json(PBI / "tema-raio-x.json", t)
    escrever_json(RP / "StaticResources" / "RegisteredResources" / "tema-raio-x.json", t)
    base = RP / "StaticResources" / "SharedResources" / "BaseThemes" / "CY24SU10.json"
    if not base.exists():
        raise FileNotFoundError(f"Tema base do Power BI ausente: {base} (veja docs/DECISOES.md, D13)")


def gerar_pbip() -> None:
    escrever_json(PBI / f"{NOME}.pbip", {
        "$schema": f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": f"{NOME}.Report"}}],
        "settings": {"enableAutoRecovery": True}})


def main() -> int:
    if (SM / "definition").exists():
        shutil.rmtree(SM / "definition")
    gerar_modelo()
    gerar_relatorio()
    gerar_pbip()
    n_vis = len(list((RP / "definition" / "pages").rglob("visual.json")))
    print(f"PBIP gerado em {PBI}: {len(M.TABELAS)} tabelas, {len(M.MEDIDAS)} medidas, {len(M.RELACOES)} "
          f"relacionamentos, {n_vis} visuais em 5 páginas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
