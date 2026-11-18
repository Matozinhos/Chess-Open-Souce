"""Garantia de compatibilidade das APIs públicas dos pacotes."""

import importlib
import subprocess
import sys
from pathlib import Path

import core
import core.pecas
import core.validador


def test_exportacoes_publicas():
    for pacote in (core, core.pecas, core.validador):
        assert pacote.__all__
        assert len(pacote.__all__) == len(set(pacote.__all__))

        for nome in pacote.__all__:
            assert getattr(pacote, nome) is not None


def test_importacoes_diretas():
    from core import Casa, Jogo, Peao, Tabuleiro, Validador
    from core.pecas import Bispo, Cavalo, Peca, Rainha, Rei, Torre
    from core.validador import (
        can_enpassant,
        casa_atacada,
        classificar_empates,
        classificar_sem_lances,
        deixa_rei_em_xeque,
        em_xeque,
        expandir_promocoes,
        movimentos_en_passant,
        movimentos_roque,
        posicao_morta,
    )

    jogo = Jogo()
    assert isinstance(jogo.tabuleiro, Tabuleiro)
    assert isinstance(jogo.tabuleiro.get_casa(6, 4), Casa)
    assert isinstance(jogo.tabuleiro.get_peca(6, 4), Peao)
    assert len(Validador.movimentos_legais(jogo.tabuleiro)) == 20


def test_importacao_sem_ciclos_em_novo_processo():
    raiz = Path(__file__).resolve().parents[1]
    codigo = (
        "from core.validador import movimentos_roque, em_xeque; "
        "from core.pecas import Rei, Peao; "
        "from core import Jogo, Casa, Validador; "
        "assert len(Jogo().movimentos_legais()) == 20"
    )
    resultado = subprocess.run(
        [sys.executable, '-c', codigo],
        cwd=raiz,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
