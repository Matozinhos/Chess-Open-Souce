from .pecas import Peca

from dataclasses import dataclass

@dataclass
class Casa:
    linha : int
    coluna : int 
    peca : Peca = None  

    def esta_vazia(self) -> bool:
        return self.peca is None
