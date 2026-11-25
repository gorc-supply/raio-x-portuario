"""Valida o projeto Power BI sem abrir o Desktop.

1. Cada JSON do PBIP contra o schema público declarado em "$schema" (github.com/microsoft/json-schemas,
   commit fixado; baixado sob demanda para data/raw/json-schemas/).
2. Todo campo/medida referenciado nos visuais e filtros existe no modelo TMDL, com o nome exato e o tipo
   certo (coluna x medida); queryRef coerente.
3. TMDL: relacionamentos, sortByColumn e referências DAX ([Medida] e Tabela[Coluna]) apontam para objetos
   existentes; indentação só com tabs; toda tabela tem partição.
4. Publicar na Web: só visuais nativos (sem R/Python, ArcGIS, AppSource) e nenhum papel de RLS.
5. Navegação: páginas de pages.json existem; botões apontam para páginas existentes; visuais dentro da página.

Sai com código 1 se houver qualquer erro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from jsonschema import validators
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

RAIZ = Path(__file__).resolve().parents[1]
PBI = RAIZ / "powerbi"
CACHE = RAIZ / "data" / "raw" / "json-schemas"
COMMIT = "582c790d5862f8330d839bffdcf81ba23e984c96"  # microsoft/json-schemas, 2026-11-23
PREFIXO = "https://developer.microsoft.com/json-schemas/"
RAW = f"https://raw.githubusercontent.com/microsoft/json-schemas/{COMMIT}/"

VISUAIS_NATIVOS = {"card", "cardVisual", "slicer", "lineChart", "clusteredBarChart", "clusteredColumnChart",
                   "barChart", "columnChart", "scatterChart", "tableEx", "pivotTable", "donutChart", "azureMap",
                   "textbox", "actionButton", "image", "shape", "basicShape", "areaChart",
                   "decompositionTreeVisual", "multiRowCard", "kpi", "gauge", "treemap", "waterfallChart"}

erros: list[str] = []


def erro(msg: str) -> None:
    erros.append(msg)


# ---------------------------------------------------------------------------
# 1. Schemas
# ---------------------------------------------------------------------------
def baixar_schema(uri: str) -> dict:
    uri = uri.split("#")[0]
    if not uri.startswith(PREFIXO):
        raise NoSuchResource(ref=uri)
    rel = uri[len(PREFIXO):]
    local = CACHE / rel
    if not local.exists():
        r = requests.get(RAW + rel, timeout=60)
        if r.status_code == 404:
            raise FileNotFoundError(uri)
        r.raise_for_status()
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(r.content)
    return json.loads(local.read_text(encoding="utf-8"))


def recuperar(uri: str) -> Resource:
    return Resource.from_contents(baixar_schema(uri))


REGISTRO = Registry(retrieve=recuperar)
avisos: list[str] = []
# propriedades que o Power BI Desktop grava mas que a versão de schema declarada ainda não descreve
PROPRIEDADES_DO_DESKTOP = {"linguisticSchemaSyncVersion"}


def versao_publicada_anterior(uri: str) -> tuple[str, dict]:
    m = re.search(r"/(\d+)\.(\d+)\.(\d+)/", uri)
    maior, menor = int(m.group(1)), int(m.group(2))
    while menor > 0:
        menor -= 1
        candidato = uri.replace(m.group(0), f"/{maior}.{menor}.0/")
        try:
            return candidato, baixar_schema(candidato)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(uri)


def validar_schemas() -> int:
    n = 0
    for arq in sorted(PBI.rglob("*")):
        if arq.is_dir() or arq.suffix not in {".json", ".pbir", ".pbism", ".pbip", ".platform"}:
            continue
        # arquivos sem schema público: tema, recursos estáticos e o layout de diagrama que o Desktop grava
        if "StaticResources" in arq.parts or arq.name in {"tema-raio-x.json", "diagramLayout.json"}:
            try:
                json.loads(arq.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                erro(f"{arq.relative_to(RAIZ)}: JSON inválido ({e})")
            continue
        doc = json.loads(arq.read_text(encoding="utf-8"))
        uri = doc.get("$schema")
        if not uri:
            erro(f"{arq.relative_to(RAIZ)}: sem $schema")
            continue
        uri_usado = uri
        try:
            schema = baixar_schema(uri)
        except FileNotFoundError:
            # O Desktop grava versões de schema que a Microsoft publica semanas depois (ex.: visualContainer
            # 2.15.0 em nov/2026). Valida contra a maior versão já publicada da mesma família e avisa.
            uri_usado, schema = versao_publicada_anterior(uri)
            avisos.append(f"{arq.relative_to(RAIZ)}: {uri.split('/definition/')[-1]} ainda não publicado; "
                          f"validado com {uri_usado.split('/definition/')[-1]}")
            doc = {**doc, "$schema": uri_usado}
        cls = validators.validator_for(schema)
        v = cls(schema, registry=REGISTRO.with_resource(uri_usado, Resource.from_contents(schema)))
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path)):
            if any(f"'{k}' was unexpected" in e.message for k in PROPRIEDADES_DO_DESKTOP):
                avisos.append(f"{arq.relative_to(RAIZ)}: propriedade gravada pelo Desktop fora do schema: {e.message[:90]}")
                continue
            erro(f"{arq.relative_to(RAIZ)}: schema: {'/'.join(map(str, e.path))}: {e.message[:200]}")
        n += 1
    return n


# ---------------------------------------------------------------------------
# 2/3. Modelo TMDL
# ---------------------------------------------------------------------------
def nome(s: str) -> str:
    s = s.strip()
    return s[1:-1].replace("''", "'") if s.startswith("'") and s.endswith("'") else s


def ler_modelo() -> dict:
    defin = PBI / "RaioXPortuario.SemanticModel" / "definition"
    modelo = {"colunas": {}, "medidas": {}, "dax": [], "sort": [], "roles": 0, "particoes": {}}
    for arq in sorted((defin / "tables").glob("*.tmdl")):
        texto = arq.read_text(encoding="utf-8")
        for i, linha in enumerate(texto.split("\n"), 1):
            if linha and re.match(r"^ +\S", linha):
                erro(f"{arq.name}:{i}: indentação com espaços (TMDL exige tabs)")
        m = re.search(r"^table (.+)$", texto, re.M)
        tabela = nome(m.group(1))
        modelo["colunas"][tabela] = {nome(c) for c in re.findall(r"^\tcolumn (.+)$", texto, re.M)}
        modelo["particoes"][tabela] = bool(re.search(r"^\tpartition ", texto, re.M))
        for c, s in re.findall(r"^\tcolumn (.+)\n(?:\t\t.*\n|\n)*?\t\tsortByColumn: (.+)$", texto, re.M):
            modelo["sort"].append((tabela, nome(c), nome(s)))
        for bloco in re.split(r"\n(?=\t(?:///|measure |column |partition ))", texto):
            mm = re.match(r"\tmeasure ('(?:[^']|'')+'|\S+) =(.*)", bloco, re.S)
            if mm:
                med = nome(mm.group(1))
                corpo = re.split(r"\n\t\t(?:formatString|displayFolder|lineageTag):", mm.group(2))[0]
                modelo["medidas"][med] = tabela
                modelo["dax"].append((med, corpo))
    modelo["rel"] = re.findall(r"fromColumn: (.+)\n\ttoColumn: (.+)", (defin / "relationships.tmdl").read_text("utf-8"))
    modelo["roles"] = len(list(defin.rglob("roles/*.tmdl")))
    return modelo


def checar_modelo(mod: dict) -> None:
    for t, tem in mod["particoes"].items():
        if not tem:
            erro(f"tabela {t} sem partição")
    for de, para in mod["rel"]:
        for ref in (de, para):
            t, c = ref.split(".", 1)
            if nome(c) not in mod["colunas"].get(nome(t), set()):
                erro(f"relacionamento aponta para coluna inexistente: {ref}")
    for t, c, s in mod["sort"]:
        if s not in mod["colunas"][t]:
            erro(f"{t}[{c}] ordenada por coluna inexistente {s}")
    for med, dax in mod["dax"]:
        sem_texto = re.sub(r'"[^"]*"', '""', dax)
        sem_texto = re.sub(r"//[^\n]*", "", sem_texto)
        for tab, col in re.findall(r"(?:'([^']+)'|\b([A-Za-z_]\w*))\[([^\]]+)\]", sem_texto) and \
                [(a or b, c) for a, b, c in re.findall(r"(?:'([^']+)'|\b([A-Za-z_]\w*))\[([^\]]+)\]", sem_texto)]:
            if tab not in mod["colunas"]:
                erro(f"medida [{med}]: tabela inexistente {tab}")
            elif col not in mod["colunas"][tab]:
                erro(f"medida [{med}]: coluna inexistente {tab}[{col}]")
        for ref in re.findall(r"(?<![\w'\]])\[([^\]]+)\]", sem_texto):
            if ref.startswith("@"):
                continue
            if ref not in mod["medidas"]:
                erro(f"medida [{med}]: referência a medida inexistente [{ref}]")
    if mod["roles"]:
        erro("o modelo tem papéis de RLS — incompatível com Publicar na Web")


# ---------------------------------------------------------------------------
# 2/4/5. Relatório
# ---------------------------------------------------------------------------
def campos(obj, aliases=None):
    """Percorre um JSON e devolve (tipo, entidade, propriedade) de cada Column/Measure referenciado."""
    aliases = dict(aliases or {})
    if isinstance(obj, dict):
        if "From" in obj and isinstance(obj["From"], list):
            for f in obj["From"]:
                aliases[f.get("Name")] = f.get("Entity")
        for k in ("Column", "Measure"):
            if k in obj and isinstance(obj[k], dict) and "Property" in obj[k]:
                src = obj[k].get("Expression", {}).get("SourceRef", {})
                ent = src.get("Entity") or aliases.get(src.get("Source"))
                yield k, ent, obj[k]["Property"]
        for v in obj.values():
            yield from campos(v, aliases)
    elif isinstance(obj, list):
        for v in obj:
            yield from campos(v, aliases)


def checar_relatorio(mod: dict) -> int:
    defin = PBI / "RaioXPortuario.Report" / "definition"
    pages = json.loads((defin / "pages" / "pages.json").read_text("utf-8"))
    nomes_pag = set(pages["pageOrder"])
    if pages.get("activePageName") not in nomes_pag:
        erro("pages.json: activePageName não está em pageOrder")
    pastas = {p.name for p in (defin / "pages").iterdir() if p.is_dir()}
    if pastas != nomes_pag:
        erro(f"pages.json x pastas divergentes: {sorted(pastas ^ nomes_pag)}")
    n_ref = 0
    for arq in sorted(defin.rglob("*.json")):
        doc = json.loads(arq.read_text("utf-8"))
        rel = arq.relative_to(RAIZ)
        for tipo, ent, prop in campos(doc):
            n_ref += 1
            if tipo == "Measure":
                if mod["medidas"].get(prop) != ent:
                    erro(f"{rel}: medida inexistente {ent}[{prop}]")
            elif prop not in mod["colunas"].get(ent, set()):
                erro(f"{rel}: coluna inexistente {ent}[{prop}]")
        if arq.name == "page.json":
            if (doc.get("width"), doc.get("height")) != (1280, 720):
                erro(f"{rel}: página não é 1280x720")
        if arq.name == "visual.json":
            pos = doc["position"]
            if pos["x"] < 0 or pos["y"] < 0 or pos["x"] + pos["width"] > 1280.5 or pos["y"] + pos["height"] > 720.5:
                erro(f"{rel}: visual fora da página 1280x720 ({pos})")
            v = doc.get("visual", {})
            vt = v.get("visualType")
            if vt and vt not in VISUAIS_NATIVOS:
                erro(f"{rel}: visual não nativo ou não previsto: {vt}")
            for papel in v.get("query", {}).get("queryState", {}).values():
                for p in papel.get("projections", []):
                    f = p["field"]
                    prefixo = ""
                    if "Aggregation" in f:
                        prefixo = {0: "Sum", 1: "Avg", 2: "Count", 3: "Min", 4: "Max"}.get(f["Aggregation"]["Function"], "")
                        f = f["Aggregation"]["Expression"]
                    k = "Column" if "Column" in f else "Measure"
                    esperado = f"{f[k]['Expression']['SourceRef']['Entity']}.{f[k]['Property']}"
                    if prefixo:
                        esperado = f"{prefixo}({esperado})"
                    if p.get("queryRef") != esperado:
                        erro(f"{rel}: queryRef {p.get('queryRef')} != {esperado}")
            for link in v.get("visualContainerObjects", {}).get("visualLink", []):
                alvo = link["properties"].get("navigationSection", {}).get("expr", {}).get("Literal", {}).get("Value")
                if alvo and alvo.strip("'") not in nomes_pag:
                    erro(f"{rel}: botão aponta para página inexistente {alvo}")
    return n_ref


def main() -> int:
    n_json = validar_schemas()
    mod = ler_modelo()
    checar_modelo(mod)
    n_ref = checar_relatorio(mod)
    print(f"{n_json} arquivos JSON validados contra o schema; {n_ref} referências de campo/medida conferidas; "
          f"{len(mod['medidas'])} medidas e {sum(map(len, mod['colunas'].values()))} colunas no modelo")
    for a in sorted(set(avisos))[:5]:
        print("  aviso:", a)
    if len(set(avisos)) > 5:
        print(f"  aviso: ... e mais {len(set(avisos)) - 5} arquivos com schema ainda não publicado")
    if erros:
        print(f"*** {len(erros)} ERRO(S):")
        for e in erros:
            print("  -", e)
        return 1
    print("OK: nenhum erro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
