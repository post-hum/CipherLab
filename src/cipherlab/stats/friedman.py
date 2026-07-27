"""Тест Фридмана: оценка длины ключа Виженера по индексу совпадения.

Общая формула (параметризована языком, а не жёстко английскими константами):
    keyLength ~= (IC_язык - IC_случайный) / (IC_наблюдаемый - IC_случайный)
"""
from __future__ import annotations

from cipherlab.stats.ic import NATURAL_IC, index_of_coincidence, random_ic


def friedman_key_length(ciphertext: str, lang: str) -> float:
    ic_observed = index_of_coincidence(ciphertext)
    ic_lang = NATURAL_IC[lang]
    ic_random = random_ic(lang)

    denominator = ic_observed - ic_random
    if abs(denominator) < 1e-9:
        return float("inf")
    return (ic_lang - ic_random) / denominator
