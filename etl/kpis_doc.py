"""Gera docs/kpis.md a partir das medidas do modelo (pbip_modelo.MEDIDAS) e dos valores de referência (kpis.py).

Para cada medida: fórmula DAX, definição, significado na operação portuária, por que média ou mediana e um
exemplo numérico (Brasil e Suape, último ano completo).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402
import kpis as K  # noqa: E402
import pbip_modelo as M  # noqa: E402

# medida -> (significado na operação, por que média/mediana/razão)
OPERACAO = {
    "Toneladas": ("Volume físico que passou pelo cais: dimensiona receita de tarifa portuária, uso de berço, "
                  "armazenagem e fluxo de caminhão/trem.", "Soma — volume é aditivo."),
    "Toneladas AA": ("Base de comparação para separar crescimento real de sazonalidade.",
                     "Soma no mesmo recorte de meses do ano anterior (evita comparar mês parcial com ano cheio)."),
    "Var % Toneladas AA": ("Mostra se o porto ganha ou perde carga; num porto, crescimento sustentado pressiona "
                           "berço, pátio e acesso terrestre.", "Razão entre somas (não média de variações mensais)."),
    "TEU": ("Escala do terminal de contêiner — o produto de maior valor agregado e mais disputado entre portos.",
            "Soma."),
    "Nº Atracações": ("Quantas vezes um navio ocupou um berço para operar carga: proxy de demanda de berço, "
                      "praticagem e rebocador.", "Contagem."),
    "Toneladas por Atracação": ("Tamanho médio da consignação: navios maiores diluem custo fixo de atracação.",
                                "Razão de somas (total de toneladas ÷ total de atracações)."),
    "% do Total Brasil": ("Peso do porto no sistema nacional.", "Razão de somas."),
    "% Cabotagem": ("Dependência da navegação entre portos brasileiros (petróleo de plataforma, contêiner "
                    "doméstico).", "Razão de somas."),
    "% Longo Curso": ("Exposição ao comércio exterior.", "Razão de somas."),
    "% Contêiner": ("Quanto da carga é conteinerizada — perfil de porto concentrador de carga geral de maior valor.",
                    "Razão de somas."),
    "Ranking Porto": ("Posição relativa entre os portos visíveis.", "Ranking denso por toneladas."),
    "Ranking Suape Brasil": ("Posição de Suape no país.", "Contagem de instalações com mais toneladas + 1."),
    "Espera Média (h)": ("Custo de fila: horas de navio parado esperando berço (sobre-estadia/demurrage).",
                         "Média — útil para custo total de fila, mas puxada por poucos navios que esperam semanas."),
    "Espera Mediana (h)": ("A espera do navio típico. É o indicador de gargalo usado no painel.",
                           "Mediana — a distribuição da espera tem cauda longa (mediana nacional ~1–2 h, média ~40 h); "
                           "a mediana não é distorcida pelas filas extremas."),
    "Tempo Atracado Médio (h)": ("Quanto tempo cada navio ocupa o berço — define a capacidade de berço.",
                                 "Média — o tempo atracado é mais simétrico e somável (ocupação total = média × nº)."),
    "Tempo de Operação Médio (h)": ("Tempo efetivo de carga/descarga por navio.", "Média, pelo mesmo motivo."),
    "% Atracado em Operação": ("Eficiência do uso do berço: o restante do tempo atracado é espera de início, "
                               "paralisações, documentação e espera de desatracação.",
                               "Razão de somas (horas de operação ÷ horas atracado), não média de percentuais."),
    "Prancha Média Operacional (t/h)": ("Produtividade dos equipamentos/terno durante a operação.",
                                        "Razão de somas: toneladas ÷ horas de operação. Média de pranchas por navio "
                                        "daria o mesmo peso a uma barcaça e a um capesize."),
    "Prancha Média Geral (t/h)": ("Produtividade do berço considerando todo o tempo atracado.",
                                  "Razão de somas: toneladas ÷ horas atracado."),
    "Horas Paralisadas": ("Horas perdidas por chuva, quebra, falta de carga etc. — mostra onde agir.", "Soma."),
    "Espera Mediana Suape (h)": ("Espera do navio típico em Suape.", "Mediana (ver Espera Mediana)."),
    "Espera Mediana Média Pares (h)": ("Referência regional para Suape.",
                                       "Média simples das medianas dos 8 pares (cada porto pesa igual). Atenção: "
                                       "Itaqui, com filas de granel de vários dias, puxa essa média para cima."),
    "Diferença Espera Suape vs Pares (h)": ("Vantagem (negativa) ou desvantagem (positiva) de Suape.",
                                            "Diferença simples."),
    "Toneladas Suape": ("Volume de Suape.", "Soma."),
    "TEU Suape": ("Contêineres de Suape.", "Soma."),
    "Var % Toneladas Suape AA": ("Crescimento de Suape.", "Razão de somas."),
    "% Contêiner Suape": ("Perfil de carga de Suape.", "Razão de somas."),
}


def br(v, casas=0, pct=False):
    if v is None:
        return "—"
    if pct:
        v *= 100
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s + ("%" if pct else "")


def fmt_valor(medida: str, v) -> str:
    if v is None:
        return "—"
    if medida.startswith("%") or "Var %" in medida:
        return br(v, 1, True)
    if "(h)" in medida:
        return br(v, 1) + " h"
    if "t/h" in medida:
        return br(v) + " t/h"
    return br(v)


def main() -> int:
    con = K.conectar()
    ano = int(K.ultimo_mes(con)[:4]) - 1
    bra, sua = K.kpis(con, ano), K.kpis(con, ano, "'BRSUA'")
    extra_bra = {"Ranking Suape Brasil": K.ranking(con, ano, "BRSUA"),
                 "Espera Mediana Suape (h)": sua["Espera Mediana (h)"],
                 "Espera Mediana Média Pares (h)": K.espera_mediana_media_pares(con, ano),
                 "Toneladas Suape": sua["Toneladas"], "TEU Suape": sua["TEU"],
                 "Var % Toneladas Suape AA": sua["Var % Toneladas AA"], "% Contêiner Suape": sua["% Contêiner"]}
    extra_bra["Diferença Espera Suape vs Pares (h)"] = (extra_bra["Espera Mediana Suape (h)"] -
                                                        extra_bra["Espera Mediana Média Pares (h)"])
    out = ["# Dicionário de KPIs", "",
           "> Gerado por `etl/kpis_doc.py` a partir das mesmas definições usadas no TMDL "
           "(`etl/pbip_modelo.py`). Exemplos numéricos de [valores_referencia.md](valores_referencia.md), "
           f"ano **{ano}** (último ano completo), sem outros filtros.", "",
           "Regras gerais: toneladas vêm de `fCarga` (regra oficial ANTAQ, `FlagMCOperacaoCarga = 1`); "
           "tempos e pranchas vêm de `fAtracacao` (uma linha por atracação com carga, tempos já limpos); "
           "o período é o mês da desatracação. Todas as razões são **razão de somas**, o que deixa os totais "
           "corretos em qualquer nível (porto, região, Brasil).", ""]
    pasta_atual = None
    for pasta, nome, fmt, desc, dax in M.MEDIDAS:
        topo = pasta.split("\\")[0]
        if topo != pasta_atual:
            out += [f"## {topo}", ""]
            pasta_atual = topo
        out += [f"### [{nome}]", "", f"**Definição:** {desc}", ""]
        if nome in OPERACAO:
            sig, porque = OPERACAO[nome]
            out += [f"**Na operação do porto:** {sig}", "", f"**Média, mediana ou razão:** {porque}", ""]
            vb = bra.get(nome, extra_bra.get(nome))
            vs = sua.get(nome)
            if nome == "Ranking Porto":
                exemplo = f"Suape aparece em {extra_bra['Ranking Suape Brasil']}º num ranking com todas as instalações."
            elif vs is not None and nome in bra:
                exemplo = f"Brasil: **{fmt_valor(nome, vb)}** · Suape: **{fmt_valor(nome, vs)}**."
            else:
                exemplo = f"**{fmt_valor(nome, vb) if not nome.startswith('Ranking') else str(vb) + 'º'}**."
            out += [f"**Exemplo ({ano}):** {exemplo}", ""]
        out += ["```dax", dax, "```", f"Formato: `{fmt or 'texto'}` · Pasta: `{pasta}`", ""]
    con.close()
    (C.DOCS_DIR / "kpis.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("docs/kpis.md gerado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
