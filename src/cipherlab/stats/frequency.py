"""Подсчёт частот монограмм и биграмм, загрузка/сохранение таблиц в JSON."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from cipherlab.alphabets import alphabet


def _get_data_dir() -> Path:
    """Определяет правильную папку с данными для PyInstaller и разработки."""
    # Если запущено из PyInstaller
    if getattr(sys, 'frozen', False):
        # sys._MEIPASS - временная папка с распакованными ресурсами
        if hasattr(sys, '_MEIPASS'):
            bundled_data = Path(sys._MEIPASS) / 'data'
            if bundled_data.exists():
                return bundled_data
        
        # Фолбэк: data рядом с .exe
        exe_dir = Path(sys.executable).parent
        local_data = exe_dir / 'data'
        if local_data.exists():
            return local_data
    
    # Обычный запуск из исходников
    project_root = Path(__file__).resolve().parents[3]
    project_data = project_root / 'data'
    if project_data.exists():
        return project_data
    
    return Path('data')


def monogram_freq(text: str, lang: str) -> dict[str, float]:
    letters = alphabet(lang)
    counts = Counter(ch for ch in text if ch in letters)
    total = sum(counts.values())
    if total == 0:
        return {ch: 0.0 for ch in letters}
    return {ch: counts.get(ch, 0) / total for ch in letters}


def bigram_freq(text: str, lang: str, top_n: int = 200) -> dict[str, float]:
    letters = set(alphabet(lang))
    bigrams = [text[i:i+2] for i in range(len(text)-1) if text[i] in letters and text[i+1] in letters]
    counts = Counter(bigrams)
    total = sum(counts.values())
    if total == 0:
        return {}
    freqs = {bg: c/total for bg, c in counts.most_common(top_n)}
    return freqs


def save_json(data: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_json(path: str | Path) -> dict:
    path = Path(path)
    if path.is_absolute() and path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    data_dir = _get_data_dir()
    full_path = data_dir / path.name
    if not full_path.exists():
        raise FileNotFoundError(
            f"Файл {path.name} не найден! Искали в: {data_dir}\n"
            f"Убедитесь, что папка data находится рядом с исполняемым файлом."
        )
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)
