"""Строит эталонные таблицы частот из вложенных корпусов data/raw_corpora.

Запуск: python -m cipherlab.build_frequency_data
"""
from __future__ import annotations

from pathlib import Path

from cipherlab.alphabets import normalize
from cipherlab.stats.frequency import bigram_freq, monogram_freq, save_json

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw_corpora"

CORPORA = {"ru": RAW_DIR / "ru_sample.txt", "en": RAW_DIR / "en_sample.txt"}


def build() -> None:
    for lang, path in CORPORA.items():
        raw_text = path.read_text(encoding="utf-8")
        text = normalize(raw_text, lang)
        if not text:
            raise ValueError(f"корпус для языка {lang!r} пуст после нормализации: {path}")

        mono = monogram_freq(text, lang)
        bi = bigram_freq(text, lang)

        save_json(mono, DATA_DIR / f"freq_{lang}_monogram.json")
        save_json(bi, DATA_DIR / f"freq_{lang}_bigram.json")
        print(f"[{lang}] буквы: {len(text)}, уникальных биграмм: {len(bi)} -> сохранено")


if __name__ == "__main__":
    build()
