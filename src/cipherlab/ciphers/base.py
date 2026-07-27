"""Общий интерфейс для всех реализованных шифров."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class Cipher(ABC):
    name: str

    @abstractmethod
    def encrypt(self, plaintext: str, key: Any, lang: str) -> str:
        ...

    @abstractmethod
    def decrypt(self, ciphertext: str, key: Any, lang: str) -> str:
        ...

    def keyspace(self, lang: str) -> Iterable[Any]:
        """Полный перебираемый набор ключей для данного языка (если конечен)."""
        raise NotImplementedError(f"{self.name}: ключевое пространство не является перебираемым")
