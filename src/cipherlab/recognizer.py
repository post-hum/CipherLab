"""Распознавание семейства шифра по шифртексту (без расшифровки).

Метод — индекс совпадения (IC). Моноалфавитные шифры (Цезарь, Атбаш) лишь
переставляют буквы, сохраняя их частоты, поэтому IC шифртекста ≈ IC языка.
Многоалфавитный Виженер «размывает» распределение к равномерному, и IC падает
к значению случайного текста (1/n). Полибий распознаётся отдельно — по тому,
что его шифртекст состоит только из цифр.

Взлом (breaker) на это распознавание НЕ опирается: он перебирает все семейства
и выбирает результат по объективной оценке текста. Здесь распознавание —
самостоятельный аналитический вывод для пользователя.
"""
from __future__ import annotations

from dataclasses import dataclass

from cipherlab.alphabets import normalize
from cipherlab.language import detect_language
from cipherlab.stats.ic import NATURAL_IC, index_of_coincidence, random_ic


@dataclass
class Hypothesis:
    cipher: str  # "polybius" | "monoalphabetic" (Цезарь/Атбаш) | "vigenere"
    lang: str
    confidence: float  # доля уверенности в [0, 1]


def is_polybius_ciphertext(raw_text: str) -> bool:
    """Шифртекст Полибия состоит только из цифр (и, возможно, пробелов)."""
    stripped = raw_text.strip()
    if not stripped:
        return False
    return all(ch.isdigit() or ch.isspace() for ch in stripped)


def classify_cipher(raw_text: str) -> list[Hypothesis]:
    """Ранжированный список гипотез о семействе шифра (наиболее вероятная — первой)."""
    if is_polybius_ciphertext(raw_text):
        return [Hypothesis("polybius", "ru", 1.0), Hypothesis("polybius", "en", 1.0)]

    lang = detect_language(raw_text)
    text = normalize(raw_text, lang)

    ic_observed = index_of_coincidence(text)
    ic_lang = NATURAL_IC[lang]
    ic_random = random_ic(lang)

    # Положение наблюдаемого IC на отрезке [случайный, языковой]: ближе к
    # языковому → моноалфавит, ближе к случайному → Виженер.
    span = ic_lang - ic_random
    position = 0.5 if span <= 0 else (ic_observed - ic_random) / span
    position = max(0.0, min(1.0, position))

    hypotheses = [
        Hypothesis("monoalphabetic", lang, position),
        Hypothesis("vigenere", lang, 1.0 - position),
    ]
    hypotheses.sort(key=lambda h: h.confidence, reverse=True)
    return hypotheses
