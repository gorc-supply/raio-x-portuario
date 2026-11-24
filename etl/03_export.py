"""Etapa 3 — exportação das tabelas finais para data/processed/ (CSV UTF-8, ponto decimal, datas ISO).

Também grava meta.csv (data de processamento, último mês com dado, origem dos dados),
lida pelo Power BI na medida [Última Atualização].
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

DB_PATH = C.RAW_DIR / "staging.duckdb"

# fAtracacao sai em um arquivo por ano (pasta data/processed/fAtracacao/) para que nenhum
# arquivo passe de 50 MB no GitHub; o Power Query combina a pasta.
TABELAS = {
    "fCarga": "SELECT * FROM fCarga",
    "fParalisacao": "SELECT * FROM fParalisacao",
    "dInstalacao": "SELECT * FROM dInstalacao ORDER BY IDInstalacao",
    "dMercadoria": "SELECT * FROM dMercadoria ORDER BY CodMercadoria",
    "dNavegacao": "SELECT * FROM dNavegacao ORDER BY OrdemNavegacao",
    "dNaturezaCarga": "SELECT * FROM dNaturezaCarga ORDER BY OrdemNatureza",
    "dSentido": "SELECT * FROM dSentido ORDER BY OrdemSentido",
}


def main() -> int:
    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    total = 0
    pasta_atr = C.PROCESSED_DIR / "fAtracacao"
    pasta_atr.mkdir(exist_ok=True)
    for velho in pasta_atr.glob("*.csv"):
        velho.unlink()
    (C.PROCESSED_DIR / "fAtracacao.csv").unlink(missing_ok=True)
    for (ano,) in con.sql("SELECT DISTINCT year(DataDesatracacao) FROM fAtracacao ORDER BY 1").fetchall():
        destino = pasta_atr / f"fAtracacao_{ano}.csv"
        con.sql(f"""COPY (SELECT * FROM fAtracacao WHERE year(DataDesatracacao) = {ano}
                          ORDER BY DataDesatracacao, IDAtracacao) TO '{destino.as_posix()}'
                    (HEADER, DELIMITER ',', TIMESTAMPFORMAT '%Y-%m-%d %H:%M')""")
        total += destino.stat().st_size
        print(f"fAtracacao/{destino.name:22s} {destino.stat().st_size/1e6:8.2f} MB")
    for nome, sql in TABELAS.items():
        destino = C.PROCESSED_DIR / f"{nome}.csv"
        con.sql(f"""COPY ({sql}) TO '{destino.as_posix()}'
                    (HEADER, DELIMITER ',', DATEFORMAT '%Y-%m-%d', TIMESTAMPFORMAT '%Y-%m-%d %H:%M:%S')""")
        tam = destino.stat().st_size
        total += tam
        print(f"{nome:16s} {tam/1e6:8.2f} MB")

    ultimo = con.sql("SELECT max(DataRef) FROM fCarga").fetchall()[0][0]
    meta_t = json.loads((C.RAW_DIR / "transform_meta.json").read_text(encoding="utf-8"))
    origens = sorted({o for tab in meta_t["origens"].values() for o in tab.values()})
    con.close()
    meta = C.PROCESSED_DIR / "meta.csv"
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with meta.open("w", encoding="utf-8", newline="\n") as f:
        f.write("DataProcessamento,UltimoMesDisponivel,AnoInicial,AnoFinal,OrigemDados\n")
        f.write(f'{agora},{ultimo:%Y-%m-%d},{C.ANO_INICIAL},{C.ANO_FINAL},"{" + ".join(origens)}"\n')
    total += meta.stat().st_size
    print(f"{'TOTAL':16s} {total/1e6:8.2f} MB  (último mês com dado: {ultimo:%m/%Y})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
