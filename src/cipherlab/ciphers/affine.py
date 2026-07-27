"""Аффинный шифр: c = (a * p + b) mod n.

Для существования обратного преобразования требуется gcd(a, n) = 1.
Ключ — пара (a, b), где a взаимно просто с размером алфавита.
"""
from __future__ import annotations

import math
from typing import Any

from cipherlab.alphabets import alphabet_size, char_to_index, index_to_char, normalize
from cipherlab.ciphers.base import Cipher


def mod_inverse(a: int, m: int) -> int:
    """Находит обратный элемент a mod m через расширенный алгоритм Евклида."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"нет обратного элемента для {a} по модулю {m}")


class AffineCipher(Cipher):
    name = "affine"

    def encrypt(self, plaintext: str, key: tuple[int, int], lang: str) -> str:
        """Шифрует текст аффинным преобразованием.
        
        Args:
            plaintext: открытый текст
            key: пара (a, b), где a и b — целые числа, gcd(a, n) = 1
            lang: язык ('en' или 'ru')
        """
        text = normalize(plaintext, lang, keep_yo=True)
        if not text:
            return ""
        
        a, b = key
        n = alphabet_size(lang)
        
        # Проверяем, что a взаимно просто с n
        if math.gcd(a, n) != 1:
            raise ValueError(f"a={a} не взаимно просто с размером алфавита {n}")
        
        result = []
        for ch in text:
            p = char_to_index(ch, lang)
            c = (a * p + b) % n
            result.append(index_to_char(c, lang))
        return "".join(result)

    def decrypt(self, ciphertext: str, key: tuple[int, int], lang: str) -> str:
        """Расшифровывает аффинный текст.
        
        Args:
            ciphertext: шифртекст
            key: пара (a, b), где a и b — целые числа
            lang: язык ('en' или 'ru')
        """
        text = normalize(ciphertext, lang, keep_yo=True)
        if not text:
            return ""
        
        a, b = key
        n = alphabet_size(lang)
        
        # Находим обратный элемент для a
        try:
            a_inv = mod_inverse(a, n)
        except ValueError as e:
            raise ValueError(f"нельзя расшифровать: {e}")
        
        result = []
        for ch in text:
            c = char_to_index(ch, lang)
            p = (a_inv * (c - b)) % n
            result.append(index_to_char(p, lang))
        return "".join(result)

    def keyspace(self, lang: str):
        """Генерирует все допустимые ключи (a, b) для данного языка.
        
        a должно быть взаимно просто с размером алфавита,
        b может быть любым числом от 0 до n-1.
        """
        n = alphabet_size(lang)
        for a in range(1, n):
            if math.gcd(a, n) == 1:
                for b in range(n):
                    yield (a, b)
