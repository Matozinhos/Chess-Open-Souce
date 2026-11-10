from .casa import Casa
from .pecas import Torre, Cavalo, Bispo, Rainha, Rei, Peao

class Tabuleiro:
    def __init__(self):
        self.casas = [[Casa(linha, coluna) for coluna in range(8)] for linha in range(8)]
        self.MOVIMENTOS = [] # PAR = branco, IMPAR = preto

        self.PECAS_PRETAS = []
        self.PECAS_BRANCAS = []


    @staticmethod
    def is_dentro_dos_limites(linha: int, coluna: int) -> bool:
        return 0 <= linha < 8 and 0 <= coluna < 8

    def __getitem__(self, linha):
        if 0 <= linha < 8:
            return self.casas[linha]
        else: 
            raise IndexError("Linha fora dos limites do tabuleiro.")

    def get_peca(self, linha: int, coluna: int):
        casa = self[linha][coluna]
        return casa.peca if casa else None

    def set_peca(self, linha: int, coluna: int, peca):
        casa = self[linha][coluna]
        if casa:
            casa.peca = peca

    def remover_peca(self, linha: int, coluna: int):
        casa = self[linha][coluna]
        if casa:
            casa.peca = None

    def mover_peca(self, linha_origem: int, coluna_origem: int, linha_destino: int, coluna_destino: int):

        peca = self.get_peca(linha_origem, coluna_origem)
        peca_destino = self.get_peca(linha_destino, coluna_destino)

        if peca:
            self.MOVIMENTOS.append(((peca, linha_origem, coluna_origem), (peca_destino, linha_destino, coluna_destino)))

            self.set_peca(linha_destino, coluna_destino, peca)
            self.remover_peca(linha_origem, coluna_origem)

        else: 
            raise ValueError("Não há peça na posição de origem.")

    def montar_posicao_inicial(self):
        from .pecas import Peao, Torre, Cavalo, Bispo, Rainha, Rei

        for coluna in range(8):
            self.set_peca(1, coluna, Peao("preto", 1, coluna))
            self.set_peca(6, coluna, Peao("branco", 6, coluna))

        pecas_pretas = [
            Torre("preto", 0, 0), Cavalo("preto", 0, 1), Bispo("preto", 0, 2),
            Rainha("preto", 0, 3), Rei("preto", 0, 4), Bispo("preto", 0, 5),
            Cavalo("preto", 0, 6), Torre("preto", 0, 7)
        ]
        self.PECAS_PRETAS = pecas_pretas

        pecas_brancas = [
            Torre("branco", 7, 0), Cavalo("branco", 7, 1), Bispo("branco", 7, 2),
            Rainha("branco", 7, 3), Rei("branco", 7, 4), Bispo("branco", 7, 5),
            Cavalo("branco", 7, 6), Torre("branco", 7, 7)
        ]
        self.PECAS_BRANCAS = pecas_brancas

        for peca in self.PECAS_PRETAS:
            self.set_peca(peca.linha, peca.coluna, peca)

        for peca in self.PECAS_BRANCAS:
            self.set_peca(peca.linha, peca.coluna, peca)

    def __str__(self):
        tabuleiro_str = ""
        for linha in self.casas:
            linha_str = " | ".join(str(str(casa.peca)[0]) if casa.peca else " " for casa in linha)
            tabuleiro_str += f"| {linha_str} |\n"
        return tabuleiro_str