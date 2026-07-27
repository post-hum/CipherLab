from pathlib import Path

import pytest

from cipherlab.alphabets import normalize
from cipherlab.breaker import auto_break
from cipherlab.ciphers.atbash import AtbashCipher
from cipherlab.ciphers.caesar import CaesarCipher
from cipherlab.ciphers.polybius import PolybiusCipher
from cipherlab.ciphers.vigenere import VigenereCipher
from cipherlab.format_preserving import encrypt_preserving_format

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw_corpora"


def _load_plaintext(lang: str) -> str:
    path = DATA_DIR / f"{lang}_sample.txt"
    return normalize(path.read_text(encoding="utf-8"), lang)


def _load_raw(lang: str) -> str:
    """Полный текст корпуса как есть — с пунктуацией, регистром и переносами строк.

    Используется вместо коротких фраз, потому что частотному/χ² взлому и
    методу Касиски нужен достаточно длинный текст, чтобы статистика была
    надёжной.
    """
    path = DATA_DIR / f"{lang}_sample.txt"
    return path.read_text(encoding="utf-8")


def _fold(text: str) -> str:
    # "ё" необратимо сворачивается в "е" при нормализации, поэтому сравнение
    # результата с оригиналом должно закрывать глаза на эту разницу.
    return text.lower().replace("ё", "е")


@pytest.mark.parametrize("lang,shift", [("en", 7), ("ru", 15)])
def test_break_caesar(lang, shift):
    plaintext = _load_plaintext(lang)
    ciphertext = CaesarCipher().encrypt(plaintext, shift, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "caesar"
    assert result.lang == lang
    assert result.key == shift
    assert result.plaintext == plaintext


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_break_atbash(lang):
    plaintext = _load_plaintext(lang)
    ciphertext = AtbashCipher().encrypt(plaintext, None, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "atbash"
    assert result.lang == lang
    assert result.plaintext == plaintext


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_break_polybius(lang):
    plaintext = _load_plaintext(lang)
    ciphertext = PolybiusCipher().encrypt(plaintext, None, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "polybius"
    assert result.lang == lang
    expected = plaintext.replace("j", "i") if lang == "en" else plaintext
    assert result.plaintext == expected


@pytest.mark.parametrize("lang,key", [("en", "secret"), ("ru", "ключик")])
def test_break_vigenere(lang, key):
    plaintext = _load_plaintext(lang)
    ciphertext = VigenereCipher().encrypt(plaintext, key, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "vigenere"
    assert result.lang == lang
    assert result.plaintext == plaintext


@pytest.mark.parametrize("lang,shift", [("en", 7), ("ru", 15)])
def test_break_caesar_preserves_punctuation_and_case(lang, shift):
    original = _load_raw(lang)
    ciphertext = encrypt_preserving_format(CaesarCipher(), original, shift, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "caesar"
    assert _fold(result.plaintext) == _fold(original)


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_break_atbash_preserves_punctuation_and_case(lang):
    original = _load_raw(lang)
    ciphertext = encrypt_preserving_format(AtbashCipher(), original, None, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "atbash"
    assert _fold(result.plaintext) == _fold(original)


@pytest.mark.parametrize("lang,key", [("en", "secret"), ("ru", "ключик")])
def test_break_vigenere_preserves_punctuation_and_case(lang, key):
    original = _load_raw(lang)
    ciphertext = encrypt_preserving_format(VigenereCipher(), original, key, lang)

    result = auto_break(ciphertext)

    assert result.cipher == "vigenere"
    assert _fold(result.plaintext) == _fold(original)
