"""Regressão dos requisitos de retomada, contador, vencedor e migração."""
import sqlite3
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from database.conexao import criar_engine, criar_tabelas
from database.consultas import relatorio
from database.modelos import Partida
from servicos.partida_servico import ServicoPartida


def test_nova_partida_retomada_e_desfazer_apos_reabrir(tmp_path):
    engine = criar_engine(f"sqlite:///{tmp_path / 'xadrez.db'}")
    criar_tabelas(engine)
    fabrica = sessionmaker(bind=engine, expire_on_commit=False)
    with fabrica() as sessao:
        servico = ServicoPartida(sessao)
        primeira = servico.criar_com_nomes()
        servico.jogar_uci("e2e4")
        servico.jogar_uci("e7e5")
        assert primeira.numero_lances == 2
        assert servico.jogo.notacoes == ["e4", "e5"]
        assert servico.retomar_ultima().id == primeira.id

    # Simula fechar o aplicativo e abrir novamente (outra sessão SQLAlchemy).
    with fabrica() as sessao:
        reaberta = ServicoPartida(sessao)
        assert reaberta.retomar_ultima().id == primeira.id
        assert reaberta.jogo.turno == "branco"
        assert reaberta.jogo.notacoes == ["e4", "e5"]
        assert reaberta.desfazer()
        assert sessao.get(Partida, primeira.id).numero_lances == 1
        assert reaberta.jogo.notacoes == ["e4"]
        nova = reaberta.criar_com_nomes()
        assert nova.id != primeira.id
        assert reaberta.retomar_ultima().id == nova.id
    engine.dispose()


def test_vencedor_contagem_de_lances_e_consultas(tmp_path):
    engine = criar_engine(f"sqlite:///{tmp_path / 'xadrez.db'}")
    criar_tabelas(engine)
    fabrica = sessionmaker(bind=engine, expire_on_commit=False)
    with fabrica() as sessao:
        servico = ServicoPartida(sessao)
        partida = servico.criar_com_nomes()
        for lance in ("f2f3", "e7e5", "g2g4", "d8h4"):
            servico.jogar_uci(lance)
        assert partida.status == "encerrada"
        assert partida.numero_lances == 4
        assert partida.vencedor_cor == "preto"
        assert partida.resultado == "0-1"
        assert partida.encerrada_em is not None
        texto = relatorio(sessao)
        assert "4 lance(s)" in texto
        assert "vencedor=preto" in texto
        assert "Qh4#" in texto
        assert "Jogador 2" in texto
        assert servico.desfazer()
        assert partida.status == "em_andamento"
        assert partida.numero_lances == 3
        assert partida.vencedor_cor is None
        assert partida.encerrada_em is None
    engine.dispose()


def test_migracao_banco_antigo_preserva_partidas(tmp_path):
    caminho = tmp_path / "antigo.db"
    con = sqlite3.connect(caminho)
    con.executescript("""
        CREATE TABLE partidas (
            id INTEGER PRIMARY KEY, fen_inicial VARCHAR(100) NOT NULL,
            fen_atual VARCHAR(100) NOT NULL, status VARCHAR(20) NOT NULL,
            resultado VARCHAR(7), vencedor_cor VARCHAR(6), motivo VARCHAR(80),
            criada_em DATETIME NOT NULL
        );
        CREATE TABLE lances (
            id INTEGER PRIMARY KEY, partida_id INTEGER, numero INTEGER,
            uci VARCHAR(5), san VARCHAR(12), fen_apos VARCHAR(100)
        );
    """)
    # O metadata.create_all cria as outras tabelas ausentes, sem eliminar as antigas.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    con.execute(
        "INSERT INTO partidas VALUES (1, ?, ?, 'em_andamento', null, null, null, CURRENT_TIMESTAMP)",
        (fen, fen),
    )
    con.execute("INSERT INTO lances VALUES (1, 1, 1, 'e2e4', 'e4', ?)", (fen,))
    con.commit()
    con.close()

    engine = criar_engine(f"sqlite:///{caminho}")
    criar_tabelas(engine)
    with engine.connect() as c:
        resultado = c.execute(select(Partida.numero_lances).where(Partida.id == 1)).scalar_one()
        assert resultado == 1
        colunas = {r[1] for r in c.exec_driver_sql("PRAGMA table_info(partidas)")}
        assert {"numero_lances", "atualizada_em", "encerrada_em"} <= colunas
    engine.dispose()
