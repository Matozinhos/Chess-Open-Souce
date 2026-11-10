from ._peca import Peca

class Peao(Peca):
    def __init__(self, cor: str, linha: int, coluna: int):
        super().__init__(cor, linha, coluna)

    def movimentos_possiveis(self, tabuleiro):
        movimentos = []
        direcao = 1 if self.cor == 'branco' else -1
        nova_linha = self.linha + direcao

        # Movimento para frente
        if 0 <= nova_linha < 8 and tabuleiro[nova_linha][self.coluna] is None:
            movimentos.append((nova_linha, self.coluna))

            # Movimento inicial
            if (self.cor == 'branco' and self.linha == 1) or (self.cor == 'preto' and self.linha == 6):
                nova_linha_dois_passos = self.linha + 2 * direcao
                if tabuleiro[nova_linha_dois_passos][self.coluna] is None:
                    movimentos.append((nova_linha_dois_passos, self.coluna))

        # Captura diagonal
        for delta_coluna in [-1, 1]:
            nova_coluna = self.coluna + delta_coluna
            if 0 <= nova_coluna < 8 and 0 <= nova_linha < 8:
                peca_alvo = tabuleiro[nova_linha][nova_coluna]
                if peca_alvo is not None and peca_alvo.cor != self.cor:
                    movimentos.append((nova_linha, nova_coluna))

        return movimentos
