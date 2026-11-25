"""Gera a imagem de fundo do mapa próprio (plano B, sem serviço externo) a partir da malha oficial do IBGE.

Projeção equiretangular (x = longitude, y = latitude), com a MESMA extensão fixa usada nos eixos do gráfico de
dispersão do Power BI (EXTENSAO abaixo). Fundo transparente, país em cinza-escuro e divisas de UF discretas,
na paleta do tema.

Fonte: IBGE, API de malhas v3 (https://servicodados.ibge.gov.br/api/docs/malhas?versao=3).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

URL_UF = ("https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson"
          "&qualidade=intermediaria&intrarregiao=UF")
URL_PAIS = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&qualidade=intermediaria"
# Extensão fixa (graus) — de Roraima ao RS e de Tabatinga ao litoral; igual aos eixos do visual.
EXTENSAO = {"lon_min": -74.5, "lon_max": -33.5, "lat_min": -34.5, "lat_max": 5.9}
PX_POR_GRAU = 40
DESTINOS = [C.ROOT / "powerbi" / "RaioXPortuario.Report" / "StaticResources" / "RegisteredResources" / "mapa_brasil_ibge.png",
            C.ROOT / "docs" / "img" / "mapa_brasil_ibge.png"]


def baixar(url: str, nome: str) -> dict:
    destino = C.RAW_DIR / "ibge" / nome
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        destino.write_bytes(r.content)
    return json.loads(destino.read_text(encoding="utf-8"))


def aneis(geom: dict):
    if geom["type"] == "Polygon":
        yield from geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        for poligono in geom["coordinates"]:
            yield from poligono


def main() -> int:
    ufs = baixar(URL_UF, "malha_br_uf.json")
    pais = baixar(URL_PAIS, "malha_br.json")
    e = EXTENSAO
    largura = round((e["lon_max"] - e["lon_min"]) * PX_POR_GRAU)
    altura = round((e["lat_max"] - e["lat_min"]) * PX_POR_GRAU)

    def xy(lon, lat):
        return ((lon - e["lon_min"]) / (e["lon_max"] - e["lon_min"]) * largura,
                (e["lat_max"] - lat) / (e["lat_max"] - e["lat_min"]) * altura)

    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in pais["features"]:
        for anel in aneis(f["geometry"]):
            d.polygon([xy(*p) for p in anel], fill=(24, 27, 33, 255))
    for f in ufs["features"]:
        for anel in aneis(f["geometry"]):
            d.line([xy(*p) for p in anel] + [xy(*anel[0])], fill=(52, 58, 68, 255), width=2)
    for f in pais["features"]:
        for anel in aneis(f["geometry"]):
            d.line([xy(*p) for p in anel] + [xy(*anel[0])], fill=(90, 98, 110, 255), width=3)
    for destino in DESTINOS:
        destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(destino, optimize=True)
    print(f"mapa base {largura}x{altura}px salvo em {DESTINOS[0].name} (extensão {EXTENSAO})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
