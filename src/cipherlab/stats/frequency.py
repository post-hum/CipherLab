"""Подсчёт частот монограмм и биграмм, загрузка/сохранение таблиц в JSON."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from cipherlab.alphabets import alphabet


def monogram_freq(text: str, lang: str) -> dict[str, float]:
    """Частота каждой буквы алфавита в нормализованном тексте (доли от 1.0)."""
    letters = alphabet(lang)
    counts = Counter(ch for ch in text if ch in letters)
    total = sum(counts.values())
    if total == 0:
        return {ch: 0.0 for ch in letters}
    return {ch: counts.get(ch, 0) / total for ch in letters}


def bigram_freq(text: str, lang: str, top_n: int = 200) -> dict[str, float]:
    """Частота перекрывающихся биграмм; возвращает top_n самых частых."""
    letters = set(alphabet(lang))
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)
               if text[i] in letters and text[i + 1] in letters]
    counts = Counter(bigrams)
    total = sum(counts.values())
    if total == 0:
        return {}
    freqs = {bg: c / total for bg, c in counts.most_common(top_n)}
    return freqs


def save_json(data: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
