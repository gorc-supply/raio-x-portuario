"""Chaves únicas e não nulas nas dimensões."""
import pytest

CHAVES = {
    "dInstalacao": "IDInstalacao",
    "dMercadoria": "CodMercadoria",
    "dNavegacao": "CodNavegacao",
    "dNaturezaCarga": "CodNatureza",
    "dSentido": "CodSentido",
}


@pytest.mark.parametrize("tabela,chave", CHAVES.items())
def test_chave_unica_e_nao_nula(con, tabela, chave):
    n, distintos, nulos = con.sql(
        f"SELECT count(*), count(DISTINCT {chave}), count(*) FILTER (WHERE {chave} IS NULL) FROM {tabela}"
    ).fetchall()[0]
    assert n > 0
    assert nulos == 0, f"{tabela}.{chave} tem {nulos} nulos"
    assert n == distintos, f"{tabela}.{chave} tem {n - distintos} duplicadas"


@pytest.mark.parametrize("tabela,coluna", [("dInstalacao", "Instalacao"), ("dMercadoria", "Mercadoria"),
                                           ("dNavegacao", "Navegacao"), ("dNaturezaCarga", "NaturezaCarga"),
                                           ("dSentido", "Sentido")])
def test_rotulo_unico(con, tabela, coluna):
    """Rótulos usados em eixos/segmentações também precisam ser únicos (RANKX e ordenação no Power BI)."""
    n, d = con.sql(f"SELECT count(*), count(DISTINCT {coluna}) FROM {tabela}").fetchall()[0]
    assert n == d, f"{tabela}.{coluna} tem rótulos repetidos"


def test_benchmark_tem_suape_e_8_pares(con):
    r = con.sql("SELECT sum(EhSuape), count(*) FROM dInstalacao WHERE PortoBenchmarkNE IS NOT NULL").fetchall()[0]
    assert r == (1, 9)


def test_sem_texto_corrompido(con):
    for tabela, cols in {"dInstalacao": ["Instalacao", "ComplexoPortuario", "Municipio", "UFNome"],
                         "dMercadoria": ["Mercadoria"]}.items():
        for c in cols:
            # mojibake típico: 'Ã' ou 'Â' seguido de caractere U+0080–U+00BF (ex.: 'Ã§', 'Ã£', 'Â°')
            n = con.sql(f"SELECT count(*) FROM {tabela} "
                        rf"WHERE regexp_matches({c}, '[ÃÂ][\x{{80}}-\x{{BF}}]')").fetchall()[0][0]
            assert n == 0, f"{tabela}.{c} ainda tem acentuação corrompida"
