from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pecas import Peca


@dataclass(slots=True)
class Casa:
    linha: int
    coluna: int
    peca: 'Peca | None' = None

    def esta_vazia(self) -> bool:
        return self.peca is None
