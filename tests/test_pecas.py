import pytest

from core import Jogo, Peao


def uci(jogo, origem=None):
    return {lance.uci for lance in jogo.movimentos_legais(origem)}


def test_inicio_tem_trinta_e_duas_pecas_e_vinte_lances():
    jogo = Jogo()
    assert len(jogo.tabuleiro.PECAS_BRANCAS) == 16
    assert len(jogo.tabuleiro.PECAS_PRETAS) == 16
    assert len(uci(jogo)) == 20


def test_peao_avanca_duas_ou_uma_casa():
    jogo = Jogo()
    assert uci(jogo, (6, 4)) == {'e2e3', 'e2e4'}
    jogo.jogar_uci('e2e4')
    assert uci(jogo, (1, 4)) == {'e7e6', 'e7e5'}


def test_peao_captura_na_diagonal():
    jogo = Jogo()
    for lance in ('e2e4', 'd7d5'):
        jogo.jogar_uci(lance)
    assert 'e4d5' in uci(jogo)
    jogo.jogar_uci('e4d5')
    assert isinstance(jogo.tabuleiro.get_peca(3, 3), Peao)
    assert jogo.tabuleiro.get_peca(4, 4) is None


def test_caminho_bloqueado():
    jogo = Jogo()
    assert 'a1a3' not in uci(jogo)
    assert 'c1h6' not in uci(jogo)
    assert 'b1c3' in uci(jogo)


@pytest.mark.parametrize('lance', ['e7e5', 'e2e5', 'a1a4', 'd1d8', 'e2e1'])
def test_lance_ilegal_nao_modifica_tabuleiro(lance):
    jogo = Jogo()
    antes = jogo.tabuleiro.para_fen()
    with pytest.raises(ValueError):
        jogo.jogar_uci(lance)
    assert jogo.tabuleiro.para_fen() == antes
    assert not jogo.historico


def test_peca_nao_pode_capturar_rei():
    jogo = Jogo('4k3/8/8/8/8/8/4R3/K7 w - - 0 1')
    assert 'e2e8' not in uci(jogo)
