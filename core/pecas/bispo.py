from ._peca import Peca, destinos_raio, DIAGONAIS


class Bispo(Peca):
    letra = 'b'

    def movimentos_possiveis(self, tabuleiro):
        return destinos_raio(self, tabuleiro, DIAGONAIS)
