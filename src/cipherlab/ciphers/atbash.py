"""Шифр Атбаш: c[i] = (n - 1 - p[i]) mod n. Ключа нет, преобразование самообратно."""
from __future__ import annotations

from cipherlab.alphabets import alphabet_size, char_to_index, index_to_char, normalize
from cipherlab.ciphers.base import Cipher


class AtbashCipher(Cipher):
    name = "atbash"

    def _transform(self, text: str, lang: str) -> str:
        n = alphabet_size(lang)
        return "".join(index_to_char(n - 1 - char_to_index(ch, lang), lang) for ch in text)

    def encrypt(self, plaintext: str, key: None, lang: str) -> str:
        return self._transform(normalize(plaintext, lang), lang)

    def decrypt(self, ciphertext: str, key: None, lang: str) -> str:
        return self._transform(normalize(ciphertext, lang), lang)

    def keyspace(self, lang: str):
        return [None]
