"""Única entrada para gerar e validar movimentos legais."""
from .estado import MovimentoIlegal
from .pecas import Peao, Rei
from .validador import (
    deixa_rei_em_xeque,
    expandir_promocoes,
    movimentos_en_passant,
    movimentos_roque,
)


class Validador:
    @staticmethod
    def movimentos_candidatos_peca(tabuleiro, peca):
        if peca is None:
            return []

        lances = [lance for destino in peca.movimentos_possiveis(tabuleiro)
                  for lance in expandir_promocoes(peca, destino)]
        if isinstance(peca, Rei):
            lances.extend(movimentos_roque(tabuleiro, peca))
        elif isinstance(peca, Peao):
            lances.extend(movimentos_en_passant(tabuleiro, peca))
        return lances

    @staticmethod
    def movimentos_legais_peca(tabuleiro, peca):
        if peca is None or peca.cor != tabuleiro.turno:
            return []
        if tabuleiro.get_peca(*peca.posicao_atual()) is not peca:
            return []

        return [lance for lance in Validador.movimentos_candidatos_peca(tabuleiro, peca)
                if not deixa_rei_em_xeque(tabuleiro, lance, peca.cor)]

    @staticmethod
    def movimentos_legais(tabuleiro, cor=None):
        if cor is not None and cor != tabuleiro.turno:
            raise ValueError('A consulta deve respeitar o turno da posição.')
        return [lance
                for linha in tabuleiro.casas
                for casa in linha
                if casa.peca is not None and casa.peca.cor == tabuleiro.turno
                for lance in Validador.movimentos_legais_peca(tabuleiro, casa.peca)]

    @staticmethod
    def validar_movimento(peca, nova_linha, nova_coluna, tabuleiro, promocao=None, legais=None):
        if not tabuleiro.is_dentro_dos_limites(nova_linha, nova_coluna):
            raise MovimentoIlegal('Destino fora do tabuleiro.')
        if peca is None or peca.cor != tabuleiro.turno:
            raise MovimentoIlegal('Origem vazia ou peça da cor errada.')
        if tabuleiro.get_peca(*peca.posicao_atual()) is not peca:
            raise MovimentoIlegal('Peça não pertence à casa informada.')

        if legais is None:
            legais = Validador.movimentos_legais_peca(tabuleiro, peca)
        escolhas = [lance for lance in legais
                    if lance.origem == peca.posicao_atual()
                    and lance.destino == (nova_linha, nova_coluna)]
        if not escolhas:
            raise MovimentoIlegal('Movimento ilegal.')

        if any(lance.promocao for lance in escolhas):
            promocao = promocao or 'Rainha'
        elif promocao is not None:
            raise MovimentoIlegal('Esse lance não permite promoção.')

        for lance in escolhas:
            if lance.promocao == promocao:
                return lance
        raise MovimentoIlegal('Promoção inválida: Rainha, Torre, Bispo ou Cavalo.')

    @staticmethod
    def validar_enpassant(peao, tabuleiro):
        return bool(movimentos_en_passant(tabuleiro, peao))
