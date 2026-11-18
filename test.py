"""Atalho para o debug local; --smoke valida o motor sem abrir interface."""
import sys

from core import FEN_INICIAL, Jogo
from test.launcher import executar_console
from test.perft import perft


def smoke():
    jogo = Jogo()
    assert perft(jogo.tabuleiro, 3) == 8902
    jogo.jogar_uci('e2e4')
    assert jogo.desfazer()
    assert jogo.tabuleiro.para_fen() == FEN_INICIAL
    print('SMOKE OK: lances, perft e desfazer.')


if __name__ == '__main__':
    smoke() if '--smoke' in sys.argv else executar_console()
