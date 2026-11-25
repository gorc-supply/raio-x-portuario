"""Monta o zip da release: powerbi/ (sem arquivos locais do Desktop), data/processed/, o PDF e um LEIAME.

    .venv\\Scripts\\python ferramentas\\montar_release.py <destino.zip>
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IGNORAR = {"localSettings.json", "cache.abf"}
LEIAME = """RAIO-X PORTUÁRIO — painel Power BI (dados abertos da ANTAQ, 2021–2025)

Como abrir (Power BI Desktop é gratuito, Microsoft Store):
1. Extraia este zip em C:\\projetos\\  (fica C:\\projetos\\raio-x-portuario\\...).
2. Abra raio-x-portuario\\powerbi\\RaioXPortuario.pbip no Power BI Desktop.
3. Se extraiu em outra pasta: Página Inicial > Transformar dados > Editar parâmetros > CaminhoDados
   e informe a pasta ...\\raio-x-portuario\\data\\processed\\ (terminando com \\).
4. Clique em Atualizar (Página Inicial). Pronto: 5 páginas, ano 2025 selecionado.

Conteúdo:
- powerbi\\           projeto Power BI (PBIP: modelo em TMDL, relatório em PBIR, tema)
- data\\processed\\   dados tratados (CSV) que o painel lê
- RaioXPortuario.pdf  as 5 páginas em PDF

Código, método e conciliação com a ANTAQ: https://github.com/gorc-supply/raio-x-portuario
Autor: Gabriel Cunha · https://gorc-supply.github.io
"""


def main() -> int:
    destino = Path(sys.argv[1])
    n = 0
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for pasta in ("powerbi", "data/processed"):
            for arq in sorted((RAIZ / pasta).rglob("*")):
                if arq.is_file() and arq.name not in IGNORAR and arq.name != ".gitkeep":
                    z.write(arq, "raio-x-portuario/" + arq.relative_to(RAIZ).as_posix())
                    n += 1
        z.write(RAIZ / "docs" / "RaioXPortuario.pdf", "raio-x-portuario/RaioXPortuario.pdf")
        z.writestr("raio-x-portuario/LEIAME.txt", LEIAME)
    print(f"{destino}: {n + 2} arquivos, {destino.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
