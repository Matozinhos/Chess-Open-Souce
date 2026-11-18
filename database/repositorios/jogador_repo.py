from sqlalchemy import select
from sqlalchemy.orm import Session

from database.modelos import Jogador


def listar_jogadores(sessao: Session) -> list[Jogador]:
    return list(sessao.scalars(select(Jogador).order_by(Jogador.nome)))


def cadastrar_jogador(sessao: Session, nome: str) -> Jogador:
    nome = " ".join(nome.strip().split())
    if not 2 <= len(nome) <= 40:
        raise ValueError("O nome deve conter de 2 a 40 caracteres.")
    if sessao.scalar(select(Jogador.id).where(Jogador.nome == nome)) is not None:
        raise ValueError("Já existe um jogador com esse nome.")

    jogador = Jogador(nome=nome)
    sessao.add(jogador)
    sessao.commit()
    return jogador


def obter_ou_cadastrar_jogador(sessao: Session, nome: str) -> Jogador:
    nome = " ".join(nome.strip().split())
    if not 2 <= len(nome) <= 40:
        raise ValueError("O nome deve conter de 2 a 40 caracteres.")
    jogador = sessao.scalar(select(Jogador).where(Jogador.nome == nome))
    return jogador if jogador is not None else cadastrar_jogador(sessao, nome)
