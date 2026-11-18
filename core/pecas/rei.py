from ._peca import Peca, destinos_salto, TODAS_DIRECOES


class Rei(Peca):
    letra = 'k'

    def movimentos_possiveis(self, tabuleiro):
        return destinos_salto(self, tabuleiro, TODAS_DIRECOES)
