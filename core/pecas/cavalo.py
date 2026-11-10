from ._peca import Peca

class Cavalo(Peca):
    def __init__(self, cor: str, linha: int, coluna: int):
        super().__init__(cor, linha, coluna)

    def movimentos_possiveis(self, tabuleiro):
        movimentos = []
        delta_movimentos = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]

        for delta_linha, delta_coluna in delta_movimentos:
            nova_linha = self.linha + delta_linha
            nova_coluna = self.coluna + delta_coluna

            if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
                peca_alvo = tabuleiro[nova_linha][nova_coluna]
                if peca_alvo is None or peca_alvo.cor != self.cor:
                    movimentos.append((nova_linha, nova_coluna))

        return movimentos