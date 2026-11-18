from ._peca import Peca, destinos_raio, ORTOGONAIS


class Torre(Peca):
    letra = 'r'

    def movimentos_possiveis(self, tabuleiro):
        return destinos_raio(self, tabuleiro, ORTOGONAIS)
