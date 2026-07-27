"""Критерий хи-квадрат для сравнения наблюдаемого текста с эталонной частотой."""
from __future__ import annotations

from collections import Counter


def chi_squared_stat(text: str, expected_freqs: dict[str, float]) -> float:
    """Меньшее значение = лучшее соответствие эталонному распределению."""
    n = len(text)
    if n == 0:
        return float("inf")
    counts = Counter(text)
    chi2 = 0.0
    for ch, p in expected_freqs.items():
        expected = p * n
        if expected == 0:
            continue
        observed = counts.get(ch, 0)
        chi2 += (observed - expected) ** 2 / expected
    return chi2
