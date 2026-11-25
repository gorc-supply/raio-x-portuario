"""Configuração central do pipeline Raio-X Portuário.

Tudo que é "parâmetro de negócio" ou "endereço de fonte" fica aqui, num lugar só.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Pastas
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"
REF_DIR = ROOT / "etl" / "referencias"

# Zips oficiais da ANTAQ colocados à mão (ver docs/PENDENCIAS.md).
RAW_OFICIAL_DIR = RAW_DIR / "antaq_oficial"
# Cópia local do espelho público usado como contingência.
RAW_ESPELHO_DIR = RAW_DIR / "espelho_hf"
# Tabela oficial de nomenclatura SH (Comex Stat / MDIC).
RAW_SH_FILE = RAW_DIR / "comexstat_tabela_sh.json"
MANIFEST_FILE = RAW_DIR / "manifesto_download.json"
DOWNLOAD_LOG = RAW_DIR / "download.log"

# ---------------------------------------------------------------------------
# Recorte
# ---------------------------------------------------------------------------
ANO_INICIAL = 2021
ANO_FINAL = 2025  # jan/2026 (único mês de 2026 no espelho) fica fora: ver DECISOES D18
ANOS = list(range(ANO_INICIAL, ANO_FINAL + 1))

# Tabelas do Estatístico Aquaviário usadas no projeto (nomes oficiais dos arquivos).
TABELAS = ["Atracacao", "Carga", "TemposAtracacao", "TemposAtracacaoParalisacao"]

# ---------------------------------------------------------------------------
# Fontes
# ---------------------------------------------------------------------------
# Fonte primária (oficial). Fora do ar desde jun/2026 — ver docs/DECISOES.md (D02).
ANTAQ_PAGINA_DOWNLOAD = "https://web3.antaq.gov.br/ea/sense/download.html"
ANTAQ_AVISO_INDISPONIVEL = (
    "https://www.gov.br/antaq/pt-br/central-de-conteudos/publicacoes-da-antaq/"
    "publicacoes-off/painel-estatistico-aquaviario-indisponivel"
)

# Fonte de contingência: espelho público (CC-BY-4.0) dos TXT oficiais convertidos
# para Parquet, com os nomes de coluna originais. Revisão fixada para reprodutibilidade.
ESPELHO_REPO = "vinicius-souza/antaq"
ESPELHO_REVISAO = "ff0349fa6dc8cebcec161ee3ce48f6f73f7f3ba8"  # commit de 2026-04-18
ESPELHO_URL = (
    "https://huggingface.co/datasets/{repo}/resolve/{rev}/silver/{tabela}/ano={ano}/data.parquet"
)

# Nomenclatura SH oficial (capítulo SH2 > posição SH4 > subposição SH6), em português.
COMEXSTAT_SH_URL = "https://api-comexstat.mdic.gov.br/tables/hs"

# ---------------------------------------------------------------------------
# Regras de limpeza (ver docs/DECISOES.md e docs/data_quality.md)
# ---------------------------------------------------------------------------
# Percentil usado para limitar (winsorizar) outliers de TEMPO por natureza de carga.
# Nunca é aplicado à tonelagem.
PERCENTIL_OUTLIER_TEMPO = 0.995
