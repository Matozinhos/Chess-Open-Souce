import pytest

from core import Jogo, PartidaEncerrada


def test_turno_historico_san_e_desfazer():
    j = Jogo()
    assert j.turno == 'branco'
    assert j.jogar_uci('e2e4').uci == 'e2e4'
    assert j.turno == 'preto'
    assert j.notacoes == ['e4']
    assert j.jogar_uci('e7e5').uci == 'e7e5'
    assert j.notacoes == ['e4', 'e5']
    assert j.desfazer()
    assert j.turno == 'preto'
    assert j.notacoes == ['e4']


def test_mate_do_pastor_invertido_fools_mate():
    j = Jogo()
    for lance in ('f2f3', 'e7e5', 'g2g4', 'd8h4'):
        j.jogar_uci(lance)
    assert j.estado().tipo == 'xeque_mate'
    assert j.estado().vencedor == 'preto'
    assert j.notacoes[-1] == 'Qh4#'
    with pytest.raises(PartidaEncerrada):
        j.jogar_uci('g1h3')
    assert j.desfazer()
    assert not j.estado().terminado


def test_afogamento_e_mate_fen():
    afogado = Jogo('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')
    assert afogado.estado().tipo == 'afogamento'
    assert afogado.estado().vencedor is None
    mate = Jogo('7k/6Q1/5K2/8/8/8/8/8 b - - 0 1')
    assert mate.estado().tipo == 'xeque_mate'
    assert mate.estado().vencedor == 'branco'


def test_desistencia_de_qualquer_lado():
    j = Jogo()
    estado = j.desistir('branco')
    assert estado.tipo == 'desistencia' and estado.vencedor == 'preto'
    with pytest.raises(PartidaEncerrada):
        j.jogar_uci('e2e4')


def test_empate_por_acordo_requer_outra_cor():
    j = Jogo()
    j.propor_empate('branco')
    with pytest.raises(ValueError):
        j.aceitar_empate('branco')
    assert j.aceitar_empate('preto').tipo == 'empate_acordo'
    assert not j.movimentos_legais()


def test_proposta_expira_ao_jogar():
    j = Jogo()
    j.propor_empate('branco')
    j.jogar_uci('e2e4')
    with pytest.raises(ValueError):
        j.aceitar_empate('preto')


def test_reiniciar_e_carregar_fen():
    j = Jogo()
    j.jogar_uci('e2e4')
    j.reiniciar()
    assert len(j.movimentos_legais()) == 20
    assert not j.historico
    j.carregar_fen('7k/8/8/8/8/8/8/K7 w - - 0 1')
    assert j.estado().tipo == 'empate_material'
    with pytest.raises(ValueError):
        j.carregar_fen('inválida')
    assert j.estado().tipo == 'empate_material'
