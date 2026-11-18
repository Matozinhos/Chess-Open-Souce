"""Verifica invariantes essenciais do tabuleiro (lista vazia significa OK)."""
from core import Tabuleiro


def verificar_invariantes(tabuleiro) -> list[str]:
    problemas = []
    encontradas = {"branco": 0, "preto": 0}
    for linha, casas in enumerate(tabuleiro.casas):
        for coluna, casa in enumerate(casas):
            peca = casa.peca
            if peca is None:
                continue
            if peca.posicao_atual() != (linha, coluna):
                problemas.append(f"Peça fora da posição: {linha}, {coluna}")
            if peca.letra == "k":
                encontradas[peca.cor] += 1
                if tabuleiro.reis.get(peca.cor) is not peca:
                    problemas.append(f"Referência incorreta ao rei {peca.cor}")
    for cor, quantidade in encontradas.items():
        if quantidade != 1:
            problemas.append(f"Deveria haver 1 rei {cor}; há {quantidade}")
    try:
        Tabuleiro(tabuleiro.para_fen())
    except ValueError as erro:
        problemas.append(f"FEN inválida: {erro}")
    return problemas
