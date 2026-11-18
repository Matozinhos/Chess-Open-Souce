"""Testes com sequências reproduzíveis e restauração integral."""
import random

from core import FEN_INICIAL, Jogo
from test.inspecao import verificar_invariantes


def test_sequencias_legais_e_undo_nao_perdem_estado():
    for seed in range(8):
        jogo = Jogo()
        aleatorio = random.Random(seed)

        for _ in range(90):
            lances = jogo.movimentos_legais()
            if not lances:
                break
            jogo.jogar_uci(aleatorio.choice(lances).uci)
            assert not verificar_invariantes(jogo.tabuleiro)

        while jogo.desfazer():
            assert not verificar_invariantes(jogo.tabuleiro)

        assert jogo.tabuleiro.para_fen() == FEN_INICIAL
        assert len(jogo.chaves) == 1
        assert len(jogo.notacoes) == 0
        assert len(jogo.historico) == 0
