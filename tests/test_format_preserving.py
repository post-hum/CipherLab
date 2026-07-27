import pytest

from cipherlab.ciphers.atbash import AtbashCipher
from cipherlab.ciphers.caesar import CaesarCipher
from cipherlab.ciphers.vigenere import VigenereCipher
from cipherlab.format_preserving import decrypt_preserving_format, encrypt_preserving_format

SAMPLES = {
    "en": ["Hello, World! It's a Test.", "ABC   xyz"],
    "ru": ["Привет, Мир! Это тест.", "Съешь ещё этих мягких булок, да выпей чаю.", "Ёжик"],
}


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_caesar_preserves_format_exactly(lang):
    cipher = CaesarCipher()
    key = 7
    for text in SAMPLES[lang]:
        enc = encrypt_preserving_format(cipher, text, key, lang)
        dec = decrypt_preserving_format(cipher, enc, key, lang)
        assert dec.lower().replace("ё", "е") == text.lower().replace("ё", "е")
        # длина и позиции небуквенных символов не меняются
        assert len(enc) == len(text)
        for orig_ch, enc_ch in zip(text, enc):
            if not orig_ch.isalpha():
                assert enc_ch == orig_ch


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_atbash_preserves_format_and_case(lang):
    cipher = AtbashCipher()
    for text in SAMPLES[lang]:
        enc = encrypt_preserving_format(cipher, text, None, lang)
        dec = decrypt_preserving_format(cipher, enc, None, lang)
        assert dec.lower().replace("ё", "е") == text.lower().replace("ё", "е")
        for orig_ch, dec_ch in zip(text, dec):
            if orig_ch.isalpha():
                assert dec_ch.isupper() == orig_ch.isupper()


@pytest.mark.parametrize("lang,key", [("en", "Key"), ("ru", "Ключ")])
def test_vigenere_preserves_format(lang, key):
    cipher = VigenereCipher()
    for text in SAMPLES[lang]:
        enc = encrypt_preserving_format(cipher, text, key, lang)
        dec = decrypt_preserving_format(cipher, enc, key, lang)
        assert dec.lower().replace("ё", "е") == text.lower().replace("ё", "е")


def test_case_is_restored_per_letter():
    cipher = CaesarCipher()
    text = "Abc"
    enc = encrypt_preserving_format(cipher, text, 1, "en")
    assert enc == "Bcd"
    dec = decrypt_preserving_format(cipher, enc, 1, "en")
    assert dec == "Abc"
