from abc import ABC, abstractmethod

ORTOGONAIS = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIAGONAIS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
TODAS_DIRECOES = ORTOGONAIS + DIAGONAIS
SALTOS_CAVALO = tuple(
    (sinal_l * dl, sinal_c * dc)
    for dl, dc in ((1, 2), (2, 1))
    for sinal_l in (-1, 1)
    for sinal_c in (-1, 1)
)


class Peca(ABC):
    letra = '?'

    def __init__(self, cor: str, linha: int, coluna: int) -> None:
        if cor not in ('branco', 'preto'):
            raise ValueError('Cor de peça inválida.')
        self.cor = cor
        self.linha = linha
        self.coluna = coluna

    def mover_para(self, linha: int, coluna: int) -> None:
        self.linha, self.coluna = linha, coluna

    def posicao_atual(self) -> tuple[int, int]:
        return self.linha, self.coluna

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.cor!r}, {self.linha}, {self.coluna})'

    def __str__(self) -> str:
        return f'{type(self).__name__} {self.cor} ({self.linha}, {self.coluna})'

    @abstractmethod
    def movimentos_possiveis(self, tabuleiro) -> list[tuple[int, int]]:
        pass


def destinos_salto(peca: Peca, tabuleiro, direcoes) -> list[tuple[int, int]]:
    destinos = []
    for dl, dc in direcoes:
        linha, coluna = peca.linha + dl, peca.coluna + dc
        if not tabuleiro.is_dentro_dos_limites(linha, coluna):
            continue
        alvo = tabuleiro.get_peca(linha, coluna)
        if alvo is None or (alvo.cor != peca.cor and alvo.letra != 'k'):
            destinos.append((linha, coluna))
    return destinos


def destinos_raio(peca: Peca, tabuleiro, direcoes) -> list[tuple[int, int]]:
    destinos = []
    for dl, dc in direcoes:
        linha, coluna = peca.linha + dl, peca.coluna + dc
        while tabuleiro.is_dentro_dos_limites(linha, coluna):
            alvo = tabuleiro.get_peca(linha, coluna)
            if alvo is not None:
                if alvo.cor != peca.cor and alvo.letra != 'k':
                    destinos.append((linha, coluna))
                break
            destinos.append((linha, coluna))
            linha += dl
            coluna += dc
    return destinos
