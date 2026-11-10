
from ..pecas import Peao, Torre, Cavalo, Bispo, Rainha, Rei , Peca
from ..tabuleiro import Tabuleiro

from .xeque import is_em_xeque

def is_cravada(tabuleiro, peca, destino_linha, destino_coluna) -> bool:

    origem_linha, origem_coluna = peca.linha, peca.coluna
    peca_destino = tabuleiro[destino_linha][destino_coluna]

    tabuleiro[destino_linha][destino_coluna] = peca
    tabuleiro[origem_linha][origem_coluna] = None
    peca.linha, peca.coluna = destino_linha, destino_coluna

    rei_em_xeque = is_em_xeque(tabuleiro, peca.cor)[0]

    tabuleiro[origem_linha][origem_coluna] = peca
    tabuleiro[destino_linha][destino_coluna] = peca_destino
    peca.linha, peca.coluna = origem_linha, origem_coluna

    return False if rei_em_xeque == None else rei_em_xeque