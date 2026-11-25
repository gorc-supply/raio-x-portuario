"""Todo número citado no README (achados), no roteiro do vídeo e no post tem origem rastreável:
precisa aparecer na seção 4 de docs/valores_referencia.md (ou na conciliação com a ANTAQ).

O README em português é o README.pt-BR.md. O README.md em inglês é conferido contra os mesmos valores
convertidos para o formato inglês (1.403,8 milhões de t -> 1,403.8 million t; 13ª -> 13th)."""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
NUMERO = re.compile(r"-?\d[\d.]*(?:,\d+)?(?: milhões de t| mil TEU| t/h| h|%|ª)")
NUMERO_EN = re.compile(r"-?\d[\d,]*(?:\.\d+)?(?: million t| thousand TEU| t/h| h|%|st\b|nd\b|rd\b|th\b)")
UNIDADE_EN = {" milhões de t": " million t", " mil TEU": " thousand TEU"}


def valores_permitidos() -> set[str]:
    ref = (DOCS / "valores_referencia.md").read_text(encoding="utf-8")
    secao = ref.split("## 4.")[1].split("\n### ")[0]
    vals = {linha.split("|")[2].strip() for linha in secao.splitlines() if linha.startswith("| ") and
            not linha.startswith("| ID")}
    conc = (DOCS / "conciliacao_antaq.md").read_text(encoding="utf-8").split("## Quebras")[0]
    vals |= set(re.findall(r"-?\d+,\d+%", conc))
    return vals


def achados_pt() -> str:
    readme = (RAIZ / "README.pt-BR.md").read_text(encoding="utf-8")
    return readme.split("## Principais achados")[1].split("\n## ")[0]


def trechos():
    yield "README.pt-BR.md (achados)", achados_pt()
    roteiro = (DOCS / "roteiro_video.md").read_text(encoding="utf-8")
    # só a tabela de cenas (o resto são instruções de gravação, como zoom e opacidade da legenda)
    yield "roteiro_video.md", "\n".join(l for l in roteiro.splitlines() if l.startswith("| "))
    yield "post_linkedin.md", (DOCS / "post_linkedin.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("nome,texto", list(trechos()))
def test_numeros_citados_tem_origem(nome, texto):
    permitidos = valores_permitidos()
    assert permitidos, "seção 4 de valores_referencia.md vazia"
    faltando = sorted({n for n in NUMERO.findall(texto) if n not in permitidos})
    assert not faltando, f"{nome}: números sem origem em valores_referencia.md: {faltando}"


def ordinal_en(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}" + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def para_ingles(valor: str) -> str:
    """'1.403,8 milhões de t' -> '1,403.8 million t'; '-2,3%' -> '-2.3%'; '13ª' -> '13th'."""
    m = re.fullmatch(r"(-?)([\d.]+)(?:,(\d+))?(.*)", valor)
    if not m:
        return valor
    sinal, inteiro, decimal, resto = m.groups()
    if resto == "ª":
        return sinal + ordinal_en(int(inteiro.replace(".", "")))
    numero = sinal + inteiro.replace(".", ",") + ("." + decimal if decimal else "")
    return numero + UNIDADE_EN.get(resto, resto)


def test_para_ingles():
    assert para_ingles("1.403,8 milhões de t") == "1,403.8 million t"
    assert para_ingles("519 mil TEU") == "519 thousand TEU"
    assert para_ingles("-2,3%") == "-2.3%"
    assert para_ingles("13ª") == "13th"
    assert para_ingles("143,9 h") == "143.9 h"


def test_readme_ingles_usa_os_mesmos_numeros():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("**English** · [Português](README.pt-BR.md)")
    achados = readme.split("## Key findings")[1].split("\n## ")[0]
    citados = set(NUMERO_EN.findall(achados))
    faltando = sorted(citados - {para_ingles(v) for v in valores_permitidos()})
    assert not faltando, f"README.md (inglês): números sem origem em valores_referencia.md: {faltando}"
    # e cada número dos achados em português aparece, convertido, no inglês
    ausentes = sorted({para_ingles(n) for n in NUMERO.findall(achados_pt())} - citados)
    assert not ausentes, f"README.md (inglês) não cita: {ausentes}"
