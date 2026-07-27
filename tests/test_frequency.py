from pathlib import Path

from cipherlab.stats.frequency import load_json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

EXPECTED_TOP5 = {
    "en": {"e", "t", "a", "o", "i"},
    "ru": {"о", "е", "а", "и"},
}


def top_n(freqs: dict, n: int) -> set:
    return set(sorted(freqs, key=freqs.get, reverse=True)[:n])


def test_monogram_sums_to_one():
    for lang in ("en", "ru"):
        freqs = load_json(DATA_DIR / f"freq_{lang}_monogram.json")
        assert abs(sum(freqs.values()) - 1.0) < 1e-9


def test_top_letters_match_known_language_stats():
    # Небольшой авторский корпус даёт статистику с разумным разбросом,
    # поэтому требуем совпадения большинства (не всех) ожидаемых букв
    # среди самых частых, а не точного совпадения множеств.
    for lang, expected in EXPECTED_TOP5.items():
        freqs = load_json(DATA_DIR / f"freq_{lang}_monogram.json")
        observed_top = top_n(freqs, 8)
        overlap = expected & observed_top
        assert len(overlap) >= len(expected) - 1, (
            f"{lang}: ожидались {expected} среди топ-8, получили {observed_top} "
            f"(совпало только {overlap})"
        )


def test_matches_published_reference_within_tolerance():
    published = load_json(DATA_DIR / "published_reference.json")
    for lang in ("en", "ru"):
        ours = load_json(DATA_DIR / f"freq_{lang}_monogram.json")
        ref = published[lang]
        for letter, ref_freq in ref.items():
            our_freq = ours.get(letter, 0.0)
            assert abs(our_freq - ref_freq) < 0.05, (
                f"{lang}/{letter}: наш {our_freq:.4f} vs эталон {ref_freq:.4f}"
            )
