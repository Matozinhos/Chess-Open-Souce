"""Partida local: jogadas, histórico, resultados e reivindicações."""
from collections import Counter
from dataclasses import replace

from .estado import EstadoPartida, MovimentoIlegal, PartidaEncerrada
from .notacao import ler_uci, san
from .tabuleiro import FEN_INICIAL, Tabuleiro
from .validar import Validador
from .validador import classificar_empates, em_xeque


class Jogo:
    def __init__(self, fen: str = FEN_INICIAL) -> None:
        self.tabuleiro = Tabuleiro(fen)
        self.historico = []
        self.notacoes: list[str] = []
        self.chaves: list[str] = [self.tabuleiro.chave_posicao()]
        self._contagem = Counter(self.chaves)
        self._resultado_administrativo: tuple[str, str | None, str] | None = None
        self._oferta_empate: str | None = None
        self._estado_cache: EstadoPartida | None = None

    @property
    def turno(self) -> str:
        return self.tabuleiro.turno

    def movimentos_legais(self, origem: tuple[int, int] | None = None):
        if self.estado().terminado:
            return []
        if origem is None:
            return Validador.movimentos_legais(self.tabuleiro)
        return Validador.movimentos_legais_peca(
            self.tabuleiro, self.tabuleiro.get_peca(*origem)
        )

    def jogar(self, linha_origem: int, coluna_origem: int,
              linha_destino: int, coluna_destino: int, promocao: str | None = None):
        if self.estado().terminado:
            raise PartidaEncerrada('A partida já terminou.')

        tabuleiro = self.tabuleiro
        peca = tabuleiro.get_peca(linha_origem, coluna_origem)
        legais = Validador.movimentos_legais(tabuleiro)
        lance = Validador.validar_movimento(
            peca, linha_destino, coluna_destino, tabuleiro, promocao, legais
        )
        notacao = san(tabuleiro, lance, legais)

        registro = tabuleiro.aplicar_movimento(lance)
        chave = tabuleiro.chave_posicao()
        self.historico.append(registro)
        self.chaves.append(chave)
        self._contagem[chave] += 1
        self._oferta_empate = None
        self._estado_cache = None

        estado = self.estado()
        notacao += '#' if estado.tipo == 'xeque_mate' else '+' if estado.em_xeque else ''
        self.notacoes.append(notacao)
        self._estado_cache = replace(estado, ultimo_lance=notacao)
        return lance

    def jogar_uci(self, texto: str):
        origem, destino, promocao = ler_uci(texto)
        return self.jogar(*origem, *destino, promocao)

    def desfazer(self) -> bool:
        if not self.historico:
            return False
        chave = self.chaves.pop()
        self._contagem[chave] -= 1
        if self._contagem[chave] == 0:
            del self._contagem[chave]
        self.tabuleiro.desfazer_movimento(self.historico.pop())
        self.notacoes.pop()
        self._resultado_administrativo = None
        self._oferta_empate = None
        self._estado_cache = None
        return True

    def reiniciar(self, fen: str = FEN_INICIAL) -> None:
        self.__init__(fen)

    def carregar_fen(self, fen: str) -> None:
        self.reiniciar(fen)

    def estado(self) -> EstadoPartida:
        if self._estado_cache:
            return self._estado_cache

        ultimo = self.notacoes[-1] if self.notacoes else None
        if self._resultado_administrativo:
            tipo, vencedor, motivo = self._resultado_administrativo
            estado = EstadoPartida(
                tipo, True, self.turno, vencedor, motivo,
                ultimo_lance=ultimo, mensagem=motivo,
            )
        else:
            check = em_xeque(self.tabuleiro, self.turno)
            tem_lances = bool(Validador.movimentos_legais(self.tabuleiro))
            if not tem_lances:
                tipo = 'xeque_mate' if check else 'afogamento'
                vencedor = ('preto' if self.turno == 'branco' else 'branco') if check else None
                estado = EstadoPartida(
                    tipo, True, self.turno, vencedor,
                    'xeque-mate' if check else 'afogamento',
                    em_xeque=check, ultimo_lance=ultimo, mensagem=tipo,
                )
            else:
                empate, reivindicavel, motivo = classificar_empates(
                    self.tabuleiro, self._contagem
                )
                estado = EstadoPartida(
                    empate or ('xeque' if check else 'em_andamento'),
                    bool(empate), self.turno, None, motivo,
                    reivindicavel, check, ultimo,
                    motivo or ('Xeque!' if check else 'Partida em andamento.'),
                )
        self._estado_cache = estado
        return estado

    def _exigir_ativa(self) -> None:
        if self.estado().terminado:
            raise PartidaEncerrada('A partida já terminou.')

    def reivindicar_empate(self, motivo: str | None = None,
                           lance_pretendido: str | None = None) -> EstadoPartida:
        self._exigir_ativa()
        opcoes = set(self.estado().reivindicavel)

        if lance_pretendido:
            origem, destino, promocao = ler_uci(lance_pretendido)
            peca = self.tabuleiro.get_peca(*origem)
            lance = Validador.validar_movimento(
                peca, *destino, self.tabuleiro, promocao
            )
            with self.tabuleiro.simular(lance):
                # Um xeque-mate prevalece sobre uma reivindicação antecipada.
                mate = em_xeque(self.tabuleiro, self.turno) and not Validador.movimentos_legais(self.tabuleiro)
                if not mate:
                    if self._contagem[self.tabuleiro.chave_posicao()] + 1 >= 3:
                        opcoes.add('três repetições')
                    if self.tabuleiro.meio_lances >= 100:
                        opcoes.add('50 lances')

        escolha = motivo or next((v for v in ('três repetições', '50 lances') if v in opcoes), None)
        if escolha not in opcoes:
            raise ValueError('Não há empate reivindicável nessas condições.')
        self._resultado_administrativo = ('empate_reivindicado', None, escolha)
        self._estado_cache = None
        return self.estado()

    def propor_empate(self, cor: str) -> None:
        self._exigir_ativa()
        self._validar_cor(cor)
        self._oferta_empate = cor

    def aceitar_empate(self, cor: str) -> EstadoPartida:
        self._exigir_ativa()
        self._validar_cor(cor)
        if self._oferta_empate is None or cor == self._oferta_empate:
            raise ValueError('Não há proposta de empate do adversário.')
        self._resultado_administrativo = ('empate_acordo', None, 'Empate por acordo.')
        self._oferta_empate = None
        self._estado_cache = None
        return self.estado()

    def recusar_empate(self, cor: str) -> None:
        self._exigir_ativa()
        self._validar_cor(cor)
        if self._oferta_empate is None or cor == self._oferta_empate:
            raise ValueError('Não há proposta de empate do adversário.')
        self._oferta_empate = None

    def desistir(self, cor: str) -> EstadoPartida:
        self._exigir_ativa()
        self._validar_cor(cor)
        vencedor = 'preto' if cor == 'branco' else 'branco'
        self._resultado_administrativo = ('desistencia', vencedor, f'Desistência: {cor}.')
        self._oferta_empate = None
        self._estado_cache = None
        return self.estado()

    @staticmethod
    def _validar_cor(cor: str) -> None:
        if cor not in ('branco', 'preto'):
            raise ValueError('Cor inválida.')
