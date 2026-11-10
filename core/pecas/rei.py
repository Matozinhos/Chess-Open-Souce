from ._peca import Peca

class Rei(Peca):
    def __init__(self, cor: str, linha: int, coluna: int):
        super().__init__(cor, linha, coluna)

    def movimentos_possiveis(self, tabuleiro):
        movimentos = []
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  

        for delta_linha, delta_coluna in direcoes:
            nova_linha = self.linha + delta_linha
            nova_coluna = self.coluna + delta_coluna

            if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
                peca_alvo = tabuleiro[nova_linha][nova_coluna]
                if peca_alvo is None or peca_alvo.cor != self.cor:
                    movimentos.append((nova_linha, nova_coluna))

        return movimentos