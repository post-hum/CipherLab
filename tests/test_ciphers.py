import pytest

from cipherlab.alphabets import alphabet_size, normalize
from cipherlab.ciphers.affine_wrapper import AffineCipher
from cipherlab.ciphers.atbash import AtbashCipher
from cipherlab.ciphers.caesar import CaesarCipher
from cipherlab.ciphers.polybius import PolybiusCipher
from cipherlab.ciphers.vigenere import VigenereCipher

SAMPLES = {
    "en": ["hello world", "The Quick Brown Fox", "a", ""],
    "ru": ["привет мир", "Съешь ещё этих мягких булок", "а", ""],
}


@pytest.mark.parametrize("lang", ["en", "ru"])
@pytest.mark.parametrize("key", [0, 1, 5, 13])
def test_caesar_roundtrip(lang, key):
    cipher = CaesarCipher()
    for text in SAMPLES[lang]:
        norm = normalize(text, lang, keep_yo=True)
        enc = cipher.encrypt(text, key, lang)
        assert cipher.decrypt(enc, key, lang) == norm


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_atbash_roundtrip_and_self_inverse(lang):
    cipher = AtbashCipher()
    for text in SAMPLES[lang]:
        norm = normalize(text, lang, keep_yo=True)
        enc = cipher.encrypt(text, None, lang)
        assert cipher.decrypt(enc, None, lang) == norm
        assert cipher.encrypt(enc, None, lang) == norm


@pytest.mark.parametrize("lang", ["en", "ru"])
def test_polybius_roundtrip(lang):
    cipher = PolybiusCipher()
    for text in SAMPLES[lang]:
        norm = normalize(text, lang, keep_yo=True)
        enc = cipher.encrypt(text, None, lang)
        assert enc.isdigit() or enc == ""
        expected = norm.replace("j", "i") if lang == "en" else norm
        assert cipher.decrypt(enc, None, lang) == expected


@pytest.mark.parametrize("lang,key", [("en", "key"), ("en", "a"), ("ru", "ключ"), ("ru", "б")])
def test_vigenere_roundtrip(lang, key):
    cipher = VigenereCipher()
    for text in SAMPLES[lang]:
        norm = normalize(text, lang, keep_yo=True)
        enc = cipher.encrypt(text, key, lang)
        assert cipher.decrypt(enc, key, lang) == norm


def test_vigenere_empty_key_raises():
    cipher = VigenereCipher()
    with pytest.raises(ValueError):
        cipher.encrypt("hello", "!!!", "en")


# Тесты для аффинного шифра
@pytest.mark.parametrize("lang, a, b", [
    ("ru", 5, 8),
    ("ru", 7, 3),
    ("en", 3, 7),
    ("en", 5, 8),
    ("en", 7, 3),
])
def test_affine_roundtrip(lang, a, b):
    from math import gcd
    n = 33 if lang == "ru" else 26
    if gcd(a, n) != 1:
        pytest.skip(f"a={a} не взаимно просто с {n} для {lang}")
    
    cipher = AffineCipher()
    key = (a, b)
    for text in SAMPLES[lang]:
        if not text:
            continue
        enc = cipher.encrypt(text, key, lang)
        dec = cipher.decrypt(enc, key, lang)
        assert dec == text


def test_affine_invalid_key_raises():
    cipher = AffineCipher()
    # 3 не взаимно просто с 33 (русский)
    with pytest.raises(ValueError):
        cipher.encrypt("привет", (3, 5), "ru")
    
    # 2 не взаимно просто с 26 (английский)
    with pytest.raises(ValueError):
        cipher.encrypt("hello", (2, 3), "en")
    
    # 4 не взаимно просто с 26 (английский)
    with pytest.raises(ValueError):
        cipher.encrypt("hello", (4, 5), "en")


def test_affine_preserves_non_letters():
    cipher = AffineCipher()
    text = "Привет, мир! Как дела?"
    enc = cipher.encrypt(text, (5, 8), "ru")
    assert enc.count(",") == text.count(",")
    assert enc.count("!") == text.count("!")
    assert enc.count("?") == text.count("?")
    assert enc.count(" ") == text.count(" ")


def test_affine_preserves_case():
    cipher = AffineCipher()
    text = "Привет Мир"
    enc = cipher.encrypt(text, (5, 8), "ru")
    assert enc[0].isupper()
    assert enc[enc.index(" ")] == " "
    
    # Английский
    text_en = "Hello World"
    enc_en = cipher.encrypt(text_en, (3, 7), "en")
    assert enc_en[0].isupper()
    assert enc_en[enc_en.index(" ")] == " "
