"""API pública do motor de xadrez."""

from .casa import Casa
from .estado import EstadoPartida, MovimentoIlegal, PartidaEncerrada
from .jogo import Jogo
from .movimento import Movimento, RegistroMovimento
from .tabuleiro import FEN_INICIAL, Tabuleiro
from .validar import Validador

from .pecas import (
    Peca,
    Peao,
    Torre,
    Cavalo,
    Bispo,
    Rainha,
    Rei,
)

__all__ = [
    "Casa",
    "EstadoPartida",
    "MovimentoIlegal",
    "PartidaEncerrada",
    "Jogo",
    "Movimento",
    "RegistroMovimento",
    "FEN_INICIAL",
    "Tabuleiro",
    "Validador",
    "Peca",
    "Peao",
    "Torre",
    "Cavalo",
    "Bispo",
    "Rainha",
    "Rei",
]
