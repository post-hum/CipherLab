"""Алфавиты и нормализация текста для русского и английского языков.

Теперь буква "ё" считается полноценной буквой русского алфавита
(33-я буква, входит во все таблицы частот и криптосистемы).
"""
from __future__ import annotations

EN_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
RU_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

ALPHABETS = {"en": EN_ALPHABET, "ru": RU_ALPHABET}

# Для совместимости со старыми данными, где ё могла быть свернута в е
_YO_FOLD = str.maketrans({"ё": "е"})


def alphabet(lang: str) -> str:
    try:
        return ALPHABETS[lang]
    except KeyError:
        raise ValueError(f"неизвестный язык: {lang!r}, ожидается 'en' или 'ru'")


def alphabet_size(lang: str) -> int:
    return len(alphabet(lang))


def normalize(text: str, lang: str, keep_yo: bool = True) -> str:
    """Приводит текст к нижнему регистру и оставляет только буквы алфавита.
    
    Args:
        text: исходный текст
        lang: язык ('en' или 'ru')
        keep_yo: если True, сохраняет букву ё; если False, сворачивает в е
    """
    letters = alphabet(lang)
    text = text.lower()
    if not keep_yo and lang == "ru":
        text = text.translate(_YO_FOLD)
    return "".join(ch for ch in text if ch in letters)


def char_to_index(ch: str, lang: str) -> int:
    return alphabet(lang).index(ch)


def index_to_char(i: int, lang: str) -> str:
    n = alphabet_size(lang)
    return alphabet(lang)[i % n]
