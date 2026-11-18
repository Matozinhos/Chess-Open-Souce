import pytest

from core import Jogo, Peao, Rainha, Torre, Cavalo


def uci(jogo, origem=None):
    return {l.uci for l in jogo.movimentos_legais(origem)}


@pytest.mark.parametrize('lance,torre_destino', [
    ('e1g1', (7, 5)), ('e1c1', (7, 3)),
])
def test_roque_branco_e_undo(lance, torre_destino):
    fen = 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1'
    j = Jogo(fen)
    assert lance in uci(j)
    j.jogar_uci(lance)
    assert isinstance(j.tabuleiro.get_peca(*torre_destino), Torre)
    assert not {'K', 'Q'} & j.tabuleiro.direitos_roque
    assert j.desfazer()
    assert j.tabuleiro.para_fen() == fen


@pytest.mark.parametrize('lance,torre_destino', [
    ('e8g8', (0, 5)), ('e8c8', (0, 3)),
])
def test_roque_preto(lance, torre_destino):
    j = Jogo('r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
    j.jogar_uci(lance)
    assert isinstance(j.tabuleiro.get_peca(*torre_destino), Torre)
    assert not {'k', 'q'} & j.tabuleiro.direitos_roque


def test_roque_atravessando_casa_atacada_ilegal():
    j = Jogo('r3k2r/5r2/8/8/8/8/8/R3K2R w KQkq - 0 1')
    assert 'e1g1' not in uci(j)
    assert 'e1c1' in uci(j)


def test_roque_perde_direito_depois_de_mover_torre():
    j = Jogo('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
    for lance in ('h1h2', 'a8a7', 'h2h1', 'a7a8'):
        j.jogar_uci(lance)
    assert 'e1g1' not in uci(j)


def test_capturar_torre_perde_direito_do_roque_correspondente():
    j = Jogo('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
    j.jogar_uci('a1a8')
    assert 'q' not in j.tabuleiro.direitos_roque
    assert 'Q' not in j.tabuleiro.direitos_roque
    assert 'k' in j.tabuleiro.direitos_roque


def test_enpassant_execucao_e_desfazer():
    fen = '8/8/8/3pP3/8/8/8/K6k w - d6 0 1'
    j = Jogo(fen)
    assert 'e5d6' in uci(j)
    j.jogar_uci('e5d6')
    assert isinstance(j.tabuleiro.get_peca(2, 3), Peao)
    assert j.tabuleiro.get_peca(3, 3) is None
    assert j.desfazer()
    assert j.tabuleiro.para_fen() == fen


def test_enpassant_expira_apos_um_lance():
    j = Jogo('8/8/8/3pP3/8/8/8/K6k w - d6 0 1')
    j.jogar_uci('a1a2')
    assert j.tabuleiro.alvo_en_passant is None


def test_enpassant_que_expoe_rei_e_ilegal():
    j = Jogo('k3r3/8/8/3pP3/8/8/8/4K3 w - d6 0 1')
    assert 'e5d6' not in uci(j)
    assert j.tabuleiro.chave_posicao().split()[3] == '-'


def test_enpassant_legal_entra_na_chave():
    j = Jogo('8/8/8/3pP3/8/8/8/K6k w - d6 0 1')
    assert j.tabuleiro.chave_posicao().split()[3] == 'd6'


@pytest.mark.parametrize('sufixo,classe', [('q', Rainha), ('n', Cavalo), ('r', Torre)])
def test_promocao_e_desfazer(sufixo, classe):
    fen = 'k7/4P3/8/8/8/8/8/7K w - - 0 1'
    j = Jogo(fen)
    assert len([m for m in j.movimentos_legais((1, 4)) if m.promocao]) == 4
    j.jogar_uci('e7e8' + sufixo)
    assert isinstance(j.tabuleiro.get_peca(0, 4), classe)
    assert j.desfazer()
    assert j.tabuleiro.para_fen() == fen


def test_promocao_sem_sufixo_e_rainha():
    j = Jogo('k7/4P3/8/8/8/8/8/7K w - - 0 1')
    j.jogar_uci('e7e8')
    assert isinstance(j.tabuleiro.get_peca(0, 4), Rainha)
    assert j.notacoes[-1].startswith('e8=Q')


def test_promocao_invalida_nao_muda_jogo():
    j = Jogo('k7/4P3/8/8/8/8/8/7K w - - 0 1')
    fen = j.tabuleiro.para_fen()
    with pytest.raises(ValueError):
        j.jogar_uci('e7e8x')
    assert j.tabuleiro.para_fen() == fen
