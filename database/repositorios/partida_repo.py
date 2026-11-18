from sqlalchemy import insert, select
from sqlalchemy.orm import Session, selectinload

from core import FEN_INICIAL
from database.modelos import Jogador, Partida, participacoes


def criar_partida(sessao: Session, branco_id: int, preto_id: int) -> Partida:
    if branco_id == preto_id:
        raise ValueError("Escolha dois jogadores diferentes.")

    encontrados = set(sessao.scalars(
        select(Jogador.id).where(Jogador.id.in_([branco_id, preto_id]))
    ))
    if encontrados != {branco_id, preto_id}:
        raise ValueError("Um dos jogadores não está cadastrado.")

    partida = Partida(fen_inicial=FEN_INICIAL, fen_atual=FEN_INICIAL)
    sessao.add(partida)
    sessao.flush()
    sessao.execute(insert(participacoes), [
        {"partida_id": partida.id, "jogador_id": branco_id, "cor": "branco"},
        {"partida_id": partida.id, "jogador_id": preto_id, "cor": "preto"},
    ])
    sessao.commit()
    return partida


def abrir_partida(sessao: Session, partida_id: int) -> Partida:
    partida = sessao.scalar(
        select(Partida)
        .options(selectinload(Partida.lances))
        .where(Partida.id == partida_id)
    )
    if partida is None:
        raise ValueError("Partida não encontrada.")
    return partida


def listar_partidas(sessao: Session) -> list[Partida]:
    return list(sessao.scalars(select(Partida).order_by(Partida.id.desc())))


def participantes(sessao: Session, partida_id: int) -> dict[str, Jogador]:
    linhas = sessao.execute(
        select(participacoes.c.cor, Jogador)
        .join(Jogador, Jogador.id == participacoes.c.jogador_id)
        .where(participacoes.c.partida_id == partida_id)
    )
    return {cor: jogador for cor, jogador in linhas}
