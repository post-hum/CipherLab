"""Оценка «похожести на естественный язык» через биграммы (логарифм правдоподобия).

Почему биграммы, а не только монограммы. Монограммный χ² сравнивает лишь то,
КАК ЧАСТО встречается каждая буква, игнорируя ПОРЯДОК. На коротком тексте
(десятки букв) частоты отдельных букв — это шум, поэтому монограммный анализ
регулярно выбирает неверный сдвиг. Биграммная модель учитывает, какие ПАРЫ
букв естественны для языка («ст», «но», «ов» — часты; «ъь», «фх» — почти нет),
и потому надёжно распознаёт осмысленный текст на гораздо более коротких
фрагментах (эмпирически — уже от ~12 букв нормального текста).

Ключевое свойство для взлома Виженера: оценка нормирована на число биграмм
(средний логарифм правдоподобия на одну биграмму), поэтому у более длинного
ключа НЕТ искусственного преимущества. Неверная длина ключа перемешивает
столбцы и разрушает биграммную структуру → средняя оценка падает; верная длина
(и кратные ей) её восстанавливают. Это позволяет честно сравнивать варианты с
разной длиной ключа, чего монограммный χ² не умеет (там больше параметров →
всегда меньше χ², то есть длинный ключ всегда «переобучается»).
"""
from __future__ import annotations

import math
from pathlib import Path

from cipherlab.alphabets import alphabet_size
from cipherlab.stats.frequency import load_json

DATA_DIR = Path(__file__).resolve().parents[3] / "data"

# кэш: язык -> (словарь логарифмов вероятностей биграмм, логарифм-«пол» для
# биграмм, которых нет в таблице)
_MODEL_CACHE: dict[str, tuple[dict[str, float], float]] = {}


def _load_model(lang: str) -> tuple[dict[str, float], float]:
    if lang not in _MODEL_CACHE:
        freqs = load_json(DATA_DIR / f"freq_{lang}_bigram.json")
        if not freqs:
            raise ValueError(f"пустая таблица биграмм для языка {lang!r}")
        # Биграммам вне таблицы (редким, но возможным) назначаем маленькую
        # ненулевую вероятность — «пол». Иначе одна невиданная пара обнулила бы
        # (log 0 = -inf) всю оценку кандидата.
        floor = min(freqs.values()) / 10.0
        log_probs = {bg: math.log(p) for bg, p in freqs.items()}
        _MODEL_CACHE[lang] = (log_probs, math.log(floor))
    return _MODEL_CACHE[lang]


def bigram_fitness(text: str, lang: str) -> float:
    """Средний логарифм правдоподобия биграмм текста. Больше = «естественнее».

    Текст ожидается уже нормализованным (только буквы алфавита). Для текста
    короче двух букв возвращается -inf: сравнивать не с чем.
    """
    if len(text) < 2:
        return float("-inf")
    log_probs, floor = _load_model(lang)
    total = 0.0
    for i in range(len(text) - 1):
        total += log_probs.get(text[i:i + 2], floor)
    return total / (len(text) - 1)


# кэш опорных значений оценки для перевода в уверенность: язык -> (good, bad)
_ANCHOR_CACHE: dict[str, tuple[float, float]] = {}


def _anchors(lang: str) -> tuple[float, float]:
    """Опорные значения биграммной оценки, вычисленные из самой модели.

    good — ожидаемая оценка текста, идеально следующего модели (−энтропия
    распределения биграмм). bad — оценка равномерно случайного текста (среднее
    по всем n² возможным биграммам). Реальный осмысленный текст лежит близко к
    good, «шум» неудачной расшифровки — близко к bad.
    """
    if lang not in _ANCHOR_CACHE:
        log_probs, floor = _load_model(lang)
        good = sum(math.exp(lp) * lp for lp in log_probs.values())
        n = alphabet_size(lang)
        cells = n * n
        bad = (sum(log_probs.values()) + (cells - len(log_probs)) * floor) / cells
        _ANCHOR_CACHE[lang] = (good, bad)
    return _ANCHOR_CACHE[lang]


def fitness_confidence(fitness: float, lang: str) -> float:
    """Переводит биграммную оценку в уверенность [0, 1] через опорные значения.

    ~0 — результат неотличим от случайного набора букв (расшифровка не удалась,
    чаще всего из-за слишком короткого текста); ближе к 1 — текст уверенно
    похож на естественный язык.
    """
    good, bad = _anchors(lang)
    if good <= bad:
        return 0.0
    return max(0.0, min(1.0, (fitness - bad) / (good - bad)))
