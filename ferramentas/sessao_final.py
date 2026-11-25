"""Sessão final no Power BI Desktop: capturas definitivas das 5 páginas + gravação do vídeo + salvar.

    .venv\\Scripts\\python ferramentas\\sessao_final.py [--sem-video]

1. Abre o PBIP, atualiza, recolhe os painéis e ajusta à página (monitor 2, 1920x1080).
2. Captura cada página visível em docs/img/pagina-N.png (recorte exato da página).
3. Grava a área do relatório (30 fps, mss + PyAV/libx264) enquanto navega com pyautogui: Ctrl+clique nos botões,
   filtro "Nordeste" na segmentação de Região, dicas de ferramenta em 3 visuais. Grava os tempos de cada cena
   (docs/video/cenas.json) para as legendas.
4. Desfaz o filtro, volta para a Visão Geral (2025 selecionado), salva (Ctrl+S) e fecha.
Nunca clica em Publicar, Entrar, Sair ou Compartilhar.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import av  # noqa: E402
import ciclo_qa as Q  # noqa: E402
import mss  # noqa: E402
import numpy as np  # noqa: E402
import pbi  # noqa: E402
import pyautogui  # noqa: E402
from PIL import Image  # noqa: E402

IMG = pbi.RAIZ / "docs" / "img"
VID = pbi.RAIZ / "docs" / "video"
PAGINAS = ["Visão Geral", "Nordeste & Suape", "Eficiência e Gargalos", "Perfil de Carga", "Sobre"]
BOTOES = ["Visão Geral", "Nordeste & Suape", "Eficiência", "Perfil de Carga", "Sobre"]


def item_lista(w, L, T, esc, texto):
    """Item da lista suspensa da segmentação de Região (abaixo da caixa, dentro da largura da segmentação)."""
    x0, x1, y0 = L + 180 * esc, L + 420 * esc, T + 140 * esc
    for c in w.descendants():
        try:
            if c.window_text() != texto:
                continue
            r = c.rectangle()
            if r.left >= x0 and r.right <= x1 and r.top >= y0 and r.width() > 0:
                return c
        except Exception:  # noqa: BLE001
            continue
    return None


def retangulo_pagina() -> tuple[int, int, int, int]:
    """(esquerda, topo, largura, altura) da página do relatório na tela (coordenadas absolutas)."""
    tela = pbi.capturar(Q.QA / "final_tela.png", Q.MON)
    img = Image.open(tela).convert("L").crop((44, 162, 1848, 968))
    bbox = img.point(lambda v: 255 if 8 < v < 70 else 0).getbbox()
    esc = (bbox[2] - bbox[0]) / (1280 - 32)
    esq = 44 + bbox[0] - 16 * esc
    baixo = 162 + bbox[3] + 16 * esc
    larg, alt = 1280 * esc, 720 * esc
    return 1920 + round(esq), round(baixo - alt), round(larg) // 2 * 2, round(alt) // 2 * 2


class Gravador(threading.Thread):
    def __init__(self, area: dict, destino: Path, fps: int = 30):
        super().__init__(daemon=True)
        self.area, self.destino, self.fps = area, destino, fps
        self.parar = threading.Event()
        self.t0 = None

    def run(self):
        out = av.open(str(self.destino), "w")
        s = out.add_stream("libx264", rate=self.fps)
        s.width, s.height, s.pix_fmt = self.area["width"], self.area["height"], "yuv420p"
        s.options = {"preset": "veryfast", "crf": "16"}
        intervalo = 1 / self.fps
        with mss.MSS() as m:
            self.t0 = time.perf_counter()
            n = 0
            ultimo = None
            while not self.parar.is_set():
                alvo = self.t0 + n * intervalo
                agora = time.perf_counter()
                if agora < alvo:
                    time.sleep(alvo - agora)
                if ultimo is None or time.perf_counter() - alvo < intervalo:
                    ultimo = np.asarray(m.grab(self.area))[:, :, :3][:, :, ::-1]
                quadro = av.VideoFrame.from_ndarray(np.ascontiguousarray(ultimo), format="rgb24")
                quadro.pts = n
                for pac in s.encode(quadro):
                    out.mux(pac)
                n += 1
        for pac in s.encode():
            out.mux(pac)
        out.close()


def main() -> int:
    VID.mkdir(parents=True, exist_ok=True)
    pbi.abrir()
    w = pbi.janela(300)
    time.sleep(10)
    pbi.no_monitor2(w)
    w = pbi.janela(30)
    w.set_focus()
    for _ in range(60):
        if pbi._buscar(w, "Sobre", "TabItem", tentativas=1):
            break
        time.sleep(5)
    pbi.atualizar(w)
    pbi.recolher_paineis(w)
    pbi.ajustar_pagina(w)
    time.sleep(4)

    # ---- capturas definitivas ----
    for i, nome in enumerate(PAGINAS, 1):
        pbi.ir_pagina_parcial(w, nome)
        pbi.ajustar_pagina(w)
        pyautogui.moveTo(1920 + 1880, 1050)
        time.sleep(7)
        tela = pbi.capturar(Q.QA / f"final_tela_{i}.png", Q.MON)
        Q.recortar_pagina(tela, IMG / f"pagina-{i}.png")
        print("captura:", IMG / f"pagina-{i}.png")

    if "--sem-video" not in sys.argv:
        pbi.ir_pagina_parcial(w, "Visão Geral")
        pbi.ajustar_pagina(w)
        time.sleep(5)
        L, T, W, H = retangulo_pagina()
        esc = W / 1280

        def P(x, y):  # coordenada da página -> tela
            return L + x * esc, T + y * esc

        def mover(x, y, dur=1.1):
            pyautogui.moveTo(*P(x, y), duration=dur, tween=pyautogui.easeInOutQuad)

        def botao(i):
            x0 = 1264 - (5 * 148 + 4 * 8)
            mover(x0 + i * 156 + 74, 38, 1.2)
            time.sleep(0.4)
            pyautogui.keyDown("ctrl")
            pyautogui.click()
            pyautogui.keyUp("ctrl")

        cenas = []
        grav = Gravador({"left": L, "top": T, "width": W, "height": H}, VID / "gravacao_bruta.mp4")
        mover(640, 690, 0.1)
        grav.start()
        while grav.t0 is None:
            time.sleep(0.05)

        def cena(texto):
            cenas.append({"t": round(time.perf_counter() - grav.t0, 2), "legenda": texto})

        time.sleep(0.8)
        cena("abertura")
        time.sleep(3.0)
        cena("kpis")
        mover(150, 200, 1.4); time.sleep(1.5)
        cena("linha")
        mover(352, 345, 1.4); time.sleep(3.5)
        cena("mapa_suape")
        mover(1247, 434, 1.6); time.sleep(3.8)
        cena("filtro_nordeste")
        mover(293, 128, 1.4); pyautogui.click(); time.sleep(1.8)
        item = item_lista(w, L, T, esc, "Nordeste")
        if item is not None:
            r = item.rectangle()
            pyautogui.moveTo((r.left + r.right) // 2, (r.top + r.bottom) // 2, duration=0.9)
            pyautogui.click()
        else:
            print("aviso: item Nordeste não encontrado na lista suspensa")
        time.sleep(1.2)
        mover(720, 72, 0.8); pyautogui.click(); time.sleep(3.5)   # área vazia da página: fecha a lista
        cena("nordeste_suape")
        botao(1); time.sleep(3.0)
        mover(110, 330, 1.4); time.sleep(3.8)
        mover(640, 640, 1.4); time.sleep(2.5)
        cena("eficiencia")
        botao(2); time.sleep(3.0)
        mover(700, 340, 1.4); time.sleep(3.8)
        cena("perfil")
        botao(3); time.sleep(3.0)
        mover(1000, 350, 1.4); time.sleep(3.5)
        cena("sobre")
        botao(4); time.sleep(5.0)
        cena("fim")
        grav.parar.set()
        grav.join()
        (VID / "cenas.json").write_text(json.dumps({"area": [L, T, W, H], "cenas": cenas}, ensure_ascii=False,
                                                   indent=2), encoding="utf-8")
        # desfaz o filtro Nordeste na Visão Geral
        botao(0); time.sleep(3)
        mover(293, 128, 1.0); pyautogui.click(); time.sleep(1.8)
        item = item_lista(w, L, T, esc, "Nordeste")
        if item is not None:
            pbi.clicar(item)
        time.sleep(1)
        mover(720, 72, 0.6); pyautogui.click(); time.sleep(2)
        pbi.capturar(Q.QA / "final_depois_video.png", Q.MON)

    pbi.ir_pagina_parcial(w, "Visão Geral")
    time.sleep(3)
    pyautogui.hotkey("ctrl", "s")
    time.sleep(15)
    pbi.fechar()
    print("sessão final concluída")
    return 0


if __name__ == "__main__":
    sys.exit(main())
