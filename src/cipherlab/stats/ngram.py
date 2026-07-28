"""Оценка «похожести на естественный язык» через биграммы (логарифм правдоподобия)."""
from __future__ import annotations

import math
from pathlib import Path

from cipherlab.alphabets import alphabet_size
from cipherlab.stats.frequency import load_json, _get_data_dir

DATA_DIR = _get_data_dir()

_MODEL_CACHE: dict[str, tuple[dict[str, float], float]] = {}


def _load_model(lang: str) -> tuple[dict[str, float], float]:
    if lang not in _MODEL_CACHE:
        freqs = load_json(DATA_DIR / f"freq_{lang}_bigram.json")
        if not freqs:
            raise ValueError(f"пустая таблица биграмм для языка {lang!r}")
        floor = min(freqs.values()) / 10.0
        log_probs = {bg: math.log(p) for bg, p in freqs.items()}
        _MODEL_CACHE[lang] = (log_probs, math.log(floor))
    return _MODEL_CACHE[lang]


def bigram_fitness(text: str, lang: str) -> float:
    if len(text) < 2:
        return float("-inf")
    log_probs, floor = _load_model(lang)
    total = 0.0
    for i in range(len(text) - 1):
        total += log_probs.get(text[i:i + 2], floor)
    return total / (len(text) - 1)


_ANCHOR_CACHE: dict[str, tuple[float, float]] = {}


def _anchors(lang: str) -> tuple[float, float]:
    if lang not in _ANCHOR_CACHE:
        log_probs, floor = _load_model(lang)
        good = sum(math.exp(lp) * lp for lp in log_probs.values())
        n = alphabet_size(lang)
        cells = n * n
        bad = (sum(log_probs.values()) + (cells - len(log_probs)) * floor) / cells
        _ANCHOR_CACHE[lang] = (good, bad)
    return _ANCHOR_CACHE[lang]


def fitness_confidence(fitness: float, lang: str) -> float:
    good, bad = _anchors(lang)
    if good <= bad:
        return 0.0
    return max(0.0, min(1.0, (fitness - bad) / (good - bad)))
