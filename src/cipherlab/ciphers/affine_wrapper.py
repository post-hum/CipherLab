"""Обертка для C++ реализации аффинного шифра.

Поддерживает русский (с ё) и английский языки.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from cipherlab.ciphers.base import Cipher

# Определяем имя бинарника в зависимости от ОС
if sys.platform == "win32":
    AFFINE_BIN = Path(__file__).parent / "affine.exe"
else:
    AFFINE_BIN = Path(__file__).parent / "affine"


class AffineCipher(Cipher):
    name = "affine"

    def _get_binary_path(self) -> Path:
        """Возвращает путь к бинарнику с учётом ОС."""
        # На Windows ищем .exe
        if sys.platform == "win32":
            exe_path = Path(__file__).parent / "affine.exe"
            if exe_path.exists():
                return exe_path
            # Если нет .exe, может быть просто affine (для совместимости)
            alt_path = Path(__file__).parent / "affine"
            if alt_path.exists():
                return alt_path
            return exe_path  # Вернём .exe, хотя его нет
        else:
            # На Linux ищем без расширения
            bin_path = Path(__file__).parent / "affine"
            if bin_path.exists():
                return bin_path
            # Если нет, может быть .exe (редко, но бывает)
            alt_path = Path(__file__).parent / "affine.exe"
            if alt_path.exists():
                return alt_path
            return bin_path

    def _run_cpp(self, mode: str, text: str, a: int, b: int, lang: str) -> str:
        """Запускает C++ исполняемый файл с переданными аргументами."""
        if lang not in ("ru", "en"):
            raise ValueError(f"Аффинный шифр поддерживает только 'ru' или 'en', получен: {lang}")
        
        binary = self._get_binary_path()
        if not binary.exists():
            if sys.platform == "win32":
                raise RuntimeError(
                    f"C++ бинарник не найден: {binary}. "
                    f"Скомпилируйте его: cl /EHsc /std:c++17 /Fe:{binary.name} affine.cpp"
                )
            else:
                raise RuntimeError(
                    f"C++ бинарник не найден: {binary}. "
                    f"Скомпилируйте его: g++ -std=c++17 -o {binary.name} affine.cpp"
                )
        
        # Проверяем валидность ключа
        from math import gcd
        n = 33 if lang == "ru" else 26
        if gcd(a, n) != 1:
            raise ValueError(f"a={a} не взаимно просто с {n} для языка {lang}")
        
        # Запускаем процесс
        proc = subprocess.run(
            [str(binary), mode, str(a), str(b), lang],
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
