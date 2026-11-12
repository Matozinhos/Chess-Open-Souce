from abc import ABC, abstractmethod
from ..debug import DEBUG

class Peca(ABC):
    def __init__(self, cor: str, linha: int, coluna: int):
        self.cor = cor # 'branco' ou 'preto'
        self.linha = linha
        self.coluna = coluna
        self.moveu = False

    @abstractmethod
    def movimentos_possiveis(self, tabuleiro):
        pass

    def mover_para(self, nova_linha: int, nova_coluna: int):
        self.linha = nova_linha
        self.coluna = nova_coluna
        if not self.moveu: 
            self.moveu = True

    def posicao_atual(self):
        return (self.linha, self.coluna)

    def __str__(self):
        return f"{DEBUG.PECAS_EMOJI[self.__class__.__name__, self.cor]} {self.cor} ({self.linha}, {self.coluna})" 

