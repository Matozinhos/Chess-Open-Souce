from dataclasses import dataclass

@dataclass
class Debug:
    PECAS_EMOJI = {
    ("Rei", "branco"): "♔",
    ("Rainha", "branco"): "♕",
    ("Torre", "branco"): "♖",
    ("Bispo", "branco"): "♗",
    ("Cavalo", "branco"): "♘",
    ("Peao", "branco"): "♙",
    
    ("Rei", "preto"): "♚",
    ("Rainha", "preto"): "♛",
    ("Torre", "preto"): "♜",
    ("Bispo", "preto"): "♝",
    ("Cavalo", "preto"): "♞",
    ("Peao", "preto"): "♟",
}

DEBUG = Debug()