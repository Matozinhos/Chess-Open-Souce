import pytest

from core import Jogo
from core import EstadoPartida


def test_san_normal_captura_e_xeque():
    j = Jogo()
    for lance in ('e2e4', 'd7d5', 'e4d5', 'd8d5'):
        j.jogar_uci(lance)
    assert j.notacoes == ['e4', 'd5', 'exd5', 'Qxd5']


def test_san_desambiguacao_por_coluna():
    j = Jogo('7k/8/8/8/8/8/8/KN3N2 w - - 0 1')
    j.jogar_uci('b1d2')
    assert j.notacoes[-1] == 'Nbd2'


def test_san_desambiguacao_por_linha():
    j = Jogo('7k/8/8/8/8/1N6/8/KN6 w - - 0 1')
    j.jogar_uci('b1d2')
    assert j.notacoes[-1] == 'N1d2'


def test_estado_eh_imutavel_e_acessivel_por_chave():
    j = Jogo()
    estado = j.estado()
    assert estado['tipo'] == estado.tipo
    with pytest.raises((AttributeError, TypeError)):
        estado.terminado = True


def test_uci_invalido_antes_de_mutar_estado():
    j = Jogo()
    fen = j.tabuleiro.para_fen()
    for texto in ('e2e9', 'a9a1', 'e2e4X', 'a2a2zz', ''):
        with pytest.raises(ValueError):
            j.jogar_uci(texto)
    assert j.tabuleiro.para_fen() == fen
