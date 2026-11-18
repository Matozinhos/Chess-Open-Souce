
def tela_para_modelo(linha: int, coluna: int, invertido: bool = False) -> tuple[int, int]:
    return (7 - linha if invertido else linha), coluna


def modelo_para_tela(linha: int, coluna: int, invertido: bool = False) -> tuple[int, int]:
    return (7 - linha if invertido else linha), coluna
