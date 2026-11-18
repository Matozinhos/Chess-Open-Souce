"""Formatador opcional para console; nenhuma peça depende deste módulo."""

SIMBOLOS = {
    ('k', 'branco'): '♔', ('q', 'branco'): '♕', ('r', 'branco'): '♖',
    ('b', 'branco'): '♗', ('n', 'branco'): '♘', ('p', 'branco'): '♙',
    ('k', 'preto'): '♚', ('q', 'preto'): '♛', ('r', 'preto'): '♜',
    ('b', 'preto'): '♝', ('n', 'preto'): '♞', ('p', 'preto'): '♟',
}


def formatar_tabuleiro(tabuleiro, inverter_linhas: bool = False) -> str:
    linhas = range(7, -1, -1) if inverter_linhas else range(8)
    return '\n'.join(' '.join(
        SIMBOLOS[peca.letra, peca.cor] if (peca := tabuleiro.get_peca(l, c)) else '·'
        for c in range(8)
    ) for l in linhas)
