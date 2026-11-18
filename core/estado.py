"""Status e erros públicos do domínio, sem dependências de interface."""
from dataclasses import dataclass


class MovimentoIlegal(ValueError):
    pass


class PartidaEncerrada(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class EstadoPartida:
    tipo: str
    terminado: bool
    turno: str
    vencedor: str | None = None
    motivo: str | None = None
    reivindicavel: tuple[str, ...] = ()
    em_xeque: bool = False
    ultimo_lance: str | None = None
    mensagem: str = ''

    def __getitem__(self, campo: str):
        return getattr(self, campo)
