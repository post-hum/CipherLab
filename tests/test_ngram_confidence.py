"""Тесты биграммной оценки, уверенности и устойчивости автовзлома.

Регрессия на исходную проблему: короткий/обычный шифртекст Цезаря ошибочно
распознавался как Виженер и расшифровывался в бессмыслицу.
"""
import random
from pathlib import Path

import pytest

from cipherlab.alphabets import normalize
from cipherlab.breaker import auto_break
from cipherlab.ciphers.caesar import CaesarCipher
from cipherlab.ciphers.vigenere import VigenereCipher
from cipherlab.format_preserving import encrypt_preserving_format
from cipherlab.stats.ngram import bigram_fitness, fitness_confidence

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw_corpora"


def _corpus(lang: str) -> str:
    return normalize((DATA_DIR / f"{lang}_sample.txt").read_text(encoding="utf-8"), lang)


@pytest.mark.parametrize("lang", ["ru", "en"])
def test_bigram_fitness_real_beats_shuffled(lang):
    real = _corpus(lang)[:400]
    chars = list(real)
    random.Random(0).shuffle(chars)
    shuffled = "".join(chars)
    assert bigram_fitness(real, lang) > bigram_fitness(shuffled, lang)


@pytest.mark.parametrize("lang", ["ru", "en"])
def test_confidence_high_for_real_low_for_random(lang):
    from cipherlab.alphabets import alphabet

    real = _corpus(lang)[:400]
    letters = alphabet(lang)
    rng = random.Random(1)
    noise = "".join(rng.choice(letters) for _ in range(400))

    conf_real = fitness_confidence(bigram_fitness(real, lang), lang)
    conf_noise = fitness_confidence(bigram_fitness(noise, lang), lang)
    assert conf_real > 0.5
    assert conf_noise < 0.35
    assert conf_real > conf_noise + 0.3


@pytest.mark.parametrize(
    "lang,text",
    [
        ("ru", "программирование это искусство решать задачи при помощи логики"),
        ("en", "cryptography is the study of techniques for secure communication"),
    ],
)
def test_caesar_not_misclassified_as_vigenere(lang, text):
    # Ядро исходного бага: обычный текст Цезаря выдавался за Виженер.
    for shift in (3, 11):
        ciphertext = encrypt_preserving_format(CaesarCipher(), text, shift, lang)
        result = auto_break(ciphertext)
        assert result.cipher == "caesar", f"{lang}/{shift}: получили {result.cipher}"
        assert result.key == shift
        assert normalize(result.plaintext, lang) == normalize(text, lang)


def test_auto_break_reports_confidence():
    text = "программирование это искусство решать задачи при помощи логики и внимания"
    ciphertext = encrypt_preserving_format(CaesarCipher(), text, 5, "ru")
    result = auto_break(ciphertext)
    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence > 0.4  # корректная расшифровка обычного текста


def test_short_gibberish_gets_low_confidence():
    # Слишком короткий/несловесный ввод не должен выдаваться за уверенный результат.
    result = auto_break("КОСИДЦЪЛМ СДЭИДЦЪЛМ ФЦНЛР ФЮР")
    assert result.confidence < 0.45


@pytest.mark.parametrize("lang,key", [("ru", "ключевое"), ("en", "password")])
def test_vigenere_recovered_on_sufficient_length(lang, key):
    # На достаточно длинном тексте ключ восстанавливается точно.
    plaintext = _corpus(lang)
    ciphertext = VigenereCipher().encrypt(plaintext, key, lang)
    result = auto_break(ciphertext)
    assert result.cipher == "vigenere"
    assert result.key == key
    assert result.plaintext == plaintext
    assert result.confidence > 0.5
