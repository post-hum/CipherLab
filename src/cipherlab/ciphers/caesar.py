"""Шифр Цезаря: c[i] = (p[i] + key) mod n."""
from __future__ import annotations

from cipherlab.alphabets import alphabet_size, char_to_index, index_to_char, normalize
from cipherlab.ciphers.base import Cipher


class CaesarCipher(Cipher):
    name = "caesar"

    def encrypt(self, plaintext: str, key: int, lang: str) -> str:
        text = normalize(plaintext, lang)
        n = alphabet_size(lang)
        return "".join(index_to_char((char_to_index(ch, lang) + key) % n, lang) for ch in text)

    def decrypt(self, ciphertext: str, key: int, lang: str) -> str:
        text = normalize(ciphertext, lang)
        n = alphabet_size(lang)
        return "".join(index_to_char((char_to_index(ch, lang) - key) % n, lang) for ch in text)

    def keyspace(self, lang: str):
        return range(alphabet_size(lang))
