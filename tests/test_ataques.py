from core import Jogo
from core.validador import casa_atacada, em_xeque


def moves(jogo):
    return {l.uci for l in jogo.movimentos_legais()}


def test_ataque_peao_independe_da_ocupacao():
    jogo = Jogo('7k/8/8/4p3/8/8/8/K7 w - - 0 1')
    assert casa_atacada(jogo.tabuleiro, 4, 3, 'preto')
    assert casa_atacada(jogo.tabuleiro, 4, 5, 'preto')
    assert not casa_atacada(jogo.tabuleiro, 4, 4, 'preto')


def test_cravada_absoluta():
    jogo = Jogo('k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1')
    assert 'e2f2' not in moves(jogo)
    assert 'e2e8' in moves(jogo)
    assert not em_xeque(jogo.tabuleiro, 'branco')


def test_en_xeque_duplo_so_rei_move():
    jogo = Jogo('4r2k/8/8/8/1b6/8/4R3/4K3 w - - 0 1')
    assert em_xeque(jogo.tabuleiro, 'branco')
    assert all(l.origem == (7, 4) for l in jogo.movimentos_legais())


def test_reis_nao_podem_ficar_adjacentes():
    jogo = Jogo('8/8/8/8/8/4k3/8/4K3 w - - 0 1')
    assert {'e1d2', 'e1e2', 'e1f2'}.isdisjoint(moves(jogo))
