import pytest

from core import FEN_INICIAL, Tabuleiro


@pytest.mark.parametrize('fen', [
    FEN_INICIAL,
    'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1',
    '8/8/8/3pP3/8/8/8/K6k w - d6 0 1',
    'k7/4P3/8/8/8/8/8/7K w - - 0 1',
])
def test_roundtrip_fen(fen):
    assert Tabuleiro.from_fen(fen).para_fen() == fen


@pytest.mark.parametrize('fen', [
    '8/8/8/8/8/8/8/8 w - - 0 1',
    '8/8/8/8/8/8/8/K6k w - - 0',
    '8/8/8/8/8/8/8/K6k z - - 0 1',
    '8/8/8/8/8/8/8/K6k w K - 0 1',
    '8/8/8/8/8/8/8/K6k w - a3 0 1',
    '8/8/8/8/8/8/8/K6k w - - -1 1',
    '8/8/8/8/8/8/8/K6k w - - 0 0',
    '8/8/8/8/8/8/8/K6P w - - 0 1',
    '8/8/8/8/8/8/8/K6k w KK - 0 1',
])
def test_fen_invalida_rejeitada(fen):
    with pytest.raises(ValueError):
        Tabuleiro(fen)


def test_fen_invalida_nao_destroi_posicao():
    tabuleiro = Tabuleiro()
    with pytest.raises(ValueError):
        tabuleiro.carregar_fen('8/8/8/8/8/8/8/8 w - - 0 1')
    assert tabuleiro.para_fen() == FEN_INICIAL


def test_coordenadas_algebricas():
    assert Tabuleiro.coordenadas('a8') == (0, 0)
    assert Tabuleiro.coordenadas('h1') == (7, 7)
    assert Tabuleiro.algebraica((7, 4)) == 'e1'
    with pytest.raises(ValueError):
        Tabuleiro.coordenadas('i9')
    with pytest.raises(ValueError):
        Tabuleiro.algebraica((8, 0))


def test_inversao_apenas_das_linhas():
    tabuleiro = Tabuleiro()
    normal = tabuleiro.print_tabuleiro('branco').splitlines()
    invertido = tabuleiro.print_tabuleiro('preto').splitlines()
    assert invertido == list(reversed(normal))
