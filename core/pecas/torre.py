from ._peca import Peca

class Torre(Peca):
    def __init__(self, cor: str, linha: int, coluna: int):
        super().__init__(cor, linha, coluna)

    def movimentos_possiveis(self, tabuleiro):
        movimentos = []
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]  

        for delta_linha, delta_coluna in direcoes:
            nova_linha = self.linha + delta_linha
            nova_coluna = self.coluna + delta_coluna

            while 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
                peca_alvo = tabuleiro[nova_linha][nova_coluna]
                if peca_alvo is None:
                    movimentos.append((nova_linha, nova_coluna))
                elif peca_alvo.cor != self.cor:
                    movimentos.append((nova_linha, nova_coluna))
                    break
                else:
                    break

                nova_linha += delta_linha
                nova_coluna += delta_coluna

        return movimentos