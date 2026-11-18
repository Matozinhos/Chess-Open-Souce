from ..pecas._peca import DIAGONAIS, ORTOGONAIS, SALTOS_CAVALO


def casa_atacada(tabuleiro, linha: int, coluna: int, por_cor: str) -> bool:
    direcao = 1 if por_cor == 'branco' else -1
    origem_peao = linha + direcao

    for vizinha in (coluna - 1, coluna + 1):
        if tabuleiro.is_dentro_dos_limites(origem_peao, vizinha):
            peca = tabuleiro.get_peca(origem_peao, vizinha)
            if peca and peca.cor == por_cor and peca.letra == 'p':
                return True

    for dl, dc in SALTOS_CAVALO:
        l, c = linha + dl, coluna + dc
        if tabuleiro.is_dentro_dos_limites(l, c):
            peca = tabuleiro.get_peca(l, c)
            if peca and peca.cor == por_cor and peca.letra == 'n':
                return True

    for direcoes, pecas in ((ORTOGONAIS, ('r', 'q')), (DIAGONAIS, ('b', 'q'))):
        for dl, dc in direcoes:
            l, c, distancia = linha + dl, coluna + dc, 1
            while tabuleiro.is_dentro_dos_limites(l, c):
                peca = tabuleiro.get_peca(l, c)
                if peca:
                    if peca.cor == por_cor and (
                        peca.letra in pecas or (distancia == 1 and peca.letra == 'k')
                    ):
                        return True
                    break
                l += dl
                c += dc
                distancia += 1

    return False


def em_xeque(tabuleiro, cor: str) -> bool:
    rei = tabuleiro.reis[cor]
    adversario = 'preto' if cor == 'branco' else 'branco'
    return casa_atacada(tabuleiro, rei.linha, rei.coluna, adversario)
