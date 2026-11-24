"""Integridade referencial dos fatos e limpeza dos tempos."""
from pathlib import Path

import pytest

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

RELACOES = [
    ("fCarga", "IDInstalacao", "dInstalacao", "IDInstalacao"),
    ("fCarga", "CodMercadoria", "dMercadoria", "CodMercadoria"),
    ("fCarga", "CodNavegacao", "dNavegacao", "CodNavegacao"),
    ("fCarga", "CodNatureza", "dNaturezaCarga", "CodNatureza"),
    ("fCarga", "CodSentido", "dSentido", "CodSentido"),
    ("fAtracacao", "IDInstalacao", "dInstalacao", "IDInstalacao"),
    ("fAtracacao", "CodNavegacao", "dNavegacao", "CodNavegacao"),
    ("fAtracacao", "CodNatureza", "dNaturezaCarga", "CodNatureza"),
    ("fParalisacao", "IDInstalacao", "dInstalacao", "IDInstalacao"),
]
TEMPOS = ["EsperaAtracacao_h", "Operacao_h", "Atracado_h", "Estadia_h"]


@pytest.mark.parametrize("fato,fk,dim,pk", RELACOES)
def test_sem_chave_orfa(con, fato, fk, dim, pk):
    orfas = con.sql(f"SELECT count(*) FROM {fato} f LEFT JOIN {dim} d ON f.{fk} = d.{pk} "
                    f"WHERE d.{pk} IS NULL").fetchall()[0][0]
    assert orfas == 0, f"{fato}.{fk}: {orfas} linhas sem correspondente em {dim}"


def test_fatos_sem_chave_nula(con):
    for fato, fk, *_ in RELACOES:
        assert con.sql(f"SELECT count(*) FROM {fato} WHERE {fk} IS NULL").fetchall()[0][0] == 0, f"{fato}.{fk}"


def test_id_atracacao_unico(con):
    n, d = con.sql("SELECT count(*), count(DISTINCT IDAtracacao) FROM fAtracacao").fetchall()[0]
    assert n == d


@pytest.mark.parametrize("col", TEMPOS)
def test_nenhuma_hora_negativa(con, col):
    assert con.sql(f"SELECT count(*) FROM fAtracacao WHERE {col} < 0").fetchall()[0][0] == 0


def test_paralisacao_sem_hora_negativa(con):
    assert con.sql("SELECT count(*) FROM fParalisacao WHERE HorasParalisadas < 0").fetchall()[0][0] == 0


def test_operacao_nao_maior_que_atracado(con):
    assert con.sql("SELECT count(*) FROM fAtracacao WHERE Operacao_h > Atracado_h + 0.01").fetchall()[0][0] == 0


def test_tonelagem_nunca_negativa_e_atracacoes_tem_carga(con):
    assert con.sql("SELECT count(*) FROM fCarga WHERE Toneladas < 0").fetchall()[0][0] == 0
    assert con.sql("SELECT count(*) FROM fAtracacao WHERE Toneladas < 0").fetchall()[0][0] == 0


def test_tonelagem_igual_entre_fatos(con):
    """A tonelagem por atracação (eficiência) soma o mesmo que a fCarga (volume), ano a ano."""
    r = con.sql("""SELECT a.ano, a.t, c.t FROM
                   (SELECT year(DataDesatracacao) ano, sum(Toneladas) t FROM fAtracacao GROUP BY 1) a
                   JOIN (SELECT year(DataRef) ano, sum(Toneladas) t FROM fCarga GROUP BY 1) c USING (ano)""").fetchall()
    assert r
    for ano, ta, tc in r:
        assert abs(ta - tc) / tc < 1e-6, f"{ano}: fAtracacao {ta} x fCarga {tc}"


def test_tamanho_dos_arquivos():
    arquivos = [p for p in PROCESSED.rglob("*.csv")]
    assert arquivos
    assert max(p.stat().st_size for p in arquivos) < 50e6, "algum CSV passou de 50 MB"
    assert sum(p.stat().st_size for p in arquivos) < 100e6, "data/processed passou de 100 MB"
