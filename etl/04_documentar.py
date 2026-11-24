"""Etapa 4 — gera a documentação numérica a partir dos CSV finais:

  docs/valores_referencia.md  valores esperados de cada KPI (Brasil e Suape por ano, benchmark NE)
  docs/data_quality.md        quantas linhas cada regra de limpeza afetou, por ano
  docs/conciliacao_antaq.md   total do pipeline x total oficial publicado pela ANTAQ
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402
import kpis as K  # noqa: E402

TOLERANCIA = 0.02


def br(v, casas=0, pct=False) -> str:
    """Formata número no padrão brasileiro."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if pct:
        v = v * 100
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s + ("%" if pct else "")


FORMATOS = {
    "Toneladas": (0, False), "Toneladas AA": (0, False), "Var % Toneladas AA": (1, True), "TEU": (0, False),
    "Nº Atracações": (0, False), "Toneladas por Atracação": (0, False), "% Cabotagem": (1, True),
    "% Longo Curso": (1, True), "% Contêiner": (1, True), "% do Total Brasil": (1, True),
    "Espera Média (h)": (1, False), "Espera Mediana (h)": (1, False), "Tempo Atracado Médio (h)": (1, False),
    "Tempo de Operação Médio (h)": (1, False), "% Atracado em Operação": (1, True),
    "Prancha Média Operacional (t/h)": (0, False), "Prancha Média Geral (t/h)": (0, False),
    "Horas Paralisadas": (0, False),
}
PASTA = {
    "Toneladas": "Volume", "Toneladas AA": "Volume", "Var % Toneladas AA": "Volume", "TEU": "Volume",
    "Nº Atracações": "Volume", "Toneladas por Atracação": "Volume", "% Cabotagem": "Participação",
    "% Longo Curso": "Participação", "% Contêiner": "Participação", "% do Total Brasil": "Participação",
}


def tabela_kpis(con, anos, inst=None, id_rank=None) -> str:
    dados = {a: K.kpis(con, a, inst) for a in anos}
    linhas = ["| Medida | Pasta | " + " | ".join(str(a) for a in anos) + " |",
              "|---|---|" + "---:|" * len(anos)]
    for m, (c, p) in FORMATOS.items():
        linhas.append(f"| [{m}] | {PASTA.get(m, 'Eficiência')} | " +
                      " | ".join(br(dados[a][m], c, p) for a in anos) + " |")
    if id_rank:
        linhas.append("| [Ranking Porto] (entre todas as instalações) | Participação | " +
                      " | ".join(f"{K.ranking(con, a, id_rank)}º" for a in anos) + " |")
    return "\n".join(linhas)


def valores_referencia(con) -> str:
    um = K.ultimo_mes(con)
    anos = list(range(C.ANO_INICIAL, int(um[:4]) + 1))
    ids = K.ids_benchmark(con)
    lista_pares = ", ".join(f"'{i}'" for i, _, s in ids)
    out = [
        "# Valores de referência dos KPIs",
        "",
        f"> Gerado automaticamente por `etl/04_documentar.py` em {datetime.now():%d/%m/%Y %H:%M} "
        "a partir dos mesmos CSV de `data/processed/` que o Power BI lê.",
        f"> Último mês com dado: **{um[5:7]}/{um[:4]}** — o ano de {um[:4]} é **parcial** "
        f"(e o [Toneladas AA] de {um[:4]} compara só os mesmos meses de {int(um[:4]) - 1}).",
        "",
        "Use estas tabelas para conferir o Power BI número a número: selecione o ano na segmentação de período "
        "(e, para Suape, filtre a instalação) e compare com o cartão/tabela correspondente. "
        "As definições das medidas estão em [kpis.md](kpis.md).",
        "",
        "Convenções: toneladas = soma de `VLPesoCargaBruta` com `FlagMCOperacaoCarga = 1`; período = mês da "
        "desatracação; medidas de eficiência calculadas sobre atracações com movimentação de carga, já com a "
        "limpeza de tempos aplicada (ver [data_quality.md](data_quality.md)).",
        "",
        "## 1. Brasil (todas as instalações)",
        "",
        tabela_kpis(con, anos),
        "",
        "## 2. Suape (porto organizado, IDInstalacao = BRSUA)",
        "",
        tabela_kpis(con, anos, "'BRSUA'", id_rank="BRSUA"),
        "",
        "## 3. Benchmark Nordeste (página \"Nordeste & Suape\")",
        "",
    ]
    for ano in [a for a in anos if a >= int(um[:4]) - 1][::-1]:
        out += [f"### {ano}", "",
                "| Porto | Toneladas | Var % AA | Espera mediana (h) | Prancha operacional (t/h) | % Contêiner "
                "| % Atracado em operação | Nº atracações | Ranking entre os 9 |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for i, nome, _ in ids:
            k = K.kpis(con, ano, f"'{i}'")
            out.append(f"| {nome} | {br(k['Toneladas'])} | {br(k['Var % Toneladas AA'], 1, True)} | "
                       f"{br(k['Espera Mediana (h)'], 1)} | {br(k['Prancha Média Operacional (t/h)'])} | "
                       f"{br(k['% Contêiner'], 1, True)} | {br(k['% Atracado em Operação'], 1, True)} | "
                       f"{br(k['Nº Atracações'])} | {K.ranking(con, ano, i, lista_pares)}º |")
        med_pares = K.espera_mediana_media_pares(con, ano)
        suape = K.kpis(con, ano, "'BRSUA'")["Espera Mediana (h)"]
        out += ["", f"- [Espera Mediana Média Pares (h)] {ano} = **{br(med_pares, 1)} h** "
                    "(média simples das medianas dos 8 pares).",
                f"- [Espera Mediana Suape (h)] {ano} = **{br(suape, 1)} h**; "
                f"[Diferença Espera Suape vs Pares (h)] = **{br(suape - med_pares, 1)} h**.", ""]
    ano_ref = int(um[:4]) - 1
    out += [f"### Espera mediana mensal {ano_ref}: Suape x média dos pares (visual de linha)", "",
            "| Mês | Suape (h) | Média dos pares (h) |", "|---|---:|---:|"]
    for d, s, p in K.espera_mediana_mensal(con, ano_ref):
        out.append(f"| {d:%m/%Y} | {br(s, 1)} | {br(p, 1)} |")
    return "\n".join(out) + "\n"


def data_quality(meta: dict) -> str:
    log = pd.DataFrame(meta["log"])
    out = ["# Qualidade dos dados", "",
           "> Gerado automaticamente por `etl/04_documentar.py` a partir do log de `etl/02_transform.py`.", "",
           "## Origem dos dados por tabela e ano", "",
           "| Tabela | " + " | ".join(str(a) for a in C.ANOS) + " |", "|---|" + "---|" * len(C.ANOS)]
    for tab, por_ano in meta["origens"].items():
        out.append(f"| {tab} | " + " | ".join(por_ano.get(str(a), por_ano.get(a, "—")) for a in C.ANOS) + " |")
    out += ["", "## Regras e linhas afetadas", "",
            "| Regra | O que faz |", "|---|---|",
            "| R1 | Linhas de carga com `FlagMCOperacaoCarga` ≠ 1 (safamento, remoção a bordo, transferência interna, "
            "operação intermediária, abastecimento) ficam fora da tonelagem — metodologia ANTAQ. |",
            "| R2 | Atracação sem data de desatracação ou fora de 2021–2026 é excluída. |",
            "| R3 | Tempo negativo é descartado (vira nulo). Tonelagem nunca é descartada. |",
            "| R4 | Tempo ausente na base (falta a data de chegada/início/fim de operação): fica nulo e é ignorado "
            "nas médias/medianas daquela métrica. |",
            "| R5 | Tempo acima do percentil 99,5 da natureza de carga predominante da atracação é limitado ao "
            "percentil (winsorização). Só tempos. |",
            "| R6 / R6b | Paralisação com duração negativa ou sem data é descartada; acima do P99,5 da natureza "
            "é limitada. |",
            "| R7 | Texto com acentuação corrompida (UTF-8 lido como Latin-1, ex.: `BaldeaÃ§Ã£o`) é corrigido. |",
            "| R8 | Toda carga conteinerizada é agrupada na mercadoria \"Contêineres\" (como no Anuário ANTAQ). |",
            "| R9 | Carga sem atracação correspondente (órfã) é excluída. |",
            "| R10 | Tempo de operação maior que o tempo atracado (inconsistente) é descartado. |",
            "| R11 | Atracação sem movimentação de carga (apoio, passageiros, reparo etc.) não entra em "
            "fAtracacao — não participa de nenhuma métrica de eficiência. |", ""]
    com_ano = log[log.get("ano").notna()] if "ano" in log else pd.DataFrame()
    if not com_ano.empty:
        com_ano = com_ano.assign(ano=com_ano["ano"].astype(int),
                                 chave=com_ano["regra"].str.split(" ").str[0] + " " +
                                 com_ano.get("metrica", pd.Series(index=com_ano.index, dtype=str)).fillna(""))
        piv = com_ano.pivot_table(index="chave", columns="ano", values="linhas", aggfunc="sum").fillna(0)
        out += ["### Linhas afetadas por ano", "", "| Regra (métrica) | " +
                " | ".join(str(c) for c in piv.columns) + " |", "|---|" + "---:|" * len(piv.columns)]
        for idx, row in piv.iterrows():
            out.append(f"| {idx.strip()} | " + " | ".join(br(v) for v in row.values) + " |")
        if "toneladas" in com_ano:
            r1 = com_ano[com_ano["regra"].str.startswith("R1 ")]
            out += ["", "Toneladas fora da movimentação pela R1: " +
                    "; ".join(f"{int(r.ano)}: {br(r.toneladas / 1e6, 2)} Mt" for r in r1.itertuples()) + "."]
    regras_com_ocorrencia = {str(x).split(" ")[0] for x in log["regra"]}
    zeradas = [r for r in ("R3", "R6", "R10") if r not in regras_com_ocorrencia]
    if zeradas:
        out += ["", f"Regras sem nenhuma ocorrência no recorte (0 linhas em todos os anos): {', '.join(zeradas)}. "
                "A base já vem sem tempos negativos e sem operação maior que o tempo atracado; as regras "
                "continuam no código para proteger cargas futuras."]
    sem_ano = log[log["ano"].isna()] if "ano" in log else log
    out += ["", "### Regras sem quebra por ano", "", "| Regra | Tabela/coluna | Valores distintos | Linhas |",
            "|---|---|---:|---:|"]
    for r in sem_ano.to_dict("records"):
        partes = [str(r.get(k)) for k in ("tabela", "coluna") if isinstance(r.get(k), str)]
        alvo = ".".join(partes) or "—"
        vd = r.get("valores_distintos")
        out.append(f"| {r['regra']} | {alvo} | {br(vd) if pd.notna(vd) else '—'} | {br(r['linhas'])} |")
    return "\n".join(out) + "\n"


def conciliacao(con) -> tuple[str, list[dict]]:
    ref = pd.read_csv(C.REF_DIR / "totais_oficiais_antaq.csv")
    res = []
    for r in ref.itertuples():
        f = f"year(DataRef) = {r.ano}"
        if r.indicador == "total":
            sql = f"SELECT sum(Toneladas) FROM fCarga WHERE {f}"
        elif r.indicador == "navegacao":
            sql = (f"SELECT sum(Toneladas) FROM fCarga JOIN dNavegacao USING (CodNavegacao) "
                   f"WHERE {f} AND Navegacao = '{r.recorte}'")
        elif r.indicador == "regiao":
            sql = (f"SELECT sum(Toneladas) FROM fCarga JOIN dInstalacao USING (IDInstalacao) "
                   f"WHERE {f} AND Regiao = '{r.recorte}'")
        elif r.indicador == "instalacao":
            sql = (f"SELECT sum(Toneladas) FROM fCarga JOIN dInstalacao USING (IDInstalacao) "
                   f"WHERE {f} AND (Instalacao = '{r.recorte}' OR PortoBenchmarkNE = '{r.recorte}')")
        else:
            sql = (f"SELECT sum(Toneladas) FROM fCarga JOIN dMercadoria USING (CodMercadoria) "
                   f"WHERE {f} AND Mercadoria = '{r.recorte}'")
        v = (con.sql(sql).fetchall()[0][0] or 0) / 1e6
        res.append({"ano": r.ano, "indicador": r.indicador, "recorte": r.recorte, "pipeline": v,
                    "oficial": r.valor_mt, "dif": v / r.valor_mt - 1, "fonte": r.fonte, "url": r.url})
    out = ["# Conciliação com os totais oficiais da ANTAQ", "",
           "> Gerado automaticamente por `etl/04_documentar.py`. Critério de aceite: total nacional anual com "
           f"diferença de até ±{TOLERANCIA:.0%} (testado em `tests/test_conciliacao.py`).", "",
           "Regra de contagem usada: soma de `VLPesoCargaBruta` das linhas de Carga com "
           "`FlagMCOperacaoCarga = 1` (inclui transbordo e baldeação, como a ANTAQ), por ano da data de "
           "desatracação.", "",
           "## Total nacional por ano (critério de aceite)", "",
           "| Ano | Pipeline (Mt) | Oficial ANTAQ (Mt) | Diferença | Status | Fonte |", "|---|---:|---:|---:|---|---|"]
    for r in [x for x in res if x["indicador"] == "total"]:
        ok = "OK" if abs(r["dif"]) <= TOLERANCIA else "FORA DA TOLERÂNCIA"
        out.append(f"| {r['ano']} | {br(r['pipeline'], 1)} | {br(r['oficial'], 1)} | {br(r['dif'], 2, True)} | "
                   f"{ok} | [{r['fonte']}]({r['url']}) |")
    out += ["", f"2026 não entra na conciliação: só há {K.ultimo_mes(con)[5:7]}/2026 na base e a ANTAQ ainda não "
                "publicou o total anual.", "",
            "## Quebras publicadas (informativo, sem critério de aceite)", "",
            "| Ano | Recorte | Pipeline (Mt) | Oficial (Mt) | Diferença | Fonte |", "|---|---|---:|---:|---:|---|"]
    for r in [x for x in res if x["indicador"] != "total"]:
        out.append(f"| {r['ano']} | {r['indicador']}: {r['recorte']} | {br(r['pipeline'], 1)} | "
                   f"{br(r['oficial'], 1)} | {br(r['dif'], 1, True)} | [{r['fonte']}]({r['url']}) |")
    out += ["", "## Leitura das diferenças", "",
            "- Os totais oficiais são fotografias da data de publicação; a base do Estatístico é revisada depois "
            "(ex.: 2021 foi divulgado como 1.210 Mt em fev/2022 e citado como 1.214 Mt em fev/2023). "
            "Por isso usamos sempre o valor publicado mais recente.",
            "- Quebras por navegação e região diferem mais que o total: a ANTAQ classifica parte da carga de "
            "interior/cabotagem e algumas instalações de fronteira de forma diferente da coluna `Tipo Navegação`, "
            "e 0,2–0,3% da tonelagem está em instalação não identificada (sem região). O total não é afetado.",
            "- Nenhum ajuste manual foi feito para aproximar os números."]
    return "\n".join(out) + "\n", res


def main() -> int:
    con = K.conectar()
    meta = json.loads((C.RAW_DIR / "transform_meta.json").read_text(encoding="utf-8"))
    (C.DOCS_DIR / "valores_referencia.md").write_text(valores_referencia(con), encoding="utf-8")
    (C.DOCS_DIR / "data_quality.md").write_text(data_quality(meta), encoding="utf-8")
    texto, res = conciliacao(con)
    (C.DOCS_DIR / "conciliacao_antaq.md").write_text(texto, encoding="utf-8")
    for r in [x for x in res if x["indicador"] == "total"]:
        print(f"{r['ano']}: pipeline {r['pipeline']:,.1f} Mt x oficial {r['oficial']:,.1f} Mt ({r['dif']:+.2%})")
    print("docs gerados: valores_referencia.md, data_quality.md, conciliacao_antaq.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
