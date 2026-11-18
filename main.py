from database.conexao import criar_sessao, criar_tabelas
from servicos.partida_servico import ServicoPartida


def main():
    criar_tabelas()
    sessao = criar_sessao()
    try:
        servico = ServicoPartida(sessao)
        if servico.retomar_ultima() is None:
            servico.criar_com_nomes()

        from interface.app import JanelaXadrez
        janela = JanelaXadrez(servico)
        janela.mainloop()
    finally:
        sessao.close()


if __name__ == "__main__":
    main()