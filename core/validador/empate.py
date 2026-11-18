from collections import Counter


def posicao_morta(tabuleiro) -> bool:
    outras = [c.peca for linha in tabuleiro.casas for c in linha
              if c.peca and c.peca.letra != 'k']
    if not outras:
        return True
    if len(outras) == 1 and outras[0].letra in ('b', 'n'):
        return True
    if all(p.letra == 'b' for p in outras):
        return len({(p.linha + p.coluna) % 2 for p in outras}) == 1
    return False


def classificar_empates(tabuleiro, chaves: Counter | dict) -> tuple[str | None, tuple[str, ...], str | None]:
    if posicao_morta(tabuleiro):
        return 'empate_material', (), 'posição morta'

    repeticoes = chaves.get(tabuleiro.chave_posicao(), 0)
    if repeticoes >= 5:
        return 'empate_automatico', (), 'cinco repetições'
    if tabuleiro.meio_lances >= 150:
        return 'empate_automatico', (), '75 lances'

    reivindicaveis = []
    if repeticoes >= 3:
        reivindicaveis.append('três repetições')
    if tabuleiro.meio_lances >= 100:
        reivindicaveis.append('50 lances')
    return None, tuple(reivindicaveis), None
