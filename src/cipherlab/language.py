"""Определение языка по набору символов текста.

Шифры Цезаря, Атбаша и Виженера — это замены внутри одного и того же
алфавита (кириллица остаётся кириллицей, латиница — латиницей), поэтому
принадлежность к языку можно установить напрямую по составу символов
шифртекста, не дожидаясь расшифровки. Это надёжнее и проще, чем сравнение
частот через хи-квадрат, которое имеет смысл только для уже читаемого текста.
"""
from __future__ import annotations

from cipherlab.alphabets import normalize


def detect_language(text: str) -> str:
    ru_count = len(normalize(text, "ru"))
    en_count = len(normalize(text, "en"))
    return "ru" if ru_count >= en_count else "en"
