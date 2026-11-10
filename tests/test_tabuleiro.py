from core import Tabuleiro

def test_mostrar_tabuleiro_inicial():
    a = Tabuleiro()
    a.montar_posicao_inicial()
    a.mover_peca(1, 0, 3, 0) 

    print("\n" + str(a))
