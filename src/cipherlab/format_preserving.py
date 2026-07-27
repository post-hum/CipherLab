"""Шифрование/дешифрование с сохранением исходного форматирования.

Применимо к шифрам типа "буква -> буква" (Цезарь, Атбаш, Виженер): пробелы,
знаки препинания и регистр букв в исходном тексте сохраняются на своих
позициях, преобразуются только буквы. Не применяется к Полибию — он
преобразует каждую букву в пару цифр, поэтому позиционное соответствие
"один символ входа -> один символ выхода" не сохраняется.
"""
from __future__ import annotations

from typing import Any

from cipherlab.alphabets import alphabet, normalize
from cipherlab.ciphers.base import Cipher


def _fold(ch: str, lang: str) -> str:
    folded = ch.lower()
    if lang == "ru" and folded == "ё":
        folded = "е"
    return folded


def _is_letter(ch: str, lang: str) -> bool:
    return _fold(ch, lang) in alphabet(lang)


def _reinsert_format(original: str, transformed_letters: str, lang: str) -> str:
    result = []
    idx = 0
    for ch in original:
        if _is_letter(ch, lang):
            out_ch = transformed_letters[idx]
            idx += 1
            result.append(out_ch.upper() if ch.isupper() else out_ch)
        else:
            result.append(ch)
    return "".join(result)


def encrypt_preserving_format(cipher: Cipher, plaintext: str, key: Any, lang: str) -> str:
    transformed = cipher.encrypt(normalize(plaintext, lang), key, lang)
    return _reinsert_format(plaintext, transformed, lang)


def decrypt_preserving_format(cipher: Cipher, ciphertext: str, key: Any, lang: str) -> str:
    transformed = cipher.decrypt(normalize(ciphertext, lang), key, lang)
    return _reinsert_format(ciphertext, transformed, lang)
