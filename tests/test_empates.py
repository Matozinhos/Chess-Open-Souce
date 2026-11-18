import pytest

from core import Jogo


def repetir(j, vezes):
    for _ in range(vezes):
        for m in ('g1f3', 'g8f6', 'f3g1', 'f6g8'):
            j.jogar_uci(m)


def test_tres_repeticoes_so_por_reivindicacao():
    j = Jogo()
    repetir(j, 2)
    assert 'três repetições' in j.estado().reivindicavel
    assert not j.estado().terminado
    assert j.reivindicar_empate().tipo == 'empate_reivindicado'
    assert j.desfazer()
    assert not j.estado().terminado


def test_cinco_repeticoes_encerram_automaticamente():
    j = Jogo()
    repetir(j, 4)
    assert j.estado().tipo == 'empate_automatico'
    assert j.estado().motivo == 'cinco repetições'


def test_reivindicacao_antecipada_de_repeticao():
    j = Jogo()
    repetir(j, 1)
    for lance in ('g1f3', 'g8f6', 'f3g1'):
        j.jogar_uci(lance)
    assert not j.estado().reivindicavel
    fen = j.tabuleiro.para_fen()
    assert j.reivindicar_empate(lance_pretendido='f6g8').tipo == 'empate_reivindicado'
    assert j.tabuleiro.para_fen() == fen


def test_cinquenta_e_setenta_cinco_lances():
    j = Jogo('7k/8/8/8/8/8/8/K5R1 w - - 100 60')
    assert '50 lances' in j.estado().reivindicavel
    assert not j.estado().terminado
    j.reivindicar_empate('50 lances')
    assert j.estado().terminado

    automatico = Jogo('7k/8/8/8/8/8/8/K5R1 w - - 150 85')
    assert automatico.estado().tipo == 'empate_automatico'
    assert automatico.estado().motivo == '75 lances'


def test_reivindicacao_antecipada_de_cinquenta_lances():
    j = Jogo('7k/8/8/8/8/8/8/K5R1 w - - 99 60')
    assert not j.estado().reivindicavel
    fen = j.tabuleiro.para_fen()
    j.reivindicar_empate('50 lances', lance_pretendido='g1g2')
    assert j.estado().tipo == 'empate_reivindicado'
    assert j.tabuleiro.para_fen() == fen


def test_mate_prevalece_sobre_setenta_cinco_lances():
    j = Jogo('7k/6Q1/5K2/8/8/8/8/8 b - - 150 85')
    assert j.estado().tipo == 'xeque_mate'


@pytest.mark.parametrize('fen', [
    '7k/8/8/8/8/8/8/K7 w - - 0 1',
    '7k/8/8/8/8/8/8/KN6 w - - 0 1',
    '7k/8/8/8/8/8/8/K5B1 w - - 0 1',
    '5b1k/8/8/8/8/8/8/K1B5 w - - 0 1',
])
def test_posicoes_mortas_simples(fen):
    assert Jogo(fen).estado().tipo == 'empate_material'


def test_dois_cavalos_nao_sao_classificados_automaticamente_como_posicao_morta():
    assert Jogo('7k/8/8/8/8/8/8/KNN5 w - - 0 1').estado().tipo != 'empate_material'
