from .pecas import Peao, Torre, Cavalo, Bispo, Rainha, Rei , Peca
from .tabuleiro import Tabuleiro

class Validador:
    @staticmethod
    def validar_movimento(self, peca : Peca, nova_linha: int, nova_coluna: int, tabuleiro : Tabuleiro):
        movimentos_possiveis = peca.movimentos_possiveis(tabuleiro)

        if (nova_linha, nova_coluna) not in movimentos_possiveis:
            raise ValueError(f"Movimento inválido para a peça {peca} para ({nova_linha}, {nova_coluna}).")

        # Caso a peca esteja cravada.

            
    @staticmethod
    def validar_enpassant(self, peao : Peao, tabuleiro : Tabuleiro):

        if not isinstance(peao, Peao):
            raise ValueError("A peça fornecida não é um peão.")
        if peao.cor == 'branco':
            linha_alvo = peao.linha - 1
        else:
            linha_alvo = peao.linha + 1

        if not (0 <= linha_alvo < 8):
            raise ValueError("Movimento en passant inválido: fora do tabuleiro.")

        coluna_alvo = peao.coluna
        peca_alvo = tabuleiro[linha_alvo][coluna_alvo]

        if peca_alvo is None or not isinstance(peca_alvo, Peao) or peca_alvo.cor == peao.cor:
            raise ValueError("Movimento en passant inválido: não há um peão adversário para capturar.")
