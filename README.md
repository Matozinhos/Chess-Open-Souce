# Chess - Open Source | Nerfado
```text
Chess-Open-Source-Xandrez-T3/
├── main.py                        # inicializa SQLite, retoma a partida e abre a GUI
├── consultas.py                   # executa as três consultas e imprime os resultados
├── interface/
│   ├── app.py                     # tabuleiro original + histórico + controles
│   ├── coordenadas.py             # inversão apenas das linhas
│   ├── formatacao.py              # histórico SAN em duas colunas
│   └── imgs/                      # sprites originais do Xandrez
├── core/                          # regras do xadrez
├── servicos/
│   ├── partida_servico.py         # integra interface, core e banco
│   └── partida_local_servico.py
├── database/
│   ├── modelos.py                 # mapeamento ORM
│   ├── conexao.py                 # SQLite e migração
│   ├── repositorios/
│   ├── consultas.py
│   └── seed.py
├── data/xadrez.db                 # banco SQLite de demonstração, persistente
├── docs/DER.md
├── test.py                        # smoke/debug opcional
├── test/                          # ferramentas auxiliares do motor
├── tests/                         # testes de regras, ORM e retomada
└── requirements.txt
```

# Membros 

    Apenas o matozinhos!
    Arthur Soares Pezzini Moreira

# Links 
