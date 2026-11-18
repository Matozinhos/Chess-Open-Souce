import pytest

from core import Jogo, Tabuleiro, Validador


@pytest.mark.parametrize('fen', [
    'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1',
    '8/8/8/3pP3/8/8/8/K6k w - d6 0 1',
    'k7/4P3/8/8/8/8/8/7K w - - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
])
def test_apply_unmake_preserva_objetos_e_estado(fen):
    tabuleiro = Tabuleiro(fen)
    referencias = tuple(c.peca for linha in tabuleiro.casas for c in linha)
    coordenadas = [(p, p.posicao_atual()) for p in referencias if p]
    chaves = tabuleiro.chave_posicao()
    reis = tabuleiro.reis.copy()

    for lance in Validador.movimentos_legais(tabuleiro):
        with tabuleiro.simular(lance):
            assert tabuleiro.para_fen() != fen
        assert tabuleiro.para_fen() == fen
        assert tuple(c.peca for linha in tabuleiro.casas for c in linha) == referencias
        assert all(p.posicao_atual() == pos for p, pos in coordenadas)
        assert tabuleiro.chave_posicao() == chaves
        assert tabuleiro.reis == reis


def test_simulacao_reverte_mesmo_ao_lancar_excecao():
    t = Tabuleiro()
    fen = t.para_fen()
    lance = next(m for m in Validador.movimentos_legais(t) if m.uci == 'e2e4')
    with pytest.raises(RuntimeError):
        with t.simular(lance):
            raise RuntimeError('falha artificial')
    assert t.para_fen() == fen


def test_contador_repeticoes_e_undo():
    j = Jogo()
    for _ in range(2):
        for lance in ('g1f3', 'g8f6', 'f3g1', 'f6g8'):
            j.jogar_uci(lance)
    assert 'três repetições' in j.estado().reivindicavel
    assert j.desfazer()
    assert 'três repetições' not in j.estado().reivindicavel
