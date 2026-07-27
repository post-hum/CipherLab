"""Индекс совпадения (IC) и опорные значения для классификации шифров."""
from __future__ import annotations

from collections import Counter

from cipherlab.alphabets import alphabet_size

# Опубликованные значения IC для естественного текста (см. README).
NATURAL_IC = {"en": 0.0667, "ru": 0.0553}


def random_ic(lang: str) -> float:
    """IC случайного (равновероятного) текста в данном алфавите: 1/n."""
    return 1.0 / alphabet_size(lang)


def index_of_coincidence(text: str) -> float:
    n = len(text)
    if n <= 1:
        return 0.0
    counts = Counter(text)
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    return numerator / denominator
