from ._peca import Peca


class Peao(Peca):
    letra = 'p'

    def movimentos_possiveis(self, tabuleiro):
        direcao = -1 if self.cor == 'branco' else 1
        inicial = 6 if self.cor == 'branco' else 1
        linha = self.linha + direcao
        movimentos = []

        if not 0 <= linha < 8:
            return movimentos

        if tabuleiro.get_peca(linha, self.coluna) is None:
            movimentos.append((linha, self.coluna))
            dupla = linha + direcao
            if self.linha == inicial and tabuleiro.get_peca(dupla, self.coluna) is None:
                movimentos.append((dupla, self.coluna))

        for coluna in (self.coluna - 1, self.coluna + 1):
            if not 0 <= coluna < 8:
                continue
            alvo = tabuleiro.get_peca(linha, coluna)
            if alvo is not None and alvo.cor != self.cor and alvo.letra != 'k':
                movimentos.append((linha, coluna))

        return movimentos
