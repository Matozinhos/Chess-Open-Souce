from ..movimento import Movimento
from ..pecas import Peao


def movimentos_en_passant(tabuleiro, peao: Peao) -> list[Movimento]:
    alvo = tabuleiro.alvo_en_passant
    if alvo is None or peao.cor != tabuleiro.turno:
        return []

    linha, coluna = alvo
    direcao = -1 if peao.cor == 'branco' else 1
    if (peao.linha + direcao != linha or abs(peao.coluna - coluna) != 1
            or tabuleiro.get_peca(linha, coluna) is not None):
        return []

    capturada = tabuleiro.get_peca(peao.linha, coluna)
    if not isinstance(capturada, Peao) or capturada.cor == peao.cor:
        return []

    return [Movimento(peao.posicao_atual(), alvo, en_passant=True)]


def can_enpassant(peao: Peao, tabuleiro) -> bool:
    return bool(movimentos_en_passant(tabuleiro, peao))
