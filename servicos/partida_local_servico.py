"""Adaptador local do core para futuras interfaces e ferramentas de debug."""
from core import Jogo


class PartidaLocalServico:
    def __init__(self, fen: str | None = None) -> None:
        self.jogo = Jogo(fen) if fen is not None else Jogo()

    def estado(self):
        return self.jogo.estado()

    def posicao(self):
        return tuple(tuple(
            (c.peca.letra, c.peca.cor) if c.peca else None
            for c in linha
        ) for linha in self.jogo.tabuleiro.casas)

    def consultar_lances(self, origem=None):
        return self.jogo.movimentos_legais(origem)

    def jogar(self, origem, destino, promocao=None):
        return self.jogo.jogar(*origem, *destino, promocao)

    def jogar_uci(self, lance):
        return self.jogo.jogar_uci(lance)

    def desfazer(self):
        return self.jogo.desfazer()

    def carregar_fen(self, fen):
        self.jogo.carregar_fen(fen)

    def reiniciar(self):
        self.jogo.reiniciar()

    def reivindicar_empate(self, motivo=None, lance_pretendido=None):
        return self.jogo.reivindicar_empate(motivo, lance_pretendido)

    def propor_empate(self, cor):
        self.jogo.propor_empate(cor)

    def aceitar_empate(self, cor):
        return self.jogo.aceitar_empate(cor)

    def desistir(self, cor):
        return self.jogo.desistir(cor)
