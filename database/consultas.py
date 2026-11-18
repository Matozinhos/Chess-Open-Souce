"""Três consultas ORM exigidas no trabalho de POO."""
from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from .conexao import criar_sessao, criar_tabelas
from .modelos import Jogador, Lance, Partida, participacoes


def consulta_1_partidas_por_jogador(sessao: Session):
    comando = (
        select(Jogador.nome, func.count(participacoes.c.partida_id).label("total"))
        .outerjoin(participacoes, participacoes.c.jogador_id == Jogador.id)
        .group_by(Jogador.id)
        .order_by(func.count(participacoes.c.partida_id).desc(), Jogador.nome)
    )
    return list(sessao.execute(comando).all())


def consulta_1_resumo_partidas(sessao: Session):
    comando = (
        select(
            Partida.id, Partida.status, Partida.numero_lances,
            Partida.vencedor_cor, Partida.resultado, Partida.motivo,
        )
        .order_by(Partida.id.desc())
    )
    return list(sessao.execute(comando).all())


def consulta_2_historico_de_lances(sessao: Session, partida_id: int):
    comando = (
        select(Lance.numero, Lance.san, Lance.uci)
        .where(Lance.partida_id == partida_id)
        .order_by(Lance.numero)
    )
    return list(sessao.execute(comando).all())


def consulta_3_vitorias_por_jogador(sessao: Session):
    ganhou = and_(
        Partida.status == "encerrada",
        Partida.vencedor_cor == participacoes.c.cor,
    )
    comando = (
        select(
            Jogador.nome,
            func.coalesce(func.sum(case((ganhou, 1), else_=0)), 0).label("vitorias"),
        )
        .outerjoin(participacoes, participacoes.c.jogador_id == Jogador.id)
        .outerjoin(Partida, Partida.id == participacoes.c.partida_id)
        .group_by(Jogador.id)
        .order_by(func.sum(case((ganhou, 1), else_=0)).desc(), Jogador.nome)
    )
    return list(sessao.execute(comando).all())


def relatorio(sessao: Session, partida_id: int | None = None) -> str:
    """
        Três consultas SELECT.

    1. Resumo de todas as partidas.
    2. Histórico da partida recente.
    3. Quantidade de vitórias por cor.
    """
    partidas = consulta_1_resumo_partidas(sessao)
    linhas = ["CONSULTA 1 — PARTIDAS, RESULTADOS E TOTAL DE LANCES", ""]
    if not partidas:
        linhas.append("Nenhuma partida cadastrada.")
    for id_, status, total, vencedor, resultado, motivo in partidas:
        linhas.append(
            f"#{id_:<4} {status:<13} {total:>3} lance(s)  "
            f"vencedor={vencedor or '-':<7}  resultado={resultado or '-':<7}"
            f"  motivo={motivo or '-'}"
        )

    if partida_id is None and partidas:
        partida_id = partidas[0][0]
    linhas += ["", f"CONSULTA 2 — HISTÓRICO DA PARTIDA #{partida_id or '-'}", ""]
    if partida_id is not None:
        historico = consulta_2_historico_de_lances(sessao, partida_id)
        linhas.extend(
            f"{numero:>3}. {san:<9} ({uci})" for numero, san, uci in historico
        )
        if not historico:
            linhas.append("Nenhum lance registrado nesta partida.")
    else:
        linhas.append("Nenhuma partida cadastrada.")

    linhas += ["", "CONSULTA 3 — VITÓRIAS POR JOGADOR", ""]
    linhas.extend(
        f"{nome:<20} {vitorias:>3} vitória(s)"
        for nome, vitorias in consulta_3_vitorias_por_jogador(sessao)
    )
    return "\n".join(linhas)


def main() -> None:
    criar_tabelas()
    with criar_sessao() as sessao:
        print(relatorio(sessao))


if __name__ == "__main__":
    main()
