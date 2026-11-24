"""KPIs calculados em DuckDB sobre os CSV de data/processed/ — os MESMOS arquivos que o Power BI lê.

Cada função replica a definição da medida DAX de mesmo nome (ver powerbi/.../_Medidas.tmdl e docs/kpis.md).
Serve para gerar docs/valores_referencia.md e para os testes.
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402


def conectar() -> duckdb.DuckDBPyConnection:
    P = C.PROCESSED_DIR.as_posix()
    con = duckdb.connect()
    con.sql(f"CREATE VIEW fCarga AS SELECT * FROM read_csv('{P}/fCarga.csv', header=true, "
            "types={'CodMercadoria':'VARCHAR','DataRef':'DATE'})")
    con.sql(f"CREATE VIEW fAtracacao AS SELECT *, date_trunc('month', DataDesatracacao)::DATE AS DataRef "
            f"FROM read_csv('{P}/fAtracacao/*.csv', header=true, union_by_name=true, "
            "types={'DataChegada':'TIMESTAMP','DataAtracacao':'TIMESTAMP','DataDesatracacao':'TIMESTAMP'})")
    con.sql(f"CREATE VIEW fParalisacao AS SELECT * FROM read_csv('{P}/fParalisacao.csv', header=true, "
            "types={'DataRef':'DATE'})")
    for d in ["dInstalacao", "dMercadoria", "dNavegacao", "dNaturezaCarga", "dSentido"]:
        tipos = "{'CodMercadoria':'VARCHAR','CapituloSH2':'VARCHAR'}" if d == "dMercadoria" else "{}"
        con.sql(f"CREATE VIEW {d} AS SELECT * FROM read_csv('{P}/{d}.csv', header=true, types={tipos})")
    con.sql(f"CREATE VIEW meta AS SELECT * FROM read_csv('{P}/meta.csv', header=true)")
    return con


def ultimo_mes(con) -> str:
    return str(con.sql("SELECT max(UltimoMesDisponivel) FROM meta").fetchall()[0][0])


def _filtro(ano: int, inst: str | None, meses_ate: int | None = None) -> str:
    f = f"year(DataRef) = {ano}"
    if meses_ate:
        f += f" AND month(DataRef) <= {meses_ate}"
    if inst:
        f += f" AND IDInstalacao IN ({inst})"
    return f


def kpis(con, ano: int, inst: str | None = None) -> dict:
    """KPIs de um ano. `inst` = lista SQL de IDInstalacao (ex.: "'BRSUA'") ou None (Brasil)."""
    um = con.sql("SELECT max(UltimoMesDisponivel)::DATE FROM meta").fetchall()[0][0]
    # [Toneladas AA] compara só os meses com dado do ano corrente (ex.: jan/2026 x jan/2025)
    meses = um.month if ano == um.year else None
    f = _filtro(ano, inst)
    fa = _filtro(ano - 1, inst, meses)
    r = {}
    r["Toneladas"] = con.sql(f"SELECT coalesce(sum(Toneladas),0) FROM fCarga WHERE {f}").fetchall()[0][0]
    r["Toneladas AA"] = con.sql(f"SELECT sum(Toneladas) FROM fCarga WHERE {fa}").fetchall()[0][0]
    r["Var % Toneladas AA"] = (r["Toneladas"] / r["Toneladas AA"] - 1) if r["Toneladas AA"] else None
    r["TEU"] = con.sql(f"SELECT coalesce(sum(TEU),0) FROM fCarga WHERE {f}").fetchall()[0][0]
    a = con.sql(f"""
        SELECT count(*) n, sum(Toneladas) t,
               avg(EsperaAtracacao_h) esp_media, median(EsperaAtracacao_h) esp_mediana,
               avg(Atracado_h) atr_medio, avg(Operacao_h) op_medio,
               sum(Operacao_h) FILTER (WHERE Operacao_h IS NOT NULL AND Atracado_h IS NOT NULL)
                 / nullif(sum(Atracado_h) FILTER (WHERE Operacao_h IS NOT NULL AND Atracado_h IS NOT NULL), 0) pct_op,
               sum(Toneladas) FILTER (WHERE Operacao_h > 0) / nullif(sum(Operacao_h) FILTER (WHERE Operacao_h > 0), 0) pr_op,
               sum(Toneladas) FILTER (WHERE Atracado_h > 0) / nullif(sum(Atracado_h) FILTER (WHERE Atracado_h > 0), 0) pr_ger
        FROM fAtracacao WHERE {f}""").fetchall()[0]
    r["Nº Atracações"] = a[0]
    r["Toneladas por Atracação"] = (a[1] / a[0]) if a[0] else None
    tot = r["Toneladas"]
    nav = dict(con.sql(f"""SELECT n.Navegacao, sum(Toneladas) FROM fCarga c JOIN dNavegacao n USING (CodNavegacao)
                           WHERE {f} GROUP BY 1""").fetchall())
    nat = dict(con.sql(f"""SELECT n.NaturezaCarga, sum(Toneladas) FROM fCarga c JOIN dNaturezaCarga n USING (CodNatureza)
                           WHERE {f} GROUP BY 1""").fetchall())
    r["% Cabotagem"] = nav.get("Cabotagem", 0) / tot if tot else None
    r["% Longo Curso"] = nav.get("Longo Curso", 0) / tot if tot else None
    r["% Contêiner"] = nat.get("Contêiner", 0) / tot if tot else None
    brasil = con.sql(f"SELECT sum(Toneladas) FROM fCarga WHERE {_filtro(ano, None)}").fetchall()[0][0]
    r["% do Total Brasil"] = tot / brasil if brasil else None
    r["Espera Média (h)"], r["Espera Mediana (h)"] = a[2], a[3]
    r["Tempo Atracado Médio (h)"], r["Tempo de Operação Médio (h)"] = a[4], a[5]
    r["% Atracado em Operação"] = a[6]
    r["Prancha Média Operacional (t/h)"], r["Prancha Média Geral (t/h)"] = a[7], a[8]
    r["Horas Paralisadas"] = con.sql(f"SELECT coalesce(sum(HorasParalisadas),0) FROM fParalisacao WHERE {f}"
                                     ).fetchall()[0][0]
    return r


def ranking(con, ano: int, id_inst: str, universo: str | None = None) -> int | None:
    """[Ranking Porto]: posição por toneladas entre as instalações do universo (todas, por padrão)."""
    filtro_u = f"AND IDInstalacao IN ({universo})" if universo else ""
    res = con.sql(f"""
        WITH t AS (SELECT i.Instalacao, i.IDInstalacao, sum(c.Toneladas) ton
                   FROM fCarga c JOIN dInstalacao i USING (IDInstalacao)
                   WHERE year(DataRef) = {ano} {filtro_u} GROUP BY 1, 2)
        SELECT r FROM (SELECT IDInstalacao, dense_rank() OVER (ORDER BY ton DESC) r FROM t) WHERE IDInstalacao = '{id_inst}'
    """).fetchall()
    return res[0][0] if res else None


def ids_benchmark(con) -> list[tuple[str, str, int]]:
    return con.sql("""SELECT IDInstalacao, PortoBenchmarkNE, EhSuape FROM dInstalacao
                      WHERE PortoBenchmarkNE IS NOT NULL ORDER BY OrdemBenchmark""").fetchall()


def espera_mediana_mensal(con, ano: int) -> list[tuple]:
    """Suape x média simples das medianas dos pares, por mês (medida [Espera Mediana Média Pares (h)])."""
    return con.sql(f"""
        WITH m AS (
            SELECT DataRef, i.PortoBenchmarkNE p, i.EhSuape s, median(EsperaAtracacao_h) med
            FROM fAtracacao a JOIN dInstalacao i USING (IDInstalacao)
            WHERE i.PortoBenchmarkNE IS NOT NULL AND year(DataRef) = {ano} GROUP BY 1, 2, 3)
        SELECT DataRef, max(med) FILTER (WHERE s = 1) suape, avg(med) FILTER (WHERE s = 0) pares
        FROM m GROUP BY 1 ORDER BY 1
    """).fetchall()


def espera_mediana_media_pares(con, ano: int) -> float | None:
    return con.sql(f"""
        SELECT avg(med) FROM (
            SELECT i.PortoBenchmarkNE, median(EsperaAtracacao_h) med
            FROM fAtracacao a JOIN dInstalacao i USING (IDInstalacao)
            WHERE i.GrupoBenchmark = 'Pares do Nordeste' AND year(DataRef) = {ano} GROUP BY 1)
    """).fetchall()[0][0]
