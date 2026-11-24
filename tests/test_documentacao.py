"""Todo número citado no README (achados), no roteiro do vídeo e no post tem origem rastreável:
precisa aparecer na seção 4 de docs/valores_referencia.md (ou na conciliação com a ANTAQ)."""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
NUMERO = re.compile(r"-?\d[\d.]*(?:,\d+)?(?: milhões de t| mil TEU| t/h| h|%|ª)")


def valores_permitidos() -> set[str]:
    ref = (DOCS / "valores_referencia.md").read_text(encoding="utf-8")
    secao = ref.split("## 4.")[1].split("\n### ")[0]
    vals = {linha.split("|")[2].strip() for linha in secao.splitlines() if linha.startswith("| ") and
            not linha.startswith("| ID")}
    conc = (DOCS / "conciliacao_antaq.md").read_text(encoding="utf-8").split("## Quebras")[0]
    vals |= set(re.findall(r"-?\d+,\d+%", conc))
    return vals


def trechos():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    achados = readme.split("## Principais achados")[1].split("\n## ")[0]
    yield "README (achados)", achados
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
