"""Шифр Виженера: c[i] = (p[i] + key[i mod len(key)]) mod n."""
from __future__ import annotations

from cipherlab.alphabets import alphabet_size, char_to_index, index_to_char, normalize
from cipherlab.ciphers.base import Cipher


class VigenereCipher(Cipher):
    name = "vigenere"

    def encrypt(self, plaintext: str, key: str, lang: str) -> str:
        text = normalize(plaintext, lang)
        key_norm = normalize(key, lang)
        if not key_norm:
            raise ValueError("ключ Виженера не может быть пустым")
        n = alphabet_size(lang)
        out = []
        for i, ch in enumerate(text):
            shift = char_to_index(key_norm[i % len(key_norm)], lang)
            out.append(index_to_char((char_to_index(ch, lang) + shift) % n, lang))
        return "".join(out)

    def decrypt(self, ciphertext: str, key: str, lang: str) -> str:
        text = normalize(ciphertext, lang)
        key_norm = normalize(key, lang)
        if not key_norm:
            raise ValueError("ключ Виженера не может быть пустым")
        n = alphabet_size(lang)
        out = []
        for i, ch in enumerate(text):
            shift = char_to_index(key_norm[i % len(key_norm)], lang)
            out.append(index_to_char((char_to_index(ch, lang) - shift) % n, lang))
        return "".join(out)

    def keyspace(self, lang: str):
        raise NotImplementedError(
            "ключевое пространство Виженера практически бесконечно; "
            "используйте оценку длины ключа (Касиски/Фридман) вместо перебора"
        )
