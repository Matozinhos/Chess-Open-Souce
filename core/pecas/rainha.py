from ._peca import Peca, destinos_raio, TODAS_DIRECOES


class Rainha(Peca):
    letra = 'q'

    def movimentos_possiveis(self, tabuleiro):
        return destinos_raio(self, tabuleiro, TODAS_DIRECOES)
