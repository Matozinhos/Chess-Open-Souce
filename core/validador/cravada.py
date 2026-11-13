
from ..pecas import Peao, Torre, Cavalo, Bispo, Rainha, Rei , Peca
from ..tabuleiro import Tabuleiro

from .xeque import is_em_xeque

def is_cravada(tabuleiro : Tabuleiro, peca : Peca, destino_linha, destino_coluna) -> bool:

    peca_destino = tabuleiro[destino_linha][destino_coluna]

    tabuleiro.test_mover_peca(peca.linha, peca.coluna, destino_linha, destino_coluna)

    xeque = is_em_xeque(tabuleiro, peca.cor)
    
    tabuleiro.test_mover_peca( destino_linha, destino_coluna, peca.linha, peca.coluna)
    tabuleiro[destino_linha][destino_coluna].peca = peca_destino

    if xeque != None:
        xeque = linha_de_cravada(xeque, tabuleiro)

    return xeque

def linha_de_cravada(xeque : list, tabuleiro):
    # ISSO COM A PECA JA CRAVADA
    # def para encontrar o caminho da peca que deverá dar xeque no rei, mas cravando outra peca
    if xeque >= 3: 
        return [] # Caso o xeque seja duplo nao tem oq fazer, a peca cravada esta cravada
    else:

        rei : Rei = xeque[0]
        peca = xeque[1]

        # DEFINIR DELTA DE MOVIMENTO | CALCULAR A PARTIR DA POSICAO DA PECA
        
        if rei.linha > peca.linha: dx = 1
        elif rei.linha < peca.linha: dx = -1
        else: dx = 0

        if rei.coluna > peca.coluna: dy = 1
        elif rei.coluna < peca.coluna: dy = -1
        else: dy = 0

        pos = peca.posicao_atual()
        MOVIMENTOS = [pos]
        
        while(pos != rei.posicao_atual()):
            pos = (pos[0] + dx, pos[1] + dy)
            MOVIMENTOS.append(pos)

        return MOVIMENTOS


        # ESSA É A MATRIZ, LINHA|COLUNA
            # 00 01 02 03 04 05 06 07
            # 10 11 12 13 14 15 16 17
            # 20 21 22 23 24 25 26 27
            # 30 31 32 33 34 35 36 37
            # 40 41 42 43 44 45 46 47
            # 50 51 52 53 54 55 56 57
            # 60 61 62 63 64 65 66 67
            # 70 71 72 73 74 75 76 77