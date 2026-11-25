"""Gera o projeto Power BI (PBIP) em powerbi/: modelo semântico em TMDL, relatório em PBIR e tema JSON.

    .venv\\Scripts\\python etl\\gerar_pbip.py [--mapa azure|dispersao]

`--mapa` escolhe o mapa da página Visão Geral (o outro vai para a página oculta "Mapa (plano B)").

Versões de formato (as mesmas de um PBIP público salvo pelo Power BI Desktop): report 1.3.0, page 1.4.0,
visualContainer 2.0.0, pagesMetadata/versionMetadata 1.0.0, definition.pbir 4.0, definition.pbism 4.1, TMDL
compatibilityLevel 1601. Ao salvar, o Desktop atualiza as versões sozinho.

Grade do relatório: página 1280x720, margem externa 16 px, espaçamento 12 px.
"""
from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapa_base  # noqa: E402
import pbip_modelo as M  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PBI = RAIZ / "powerbi"
NOME = "RaioXPortuario"
SM = PBI / f"{NOME}.SemanticModel"
RP = PBI / f"{NOME}.Report"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric"
NS = uuid.UUID("6f1c2d4e-8a9b-4c3d-9e2f-1a2b3c4d5e6f")
IMG_MAPA = "mapa_brasil_ibge.png"

# grade
MG, GAP, LARG, ALT = 16, 12, 1280, 720
COL_ESQ = 824                     # largura da coluna esquerda nas páginas com coluna direita
X_DIR = MG + COL_ESQ + GAP        # 852
L_DIR = LARG - MG - X_DIR         # 412
Y_CARD, H_CARD = 156, 68
Y_CONT = Y_CARD + H_CARD + GAP    # 252
Y_FIM = ALT - MG                  # 704


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
        L.append(f"\tcolumn {nome_tmdl(c['rotulo'])}")
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
# RELATÓRIO (PBIR) — utilitários
# ===========================================================================
MED = "_Medidas"
T_SUAVE, T_BRANCO = M.COR_TEXTO_SUAVE, M.COR_TEXTO


def lit(v) -> dict:
    return {"expr": {"Literal": {"Value": v}}}


def txt(s: str) -> dict:
    return lit("'" + s.replace("'", "''") + "'")


def num(v) -> dict:
    return lit(f"{v}D")


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


def media(ent: str, prop: str, nome: str | None = None) -> dict:
    """Coluna com agregação Média (Function 1) — exigida pelo Azure Maps quando há Local + lat/long."""
    p = {"field": {"Aggregation": {"Expression": campo_col(ent, prop), "Function": 1}},
         "queryRef": f"Avg({ent}.{prop})", "nativeQueryRef": f"Average of {prop}"}
    if nome:
        p["displayName"] = nome
    return p


def C(ent, prop, **kw):
    return proj(campo_col(ent, prop), **kw)


def Me(prop, **kw):
    return proj(campo_med(prop), **kw)


def todos(sel: dict | None = None) -> dict:
    return {"data": [{"dataViewWildcard": {"matchingOption": 1}}], **(sel or {})}


def titulo(texto: str | None = None, medida: str | None = None, tamanho: int = 11) -> dict:
    props = {"show": lit("true"), "fontSize": num(tamanho), "fontColor": cor(T_BRANCO),
             "titleWrap": lit("false"), "bold": lit("true")}
    props["text"] = {"expr": {"Measure": campo_med(medida)["Measure"]}} if medida else txt(texto)
    return {"title": [{"properties": props}],
            "padding": [{"properties": {"top": num(6), "bottom": num(4), "left": num(8), "right": num(8)}}]}


def sem_fundo() -> dict:
    return {"background": [{"properties": {"show": lit("false")}}],
            "border": [{"properties": {"show": lit("false")}}],
            "dropShadow": [{"properties": {"show": lit("false")}}]}


def ordenar(campo: dict, desc: bool = True) -> dict:
    return {"sort": [{"field": campo, "direction": "Descending" if desc else "Ascending"}]}


def filtro_in(nome: str, ent: str, prop: str, valores: list) -> dict:
    vals = [[{"Literal": {"Value": "'" + str(v).replace("'", "''") + "'"}}] for v in valores]
    return {"name": nome, "field": campo_col(ent, prop), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "f", "Entity": ent, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [
                           {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": prop}}],
                           "Values": vals}}}]},
            "howCreated": "User"}


FILTRO_BENCH = ("dInstalacao", "Grupo do Benchmark", ["Suape", "Pares do Nordeste"])


def filtro_nao_vazio(nome: str, ent: str, prop: str) -> dict:
    """Filtro avançado 'não está em branco' (esconde o item (Em branco) das segmentações)."""
    return {"name": nome, "field": campo_col(ent, prop), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "f", "Entity": ent, "Type": 0}],
                       "Where": [{"Condition": {"Not": {"Expression": {"Comparison": {
                           "ComparisonKind": 0,
                           "Left": {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": prop}},
                           "Right": {"Literal": {"Value": "null"}}}}}}}]},
            "howCreated": "User"}


class Pagina:
    def __init__(self, nome: str, exibicao: str, oculta: bool = False):
        self.nome, self.exibicao, self.oculta = nome, exibicao, oculta
        self.visuais: list[dict] = []
        self.filtros: list[dict] = []
        self.z = 1000

    def add(self, nome: str, x, y, w, h, visual: dict | None = None, filtros=None, z: int | None = None,
            **extra) -> dict:
        self.z += 100
        zz = z if z is not None else self.z
        v = {"$schema": f"{SCHEMA}/item/report/definition/visualContainer/2.0.0/schema.json",
             "name": nome, "position": {"x": x, "y": y, "z": zz, "height": h, "width": w, "tabOrder": zz}}
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


def rotulos_fora(tamanho=9) -> dict:
    """Rótulo de dado fora da barra, claro, sem unidade automática (o formato da medida já tem a unidade)."""
    return {"labels": [{"properties": {"show": lit("true"), "color": cor(T_SUAVE), "fontSize": num(tamanho),
                                       "labelPosition": txt("OutsideEnd"), "labelDisplayUnits": num(1),
                                       "enableBackground": lit("false")}}]}


def eixos_limpos(eixo_valor: bool = False, fonte=9) -> dict:
    return {"categoryAxis": [{"properties": {"show": lit("true"), "fontSize": num(fonte), "showAxisTitle": lit("false"),
                                             "labelColor": cor(T_SUAVE), "maxMarginFactor": num(45),
                                             "innerPadding": lit("12L"), "minCategoryWidth": lit("14L")}}],
            "valueAxis": [{"properties": {"show": lit("true" if eixo_valor else "false"), "showAxisTitle": lit("false"),
                                          "fontSize": num(fonte), "labelDisplayUnits": num(1),
                                          "gridlineShow": lit("true" if eixo_valor else "false")}}]}


def barras(categoria: dict, valor: dict, titulo_med: str | None = None, titulo_txt: str | None = None,
           cor_suape: bool = False, ordem_desc: bool = True, sort_campo: dict | None = None,
           tooltips: list | None = None, fonte: int = 9) -> dict:
    obj = {**rotulos_fora(fonte), **eixos_limpos(fonte=fonte)}
    if cor_suape:
        obj["dataPoint"] = [{"properties": {"fill": cor_medida("Cor Destaque Suape")}, "selector": todos()}]
    else:
        obj["dataPoint"] = [{"properties": {"fill": cor(M.COR_PADRAO)}}]
    papeis = {"Category": [categoria], "Y": [valor]}
    if tooltips:
        papeis["Tooltips"] = tooltips
    return vis("clusteredBarChart", papeis, obj, titulo(titulo_txt, titulo_med),
               sort=ordenar(sort_campo or valor["field"], ordem_desc))


def cartao(medida: str, rotulo: str, tamanho: int = 17, cor_valor: str = T_BRANCO) -> dict:
    return vis("card", {"Values": [Me(medida, nome=rotulo)]},
               {"labels": [{"properties": {"fontSize": num(tamanho), "color": cor(cor_valor),
                                           "labelDisplayUnits": num(1)}}],
                "categoryLabels": [{"properties": {"show": lit("true"), "fontSize": num(9),
                                                   "color": cor("#8A8F98")}}],
                "wordWrap": [{"properties": {"show": lit("false")}}]},
               {"title": [{"properties": {"show": lit("false")}}],
                "padding": [{"properties": {"top": num(2), "bottom": num(2), "left": num(4), "right": num(4)}}]})


def manchete(medida: str, tamanho: int = 13) -> dict:
    """Card de texto sem rótulo (manchete da página, centralizada)."""
    return vis("card", {"Values": [Me(medida)]},
               {"labels": [{"properties": {"fontSize": num(tamanho), "color": cor(T_BRANCO)}}],
                "categoryLabels": [{"properties": {"show": lit("false")}}],
                "wordWrap": [{"properties": {"show": lit("false")}}]},
               {"title": [{"properties": {"show": lit("false")}}], **sem_fundo()})


def textbox(paragrafos: list[list[dict]], fundo: bool = False) -> dict:
    v = vis("textbox", objetos={"general": [{"properties": {"paragraphs": [
        {"textRuns": runs} for runs in paragrafos]}}]})
    if not fundo:
        v["visualContainerObjects"] = sem_fundo()
    return v


def run(texto: str, tam=11, cor_hex=T_SUAVE, negrito=False, url: str | None = None) -> dict:
    estilo = {"fontFamily": "Segoe UI", "fontSize": f"{tam}pt", "color": cor_hex}
    if negrito:
        estilo["fontWeight"] = "bold"
    r = {"value": texto, "textStyle": estilo}
    if url:
        r["url"] = url
    return r


def linha_tempo(medidas: list[tuple[str, str, str]], titulo_med: str) -> dict:
    """Linha mensal: eixo X = mês abreviado (sem inclinação), legenda no topo à esquerda."""
    return vis("lineChart", {"Category": [C("dCalendario", "Mês (abrev.)", ativo=True)],
                             "Y": [Me(m, nome=n) for m, n, _ in medidas]},
               {"dataPoint": [{"properties": {"fill": cor(c)}, "selector": {"metadata": f"{MED}.{m}"}}
                              for m, _, c in medidas],
                "legend": [{"properties": {"show": lit("true"), "position": txt("Top"), "fontSize": num(9),
                                           "labelColor": cor(T_SUAVE), "showTitle": lit("false")}}],
                "categoryAxis": [{"properties": {"show": lit("true"), "showAxisTitle": lit("false"),
                                                 "fontSize": num(9), "labelColor": cor(T_SUAVE),
                                                 "concatenateLabels": lit("false")}}],
                "valueAxis": [{"properties": {"show": lit("true"), "showAxisTitle": lit("false"), "fontSize": num(9),
                                              "labelDisplayUnits": num(1), "labelColor": cor(T_SUAVE)}}],
                "lineStyles": [{"properties": {"strokeWidth": num(3), "showMarker": lit("true")}}]},
               titulo(medida=titulo_med),
               sort=ordenar(campo_col("dCalendario", "Mês (abrev.)"), False))


# ===========================================================================
# Cabeçalho e páginas
# ===========================================================================
PAGINAS = [("visao_geral", "Visão Geral"), ("nordeste_suape", "Nordeste & Suape"),
           ("eficiencia", "Eficiência e Gargalos"), ("perfil_carga", "Perfil de Carga"), ("sobre", "Sobre")]
ROTULO_BOTAO = {"visao_geral": "Visão Geral", "nordeste_suape": "Nordeste & Suape",
                "eficiencia": "Eficiência", "perfil_carga": "Perfil de Carga", "sobre": "Sobre"}
SUBTITULO = {"visao_geral": "Visão geral do Brasil", "nordeste_suape": "Suape x pares do Nordeste",
             "eficiencia": "Onde estão os gargalos", "perfil_carga": "O que cada porto movimenta",
             "sobre": "Sobre o painel", "mapa_plano_b": "Mapa (plano B)"}
BOT_W, BOT_GAP = 148, 8


def slicer(nome_campo: tuple[str, str], cabecalho: str, grupo: str | None, padrao_ano: bool = False) -> dict:
    ent, prop = nome_campo
    obj = {"data": [{"properties": {"mode": txt("Dropdown")}}],
           "header": [{"properties": {"show": lit("true"), "text": txt(cabecalho), "fontColor": cor(T_SUAVE),
                                      "textSize": num(9)}}],
           "items": [{"properties": {"textSize": num(10), "fontColor": cor(T_BRANCO)}}],
           "selection": [{"properties": {"singleSelect": lit("true" if padrao_ano else "false"),
                                         "strictSingleSelect": lit("false")}}]}
    if padrao_ano:
        obj["general"] = [{"properties": {"filter": {"filter": {
            "Version": 2, "From": [{"Name": "c", "Entity": ent, "Type": 0}],
            "Where": [{"Condition": {"In": {"Expressions": [
                {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": prop}}],
                "Values": [[{"Literal": {"Value": f"{M.ANO_FINAL}L"}}]]}}}]}}}}]
    extra = {"syncGroup": {"groupName": grupo, "fieldChanges": True, "filterChanges": True}} if grupo else {}
    return vis("slicer", {"Values": [C(ent, prop, ativo=True)]}, obj,
               {"title": [{"properties": {"show": lit("false")}}],
                "padding": [{"properties": {"top": num(2), "bottom": num(2), "left": num(6), "right": num(6)}}]},
               sort=ordenar(campo_col(ent, prop), False), **extra)


def cabecalho(p: Pagina, manchete_med: str | None, slicer_extra: tuple | None = None) -> None:
    p.add("cab_titulo", MG, 6, 440, 70, textbox([[run("Raio-X Portuário", 18, T_BRANCO, True)],
                                                 [run(SUBTITULO[p.nome], 10, M.COR_SUAPE)]]))
    x0 = LARG - MG - (5 * BOT_W + 4 * BOT_GAP)
    for i, (pag, _) in enumerate(PAGINAS):
        atual = pag == p.nome
        p.add(f"nav_{pag}", x0 + i * (BOT_W + BOT_GAP), 20, BOT_W, 36, vis(
            "actionButton",
            objetos={
                "icon": [{"properties": {"show": lit("false")}}],
                "text": [{"properties": {"show": lit("true")}},
                         {"properties": {"text": txt(ROTULO_BOTAO[pag]),
                                         "fontColor": cor("#000000" if atual else T_BRANCO),
                                         "fontSize": num(11), "bold": lit("true"),
                                         "horizontalAlignment": txt("center"), "verticalAlignment": txt("middle")},
                          "selector": {"id": "default"}}],
                "fill": [{"properties": {"show": lit("true")}},
                         {"properties": {"fillColor": cor(M.COR_SUAPE if atual else "#1D2127"),
                                         "transparency": num(0)}, "selector": {"id": "default"}}],
                "outline": [{"properties": {"show": lit("false")}}],
                "shape": [{"properties": {"tileShape": txt("rectangleRounded"), "roundEdge": num(6)}}]},
            container={"visualLink": [{"properties": {"show": lit("true"), "type": txt("PageNavigation"),
                                                      "navigationSection": txt(pag)}}],
                       **sem_fundo()}),
            howCreated="InsertVisualButton")
    y, h = 84, 60
    p.add("seg_ano", MG, y, 160, h, slicer(("dCalendario", "Ano"), "Ano", "Ano", padrao_ano=True))
    p.add("seg_regiao", MG + 160 + GAP, y, 210, h, slicer(("dInstalacao", "Região"), "Região", "Regiao"),
          filtros=[filtro_nao_vazio("RegiaoNaoVazia", "dInstalacao", "Região")])
    x = MG + 160 + GAP + 210 + GAP
    if slicer_extra:
        ent, prop, cab, larg = slicer_extra
        p.add("seg_extra", x, y, larg, h, slicer((ent, prop), cab, None),
              filtros=[filtro_nao_vazio("ExtraNaoVazio", ent, prop)])
        x += larg + GAP
    if manchete_med:
        p.add("manchete", x, y + 8, LARG - MG - x, h - 16, manchete(manchete_med))


def linha_cartoes(p: Pagina, itens: list[tuple[str, str]], prefixo: str = "kpi", cor_valor: str = T_BRANCO) -> None:
    n = len(itens)
    w = (LARG - 2 * MG - (n - 1) * GAP) / n
    for i, (m, r) in enumerate(itens):
        p.add(f"{prefixo}_{i + 1}", MG + i * (w + GAP), Y_CARD, w, H_CARD, cartao(m, r, cor_valor=cor_valor))


# ---------------------------------------------------------------------------
# Mapas
# ---------------------------------------------------------------------------
TOOLTIP_MAPA = [Me("UF do Complexo", nome="UF"), Me("Toneladas (Mi t)", nome="Toneladas"),
                Me("Var % Toneladas AA", nome="Var. vs. ano anterior"), Me("Espera Mediana (h)", nome="Espera mediana"),
                Me("Prancha Média Operacional (t/h)", nome="Prancha operacional")]


def legenda_mapa(p: Pagina, x, y, w) -> None:
    p.add("mapa_legenda", x + 8, y - 6, w - 16, 32, textbox([[
        run("● ", 9, M.COR_SUAPE), run("Suape   ", 9), run("● ", 9, M.COR_PADRAO),
        run("demais complexos   ·   tamanho = toneladas", 9)]]), z=9000)


def mapa_azure(p: Pagina, x, y, w, h) -> None:
    mapa = vis("azureMap",
               {"Category": [C("dInstalacao", "Complexo Portuário", ativo=True)],
                "Y": [media("dInstalacao", "Latitude do Complexo", "Latitude")],
                "X": [media("dInstalacao", "Longitude do Complexo", "Longitude")],
                "Size": [Me("Toneladas (Mi t)", nome="Toneladas")], "Tooltips": TOOLTIP_MAPA},
               # nomes de propriedade lidos de um visual salvo pelo próprio Desktop (DECISOES D19)
               {"mapControls": [{"properties": {
                   "autoZoom": lit("false"), "zoom": num(2.75), "centerLatitude": num(-14.46),
                   "centerLongitude": num(-53.53), "heading": num(0), "pitch": num(0),
                   "defaultStyle": txt("grayscale_dark"), "showStylePicker": lit("false"),
                   "showNavigationControls": lit("false"), "showSelectionControl": lit("false"),
                   "showLabels": lit("false"), "worldWrap": lit("false")}}],
                "bubbleLayer": [{"properties": {"bubbleRadius": num(2), "minBubbleRadius": num(2), "maxRadius": lit("18L"),
                                                "mapTransparency": num(40), "bubbleStrokeWidth": num(1),
                                                "strokeColor": cor("#FFFFFF"), "markerRangeType": txt("magnitude")}}],
                "dataPoint": [{"properties": {"fill": cor_medida("Cor Destaque Suape")}, "selector": todos()}],
                "categoryLabels": [{"properties": {"show": lit("false")}}],
                "legend": [{"properties": {"show": lit("false")}}]},
               titulo(medida="Título Mapa", tamanho=10), sort=ordenar(campo_med("Toneladas (Mi t)")))
    p.add("mapa_bolhas", x, y, w, h, mapa)
    legenda_mapa(p, x, y + h - 30, w)


def imagem_data_uri() -> str:
    """PNG da malha do IBGE embutido no visual de imagem (data URI), reduzido para ~20 px por grau."""
    import base64
    import io

    from PIL import Image
    origem = RP / "StaticResources" / "RegisteredResources" / IMG_MAPA
    if not origem.exists():
        mapa_base.main()
    img = Image.open(origem)
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def mapa_dispersao(p: Pagina, x, y, w, h) -> None:
    """Mapa próprio: duas dispersões sobrepostas com eixos fixos = extensão da imagem do IBGE.
    Camada de baixo: imagem de fundo + rótulos de Suape e dos 5 maiores (posição de rótulo fixa por complexo).
    Camada de cima (transparente): bolhas com dica de ferramenta. Título e legenda em caixas próprias, para
    que as duas áreas de plotagem fiquem idênticas à imagem."""
    e = mapa_base.EXTENSAO
    h_tit = 30
    painel = textbox([[run(" ", 6)]])
    painel["visualContainerObjects"] = {
        "background": [{"properties": {"show": lit("true"), "color": cor("#0C0D10"), "transparency": num(0)}}],
        "border": [{"properties": {"show": lit("true"), "color": cor("#1D2127"), "radius": num(8)}}]}
    p.add("mapa_painel", x, y, w, h, painel, z=4000)
    p.add("mapa_titulo", x + 2, y + 2, w - 4, h_tit, manchete("Título Mapa", tamanho=10), z=9000)
    eixos = {"categoryAxis": [{"properties": {"show": lit("false"), "start": num(e["lon_min"]), "end": num(e["lon_max"]),
                                              "gridlineShow": lit("false"), "showAxisTitle": lit("false")}}],
             "valueAxis": [{"properties": {"show": lit("false"), "start": num(e["lat_min"]), "end": num(e["lat_max"]),
                                           "gridlineShow": lit("false"), "showAxisTitle": lit("false")}}],
             "legend": [{"properties": {"show": lit("false")}}]}
    sem_margem = {"title": [{"properties": {"show": lit("false")}}],
                  "padding": [{"properties": {"top": num(0), "bottom": num(0), "left": num(0), "right": num(0)}}],
                  "border": [{"properties": {"show": lit("false")}}],
                  "dropShadow": [{"properties": {"show": lit("false")}}]}
    imagem = {"image": {"name": txt("Brasil (malha IBGE)"),
                        "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1,
                                                                 "ItemName": IMG_MAPA}}},
                        "scaling": txt("Fit")}}
    ym, hm = y + h_tit, h - h_tit - 4
    p.add("mapa_imagem_ibge", x + 2, ym, w - 4, hm, vis(
        "image", objetos={"general": [{"properties": {"imageUrl": lit("'" + imagem_data_uri() + "'")}}],
                          "imageScaling": [{"properties": {"imageScalingType": txt("Fit")}}]},
        container=sem_margem | {"background": [{"properties": {"show": lit("false")}}]}), z=4500)
    fundo = vis("scatterChart",
                {"Category": [C("dInstalacao", "Complexo Portuário", ativo=True)],
                 "X": [Me("Longitude (rótulo)")], "Y": [Me("Latitude (rótulo)")]},
                {**eixos,
                 "categoryLabels": [{"properties": {"show": lit("true"), "color": cor(T_BRANCO), "fontSize": num(9),
                                                    "enableBackground": lit("false")}}],
                 "dataPoint": [{"properties": {"fill": cor("#14161C"), "transparency": num(100)}}],
                 "bubbles": [{"properties": {"bubbleSize": num(-50)}}]},
                {**sem_margem, "background": [{"properties": {"show": lit("false")}}]})
    p.add("mapa_fundo_rotulos", x + 2, ym, w - 4, hm, fundo, z=5000)
    bolhas = vis("scatterChart",
                 {"Category": [C("dInstalacao", "Complexo Portuário", ativo=True)],
                  "X": [Me("Longitude do Complexo", nome="Longitude")], "Y": [Me("Latitude do Complexo", nome="Latitude")],
                  "Size": [Me("Toneladas (Mi t)", nome="Toneladas")], "Tooltips": TOOLTIP_MAPA},
                 {**eixos,
                  "dataPoint": [{"properties": {"fill": cor_medida("Cor Destaque Suape")}, "selector": todos()},
                                {"properties": {"transparency": num(40)}}],
                  "bubbles": [{"properties": {"bubbleSize": num(-22), "markerRangeType": txt("magnitude")}}],
                  "categoryLabels": [{"properties": {"show": lit("false")}}]},
                 {**sem_margem, "background": [{"properties": {"show": lit("false")}}]})
    p.add("mapa_bolhas", x + 2, ym, w - 4, hm, bolhas, z=6000)
    legenda_mapa(p, x, y + h - 30, w)


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def pagina_visao_geral(nome="visao_geral", exibicao="Visão Geral", mapa="dispersao", oculta=False) -> Pagina:
    p = Pagina(nome, exibicao, oculta)
    cabecalho(p, "Título KPI Brasil")
    linha_cartoes(p, [("Rótulo Toneladas", "Toneladas"), ("Rótulo Var % AA", "Variação vs. ano anterior"),
                      ("Rótulo Atracações", "Atracações com carga"), ("Rótulo Espera Mediana", "Espera mediana para atracar"),
                      ("Rótulo Prancha Operacional", "Prancha operacional")])
    h1 = 168
    p.add("linha_mensal", MG, Y_CONT, 506, h1, linha_tempo(
        [("Toneladas (Mi t)", "Toneladas", M.COR_PADRAO), ("Toneladas AA (Mi t)", "Ano anterior", M.COR_ANO_ANTERIOR)],
        "Título Linha Mensal"))
    p.add("barras_regiao", MG + 506 + GAP, Y_CONT, COL_ESQ - 506 - GAP, h1,
          barras(C("dInstalacao", "Região"), Me("Toneladas (Mi t)", nome="Toneladas"), titulo_med="Título Região", fonte=8),
          filtros=[filtro_in("FiltroRegiaoIdentificada", "dInstalacao", "Região",
                             ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])])
    y2 = Y_CONT + h1 + GAP
    p.add("top10_instalacoes", MG, y2, COL_ESQ, Y_FIM - y2,
          barras(C("dInstalacao", "Instalação"), Me("Toneladas (Top 10) (Mi t)", nome="Toneladas"),
                 titulo_med="Título Top 10", cor_suape=True))
    (mapa_azure if mapa == "azure" else mapa_dispersao)(p, X_DIR, Y_CONT, L_DIR, Y_FIM - Y_CONT)
    return p


def pagina_nordeste() -> Pagina:
    p = Pagina("nordeste_suape", "Nordeste & Suape")
    p.filtros.append(filtro_in("FiltroBenchmarkNE", *FILTRO_BENCH))
    cabecalho(p, "Título Benchmark Espera")
    linha_cartoes(p, [("Rótulo Toneladas Suape", "Toneladas de Suape"), ("Rótulo Var % Suape", "Variação de Suape"),
                      ("Rótulo TEU Suape", "Contêineres em Suape"), ("Rótulo % Contêiner Suape", "Fatia de contêiner"),
                      ("Rótulo Ranking Suape", "Posição de Suape")], prefixo="card_suape", cor_valor=M.COR_SUAPE)
    h_tab = 270
    tabela = vis("tableEx", {"Values": [
        C("dInstalacao", "Porto (benchmark NE)", nome="Porto"), Me("Toneladas (Mi t)", nome="Toneladas"),
        Me("Var % Toneladas AA", nome="Var. AA"), Me("Espera Mediana (h)", nome="Espera mediana"),
        Me("Prancha Média Operacional (t/h)", nome="Prancha op."), Me("% Contêiner", nome="% contêiner"),
        Me("Ranking Porto", nome="Ranking")]},
        {"values": [
            {"properties": {"fontSize": num(10), "fontColorPrimary": cor(T_SUAVE)}},
            {"properties": {"backColor": cor_medida("Cor Benchmark Espera")},
             "selector": todos({"metadata": f"{MED}.Espera Mediana (h)"})},
            {"properties": {"fontColor": cor_medida("Cor Texto Suape")},
             "selector": todos({"metadata": "dInstalacao.Porto (benchmark NE)"})}],
         "columnHeaders": [{"properties": {"fontSize": num(10), "fontColor": cor(T_BRANCO), "wordWrap": lit("false")}}],
         "grid": [{"properties": {"rowPadding": num(2)}}],
         "columnWidth": [{"properties": {"value": num(96)}, "selector": {"metadata": "dInstalacao.Porto (benchmark NE)"}}]
         + [{"properties": {"value": num(116)}, "selector": {"metadata": f"{MED}.{m}"}}
            for m in ("Toneladas (Mi t)", "Var % Toneladas AA", "Espera Mediana (h)",
                      "Prancha Média Operacional (t/h)", "% Contêiner", "Ranking Porto")],
         "total": [{"properties": {"totals": lit("false")}}]},
        titulo(medida="Título Tabela Benchmark"), sort=ordenar(campo_med("Toneladas (Mi t)")))
    p.add("tabela_benchmark", MG, Y_CONT, COL_ESQ, h_tab, tabela)
    y2 = Y_CONT + h_tab + GAP
    p.add("linha_suape_pares", MG, y2, COL_ESQ, Y_FIM - y2, linha_tempo(
        [("Espera Mediana Suape (h)", "Suape", M.COR_SUAPE),
         ("Espera Mediana Média Pares (h)", "Média dos pares", M.COR_ANO_ANTERIOR)], "Título Linha Suape Pares"))
    p.add("barras_crescimento", X_DIR, Y_CONT, L_DIR, Y_FIM - Y_CONT,
          barras(C("dInstalacao", "Porto (benchmark NE)"), Me("Var % Toneladas AA", nome="Var. vs. ano anterior"),
                 titulo_med="Título Crescimento Pares", cor_suape=True))
    return p


def pagina_eficiencia() -> Pagina:
    p = Pagina("eficiencia", "Eficiência e Gargalos")
    cabecalho(p, "Título Eficiência")
    linha_cartoes(p, [("Rótulo Espera Mediana", "Espera mediana para atracar"),
                      ("Rótulo Tempo Atracado", "Tempo atracado médio"),
                      ("Rótulo % Atracado em Operação", "Tempo atracado em operação"),
                      ("Rótulo Prancha Operacional", "Prancha operacional"),
                      ("Rótulo Horas Paralisadas", "Horas paralisadas")])
    w1, w2 = 500, LARG - 2 * MG - 500 - GAP
    h1 = 196
    disp = vis("scatterChart", {"Category": [C("dInstalacao", "Instalação", ativo=True)],
                                "X": [Me("Espera Mediana (h)", nome="Espera mediana")],
                                "Y": [Me("Prancha Média Operacional (t/h)", nome="Prancha operacional")],
                                "Size": [Me("Toneladas (Mi t)", nome="Toneladas")]},
               {"dataPoint": [{"properties": {"fill": cor_medida("Cor Destaque Suape")}, "selector": todos()}],
                "categoryLabels": [{"properties": {"show": lit("false")}}],
                "categoryAxis": [{"properties": {"show": lit("true"), "showAxisTitle": lit("false"), "fontSize": num(9),
                                                 "labelDisplayUnits": num(1)}}],
                "valueAxis": [{"properties": {"show": lit("true"), "showAxisTitle": lit("false"), "fontSize": num(9),
                                              "labelDisplayUnits": num(1)}}]},
               titulo(medida="Título Dispersão"))
    p.add("dispersao_espera_prancha", MG, Y_CONT, w1, h1, disp,
          filtros=[filtro_in("FiltroPortoOrganizado", "dInstalacao", "Tipo de Instalação", ["Porto Organizado"])])
    calor = vis("pivotTable", {"Rows": [C("dInstalacao", "Porto (benchmark NE)", ativo=True, nome="Porto")],
                               "Columns": [C("dCalendario", "Mês (abrev.)", ativo=True, nome="Mês")],
                               "Values": [Me("Espera Mediana (h)", nome="Espera mediana")]},
                {"values": [{"properties": {"fontSize": num(8)}},
                            {"properties": {"backColor": cor_medida("Cor Calor Espera"), "fontColor": cor(T_BRANCO)},
                             "selector": todos({"metadata": f"{MED}.Espera Mediana (h)"})}],
                 "subTotals": [{"properties": {"rowSubtotals": lit("false"), "columnSubtotals": lit("false")}}],
                 "columnHeaders": [{"properties": {"fontSize": num(8), "fontColor": cor(T_BRANCO)}}],
                 "rowHeaders": [{"properties": {"fontSize": num(8), "fontColor": cor(T_BRANCO)}}],
                 "grid": [{"properties": {"rowPadding": num(0)}}]},
                titulo(medida="Título Mapa de Calor"))
    p.add("mapa_calor_espera", MG + w1 + GAP, Y_CONT, w2, h1, calor,
          filtros=[filtro_in("FiltroBenchmarkNE", *FILTRO_BENCH)])
    y2 = Y_CONT + h1 + GAP
    p.add("barras_pct_operacao", MG, y2, w1, Y_FIM - y2,
          barras(C("dInstalacao", "Porto (benchmark NE)"), Me("% Atracado em Operação"),
                 titulo_med="Título Operação", cor_suape=True, fonte=8),
          filtros=[filtro_in("FiltroBenchmarkNE", *FILTRO_BENCH)])
    p.add("barras_paralisacao", MG + w1 + GAP, y2, w2, Y_FIM - y2,
          barras(C("fParalisacao", "Motivo da Paralisação"), Me("Horas Paralisadas (Top 8 motivos)", nome="Horas"),
                 titulo_med="Título Paralisação", fonte=8))
    return p


def pagina_perfil() -> Pagina:
    p = Pagina("perfil_carga", "Perfil de Carga")
    cabecalho(p, "Título Perfil", slicer_extra=("dInstalacao", "Instalação", "Porto / terminal", 300))
    linha_cartoes(p, [("Rótulo Toneladas", "Toneladas"), ("Rótulo TEU", "Contêineres (TEU)"),
                      ("Rótulo % Longo Curso", "Longo curso"), ("Rótulo % Cabotagem", "Cabotagem"),
                      ("Rótulo % Contêiner", "Contêiner")])
    w = (LARG - 2 * MG - GAP) / 2
    h1 = 280
    empilhado = vis("columnChart", {"Category": [C("dCalendario", "Mês (abrev.)", ativo=True)],
                                    "Series": [C("dNaturezaCarga", "Natureza da Carga")],
                                    "Y": [Me("Toneladas (Mi t)", nome="Toneladas")]},
                    {"legend": [{"properties": {"show": lit("true"), "position": txt("Top"), "fontSize": num(9),
                                                "labelColor": cor(T_SUAVE), "showTitle": lit("false")}}],
                     **eixos_limpos(eixo_valor=True)},
                    titulo(medida="Título Natureza"), sort=ordenar(campo_col("dCalendario", "Mês (abrev.)"), False))
    p.add("empilhado_natureza", MG, Y_CONT, w, h1, empilhado)
    p.add("top_mercadorias", MG + w + GAP, Y_CONT, w, h1,
          barras(C("dMercadoria", "Mercadoria"), Me("Toneladas (Top 10 mercadorias) (Mi t)", nome="Toneladas"),
                 titulo_med="Título Mercadorias", fonte=8))
    y2 = Y_CONT + h1 + GAP
    p.add("barras_navegacao", MG, y2, w, Y_FIM - y2,
          barras(C("dNavegacao", "Navegação"), Me("Toneladas (Mi t)", nome="Toneladas"), titulo_med="Título Navegação"))
    rosca = vis("donutChart", {"Category": [C("dSentido", "Sentido")], "Y": [Me("Toneladas (Mi t)", nome="Toneladas")]},
                {"legend": [{"properties": {"show": lit("true"), "position": txt("Right"), "fontSize": num(10),
                                            "labelColor": cor(T_SUAVE), "showTitle": lit("false")}}],
                 "labels": [{"properties": {"show": lit("true"), "labelStyle": txt("Percent of total"),
                                            "color": cor(T_BRANCO), "fontSize": num(10)}}],
                 "dataPoint": [{"properties": {"fill": cor(M.COR_PADRAO)}, "selector": {"data": [{"scopeId": {
                     "Comparison": {"ComparisonKind": 0, "Left": campo_col("dSentido", "Sentido"),
                                    "Right": {"Literal": {"Value": "'Embarque'"}}}}}]}},
                               {"properties": {"fill": cor("#7DB592")}, "selector": {"data": [{"scopeId": {
                                   "Comparison": {"ComparisonKind": 0, "Left": campo_col("dSentido", "Sentido"),
                                                  "Right": {"Literal": {"Value": "'Desembarque'"}}}}}]}},
                               {"properties": {"fill": cor(M.COR_ANO_ANTERIOR)}, "selector": {"data": [{"scopeId": {
                                   "Comparison": {"ComparisonKind": 0, "Left": campo_col("dSentido", "Sentido"),
                                                  "Right": {"Literal": {"Value": "'Não informado'"}}}}}]}}]},
                titulo(medida="Título Sentido"), sort=ordenar(campo_med("Toneladas (Mi t)")))
    p.add("rosca_sentido", MG + w + GAP, y2, w, Y_FIM - y2, rosca)
    return p


def pagina_sobre() -> Pagina:
    p = Pagina("sobre", "Sobre")
    cabecalho(p, "Última Atualização")
    h = lambda s: [run(s, 12, M.COR_SUAPE, True)]  # noqa: E731
    t = lambda s: [run(s, 10)]  # noqa: E731
    esquerda = [
        h("O que é"),
        t("Painel sobre o desempenho dos portos brasileiros com foco em Suape e nos pares do Nordeste: "
          "quanto se movimenta, onde estão os gargalos e o que cada porto movimenta."),
        h("Fonte e recorte"),
        [run("ANTAQ — Estatístico Aquaviário (dados abertos): Atracação, Carga, Tempos de Atracação e Paralisações. ", 10),
         run("gov.br/antaq", 10, M.COR_PADRAO, url="https://www.gov.br/antaq/pt-br/assuntos/estatistica")],
        t(f"Anos completos {M.ANO_INICIAL}–{M.ANO_FINAL}; período = mês da desatracação, como na ANTAQ. "
          "Com o portal de download da ANTAQ fora do ar desde jun/2026, os arquivos oficiais vieram de um espelho "
          "público (Hugging Face, CC-BY-4.0, versão fixada)."),
        t("Suape = porto organizado de Suape; pares = Pecém, Itaqui, Salvador, Aratu, Recife, Natal, Cabedelo e Maceió. "
          "No mapa, os pontos são complexos portuários (ANTAQ); Suape aparece no complexo Suape - Recife."),
        h("Conferência com a ANTAQ"),
        t("O total anual do painel difere do publicado pela ANTAQ entre −0,13% e +1,16% (2021–2025). "
          "Nota: o painel mostra +5,9% em 2025 x 2024; o Anuário publica +6,1%. Os totais de 2025 batem "
          "(+0,05%), mas a base de 2024 do painel está 0,26% acima da do Anuário (dados revisados depois da "
          "publicação), o que reduz a variação em 0,2 ponto. O número não foi forçado a bater."),
        h("Regras de limpeza"),
        t("Toneladas = peso bruto das cargas marcadas como movimentação (FlagMCOperacaoCarga = 1), com transbordo. "
          "Tempos: os calculados pela ANTAQ; negativos descartados; acima do percentil 99,5 da natureza de carga, "
          "limitados ao percentil. Tonelagem nunca é cortada."),
    ]
    direita = [
        h("Como ler as métricas"),
        t("Espera = chegada até atracação. A mediana mostra o navio típico; a média é puxada por filas longas."),
        t("Tempo atracado = atracação até desatracação. Tempo de operação = início ao fim da carga/descarga."),
        t("% do tempo atracado em operação = horas operando ÷ horas no berço."),
        t("Prancha operacional = toneladas ÷ horas de operação (sempre razão de somas). Mi t = milhões de toneladas."),
        h("Créditos"),
        t("Dados: ANTAQ. Nomenclatura de mercadorias: Comex Stat/MDIC. Malha do mapa: IBGE."),
        h("Projeto"),
        [run("Código, dados tratados e método: ", 10),
         run("github.com/gorc-supply/raio-x-portuario", 10, M.COR_PADRAO,
             url="https://github.com/gorc-supply/raio-x-portuario")],
        [run("Portfólio: ", 10), run("gorc-supply.github.io", 10, M.COR_PADRAO, url="https://gorc-supply.github.io")],
        [run("Gabriel Cunha · Supply Chain & Operations · Recife/PE · ", 10, T_BRANCO, True),
         run("LinkedIn", 10, M.COR_PADRAO, url="https://www.linkedin.com/in/gabriel-cunha-xp")],
    ]
    w = (LARG - 2 * MG - GAP) / 2
    p.add("texto_sobre_esq", MG, Y_CARD, w, Y_FIM - Y_CARD, textbox(esquerda, fundo=True))
    p.add("texto_sobre_dir", MG + w + GAP, Y_CARD, w, Y_FIM - Y_CARD, textbox(direita, fundo=True))
    return p


def tema() -> dict:
    fundo, painel, linha, texto, suave = "#000000", "#0C0D10", "#1D2127", T_BRANCO, T_SUAVE
    return {
        "name": "Raio-X Portuário (identidade gorc-supply)",
        "dataColors": ["#8FB4D9", "#7DB592", "#D98A86", "#D9A87A", "#8A8F98", "#5B7A99", "#B39DDB", "#4DB6AC"],
        "background": painel, "foreground": texto, "tableAccent": M.COR_SUAPE,
        "good": "#7DB592", "neutral": "#D9A87A", "bad": "#D98A86",
        "maximum": "#7A1C2A", "center": "#6E5F33", "minimum": "#1E3A2F",
        "textClasses": {
            "callout": {"fontSize": 20, "fontFace": "Segoe UI Semibold", "color": texto},
            "title": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": texto},
            "header": {"fontSize": 10, "fontFace": "Segoe UI Semibold", "color": texto},
            "label": {"fontSize": 9, "fontFace": "Segoe UI", "color": suave},
        },
        "visualStyles": {
            "page": {"*": {
                "background": [{"color": {"solid": {"color": fundo}}, "transparency": 0}],
                "outspace": [{"color": {"solid": {"color": fundo}}, "transparency": 0}]}},
            "*": {"*": {
                "background": [{"show": True, "color": {"solid": {"color": painel}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": linha}}, "radius": 8}],
                "title": [{"show": True, "fontColor": {"solid": {"color": texto}}, "fontSize": 11, "titleWrap": False}],
                "categoryAxis": [{"labelColor": {"solid": {"color": suave}}, "titleColor": {"solid": {"color": suave}},
                                  "gridlineColor": {"solid": {"color": linha}}, "showAxisTitle": False}],
                "valueAxis": [{"labelColor": {"solid": {"color": suave}}, "titleColor": {"solid": {"color": suave}},
                               "gridlineColor": {"solid": {"color": linha}}, "showAxisTitle": False}],
                "legend": [{"labelColor": {"solid": {"color": suave}}}],
                "labels": [{"color": {"solid": {"color": suave}}}],
                "visualTooltip": [{"titleFontColor": {"solid": {"color": texto}},
                                   "valueFontColor": {"solid": {"color": texto}},
                                   "background": {"solid": {"color": "#121419"}}}],
                "visualHeader": [{"background": {"solid": {"color": painel}},
                                  "foreground": {"solid": {"color": suave}}, "border": {"solid": {"color": painel}}}]}},
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


def gerar_relatorio(mapa: str, com_plano_b: bool = True) -> None:
    d = RP / "definition"
    if d.exists():
        shutil.rmtree(d)
    outro = "azure" if mapa == "dispersao" else "dispersao"
    paginas = [pagina_visao_geral(mapa=mapa), pagina_nordeste(), pagina_eficiencia(), pagina_perfil(), pagina_sobre()]
    plano_b = pagina_visao_geral("mapa_plano_b", "Mapa (plano B)", mapa=outro, oculta=True) if com_plano_b else None
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
             "items": [{"name": "tema-raio-x.json", "path": "tema-raio-x.json", "type": "CustomTheme"},
                       {"name": IMG_MAPA, "path": IMG_MAPA, "type": "Image"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
                     "useEnhancedTooltips": True}})
    todas = paginas + ([plano_b] if plano_b else [])
    escrever_json(d / "pages" / "pages.json", {
        "$schema": f"{SCHEMA}/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p.nome for p in todas], "activePageName": paginas[0].nome})
    for p in todas:
        pg = {"$schema": f"{SCHEMA}/item/report/definition/page/1.4.0/schema.json", "name": p.nome,
              "displayName": p.exibicao, "displayOption": "FitToPage", "height": ALT, "width": LARG}
        if p.oculta:
            pg["visibility"] = "HiddenInViewMode"
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
    if not (RP / "StaticResources" / "RegisteredResources" / IMG_MAPA).exists():
        mapa_base.main()


def gerar_pbip() -> None:
    escrever_json(PBI / f"{NOME}.pbip", {
        "$schema": f"{SCHEMA}/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": f"{NOME}.Report"}}],
        "settings": {"enableAutoRecovery": True}})


def main() -> int:
    mapa = "dispersao"
    if "--mapa" in sys.argv:
        mapa = sys.argv[sys.argv.index("--mapa") + 1]
    if (SM / "definition").exists():
        shutil.rmtree(SM / "definition")
    gerar_modelo()
    gerar_relatorio(mapa, com_plano_b="--sem-plano-b" not in sys.argv)
    gerar_pbip()
    n_vis = len(list((RP / "definition" / "pages").rglob("visual.json")))
    print(f"PBIP gerado em {PBI}: {len(M.TABELAS)} tabelas, {len(M.MEDIDAS)} medidas, {len(M.RELACOES)} "
          f"relacionamentos, {n_vis} visuais em 6 páginas (mapa principal: {mapa})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
