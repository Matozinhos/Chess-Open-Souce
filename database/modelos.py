"""Quatro tabelas do DER, mapeadas com SQLAlchemy 2.x."""
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


# N:N: a cor do jogador pertence à participação, não ao cadastro.
participacoes = Table(
    "participacoes",
    Base.metadata,
    Column("partida_id", ForeignKey("partidas.id", ondelete="CASCADE"), primary_key=True),
    Column("jogador_id", ForeignKey("jogadores.id"), primary_key=True),
    Column("cor", String(6), nullable=False),
    UniqueConstraint("partida_id", "cor", name="uq_partida_cor"),
    CheckConstraint("cor IN ('branco', 'preto')", name="ck_participacao_cor"),
)


class Jogador(Base):
    __tablename__ = "jogadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    partidas: Mapped[list["Partida"]] = relationship(
        secondary=participacoes,
        back_populates="jogadores",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"Jogador(id={self.id}, nome={self.nome!r})"


class Partida(Base):
    __tablename__ = "partidas"
    __table_args__ = (
        CheckConstraint("status IN ('em_andamento', 'encerrada')", name="ck_status_partida"),
        CheckConstraint("vencedor_cor IS NULL OR vencedor_cor IN ('branco', 'preto')", name="ck_vencedor_cor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fen_inicial: Mapped[str] = mapped_column(String(100), nullable=False)
    fen_atual: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="em_andamento", nullable=False)
    resultado: Mapped[str | None] = mapped_column(String(7))
    vencedor_cor: Mapped[str | None] = mapped_column(String(6))
    motivo: Mapped[str | None] = mapped_column(String(80))
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    # Contador de meios-lances: 1.e4 e 1...e5 contam como dois lances.
    numero_lances: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    atualizada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=agora)
    encerrada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    jogadores: Mapped[list[Jogador]] = relationship(
        secondary=participacoes,
        back_populates="partidas",
        viewonly=True,
    )

    # 1:N: uma partida possui vários lances.
    lances: Mapped[list["Lance"]] = relationship(
        back_populates="partida",
        order_by="Lance.numero",
        cascade="all, delete-orphan",
    )


class Lance(Base):
    __tablename__ = "lances"
    __table_args__ = (
        UniqueConstraint("partida_id", "numero", name="uq_lance_numero"),
        CheckConstraint("numero > 0", name="ck_lance_numero"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    partida_id: Mapped[int] = mapped_column(
        ForeignKey("partidas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    uci: Mapped[str] = mapped_column(String(5), nullable=False)
    san: Mapped[str] = mapped_column(String(12), nullable=False)
    fen_apos: Mapped[str] = mapped_column(String(100), nullable=False)

    partida: Mapped[Partida] = relationship(back_populates="lances")
