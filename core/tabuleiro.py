"""Estado canônico da posição e execução reversível de lances."""
from contextlib import contextmanager

from .casa import Casa
from .movimento import Movimento, RegistroMovimento, algebraica, coordenadas
from .pecas import Bispo, Cavalo, Peao, Rainha, Rei, Torre

FEN_INICIAL = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
CLASSES = {'r': Torre, 'n': Cavalo, 'b': Bispo, 'q': Rainha, 'k': Rei, 'p': Peao}
PROMOCOES = {'Rainha': Rainha, 'Torre': Torre, 'Bispo': Bispo, 'Cavalo': Cavalo}
TORRES_ROQUE = {(7, 7): 'K', (7, 0): 'Q', (0, 7): 'k', (0, 0): 'q'}


class Tabuleiro:
    algebraica = staticmethod(algebraica)
    coordenadas = staticmethod(coordenadas)

    def __init__(self, fen: str = FEN_INICIAL) -> None:
        self.casas = [[Casa(linha, coluna) for coluna in range(8)] for linha in range(8)]
        self.reis: dict[str, Rei] = {}
        self.turno = 'branco'
        self.direitos_roque: set[str] = set()
        self.alvo_en_passant: tuple[int, int] | None = None
        self.meio_lances = 0
        self.numero_lance = 1
        self.carregar_fen(fen)

    @classmethod
    def from_fen(cls, fen: str) -> 'Tabuleiro':
        return cls(fen)

    @staticmethod
    def is_dentro_dos_limites(linha: int, coluna: int) -> bool:
        return 0 <= linha < 8 and 0 <= coluna < 8

    def __getitem__(self, linha: int) -> list[Casa]:
        if not 0 <= linha < 8:
            raise IndexError('Linha fora do tabuleiro.')
        return self.casas[linha]

    def get_casa(self, linha: int, coluna: int) -> Casa:
        if not self.is_dentro_dos_limites(linha, coluna):
            raise IndexError('Casa fora do tabuleiro.')
        return self.casas[linha][coluna]

    def get_peca(self, linha: int, coluna: int):
        return self.get_casa(linha, coluna).peca

    @property
    def PECAS_BRANCAS(self) -> list:
        return [c.peca for linha in self.casas for c in linha
                if c.peca and c.peca.cor == 'branco']

    @property
    def PECAS_PRETAS(self) -> list:
        return [c.peca for linha in self.casas for c in linha
                if c.peca and c.peca.cor == 'preto']

    def montar_posicao_inicial(self) -> None:
        self.carregar_fen(FEN_INICIAL)

    def carregar_fen(self, fen: str) -> None:
        campos = fen.split()
        if len(campos) != 6:
            raise ValueError('FEN deve conter exatamente seis campos.')

        disposicao, lado, roques, ep, meio_texto, lance_texto = campos
        if lado not in ('w', 'b'):
            raise ValueError('Turno inválido na FEN.')
        if roques != '-' and (set(roques) - set('KQkq') or len(set(roques)) != len(roques)):
            raise ValueError('Direitos de roque inválidos.')

        linhas = disposicao.split('/')
        if len(linhas) != 8:
            raise ValueError('FEN deve conter oito fileiras.')

        grade = [[None] * 8 for _ in range(8)]
        reis = {}
        for linha, texto in enumerate(linhas):
            coluna = 0
            for caractere in texto:
                if caractere in '12345678':
                    coluna += int(caractere)
                    continue
                classe = CLASSES.get(caractere.lower())
                if classe is None or coluna >= 8:
                    raise ValueError('Peça ou fileira inválida na FEN.')
                if caractere.lower() == 'p' and linha in (0, 7):
                    raise ValueError('Peão não pode ocupar a última fileira.')
                cor = 'branco' if caractere.isupper() else 'preto'
                peca = classe(cor, linha, coluna)
                grade[linha][coluna] = peca
                if isinstance(peca, Rei):
                    if cor in reis:
                        raise ValueError('FEN contém dois reis da mesma cor.')
                    reis[cor] = peca
                coluna += 1
            if coluna != 8:
                raise ValueError('Fileira da FEN não possui oito casas.')

        if set(reis) != {'branco', 'preto'}:
            raise ValueError('FEN exige um rei por cor.')

        if not meio_texto.isascii() or not meio_texto.isdecimal():
            raise ValueError('Contador de meio-lances inválido.')
        if not lance_texto.isascii() or not lance_texto.isdecimal():
            raise ValueError('Número de lance inválido.')
        meio, numero = int(meio_texto), int(lance_texto)
        if numero < 1:
            raise ValueError('Número de lance deve ser positivo.')

        alvo_ep = None
        if ep != '-':
            alvo_ep = coordenadas(ep)
            linha, coluna = alvo_ep
            if linha != (2 if lado == 'w' else 5):
                raise ValueError('Alvo en passant incompatível com turno.')
            linha_peao = linha + (1 if lado == 'w' else -1)
            peao = grade[linha_peao][coluna]
            esperado = 'preto' if lado == 'w' else 'branco'
            if not isinstance(peao, Peao) or peao.cor != esperado or grade[linha][coluna]:
                raise ValueError('En passant não corresponde a avanço duplo.')

        for direito in roques if roques != '-' else '':
            linha = 7 if direito.isupper() else 0
            coluna = 7 if direito.lower() == 'k' else 0
            rei, torre = grade[linha][4], grade[linha][coluna]
            cor = 'branco' if direito.isupper() else 'preto'
            if (not isinstance(rei, Rei) or rei.cor != cor
                    or not isinstance(torre, Torre) or torre.cor != cor):
                raise ValueError('Direito de roque sem rei/torre na casa original.')

        for linha in range(8):
            for coluna in range(8):
                self.casas[linha][coluna].peca = grade[linha][coluna]
        self.reis = reis
        self.turno = 'branco' if lado == 'w' else 'preto'
        self.direitos_roque = set() if roques == '-' else set(roques)
        self.alvo_en_passant = alvo_ep
        self.meio_lances = meio
        self.numero_lance = numero

    def para_fen(self) -> str:
        linhas = []
        for linha in self.casas:
            texto, vazias = '', 0
            for casa in linha:
                peca = casa.peca
                if peca is None:
                    vazias += 1
                    continue
                if vazias:
                    texto += str(vazias)
                    vazias = 0
                texto += peca.letra.upper() if peca.cor == 'branco' else peca.letra
            linhas.append(texto + (str(vazias) if vazias else ''))
        roques = ''.join(d for d in 'KQkq' if d in self.direitos_roque) or '-'
        ep = algebraica(self.alvo_en_passant) if self.alvo_en_passant else '-'
        lado = 'w' if self.turno == 'branco' else 'b'
        return f"{'/'.join(linhas)} {lado} {roques} {ep} {self.meio_lances} {self.numero_lance}"

    def chave_posicao(self) -> str:
        campos = self.para_fen().split()
        if self.alvo_en_passant:
            from .validador.enpassant import movimentos_en_passant
            from .validador.cravada import deixa_rei_em_xeque

            linha, coluna = self.alvo_en_passant
            linha_origem = linha + (1 if self.turno == 'branco' else -1)
            capturavel = False
            for vizinha in (coluna - 1, coluna + 1):
                if not 0 <= vizinha < 8:
                    continue
                peao = self.get_peca(linha_origem, vizinha)
                if isinstance(peao, Peao) and peao.cor == self.turno:
                    capturavel |= any(
                        not deixa_rei_em_xeque(self, lance, self.turno)
                        for lance in movimentos_en_passant(self, peao)
                    )
            if not capturavel:
                campos[3] = '-'
        return ' '.join(campos[:4])

    def aplicar_movimento(self, movimento: Movimento) -> RegistroMovimento:
        lo, co = movimento.origem
        ld, cd = movimento.destino
        peca = self.get_peca(lo, co)
        if peca is None:
            raise ValueError('Origem sem peça.')
        if peca.cor != self.turno:
            raise ValueError('Peça não pertence ao turno.')
        if movimento.promocao and (
            not isinstance(peca, Peao) or movimento.promocao not in PROMOCOES
            or ld != (0 if peca.cor == 'branco' else 7)
        ):
            raise ValueError('Promoção inválida.')
        if movimento.en_passant and (not isinstance(peca, Peao)
                                     or movimento.destino != self.alvo_en_passant):
            raise ValueError('En passant inválido.')
        if movimento.roque and not isinstance(peca, Rei):
            raise ValueError('Roque exige rei.')

        casa_captura = (lo, cd) if movimento.en_passant else (ld, cd)
        capturada = self.get_peca(*casa_captura)
        if capturada and (capturada.cor == peca.cor or isinstance(capturada, Rei)):
            raise ValueError('Captura de peça aliada ou rei não é permitida.')
        if movimento.en_passant and (
            not isinstance(capturada, Peao) or capturada.cor == peca.cor
            or self.get_peca(ld, cd) is not None
        ):
            raise ValueError('Captura en passant inválida.')

        torre = None
        origem_torre = destino_torre = None
        if movimento.roque:
            origem_torre = (lo, 7 if cd > co else 0)
            destino_torre = (lo, 5 if cd > co else 3)
            torre = self.get_peca(*origem_torre)
            if (not isinstance(torre, Torre) or torre.cor != peca.cor
                    or self.get_peca(ld, cd) is not None
                    or self.get_peca(*destino_torre) is not None):
                raise ValueError('Roque sem torre ou com casas ocupadas.')

        registro = RegistroMovimento(
            movimento, peca, capturada, casa_captura, torre,
            origem_torre, destino_torre, frozenset(self.direitos_roque),
            self.alvo_en_passant, self.meio_lances, self.numero_lance, self.turno,
        )

        self.casas[lo][co].peca = None
        self.casas[casa_captura[0]][casa_captura[1]].peca = None
        self.casas[ld][cd].peca = peca
        peca.mover_para(ld, cd)
        if torre:
            self.casas[origem_torre[0]][origem_torre[1]].peca = None
            self.casas[destino_torre[0]][destino_torre[1]].peca = torre
            torre.mover_para(*destino_torre)
        if movimento.promocao:
            self.casas[ld][cd].peca = PROMOCOES[movimento.promocao](peca.cor, ld, cd)

        if isinstance(peca, Rei):
            self.direitos_roque.difference_update(('K', 'Q') if peca.cor == 'branco' else ('k', 'q'))
        if isinstance(peca, Torre):
            self.direitos_roque.discard(TORRES_ROQUE.get((lo, co)))
        if isinstance(capturada, Torre):
            self.direitos_roque.discard(TORRES_ROQUE.get(casa_captura))

        self.alvo_en_passant = (
            ((lo + ld) // 2, co)
            if isinstance(peca, Peao) and abs(ld - lo) == 2 else None
        )
        self.meio_lances = 0 if isinstance(peca, Peao) or capturada else self.meio_lances + 1
        if self.turno == 'preto':
            self.numero_lance += 1
        self.turno = 'preto' if self.turno == 'branco' else 'branco'
        return registro

    def desfazer_movimento(self, registro: RegistroMovimento) -> None:
        lance = registro.movimento
        lo, co = lance.origem
        ld, cd = lance.destino
        self.casas[ld][cd].peca = None
        self.casas[lo][co].peca = registro.peca
        registro.peca.mover_para(lo, co)

        if registro.capturada:
            lc, cc = registro.casa_captura
            self.casas[lc][cc].peca = registro.capturada
        if registro.torre:
            lt, ct = registro.torre_origem
            lf, cf = registro.torre_destino
            self.casas[lf][cf].peca = None
            self.casas[lt][ct].peca = registro.torre
            registro.torre.mover_para(lt, ct)

        self.direitos_roque = set(registro.direitos_roque)
        self.alvo_en_passant = registro.alvo_en_passant
        self.meio_lances = registro.meio_lances
        self.numero_lance = registro.numero_lance
        self.turno = registro.turno

    @contextmanager
    def simular(self, movimento: Movimento):
        registro = self.aplicar_movimento(movimento)
        try:
            yield
        finally:
            self.desfazer_movimento(registro)

    def print_tabuleiro(self, cor: str = 'branco') -> str:
        if cor not in ('branco', 'preto'):
            raise ValueError('Cor inválida.')
        linhas = range(8) if cor == 'branco' else range(7, -1, -1)
        return '\n'.join(' '.join(
            casa.peca.letra.upper() if casa.peca and casa.peca.cor == 'branco'
            else casa.peca.letra if casa.peca else '.'
            for casa in self.casas[linha]
        ) for linha in linhas)
