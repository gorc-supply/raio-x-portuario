"""Ciclo de verificação visual: abre o PBIP no Desktop, atualiza, captura cada página e recorta a página.

    .venv\\Scripts\\python ferramentas\\ciclo_qa.py <rotulo> [--sem-atualizar] [--manter-aberto]

Saída: docs/img/qa/<rotulo>_<pagina>.png (recorte da página) e <rotulo>_tela_<pagina>.png (tela inteira).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pbi  # noqa: E402
from PIL import Image  # noqa: E402

QA = pbi.RAIZ / "docs" / "img" / "qa"
PAGINAS = ["Visão Geral", "Nordeste & Suape", "Eficiência e Gargalos", "Perfil de Carga", "Sobre", "Mapa (plano B)"]
SLUG = {"Visão Geral": "1_visao_geral", "Nordeste & Suape": "2_nordeste_suape", "Eficiência e Gargalos": "3_eficiencia",
        "Perfil de Carga": "4_perfil_carga", "Sobre": "5_sobre", "Mapa (plano B)": "6_mapa_plano_b"}
MON = {"left": 1920, "top": 0, "width": 1920, "height": 1080}


def recortar_pagina(tela: Path, destino: Path) -> Path:
    """Acha a página no canvas: caixa do conteúdo (visuais têm fundo/borda) + margem de 16 px na escala."""
    img = Image.open(tela).convert("RGB")
    canvas = img.crop((44, 162, 1848, 968))
    # só os tons dos painéis/bordas/botões do tema (ignora texto branco e a borda clara do canvas)
    cinza = canvas.convert("L").point(lambda v: 255 if 8 < v < 70 else 0)
    bbox = cinza.getbbox()
    if not bbox:
        canvas.save(destino)
        return destino
    esc = (bbox[2] - bbox[0]) / (1280 - 32)
    margem = 16 * esc
    esq, dir_ = bbox[0] - margem, bbox[2] + margem
    baixo = bbox[3] + margem
    topo = baixo - 720 * esc
    pagina = canvas.crop((round(esq), max(0, round(topo)), round(dir_), min(canvas.height, round(baixo))))
    pagina.save(destino)
    return destino


def main() -> int:
    rotulo = sys.argv[1] if len(sys.argv) > 1 else "ciclo"
    QA.mkdir(parents=True, exist_ok=True)
    pbi.abrir()
    w = pbi.janela(300)
    time.sleep(10)
    pbi.no_monitor2(w)
    w = pbi.janela(30)
    w.set_focus()
    # espera o relatório carregar (abas das páginas visíveis)
    for _ in range(60):
        if pbi._buscar(w, "Sobre", "TabItem", tentativas=1):
            break
        time.sleep(5)
    if "--sem-atualizar" not in sys.argv:
        pbi.atualizar(w)
    pbi.recolher_paineis(w)
    pbi.ajustar_pagina(w)
    for nome in PAGINAS:
        try:
            pbi.ir_pagina_parcial(w, nome)
        except LookupError as e:
            print("aviso:", e)
            continue
        pbi.ajustar_pagina(w)
        time.sleep(6)
        tela = pbi.capturar(QA / f"{rotulo}_tela_{SLUG[nome]}.png", MON)
        print(recortar_pagina(tela, QA / f"{rotulo}_{SLUG[nome]}.png"))
    pbi.ir_pagina(w, "Visão Geral")
    if "--manter-aberto" not in sys.argv:
        pbi.fechar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
