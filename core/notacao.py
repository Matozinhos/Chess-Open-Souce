"""Notação UCI de entrada e SAN de histórico, sem alterar o tabuleiro."""
from .movimento import ARQUIVOS, PROMOCOES_UCI, coordenadas
from .pecas import Peao

LETRAS_SAN = {'k': 'K', 'q': 'Q', 'r': 'R', 'b': 'B', 'n': 'N', 'p': ''}


def ler_uci(texto: str) -> tuple[tuple[int, int], tuple[int, int], str | None]:
    texto = texto.strip()
    if len(texto) not in (4, 5):
        raise ValueError('Use notação UCI, como e2e4 ou a7a8q.')
    origem = coordenadas(texto[:2])
    destino = coordenadas(texto[2:4])
    promocao = None
    if len(texto) == 5:
        promocao = {v: k for k, v in PROMOCOES_UCI.items()}.get(texto[4])
        if promocao is None:
            raise ValueError('Sufixo de promoção UCI inválido.')
    return origem, destino, promocao


def san(tabuleiro, movimento, movimentos_legais) -> str:
    if movimento.roque:
        return 'O-O' if movimento.destino[1] > movimento.origem[1] else 'O-O-O'

    peca = tabuleiro.get_peca(*movimento.origem)
    origem, destino = movimento.origem, movimento.destino
    captura = movimento.en_passant or tabuleiro.get_peca(*destino) is not None
    nome = LETRAS_SAN[peca.letra]

    if isinstance(peca, Peao):
        prefixo = ARQUIVOS[origem[1]] if captura else ''
    else:
        outras = [m.origem for m in movimentos_legais
                  if m.origem != origem and m.destino == destino
                  and tabuleiro.get_peca(*m.origem).letra == peca.letra]
        prefixo = nome
        if outras:
            coluna_livre = all(o[1] != origem[1] for o in outras)
            linha_livre = all(o[0] != origem[0] for o in outras)
            if coluna_livre:
                prefixo += ARQUIVOS[origem[1]]
            elif linha_livre:
                prefixo += str(8 - origem[0])
            else:
                prefixo += ARQUIVOS[origem[1]] + str(8 - origem[0])

    from .movimento import algebraica
    resultado = prefixo + ('x' if captura else '') + algebraica(destino)
    if movimento.promocao:
        resultado += '=' + LETRAS_SAN[PROMOCOES_UCI[movimento.promocao]]
    return resultado
