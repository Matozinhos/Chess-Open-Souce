"""Comandos de console para experimentar jogadas e inspecionar o motor."""
from core import Jogo, Tabuleiro
from test.inspecao import verificar_invariantes
from test.perft import perft


class ControladorDebug:
    def __init__(self):
        self.jogo = Jogo()
        self.invertido = False

    def executar(self, comando: str) -> str:
        partes = comando.strip().split()
        if not partes:
            return "Digite um comando."
        acao = partes[0].lower()
        if acao == "fen":
            return self.jogo.tabuleiro.para_fen()
        if acao == "tabuleiro":
            return self.jogo.tabuleiro.print_tabuleiro("preto" if self.invertido else "branco")
        if acao == "inverter":
            self.invertido = not self.invertido
            return self.executar("tabuleiro")
        if acao == "perft" and len(partes) == 2:
            return str(perft(self.jogo.tabuleiro, int(partes[1])))
        if acao == "invariantes":
            erros = verificar_invariantes(self.jogo.tabuleiro)
            return "\n".join(erros) if erros else "OK: posição consistente."
        if acao == "jogar" and len(partes) == 2:
            self.jogo.jogar_uci(partes[1])
            return self.jogo.notacoes[-1]
        if acao == "desfazer":
            return "Lance desfeito." if self.jogo.desfazer() else "Sem lances."
        if acao == "historico":
            return " ".join(self.jogo.notacoes)
        if acao == "legais" and len(partes) == 2:
            origem = Tabuleiro.coordenadas(partes[1])
            return " ".join(lance.uci for lance in self.jogo.movimentos_legais(origem))
        if acao == "cenario" and partes[1:] == ["promocao"]:
            self.jogo.carregar_fen("k7/4P3/8/8/8/8/8/7K w - - 0 1")
            return "Cenário de promoção carregado."
        return "Comando desconhecido."
