

def linhas_historico(notacoes: list[str]) -> list[tuple[int, str, str]]:
    return [
        (i // 2 + 1, notacoes[i], notacoes[i + 1] if i + 1 < len(notacoes) else "")
        for i in range(0, len(notacoes), 2)
    ]


def texto_historico(notacoes: list[str]) -> str:
    if not notacoes:
        return "Nenhum lance realizado."
    return "\n".join(
        f"{numero:>3}.  {brancas:<10} {pretas}" for numero, brancas, pretas
        in linhas_historico(notacoes)
    )
