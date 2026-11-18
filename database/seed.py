"""Popula o banco com jogadores, partidas e lances demonstrativos."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.conexao import criar_sessao, criar_tabelas
from database.modelos import Jogador
from servicos.partida_servico import ServicoPartida


DADOS_JOGADORES = ("Alice", "Breno", "Carla", "Diego", "Elisa", "Nicolas")


def popular_banco(sessao: Session) -> bool:
    """Insere exemplos uma única vez. Não altera um banco já utilizado."""
    if sessao.scalar(select(func.count()).select_from(Jogador)):
        return False

    jogadores = {nome: Jogador(nome=nome) for nome in DADOS_JOGADORES}
    sessao.add_all(jogadores.values())
    sessao.commit()
    servico = ServicoPartida(sessao)

    def partida(branco: str, preto: str, lances: str, desfecho: str = ""):
        servico.criar(jogadores[branco].id, jogadores[preto].id)
        for uci in lances.split():
            servico.jogar_uci(uci)
        if desfecho == "acordo":
            servico.empatar_por_acordo()

    # Dois xeques-mates, um empate acordado e uma partida aberta.
    partida("Alice", "Breno", "e2e4 e7e5 d1h5 b8c6 f1c4 g8f6 h5f7")
    partida("Carla", "Diego", "f2f3 e7e5 g2g4 d8h4")
    partida("Carla", "Elisa", "d2d4 d7d5 c2c4 e7e6", "acordo")
    partida("Nicolas", "Alice", "e2e4 c7c5 g1f3 d7d6")
    return True


def main():
    criar_tabelas()
    with criar_sessao() as sessao:
        if popular_banco(sessao):
            print("Banco populado: 6 jogadores, 4 partidas e lances de exemplo.")
        else:
            print("Banco já contém jogadores; nenhum dado foi substituído.")


if __name__ == "__main__":
    main()
