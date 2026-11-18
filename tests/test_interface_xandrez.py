"""A interface pode testar suas conversões sem iniciar uma janela gráfica."""
from interface.coordenadas import modelo_para_tela, tela_para_modelo
from interface.formatacao import linhas_historico, texto_historico


def test_orientacao_normal_e_invertida_apenas_nas_linhas():
    assert tela_para_modelo(0, 4) == (0, 4)
    assert tela_para_modelo(0, 4, True) == (7, 4)
    assert tela_para_modelo(7, 0, True) == (0, 0)

    for linha in range(8):
        for coluna in range(8):
            posicao = modelo_para_tela(linha, coluna, True)
            assert tela_para_modelo(*posicao, True) == (linha, coluna)


def test_historico_em_duas_colunas_e_numero_de_lance():
    assert linhas_historico(["e4", "e5", "Nf3"]) == [
        (1, "e4", "e5"), (2, "Nf3", ""),
    ]
    texto = texto_historico(["e4", "e5", "Nf3"])
    assert "1." in texto and "e4" in texto and "e5" in texto
    assert "2." in texto and "Nf3" in texto
    assert texto_historico([]) == "Nenhum lance realizado."

