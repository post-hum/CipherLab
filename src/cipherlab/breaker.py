"""Автоматический взлом шифртекста без знания ключа, шифра и языка.

Стратегия (без «угадывания» шифра заранее — сравниваются реальные результаты):

1. Полибий распознаётся однозначно по составу шифртекста — только цифры.
2. Для остальных (Цезарь / Атбаш / Виженер / Аффинный — все они замены в одном алфавите)
   язык определяется по набору символов (кириллица ↔ латиница), после чего для
   КАЖДОГО кандидата-решения строится расшифровка и оценивается функцией
   «похожести на язык» (средний логарифм правдоподобия биграмм, см.
   stats.ngram). Побеждает вариант с наибольшей оценкой.

Почему это надёжнее прежнего подхода. Раньше семейство шифра выбиралось заранее
по индексу совпадения, и одна ошибка распознавания приводила к полному провалу
(Цезарь расшифровывался как Виженер и наоборот). Здесь распознавание и взлом
объединены: перебираются все семейства, а решает объективная оценка готового
текста. Биграммная оценка нормирована на длину, поэтому длина ключа Виженера
сравнивается честно и «переобучение» длинным ключом невозможно (см. stats.ngram)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from math import gcd

from cipherlab.alphabets import alphabet, alphabet_size, char_to_index, index_to_char, normalize
from cipherlab.ciphers.affine_wrapper import AffineCipher
from cipherlab.ciphers.atbash import AtbashCipher
from cipherlab.ciphers.caesar import CaesarCipher
from cipherlab.ciphers.polybius import PolybiusCipher
from cipherlab.ciphers.vigenere import VigenereCipher
from cipherlab.format_preserving import decrypt_preserving_format
from cipherlab.recognizer import is_polybius_ciphertext
from cipherlab.stats.chi_squared import chi_squared_stat
from cipherlab.stats.frequency import load_json
from cipherlab.stats.ngram import bigram_fitness, fitness_confidence

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

LANGS = ("ru", "en")

# Кандидат длины ключа Виженера принимается только если на каждый столбец
# (= на одну букву ключа) приходится хотя бы столько букв шифртекста: по
# столбцу восстанавливается свой сдвиг монограммным анализом, а на слишком
# коротком столбце эта оценка вырождается в шум.
_MIN_CHARS_PER_COLUMN = 8
_MAX_KEY_LEN = 20

# Более длинный ключ принимается вместо более короткого, только если он лучше по
# биграммной оценке не меньше чем на эту величину. Так при равных (с точностью
# до шума) вариантах выбирается более простое объяснение — короткий ключ. Для
# чистого Цезаря это гарантирует длину 1 (а не кратную ей 2, 3, …).
_LONGER_KEY_MARGIN = 0.2

_REFERENCE_CACHE: dict[str, dict[str, float]] = {}
# эталонные частоты как массив, выровненный по индексам букв алфавита
_REFERENCE_VECTOR_CACHE: dict[str, list[float]] = {}


def _reference_monogram(lang: str) -> dict[str, float]:
    """Опубликованная эталонная таблица частот букв (для отображаемой χ²-оценки)."""
    if not _REFERENCE_CACHE:
        published = load_json(DATA_DIR / "published_reference.json")
        for code in LANGS:
            _REFERENCE_CACHE[code] = published[code]
    return _REFERENCE_CACHE[lang]


def _reference_vector(lang: str) -> list[float]:
    if lang not in _REFERENCE_VECTOR_CACHE:
        reference = _reference_monogram(lang)
        _REFERENCE_VECTOR_CACHE[lang] = [reference.get(ch, 0.0) for ch in alphabet(lang)]
    return _REFERENCE_VECTOR_CACHE[lang]


@dataclass
class BreakResult:
    cipher: str
    lang: str
    key: object
    plaintext: str
    score: float  # монограммный χ² восстановленного текста: меньше = лучше
    confidence: float = 0.0  # [0, 1], насколько результат похож на естественный язык


@dataclass
class _Candidate:
    cipher: str
    lang: str
    key: object
    plaintext: str
    fitness: float  # биграммная оценка: больше = лучше (для ВЫБОРА варианта)


def _best_caesar_shift(column: str, lang: str) -> int:
    """Сдвиг Цезаря для столбца по минимуму монограммного χ².

    Столбец Виженера — это буквы, зашифрованные одним сдвигом, но НЕ соседние в
    открытом тексте, поэтому биграммы в нём бессмысленны и здесь применяется
    именно монограммный анализ (частоты отдельных букв столбца ≈ частоты языка).

    Гистограмма букв столбца считается один раз, а каждый сдвиг оценивается по
    ней за O(n) без повторной расшифровки — при расшифровке сдвигом s открытая
    буква p соответствует шифрбукве (p + s) mod n, поэтому её наблюдаемая частота
    берётся из готовой гистограммы циклическим сдвигом индекса.
    """
    n = alphabet_size(lang)
    total = len(column)
    if total == 0:
        return 0

    counts = [0] * n
    for ch in column:
        counts[char_to_index(ch, lang)] += 1

    reference = _reference_vector(lang)
    best_shift = 0
    best_chi = float("inf")
    for shift in range(n):
        chi = 0.0
        for p in range(n):
            expected = reference[p] * total
            if expected == 0.0:
                continue
            observed = counts[(p + shift) % n]
            diff = observed - expected
            chi += diff * diff / expected
        if chi < best_chi:
            best_chi = chi
            best_shift = shift
    return best_shift


def _best_caesar_by_bigram(text: str, lang: str) -> tuple[int, str, float]:
    """Единственный сдвиг Цезаря по максимуму биграммной оценки всего текста.

    Здесь текст не разбит на столбцы, поэтому его биграммы — это реальные
    соседние буквы, и биграммная оценка применима напрямую. Она заметно
    надёжнее монограммного χ² на коротком тексте (десятки букв), где частоты
    отдельных букв ещё слишком зашумлены.
    """
    cipher = CaesarCipher()
    best_shift, best_plain, best_fitness = 0, text, float("-inf")
    for shift in range(alphabet_size(lang)):
        candidate = cipher.decrypt(text, shift, lang)
        fitness = bigram_fitness(candidate, lang)
        if fitness > best_fitness:
            best_shift, best_plain, best_fitness = shift, candidate, fitness
    return best_shift, best_plain, best_fitness


def _solve_with_key_length(ciphertext: str, lang: str, key_len: int) -> list[int]:
    """Восстанавливает по одному сдвигу на каждый из key_len столбцов."""
    return [_best_caesar_shift(ciphertext[col::key_len], lang) for col in range(key_len)]


def _decrypt_vigenere_with_shifts(ciphertext: str, shifts: list[int], lang: str) -> str:
    """Расшифровка Виженера с использованием списка сдвигов."""
    n = alphabet_size(lang)
    result = []
    for i, ch in enumerate(ciphertext):
        shift = shifts[i % len(shifts)]
        result.append(index_to_char((char_to_index(ch, lang) - shift) % n, lang))
    return "".join(result)


def _break_shift_family(ciphertext: str, lang: str) -> _Candidate:
    """Взлом Цезаря/Виженера: перебор длины ключа, выбор по биграммной оценке.

    Длина 1 — это, по определению, шифр Цезаря (один сдвиг на весь текст),
    поэтому такой результат помечается как caesar с числовым ключом-сдвигом.
    """
    max_key_len = max(1, min(_MAX_KEY_LEN, len(ciphertext) // _MIN_CHARS_PER_COLUMN))

    best: _Candidate | None = None
    for key_len in range(1, max_key_len + 1):
        if key_len == 1:
            # Цезарь: сдвиг подбирается по биграммам всего текста (надёжнее на
            # коротком тексте), а не по столбцовому монограммному χ².
            shift, plaintext, fitness = _best_caesar_by_bigram(ciphertext, lang)
            candidate = _Candidate("caesar", lang, shift, plaintext, fitness)
        else:
            shifts = _solve_with_key_length(ciphertext, lang, key_len)
            plaintext = _decrypt_vigenere_with_shifts(ciphertext, shifts, lang)
            fitness = bigram_fitness(plaintext, lang)
            key_display = "".join(index_to_char(s, lang) for s in shifts)
            candidate = _Candidate("vigenere", lang, key_display, plaintext, fitness)

        # Более длинный ключ должен выигрывать с запасом (Оккам: при прочих
        # равных предпочитаем короткий ключ), поэтому у уже найденного варианта
        # есть «фора» _LONGER_KEY_MARGIN.
        if best is None or fitness > best.fitness + _LONGER_KEY_MARGIN:
            best = candidate
    return best


def _break_atbash(ciphertext: str, lang: str) -> _Candidate:
    """Взлом шифра Атбаш."""
    plaintext = AtbashCipher().decrypt(ciphertext, None, lang)
    return _Candidate("atbash", lang, None, plaintext, bigram_fitness(plaintext, lang))


def _break_affine(ciphertext: str, lang: str) -> _Candidate | None:
    """Взлом аффинного шифра перебором всех возможных ключей.
    
    Аффинный шифр имеет ключевое пространство:
    - Русский: φ(33) * 33 = 20 * 33 = 660 ключей
    - Английский: φ(26) * 26 = 12 * 26 = 312 ключей
    
    Для каждого ключа расшифровываем текст и оцениваем биграммную похожесть.
    Выбираем ключ с максимальной оценкой.
    """
    n = alphabet_size(lang)
    cipher = AffineCipher()
    best: _Candidate | None = None
    
    # Перебираем все допустимые a (взаимно простые с n)
    for a in range(1, n):
        if gcd(a, n) != 1:
            continue
        # Перебираем все b
        for b in range(n):
            try:
                plaintext = cipher.decrypt(ciphertext, (a, b), lang)
                fitness = bigram_fitness(plaintext, lang)
                if best is None or fitness > best.fitness:
                    best = _Candidate("affine", lang, (a, b), plaintext, fitness)
            except Exception:
                # Если ключ невалидный или ошибка расшифровки - пропускаем
                continue
    
    return best


def _break_substitution(raw_text: str) -> _Candidate | None:
    """Лучший кандидат среди Цезаря/Атбаша/Виженера/Аффинного по всем языкам."""
    best: _Candidate | None = None
    for lang in LANGS:
        text = normalize(raw_text, lang)
        if len(text) < 2:
            continue  # слишком мало букв этого алфавита — не тот язык / не текст
        
        # Проверяем все кандидаты
        candidates = [
            _break_shift_family(text, lang),   # Цезарь + Виженер
            _break_atbash(text, lang),          # Атбаш
            _break_affine(text, lang),          # Аффинный ← НОВОЕ!
        ]
        
        for candidate in candidates:
            if candidate is None:
                continue
            if best is None or candidate.fitness > best.fitness:
                best = candidate
    
    return best


def _break_polybius(raw_text: str) -> _Candidate | None:
    """Взлом шифра Полибия."""
    best: _Candidate | None = None
    for lang in LANGS:
        plaintext = PolybiusCipher().decrypt(raw_text, None, lang)
        if len(plaintext) < 2:
            continue
        fitness = bigram_fitness(plaintext, lang)
        if best is None or fitness > best.fitness:
            best = _Candidate("polybius", lang, None, plaintext, fitness)
    return best


_CIPHER_CLASSES = {
    "atbash": AtbashCipher,
    "caesar": CaesarCipher,
    "vigenere": VigenereCipher,
    "affine": AffineCipher,  # ← НОВОЕ!
}


def auto_break(raw_text: str) -> BreakResult:
    """Определяет шифр, язык и ключ и возвращает восстановленный открытый текст."""
    if is_polybius_ciphertext(raw_text):
        best = _break_polybius(raw_text)
    else:
        best = _break_substitution(raw_text)

    if best is None:
        raise ValueError("не удалось взломать шифртекст: пустой или неподдерживаемый ввод")

    # Взлом идёт по нормализованному тексту (иначе пробелы и пунктуация сбили бы
    # статистику), а найденные шифр/ключ применяются заново к ИСХОДНОМУ тексту с
    # сохранением пробелов, пунктуации и регистра. Полибий выводит буквы без
    # исходного форматирования — его результат берётся как есть.
    if best.cipher == "polybius":
        plaintext = best.plaintext
    else:
        cipher = _CIPHER_CLASSES[best.cipher]()
        plaintext = decrypt_preserving_format(cipher, raw_text, best.key, best.lang)

    score = chi_squared_stat(normalize(plaintext, best.lang), _reference_monogram(best.lang))
    confidence = fitness_confidence(best.fitness, best.lang)
    return BreakResult(best.cipher, best.lang, best.key, plaintext, score, confidence)
