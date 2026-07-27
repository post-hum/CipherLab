"""Квадрат Полибия.

Английский алфавит (26 букв) сводится к 25 объединением I/J в классическую
решётку 5x5. Русский алфавит (33 буквы с ё) не делится нацело на квадрат — 
используется решётка 6x6 (36 клеток), 3 клетки остаются неиспользуемыми.
Ключ не требуется: базовая раскладка — буквы алфавита по порядку.
"""
from __future__ import annotations

import math

from cipherlab.alphabets import alphabet, normalize
from cipherlab.ciphers.base import Cipher

# явные схемы объединения букв, чтобы алфавит укладывался в решётку без потерь
MERGES: dict[str, dict[str, str]] = {
    "en": {"j": "i"},  # 26 -> 25 букв (5x5)
    "ru": {},          # 33 -> 33 буквы (6x6, 3 клетки пустые)
}


def grid_alphabet(lang: str) -> str:
    merge = MERGES[lang]
    return "".join(ch for ch in alphabet(lang) if ch not in merge)


def grid_size(lang: str) -> int:
    return math.ceil(math.sqrt(len(grid_alphabet(lang))))


def char_to_coord(lang: str) -> dict[str, tuple[int, int]]:
    g = grid_alphabet(lang)
    size = grid_size(lang)
    return {ch: (i // size + 1, i % size + 1) for i, ch in enumerate(g)}


def coord_to_char(lang: str) -> dict[tuple[int, int], str]:
    return {coord: ch for ch, coord in char_to_coord(lang).items()}


class PolybiusCipher(Cipher):
    name = "polybius"

    def encrypt(self, plaintext: str, key: None, lang: str) -> str:
        text = normalize(plaintext, lang, keep_yo=True)
        merge = MERGES[lang]
        text = "".join(merge.get(ch, ch) for ch in text)
        mapping = char_to_coord(lang)
        return "".join(f"{r}{c}" for ch in text for r, c in [mapping[ch]])

    def decrypt(self, ciphertext: str, key: None, lang: str) -> str:
        digits = [d for d in ciphertext if d.isdigit()]
        mapping = coord_to_char(lang)
        out = []
        for i in range(0, len(digits) - 1, 2):
            coord = (int(digits[i]), int(digits[i + 1]))
            if coord in mapping:
                out.append(mapping[coord])
        return "".join(out)

    def keyspace(self, lang: str):
        return [None]
