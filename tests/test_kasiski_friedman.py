from pathlib import Path

from cipherlab.alphabets import normalize
from cipherlab.ciphers.vigenere import VigenereCipher
from cipherlab.stats.friedman import friedman_key_length
from cipherlab.stats.kasiski import kasiski_examination

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw_corpora"


def _load_plaintext(lang: str) -> str:
    path = DATA_DIR / f"{lang}_sample.txt"
    return normalize(path.read_text(encoding="utf-8"), lang)


def test_kasiski_recovers_true_key_length():
    for lang, key in [("en", "cipher"), ("ru", "ключик")]:
        plaintext = _load_plaintext(lang)
        ciphertext = VigenereCipher().encrypt(plaintext, key, lang)
        true_len = len(normalize(key, lang))

        candidates = kasiski_examination(ciphertext)
        assert true_len in candidates[:5], (
            f"{lang}: истинная длина {true_len} не среди топ-кандидатов {candidates[:5]}"
        )


def test_friedman_estimates_close_to_true_key_length():
    for lang, key in [("en", "cipher"), ("ru", "ключик")]:
        plaintext = _load_plaintext(lang)
        ciphertext = VigenereCipher().encrypt(plaintext, key, lang)
        true_len = len(normalize(key, lang))

        estimate = friedman_key_length(ciphertext, lang)
        assert abs(estimate - true_len) <= 2, (
            f"{lang}: оценка Фридмана {estimate:.2f} далеко от истинной {true_len}"
        )
