"""Console opcional de debug. O aplicativo visual é aberto com main.py."""
from test.controlador_debug import ControladorDebug


def executar_console():
    debug = ControladorDebug()
    print("Debug Xandrez. Use 'fen', 'tabuleiro', 'legais e2', 'jogar e2e4', 'desfazer' ou 'sair'.")
    while True:
        try:
            entrada = input("xadrez> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if entrada.lower() in ("sair", "exit", "quit"):
            break
        try:
            print(debug.executar(entrada))
        except ValueError as erro:
            print(f"Erro: {erro}")
