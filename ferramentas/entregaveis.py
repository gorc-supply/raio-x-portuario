"""Gera os entregáveis visuais a partir das capturas finais e da gravação de tela:

  docs/video/raio-x-portuario.mp4  1920x1080, H.264, 30 fps, +faststart, cartelas e legendas (<= 10 MB)
  docs/video/poster.jpg            primeiro quadro bom (<= 300 KB)
  docs/img/capa.png                1920x1080, Visão Geral com título discreto
  docs/img/capa.gif                páginas alternando (<= 8 s, <= 5 MB)
  docs/RaioXPortuario.pdf          capa + 1 página por página do relatório (paisagem)
  docs/img/mapa_opcoes.png         as duas opções de mapa lado a lado
  docs/video/quadros/*.jpg         um quadro a cada 5 s (revisão)

Usa só Python (Pillow + PyAV/libx264): o ffmpeg.exe foi bloqueado pela política de Controle de Aplicativo do Windows.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
IMG, VID, QA = RAIZ / "docs" / "img", RAIZ / "docs" / "video", RAIZ / "docs" / "img" / "qa"
FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_B = "C:/Windows/Fonts/segoeuib.ttf"
LARG, ALT, FPS = 1920, 1080, 30
DOURADO, BRANCO, CINZA = (201, 169, 110), (255, 255, 255), (138, 143, 152)

LEGENDAS = {
    "abertura": "Visão Geral · ano de 2025",
    "kpis": "1.403,8 milhões de t em 2025, 5,9% acima de 2024",
    "linha": "Mês a mês, 2025 fica acima de 2024 a partir de março",
    "mapa_suape": "Mapa com malha do IBGE: Suape em dourado",
    "filtro_nordeste": "Filtro Região = Nordeste: 329,7 milhões de t",
    "nordeste_suape": "Suape espera 4,3 h (mediana); a média dos pares, 26,4 h",
    "eficiencia": "Itaqui concentra a fila: 143,9 h de espera mediana",
    "perfil": "Perfil de carga: o que cada porto movimenta",
    "sobre": "Total conferido com a ANTAQ: diferença máxima de 1,16% ao ano",
}


def fonte(tam, negrito=False):
    return ImageFont.truetype(FONTE_B if negrito else FONTE, tam)


def cartela(linhas: list[tuple[str, int, tuple, bool]]) -> Image.Image:
    img = Image.new("RGB", (LARG, ALT), (0, 0, 0))
    d = ImageDraw.Draw(img)
    alturas = [fonte(t, n).getbbox(s)[3] + 24 for s, t, _, n in linhas]
    y = (ALT - sum(alturas)) // 2
    for (s, t, c, n), h in zip(linhas, alturas):
        f = fonte(t, n)
        w = d.textlength(s, font=f)
        d.text(((LARG - w) / 2, y), s, font=f, fill=c)
        y += h
    return img


def com_legenda(img: Image.Image, texto: str | None) -> Image.Image:
    if not texto:
        return img
    img = img.convert("RGBA")
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    f = fonte(40, True)
    w = d.textlength(texto, font=f)
    caixa = (int((LARG - w) / 2 - 28), ALT - 118, int((LARG + w) / 2 + 28), ALT - 44)
    d.rounded_rectangle(caixa, radius=14, fill=(0, 0, 0, 170))
    d.text(((LARG - w) / 2, ALT - 110), texto, font=f, fill=BRANCO)
    return Image.alpha_composite(img, camada).convert("RGB")


def video() -> Path:
    meta = json.loads((VID / "cenas.json").read_text(encoding="utf-8"))
    cenas = meta["cenas"]

    def legenda_em(t):
        atual = None
        for c in cenas:
            if c["t"] <= t:
                atual = c["legenda"]
        return LEGENDAS.get(atual)

    destino = VID / "raio-x-portuario.mp4"
    out = av.open(str(destino), "w", options={"movflags": "faststart"})
    s = out.add_stream("libx264", rate=FPS)
    s.width, s.height, s.pix_fmt = LARG, ALT, "yuv420p"
    s.options = {"preset": "slow", "crf": "27", "tune": "stillimage"}
    s.time_base = Fraction(1, FPS)
    n = 0

    def emitir(img):
        nonlocal n
        q = av.VideoFrame.from_ndarray(np.asarray(img.convert("RGB")), format="rgb24")
        q.pts = n
        for pac in s.encode(q):
            out.mux(pac)
        n += 1

    abertura = cartela([("Raio-X Portuário", 96, BRANCO, True), ("Dados abertos da ANTAQ, 2021–2025", 44, DOURADO, False),
                        ("Desempenho dos portos brasileiros com foco no Nordeste", 32, CINZA, False)])
    for _ in range(2 * FPS):
        emitir(abertura)
    entrada = av.open(str(VID / "gravacao_bruta.mp4"))
    st = entrada.streams.video[0]
    for q in entrada.decode(st):
        t = float(q.pts * st.time_base)
        img = q.to_image().resize((LARG, ALT), Image.LANCZOS)
        emitir(com_legenda(img, legenda_em(t)))
    entrada.close()
    fim = cartela([("github.com/gorc-supply/raio-x-portuario", 52, BRANCO, True), ("gorc-supply.github.io", 44, DOURADO, False),
                   ("Gabriel Cunha · Supply Chain & Operations", 30, CINZA, False)])
    for _ in range(3 * FPS):
        emitir(fim)
    for pac in s.encode():
        out.mux(pac)
    out.close()
    return destino


def revisar_video(arq: Path) -> list[Path]:
    pasta = VID / "quadros"
    pasta.mkdir(exist_ok=True)
    for velho in pasta.glob("*.jpg"):
        velho.unlink()
    c = av.open(str(arq))
    st = c.streams.video[0]
    proximo, saidas, poster = 0.0, [], None
    for q in c.decode(st):
        t = float(q.pts * st.time_base)
        if poster is None and t >= 4.0:
            poster = q.to_image()
        if t >= proximo:
            p = pasta / f"t{int(proximo):03d}s.jpg"
            q.to_image().resize((960, 540)).save(p, quality=80)
            saidas.append(p)
            proximo += 5
    c.close()
    poster.save(VID / "poster.jpg", quality=82, optimize=True)
    return saidas


def capa_e_gif() -> None:
    p1 = Image.open(IMG / "pagina-1.png").convert("RGB").resize((LARG, ALT), Image.LANCZOS)
    p1.save(IMG / "capa.png", optimize=True)
    quadros = []
    for i in range(1, 6):
        im = Image.open(IMG / f"pagina-{i}.png").convert("RGB").resize((960, 540), Image.LANCZOS)
        quadros.append(im.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE))
    quadros[0].save(IMG / "capa.gif", save_all=True, append_images=quadros[1:], duration=1500, loop=0, optimize=True)


def pdf() -> None:
    capa = cartela([("Raio-X Portuário", 96, BRANCO, True),
                    ("Desempenho dos portos brasileiros com foco no Nordeste", 40, DOURADO, False),
                    ("Dados abertos da ANTAQ · anos completos 2021–2025", 32, CINZA, False),
                    ("github.com/gorc-supply/raio-x-portuario · gorc-supply.github.io", 28, CINZA, False),
                    ("Gabriel Cunha · Supply Chain & Operations · Recife/PE", 28, CINZA, False)])
    paginas = [Image.open(IMG / f"pagina-{i}.png").convert("RGB").resize((LARG, ALT), Image.LANCZOS) for i in range(1, 6)]
    capa.save(RAIZ / "docs" / "RaioXPortuario.pdf", save_all=True, append_images=paginas, resolution=150)


def mapas_lado_a_lado() -> None:
    def recorte(arq):
        im = Image.open(arq).convert("RGB")
        e = im.width / 1280
        return im.crop((int(852 * e), int(236 * e), int(1264 * e), int(704 * e))).resize((618, 702), Image.LANCZOS)
    azure = recorte(QA / "c5_6_mapa_plano_b.png")
    disp = recorte(IMG / "pagina-1.png")
    painel = Image.new("RGB", (618 * 2 + 36, 702 + 70), (0, 0, 0))
    d = ImageDraw.Draw(painel)
    painel.paste(azure, (12, 58)); painel.paste(disp, (618 + 24, 58))
    d.text((12, 12), "Opção 1 · Azure Maps ajustado", font=fonte(28, True), fill=CINZA)
    d.text((618 + 24, 12), "Opção 2 · malha do IBGE (escolhida)", font=fonte(28, True), fill=DOURADO)
    painel.save(IMG / "mapa_opcoes.png", optimize=True)


def main() -> int:
    capa_e_gif()
    pdf()
    mapas_lado_a_lado()
    v = video()
    quadros = revisar_video(v)
    for arq in [v, VID / "poster.jpg", IMG / "capa.png", IMG / "capa.gif", RAIZ / "docs" / "RaioXPortuario.pdf",
                IMG / "mapa_opcoes.png"]:
        print(f"{arq.relative_to(RAIZ)}: {arq.stat().st_size / 1e6:.2f} MB")
    c = av.open(str(v)); st = c.streams.video[0]
    print(f"vídeo: {st.width}x{st.height}, {float(st.duration * st.time_base):.1f} s, {st.average_rate} fps, {st.codec_context.name}")
    c.close()
    print(f"{len(quadros)} quadros de revisão em docs/video/quadros/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
