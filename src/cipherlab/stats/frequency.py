"""Подсчёт частот монограмм и биграмм, загрузка/сохранение таблиц в JSON."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from cipherlab.alphabets import alphabet


def _get_data_dir() -> Path:
    """Определяет правильную папку с данными.
    
    Приоритет:
    1. Папка рядом с исполняемым файлом (для PyInstaller)
    2. Папка data в корне проекта
    3. Папка src/cipherlab/../data
    """
    # Если запущено из PyInstaller
    if getattr(sys, 'frozen', False):
        # Бинарник .exe
        base_dir = Path(sys.executable).parent
        # Пробуем найти data рядом с .exe
        data_dir = base_dir / 'data'
        if data_dir.exists():
            return data_dir
        # Пробуем найти в папке выше (для структуры dist/)
        data_dir = base_dir.parent / 'data'
        if data_dir.exists():
            return data_dir
    
    # Обычный Python запуск
    # Пробуем найти data в корне проекта
    project_root = Path(__file__).resolve().parents[3]  # cipherlab/stats/ -> проект
    data_dir = project_root / 'data'
    if data_dir.exists():
        return data_dir
    
    # Если не нашли, возвращаем путь по умолчанию
    return Path('data')


def monogram_freq(text: str, lang: str) -> dict[str, float]:
    """Частота каждой буквы алфавита в нормализованном тексте (доли от 1.0)."""
    letters = alphabet(lang)
    counts = Counter(ch for ch in text if ch in letters)
    total = sum(counts.values())
    if total == 0:
        return {ch: 0.0 for ch in letters}
    return {ch: counts.get(ch, 0) / total for ch in letters}


def bigram_freq(text: str, lang: str, top_n: int = 200) -> dict[str, float]:
    """Частота перекрывающихся биграмм; возвращает top_n самых частых."""
    letters = set(alphabet(lang))
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)
               if text[i] in letters and text[i + 1] in letters]
    counts = Counter(bigrams)
    total = sum(counts.values())
    if total == 0:
        return {}
    freqs = {bg: c / total for bg, c in counts.most_common(top_n)}
    return freqs


def save_json(data: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_json(path: str | Path) -> dict:
    """Загружает JSON файл с автоматическим поиском пути."""
    path = Path(path)
    
    # Если путь абсолютный или файл существует - загружаем
    if path.is_absolute() or path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Пробуем найти относительно папки data
    data_dir = _get_data_dir()
    full_path = data_dir / path.name
    
    if not full_path.exists():
        raise FileNotFoundError(
            f"Файл {path.name} не найден! Искали в: {data_dir}\n"
            f"Убедитесь, что файлы data находятся рядом с исполняемым файлом."
        )
    
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)
