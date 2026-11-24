import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "etl"))

import kpis  # noqa: E402


@pytest.fixture(scope="session")
def con():
    """Conexão DuckDB sobre os CSV finais de data/processed/ (os mesmos que o Power BI lê)."""
    c = kpis.conectar()
    yield c
    c.close()
