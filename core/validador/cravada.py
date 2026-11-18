from .xeque import em_xeque


def deixa_rei_em_xeque(tabuleiro, movimento, cor: str) -> bool:
    with tabuleiro.simular(movimento):
        return em_xeque(tabuleiro, cor)
