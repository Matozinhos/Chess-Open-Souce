from ._peca import Peca, destinos_salto, SALTOS_CAVALO


class Cavalo(Peca):
    letra = 'n'

    def movimentos_possiveis(self, tabuleiro):
        return destinos_salto(self, tabuleiro, SALTOS_CAVALO)
