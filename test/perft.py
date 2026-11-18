"""PERFT: contador de folhas para validar a geração de lances legais."""
from core import Validador


def perft(tabuleiro, profundidade: int) -> int:
    if profundidade < 0:
        raise ValueError("Profundidade não pode ser negativa.")
    if profundidade == 0:
        return 1
    lances = Validador.movimentos_legais(tabuleiro)
    if profundidade == 1:
        return len(lances)
    total = 0
    for lance in lances:
        registro = tabuleiro.aplicar_movimento(lance)
        try:
            total += perft(tabuleiro, profundidade - 1)
        finally:
            tabuleiro.desfazer_movimento(registro)
    return total
