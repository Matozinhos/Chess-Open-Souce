from ..movimento import Movimento
from ..pecas import Rei, Torre
from .xeque import casa_atacada, em_xeque


def movimentos_roque(tabuleiro, rei: Rei) -> list[Movimento]:
    linha = 7 if rei.cor == 'branco' else 0
    if rei.posicao_atual() != (linha, 4) or em_xeque(tabuleiro, rei.cor):
        return []

    inimigo = 'preto' if rei.cor == 'branco' else 'branco'
    direitos = ('K', 'Q') if rei.cor == 'branco' else ('k', 'q')
    lances = []

    for direito, coluna_torre, coluna_rei, entre, caminho in (
        (direitos[0], 7, 6, (5, 6), (5, 6)),
        (direitos[1], 0, 2, (1, 2, 3), (3, 2)),
    ):
        if direito not in tabuleiro.direitos_roque:
            continue
        torre = tabuleiro.get_peca(linha, coluna_torre)
        if not isinstance(torre, Torre) or torre.cor != rei.cor:
            continue
        if any(tabuleiro.get_peca(linha, coluna) for coluna in entre):
            continue
        if any(casa_atacada(tabuleiro, linha, coluna, inimigo) for coluna in caminho):
            continue
        lances.append(Movimento((linha, 4), (linha, coluna_rei), roque=True))

    return lances
