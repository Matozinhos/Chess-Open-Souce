from core import FEN_INICIAL
from servicos.partida_local_servico import PartidaLocalServico
from test.controlador_debug import ControladorDebug
from test.perft import perft
from test.inspecao import verificar_invariantes


def test_servico_eh_adaptador_sem_regras_duplicadas():
    servico = PartidaLocalServico()
    assert len(servico.consultar_lances()) == 20
    assert len(servico.posicao()) == 8
    assert len(servico.posicao()[0]) == 8
    servico.jogar_uci('e2e4')
    assert servico.desfazer()
    assert servico.jogo.tabuleiro.para_fen() == FEN_INICIAL


def test_debug_fen_uci_inversao_invariantes_perft():
    debug = ControladorDebug()
    assert debug.executar('fen') == FEN_INICIAL
    assert debug.executar('perft 2') == '400'
    assert debug.executar('invariantes') == 'OK: posição consistente.'
    a = debug.executar('tabuleiro').splitlines()
    b = debug.executar('inverter').splitlines()
    assert b == a[::-1]
    debug.executar('jogar e2e4')
    assert debug.executar('historico') == 'e4'
    debug.executar('desfazer')
    assert debug.executar('fen') == FEN_INICIAL
    debug.executar('cenario promocao')
    assert 'e7e8q' in debug.executar('legais e7')


def test_perft_preserva_estado():
    servico = PartidaLocalServico()
    tabuleiro = servico.jogo.tabuleiro
    assert perft(tabuleiro, 3) == 8902
    assert tabuleiro.para_fen() == FEN_INICIAL
    assert not verificar_invariantes(tabuleiro)
