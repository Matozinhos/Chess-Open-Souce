"""Conecta o motor de xadrez ao banco, sem colocar SQL no core."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from core import Jogo
from database.modelos import Lance, Partida, agora
from database.repositorios import (
    abrir_partida,
    criar_partida,
    listar_partidas,
)
from database.repositorios.partida_repo import participantes
from database.repositorios.jogador_repo import obter_ou_cadastrar_jogador


class ServicoPartida:
    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.partida_id: int | None = None
        self.jogo: Jogo | None = None

    def listar(self):
        return listar_partidas(self.sessao)

    def criar(self, branco_id: int, preto_id: int):
        partida = criar_partida(self.sessao, branco_id, preto_id)
        return self.abrir(partida.id)

    def criar_com_nomes(self, branco: str = "Jogador 1", preto: str = "Jogador 2"):
        """Inicia uma partida sem exigir formulários ou IDs na interface."""
        if branco.strip() == preto.strip():
            raise ValueError("Os dois jogadores precisam de nomes diferentes.")
        jogador_branco = obter_ou_cadastrar_jogador(self.sessao, branco)
        jogador_preto = obter_ou_cadastrar_jogador(self.sessao, preto)
        return self.criar(jogador_branco.id, jogador_preto.id)

    def retomar_ultima(self):
        """Reabre a partida em andamento mais recente, caso exista."""
        partida_id = self.sessao.scalar(
            select(Partida.id)
            .where(Partida.status == "em_andamento")
            .order_by(Partida.id.desc())
            .limit(1)
        )
        return self.abrir(partida_id) if partida_id is not None else None

    def abrir(self, partida_id: int):
        partida = abrir_partida(self.sessao, partida_id)
        jogo = Jogo(partida.fen_inicial)

        for lance in partida.lances:
            jogo.jogar_uci(lance.uci)

        if jogo.tabuleiro.para_fen() != partida.fen_atual:
            raise ValueError("O histórico salvo não corresponde à posição FEN.")

        if partida.status == "encerrada" and not jogo.estado().terminado:
            if partida.motivo == "desistencia":
                desistente = "preto" if partida.vencedor_cor == "branco" else "branco"
                jogo.desistir(desistente)
            elif partida.motivo == "acordo":
                jogo.propor_empate("branco")
                jogo.aceitar_empate("preto")
            elif partida.motivo == "empate_reivindicado":
                jogo.reivindicar_empate()

        self.partida_id = partida.id
        self.jogo = jogo
        return partida

    def nomes(self) -> dict[str, str]:
        self._exigir()
        return {cor: jogador.nome for cor, jogador in participantes(self.sessao, self.partida_id).items()}

    def jogar(self, origem: tuple[int, int], destino: tuple[int, int], promocao: str | None = None):
        self._exigir()
        movimento = self.jogo.jogar(*origem, *destino, promocao)
        partida = abrir_partida(self.sessao, self.partida_id)

        partida.lances.append(Lance(
            numero=len(self.jogo.historico),
            uci=movimento.uci,
            san=self.jogo.notacoes[-1],
            fen_apos=self.jogo.tabuleiro.para_fen(),
        ))
        self._atualizar_partida(partida)
        self._salvar()
        return movimento

    def jogar_uci(self, texto: str):
        from core.movimento import coordenadas
        if len(texto) not in (4, 5):
            raise ValueError("UCI deve ter 4 ou 5 caracteres.")
        origem = coordenadas(texto[:2])
        destino = coordenadas(texto[2:4])
        promocao = {"q": "Rainha", "r": "Torre", "b": "Bispo", "n": "Cavalo"}.get(texto[4:])
        if len(texto) == 5 and promocao is None:
            raise ValueError("Promoção inválida.")
        return self.jogar(origem, destino, promocao)

    def desfazer(self) -> bool:
        self._exigir()
        partida = abrir_partida(self.sessao, self.partida_id)
        if not partida.lances:
            return False
        if partida.motivo in ("desistencia", "acordo", "empate_reivindicado"):
            raise ValueError("Uma partida encerrada por acordo/desistência não pode ser desfeita.")

        partida.lances.pop()
        self.jogo.desfazer()
        self._atualizar_partida(partida)
        self._salvar()
        return True

    def reivindicar_empate(self, motivo: str | None = None):
        self._exigir()
        estado = self.jogo.reivindicar_empate(motivo)
        partida = abrir_partida(self.sessao, self.partida_id)
        self._atualizar_partida(partida, motivo="empate_reivindicado")
        self._salvar()
        return estado

    def desistir(self, cor: str):
        self._exigir()
        estado = self.jogo.desistir(cor)
        partida = abrir_partida(self.sessao, self.partida_id)
        self._atualizar_partida(partida, motivo="desistencia")
        self._salvar()
        return estado

    def empatar_por_acordo(self):
        self._exigir()
        self.jogo.propor_empate("branco")
        estado = self.jogo.aceitar_empate("preto")
        partida = abrir_partida(self.sessao, self.partida_id)
        self._atualizar_partida(partida, motivo="acordo")
        self._salvar()
        return estado

    def _atualizar_partida(self, partida, motivo: str | None = None):
        estado = self.jogo.estado()
        partida.fen_atual = self.jogo.tabuleiro.para_fen()
        partida.numero_lances = len(self.jogo.historico)
        partida.atualizada_em = agora()
        partida.status = "encerrada" if estado.terminado else "em_andamento"
        partida.encerrada_em = agora() if estado.terminado else None
        partida.vencedor_cor = estado.vencedor
        partida.resultado = (
            "1-0" if estado.vencedor == "branco"
            else "0-1" if estado.vencedor == "preto"
            else "1/2-1/2" if estado.terminado else None
        )
        partida.motivo = motivo or (estado.tipo if estado.terminado else None)

    def _salvar(self):
        try:
            self.sessao.commit()
        except Exception:
            self.sessao.rollback()
            self.abrir(self.partida_id)
            raise

    def _exigir(self):
        if self.jogo is None or self.partida_id is None:
            raise ValueError("Inicie ou abra uma partida.")
