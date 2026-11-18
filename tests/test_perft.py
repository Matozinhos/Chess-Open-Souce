import pytest

from core import FEN_INICIAL, Tabuleiro
from test.perft import perft


@pytest.mark.parametrize('profundidade,esperado', [
    (1, 20), (2, 400), (3, 8902), (4, 197281),
])
def test_posicao_inicial(profundidade, esperado):
    t = Tabuleiro()
    assert perft(t, profundidade) == esperado
    assert t.para_fen() == FEN_INICIAL


@pytest.mark.parametrize('profundidade,esperado', [
    (1, 48), (2, 2039), (3, 97862),
])
def test_kiwipete(profundidade, esperado):
    fen = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
    t = Tabuleiro(fen)
    assert perft(t, profundidade) == esperado
    assert t.para_fen() == fen


@pytest.mark.parametrize('profundidade,esperado', [
    (1, 14), (2, 191), (3, 2812),
])
def test_posicao_com_en_passant(profundidade, esperado):
    fen = '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1'
    t = Tabuleiro(fen)
    assert perft(t, profundidade) == esperado
    assert t.para_fen() == fen


@pytest.mark.parametrize('fen,contagem', [
    ('r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1', 9467),
    ('rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8', 62379),
    ('r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10', 89890),
])
def test_posicoes_taticas(fen, contagem):
    tabuleiro = Tabuleiro(fen)
    assert perft(tabuleiro, 3) == contagem
    assert tabuleiro.para_fen() == fen
