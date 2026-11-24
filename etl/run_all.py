"""Roda o pipeline completo, na ordem, e para no primeiro erro.

Uso (na raiz do projeto):
    .venv\\Scripts\\python etl\\run_all.py            # pipeline + testes
    .venv\\Scripts\\python etl\\run_all.py --sem-testes
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ETL = Path(__file__).resolve().parent
RAIZ = ETL.parent
ETAPAS = [
    ("Download", "01_download.py"),
    ("Tratamento", "02_transform.py"),
    ("Exportação CSV", "03_export.py"),
    ("Exploração (docs/exploracao.md)", "explorar.py"),
    ("Documentação numérica (valores de referência, qualidade, conciliação)", "04_documentar.py"),
    ("Validação do relatório Power BI (schemas PBIR + referências)", "validar_pbip.py"),
]


def rodar(cmd: list[str], titulo: str) -> None:
    print(f"\n=== {titulo} ===", flush=True)
    t0 = time.time()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(cmd, cwd=RAIZ, env=env)
    if r.returncode != 0:
        print(f"*** FALHOU: {titulo} (código {r.returncode})")
        sys.exit(r.returncode)
    print(f"--- ok em {time.time() - t0:.1f}s")


def main() -> None:
    for titulo, script in ETAPAS:
        if (ETL / script).exists():
            rodar([sys.executable, str(ETL / script)], titulo)
    if "--sem-testes" not in sys.argv:
        rodar([sys.executable, "-m", "pytest", "-q", "tests"], "Testes (pytest)")
    print("\nPipeline concluído.")


if __name__ == "__main__":
    main()
