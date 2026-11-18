import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from .modelos import Base

CAMINHO_BANCO = Path(__file__).resolve().parent.parent / "data" / "xadrez.db"
URL_PADRAO = f"sqlite:///{CAMINHO_BANCO.as_posix()}"


def criar_engine(url: str | None = None):
    url = url or os.getenv("DATABASE_URL", URL_PADRAO)

    if url.startswith("sqlite:///") and url != "sqlite:///:memory:":
        caminho = Path(url.removeprefix("sqlite:///"))
        if caminho.is_absolute():
            caminho.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(url, echo=False)

    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def habilitar_chaves_estrangeiras(conexao, _):
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

    return engine


_engine = None
_fabrica = None


def criar_tabelas(engine=None):
    global _engine, _fabrica
    if engine is None:
        _engine = _engine or criar_engine()
        engine = _engine
    Base.metadata.create_all(engine)
    if engine.dialect.name == "sqlite":
        with engine.begin() as conexao:
            colunas = {
                coluna[1] for coluna in conexao.exec_driver_sql("PRAGMA table_info(partidas)")
            }
            alteracoes = {
                "numero_lances": "INTEGER NOT NULL DEFAULT 0",
                "atualizada_em": "DATETIME",
                "encerrada_em": "DATETIME",
            }
            for coluna, definicao in alteracoes.items():
                if coluna not in colunas:
                    conexao.exec_driver_sql(
                        f"ALTER TABLE partidas ADD COLUMN {coluna} {definicao}"
                    )
            conexao.exec_driver_sql("""
                UPDATE partidas SET numero_lances = (
                    SELECT COUNT(*) FROM lances WHERE lances.partida_id = partidas.id
                )
                WHERE numero_lances != (
                    SELECT COUNT(*) FROM lances WHERE lances.partida_id = partidas.id
                )
            """)
            conexao.exec_driver_sql(
                "UPDATE partidas SET atualizada_em = criada_em WHERE atualizada_em IS NULL"
            )
    if engine is _engine:
        _fabrica = sessionmaker(bind=engine, expire_on_commit=False)
    return engine


def criar_sessao() -> Session:
    global _fabrica
    if _fabrica is None:
        criar_tabelas()
    return _fabrica()
