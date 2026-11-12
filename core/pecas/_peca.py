from abc import ABC, abstractmethod
from ..debug import DEBUG

class Peca(ABC):
    def __init__(self, cor: str, linha: int, coluna: int):
        self.cor = cor # 'branco' ou 'preto'
        self.linha = linha
        self.coluna = coluna
        self.MOVIMENTOS = [linha, coluna] # Iniciando com a posicao inicial, então len=1 significa que nao se moveu
    @abstractmethod
    def movimentos_possiveis(self, tabuleiro):
        pass

    def mover_para(self, nova_linha: int, nova_coluna: int):
        self.linha = nova_linha
        self.coluna = nova_coluna
        self.MOVIMENTOS.append((self.linha,self.coluna))


    def posicao_atual(self):
        return (self.linha, self.coluna)

    def __str__(self):
        return f"{DEBUG.PECAS_EMOJI[self.__class__.__name__, self.cor]} {self.cor} ({self.linha}, {self.coluna})" 

