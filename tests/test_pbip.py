"""O projeto Power BI passa na validação de schemas PBIR e de referências do modelo."""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_validar_pbip():
    r = subprocess.run([sys.executable, str(RAIZ / "etl" / "validar_pbip.py")], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8",
                                                                             **__import__("os").environ})
    assert r.returncode == 0, r.stdout + r.stderr
