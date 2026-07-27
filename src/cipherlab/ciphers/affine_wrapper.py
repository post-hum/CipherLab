"""Обертка для C++ реализации аффинного шифра.

Поддерживает русский (с ё) и английский языки.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from cipherlab.ciphers.base import Cipher

AFFINE_BIN = Path(__file__).parent / "affine"


class AffineCipher(Cipher):
    name = "affine"

    def _run_cpp(self, mode: str, text: str, a: int, b: int, lang: str) -> str:
        """Запускает C++ исполняемый файл с переданными аргументами."""
        if lang not in ("ru", "en"):
            raise ValueError(f"Аффинный шифр поддерживает только 'ru' или 'en', получен: {lang}")
        
        if not AFFINE_BIN.exists():
            raise RuntimeError(
                f"C++ бинарник не найден: {AFFINE_BIN}. "
                "Скомпилируйте его: g++ -std=c++17 -o affine affine.cpp"
            )
        
        # Проверяем валидность ключа
        from math import gcd
        n = 33 if lang == "ru" else 26
        if gcd(a, n) != 1:
            raise ValueError(f"a={a} не взаимно просто с {n} для языка {lang}")
        
        # Запускаем процесс
        proc = subprocess.run(
            [str(AFFINE_BIN), mode, str(a), str(b), lang],
            input=text.encode('utf-8'),
            capture_output=True,
            check=False
        )
        
        if proc.returncode != 0:
            error_msg = proc.stderr.decode('utf-8')
            if "coprime" in error_msg or "inverse" in error_msg:
                raise ValueError(f"Невалидный ключ: {error_msg.strip()}")
            raise RuntimeError(f"C++ ошибка: {error_msg}")
        
        return proc.stdout.decode('utf-8')

    def encrypt(self, plaintext: str, key: tuple[int, int], lang: str) -> str:
        """Шифрует текст аффинным преобразованием через C++."""
        a, b = key
        return self._run_cpp("encrypt", plaintext, a, b, lang)

    def decrypt(self, ciphertext: str, key: tuple[int, int], lang: str) -> str:
        """Расшифровывает текст через C++."""
        a, b = key
        return self._run_cpp("decrypt", ciphertext, a, b, lang)

    def keyspace(self, lang: str):
        """Генерирует все допустимые ключи (a, b) для данного языка."""
        if lang == "ru":
            n = 33
        elif lang == "en":
            n = 26
        else:
            return []
        
        from math import gcd
        for a in range(1, n):
            if gcd(a, n) == 1:
                for b in range(n):
                    yield (a, b)
