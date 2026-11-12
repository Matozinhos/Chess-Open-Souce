
def is_em_xeque(tabuleiro, cor) -> str | None:

        # So é possivel um rei estar em xeque por vez, então podemos retornar a (rei, peca ameaçando) 
        # em xeque ou None se nenhum estiver em xeque.
        
        rei_branco, rei_preto = tabuleiro.PECAS_BRANCAS[4], tabuleiro.PECAS_PRETAS[4]
        posicao_rei_branco = (rei_branco.linha, rei_branco.coluna)
        posicao_rei_preto = (rei_preto.linha, rei_preto.coluna)

        xeque : list[tuple] = None # indice 0 = rei | pecas que atacam o rei, len -1 para quantidade de pecas que atacam o rei
  
        if cor == 'preto':
            xeque = [rei_preto]
            for peca in tabuleiro.PECAS_BRANCAS:
                movimentos = peca.movimentos_validos(tabuleiro)
                if posicao_rei_preto in movimentos:
                    xeque.append(peca)
        else:
            xeque = [rei_branco]
            for peca in tabuleiro.PECAS_PRETAS:
                movimentos = peca.movimentos_validos(tabuleiro)
                if posicao_rei_branco in movimentos:
                    xeque.append(peca)

        if len(xeque) == 1: xeque = None

        return xeque
