"""Testes de integração ORM, relacionamentos e persistência."""
import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from core import FEN_INICIAL
from database.conexao import criar_engine, criar_tabelas
from database.consultas import (
    consulta_1_partidas_por_jogador,
    consulta_2_historico_de_lances,
    consulta_3_vitorias_por_jogador,
)
from database.modelos import Jogador, Lance, Partida, participacoes
from database.repositorios import cadastrar_jogador
from database.seed import popular_banco
from servicos import ServicoPartida


@pytest.fixture
def sessao(tmp_path):
    engine = criar_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    criar_tabelas(engine)
    fabrica = sessionmaker(bind=engine, expire_on_commit=False)
    with fabrica() as sessao:
        yield sessao
    engine.dispose()


def jogadores(sessao):
    return (cadastrar_jogador(sessao, "Maria"), cadastrar_jogador(sessao, "João"))


def test_modelo_tem_quatro_tabelas(sessao):
    from database.modelos import Base
    assert set(Base.metadata.tables) == {"jogadores", "partidas", "participacoes", "lances"}


def test_relacao_muitos_para_muitos(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    partida = servico.criar(branco.id, preto.id)
    assert {j.nome for j in partida.jogadores} == {"Maria", "João"}
    sessao.expire_all()
    assert sessao.get(Jogador, branco.id).partidas[0].id == partida.id


def test_relacao_um_para_muitos(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    partida = servico.criar(branco.id, preto.id)
    servico.jogar_uci("e2e4")
    servico.jogar_uci("e7e5")
    sessao.expire_all()
    assert [l.uci for l in sessao.get(Partida, partida.id).lances] == ["e2e4", "e7e5"]


def test_reabrir_partida_recupera_posicao_e_turno(sessao):
    branco, preto = jogadores(sessao)
    partida = ServicoPartida(sessao).criar(branco.id, preto.id)
    s1 = ServicoPartida(sessao)
    s1.abrir(partida.id)
    s1.jogar_uci("e2e4")
    s1.jogar_uci("e7e5")
    s2 = ServicoPartida(sessao)
    s2.abrir(partida.id)
    assert s2.jogo.turno == "branco"
    assert s2.jogo.tabuleiro.para_fen() == s1.jogo.tabuleiro.para_fen()
    assert s2.jogo.notacoes == ["e4", "e5"]


def test_desfazer_muda_tabuleiro_e_banco(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    partida = servico.criar(branco.id, preto.id)
    servico.jogar_uci("e2e4")
    assert servico.desfazer()
    assert servico.jogo.tabuleiro.para_fen() == FEN_INICIAL
    assert sessao.scalar(select(func.count()).select_from(Lance)) == 0
    ServicoPartida(sessao).abrir(partida.id)


def test_erro_de_movimento_nao_suja_banco(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    servico.criar(branco.id, preto.id)
    with pytest.raises(ValueError):
        servico.jogar_uci("e2e5")
    assert sessao.scalar(select(func.count()).select_from(Lance)) == 0
    assert servico.jogo.tabuleiro.para_fen() == FEN_INICIAL


def test_nao_aceita_jogador_duplicado_na_partida(sessao):
    branco, _ = jogadores(sessao)
    with pytest.raises(ValueError):
        ServicoPartida(sessao).criar(branco.id, branco.id)


def test_integridade_da_associacao(sessao):
    branco, preto = jogadores(sessao)
    partida = ServicoPartida(sessao).criar(branco.id, preto.id)
    with pytest.raises(IntegrityError):
        sessao.execute(insert(participacoes).values(
            partida_id=partida.id, jogador_id=999999, cor="branco"
        ))
    sessao.rollback()
    with pytest.raises(IntegrityError):
        sessao.execute(insert(participacoes).values(
            partida_id=partida.id, jogador_id=999999, cor="verde"
        ))
    sessao.rollback()


def test_seed_e_as_tres_consultas(sessao):
    assert popular_banco(sessao)
    assert not popular_banco(sessao)
    assert sessao.scalar(select(func.count()).select_from(Jogador)) == 6
    assert sessao.scalar(select(func.count()).select_from(Partida)) == 4
    assert len(consulta_1_partidas_por_jogador(sessao)) == 6
    assert consulta_2_historico_de_lances(sessao, 1)[-1][1] == "Qxf7#"
    vitorias = dict(consulta_3_vitorias_por_jogador(sessao))
    assert vitorias["Alice"] == vitorias["Diego"] == 1
    assert vitorias["Carla"] == 0


def test_persistir_mate_e_reabrir(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    partida = servico.criar(branco.id, preto.id)
    for uci in ("f2f3", "e7e5", "g2g4", "d8h4"):
        servico.jogar_uci(uci)
    assert servico.jogo.estado().tipo == "xeque_mate"
    assert partida.resultado == "0-1"
    outro = ServicoPartida(sessao)
    outro.abrir(partida.id)
    assert outro.jogo.estado().terminado
    with pytest.raises(ValueError):
        outro.jogar_uci("e2e4")


def test_persistir_desistencia_e_acordo(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    partida = servico.criar(branco.id, preto.id)
    servico.jogar_uci("e2e4")
    servico.desistir("preto")
    assert partida.resultado == "1-0"
    outro = ServicoPartida(sessao)
    outro.abrir(partida.id)
    assert outro.jogo.estado().terminado
    assert outro.jogo.estado().vencedor == "branco"

    novo = servico.criar(branco.id, preto.id)
    servico.empatar_por_acordo()
    assert novo.resultado == "1/2-1/2"
    outro.abrir(novo.id)
    assert outro.jogo.estado().terminado


def test_historico_persistido_reconstroi_san_para_interface(sessao):
    from interface.formatacao import texto_historico

    branco, preto = jogadores(sessao)
    primeira = ServicoPartida(sessao)
    partida = primeira.criar(branco.id, preto.id)
    for uci in ("e2e4", "e7e5", "g1f3"):
        primeira.jogar_uci(uci)

    reaberta = ServicoPartida(sessao)
    reaberta.abrir(partida.id)
    historico = texto_historico(reaberta.jogo.notacoes)
    assert "1." in historico and "e4" in historico and "e5" in historico
    assert "2." in historico and "Nf3" in historico

    assert reaberta.desfazer()
    assert "Nf3" not in texto_historico(reaberta.jogo.notacoes)
    assert [l.uci for l in sessao.get(Partida, partida.id).lances] == ["e2e4", "e7e5"]


def test_empate_reivindicado_salvo_e_reaberto(sessao):
    branco, preto = jogadores(sessao)
    servico = ServicoPartida(sessao)
    partida = servico.criar(branco.id, preto.id)
    for _ in range(2):
        for uci in ("g1f3", "g8f6", "f3g1", "f6g8"):
            servico.jogar_uci(uci)

    assert "três repetições" in servico.jogo.estado().reivindicavel
    servico.reivindicar_empate()
    assert partida.status == "encerrada"
    assert partida.resultado == "1/2-1/2"
    assert partida.motivo == "empate_reivindicado"

    outro = ServicoPartida(sessao)
    outro.abrir(partida.id)
    assert outro.jogo.estado().terminado
