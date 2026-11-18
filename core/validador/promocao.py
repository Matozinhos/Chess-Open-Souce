from ..movimento import Movimento, PROMOCOES_UCI
from ..pecas import Peao


def expandir_promocoes(peca, destino: tuple[int, int]) -> list[Movimento]:
    if isinstance(peca, Peao) and destino[0] == (0 if peca.cor == 'branco' else 7):
        return [Movimento(peca.posicao_atual(), destino, promocao=tipo)
                for tipo in PROMOCOES_UCI]
    return [Movimento(peca.posicao_atual(), destino)]
