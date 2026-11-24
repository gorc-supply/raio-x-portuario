"""Critério de aceite: total nacional anual a ±2% do total oficial publicado pela ANTAQ."""
from pathlib import Path

import pandas as pd
import pytest

REF = Path(__file__).resolve().parents[1] / "etl" / "referencias" / "totais_oficiais_antaq.csv"
TOTAIS = pd.read_csv(REF).query("indicador == 'total'")


@pytest.mark.parametrize("ano,oficial", list(TOTAIS[["ano", "valor_mt"]].itertuples(index=False)))
def test_total_anual_bate_com_antaq(con, ano, oficial):
    pipeline = con.sql(f"SELECT sum(Toneladas) / 1e6 FROM fCarga WHERE year(DataRef) = {ano}").fetchall()[0][0]
    dif = pipeline / oficial - 1
    assert abs(dif) <= 0.02, f"{ano}: pipeline {pipeline:,.1f} Mt x oficial {oficial:,.1f} Mt ({dif:+.2%})"


def test_todos_os_anos_fechados_tem_referencia():
    assert set(TOTAIS["ano"]) == {2021, 2022, 2023, 2024, 2025}
