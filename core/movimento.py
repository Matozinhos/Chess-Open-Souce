"""Um lance é imutável; seu registro guarda somente o necessário para desfazê-lo."""
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pecas import Peca

ARQUIVOS = 'abcdefgh'
PROMOCOES_UCI = {'Rainha': 'q', 'Torre': 'r', 'Bispo': 'b', 'Cavalo': 'n'}


def algebraica(pos: tuple[int, int]) -> str:
    linha, coluna = pos
    if not (0 <= linha < 8 and 0 <= coluna < 8):
        raise ValueError('Coordenadas fora do tabuleiro.')
    return f'{ARQUIVOS[coluna]}{8 - linha}'


def coordenadas(casa: str) -> tuple[int, int]:
    if len(casa) != 2 or casa[0] not in ARQUIVOS or casa[1] not in '12345678':
        raise ValueError('Casa algébrica inválida.')
    return 8 - int(casa[1]), ARQUIVOS.index(casa[0])


@dataclass(frozen=True, slots=True)
class Movimento:
    origem: tuple[int, int]
    destino: tuple[int, int]
    promocao: str | None = None
    roque: bool = False
    en_passant: bool = False

    @property
    def uci(self) -> str:
        sufixo = PROMOCOES_UCI.get(self.promocao, '')
        return algebraica(self.origem) + algebraica(self.destino) + sufixo


@dataclass(frozen=True, slots=True)
class RegistroMovimento:
    movimento: Movimento
    peca: 'Peca'
    capturada: 'Peca | None'
    casa_captura: tuple[int, int]
    torre: 'Peca | None'
    torre_origem: tuple[int, int] | None
    torre_destino: tuple[int, int] | None
    direitos_roque: frozenset[str]
    alvo_en_passant: tuple[int, int] | None
    meio_lances: int
    numero_lance: int
    turno: str
