"""Веб-интерфейс для шифрования/дешифрования и автоматического взлома
классических шифров.

Запуск: streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Добавляем src в путь
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd
import streamlit as st

from cipherlab.breaker import auto_break
from cipherlab.ciphers import CIPHERS
from cipherlab.ciphers.affine_wrapper import AffineCipher
from cipherlab.format_preserving import decrypt_preserving_format, encrypt_preserving_format
from cipherlab.stats.frequency import load_json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

LANG_NAMES = {"ru": "Русский", "en": "English"}
CIPHER_NAMES = {
    "caesar": "Цезарь",
    "atbash": "Атбаш",
    "polybius": "Полибий",
    "vigenere": "Виженер",
    "affine": "Аффинный",
}

# Настройка страницы
st.set_page_config(page_title="Криптоанализ классических шифров", layout="wide")
st.title("Автоматическое распознавание и криптоанализ классических шифров")

tab_manual, tab_auto, tab_freq = st.tabs([
    "Шифрование / дешифрование",
    "Автоматический взлом",
    "Частотный анализ",
])

# ---------------------------------------------------------------------------
# Вкладка 1: ручное шифрование / дешифрование
# ---------------------------------------------------------------------------
with tab_manual:
    st.subheader("Ручной режим")
    col1, col2, col3 = st.columns(3)
    with col1:
        cipher_name = st.selectbox(
            "Шифр", list(CIPHER_NAMES), format_func=lambda c: CIPHER_NAMES[c], key="manual_cipher"
        )
    with col2:
        lang = st.selectbox("Язык", list(LANG_NAMES), format_func=lambda l: LANG_NAMES[l], key="manual_lang")
    with col3:
        mode = st.radio("Режим", ["Зашифровать", "Расшифровать"], horizontal=True, key="manual_mode")

    key: object = None
    if cipher_name == "caesar":
        key = st.number_input("Ключ (сдвиг)", min_value=0, max_value=32, value=3, step=1)
    elif cipher_name == "vigenere":
        key = st.text_input("Ключ (слово)", value="ключ" if lang == "ru" else "key")
    elif cipher_name == "affine":
        col_a, col_b = st.columns(2)
        with col_a:
            a = st.number_input("a (должно быть взаимно просто с размером алфавита)", 
                               min_value=1, value=5, step=1)
        with col_b:
            b = st.number_input("b", min_value=0, value=8, step=1)
        key = (a, b)

    preserve_format = False
    if cipher_name == "polybius":
        st.caption(
            "Полибий кодирует каждую букву парой цифр — сохранение пробелов, "
            "пунктуации и регистра исходного текста здесь не применяется."
        )
    else:
        preserve_format = st.checkbox(
            "Сохранить пробелы, пунктуацию и регистр", value=True, key="manual_preserve"
        )

    text = st.text_area("Текст", height=150, key="manual_text")

    if st.button("Выполнить", key="manual_run"):
        cipher = CIPHERS[cipher_name]
        try:
            if preserve_format:
                if mode == "Зашифровать":
                    result = encrypt_preserving_format(cipher, text, key, lang)
                else:
                    result = decrypt_preserving_format(cipher, text, key, lang)
            else:
                if mode == "Зашифровать":
                    result = cipher.encrypt(text, key, lang)
                else:
                    result = cipher.decrypt(text, key, lang)
            st.text_area("Результат", value=result, height=150)
        except ValueError as exc:
            st.error(str(exc))

# ---------------------------------------------------------------------------
# Вкладка 2: автоматическое распознавание и взлом
# ---------------------------------------------------------------------------
with tab_auto:
    st.subheader("Автоматический взлом (без указания шифра, языка и ключа)")
    ciphertext = st.text_area("Шифртекст", height=150, key="auto_text")

    if st.button("Взломать", key="auto_run"):
        if not ciphertext.strip():
            st.warning("Введите шифртекст.")
        else:
            try:
                result = auto_break(ciphertext)
            except ValueError as exc:
                st.error(str(exc))
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Шифр", CIPHER_NAMES.get(result.cipher, result.cipher))
                c2.metric("Язык", LANG_NAMES.get(result.lang, result.lang))
                c3.metric("Уверенность", f"{result.confidence * 100:.0f}%")

                if result.confidence < 0.40:
                    st.warning(
                        "Низкая уверенность: восстановленный текст слабо похож на "
                        "естественный язык. Чаще всего причина — слишком короткий "
                        "шифртекст. Статистический анализ надёжен примерно от 60–80 "
                        "букв для Цезаря/Атбаша и от ~150 букв для Виженера."
                    )

                if result.key is not None:
                    st.write(f"**Восстановленный ключ:** `{result.key}`")
                st.caption(f"Оценка χ² (меньше — лучше): {result.score:.1f}")
                st.text_area("Восстановленный открытый текст", value=result.plaintext, height=150)

# ---------------------------------------------------------------------------
# Вкладка 3: обзор частотных таблиц
# ---------------------------------------------------------------------------
with tab_freq:
    st.subheader("Эталонные частотные таблицы")
    freq_lang = st.selectbox(
        "Язык", list(LANG_NAMES), format_func=lambda l: LANG_NAMES[l], key="freq_lang"
    )

    mono = load_json(DATA_DIR / f"freq_{freq_lang}_monogram.json")
    published = load_json(DATA_DIR / "published_reference.json")[freq_lang]

    letters = sorted(mono, key=mono.get, reverse=True)
    df = pd.DataFrame({
        "буква": letters,
        "наш корпус": [mono[ch] for ch in letters],
        "опубликованная таблица": [published.get(ch, 0.0) for ch in letters],
    }).set_index("буква")

    st.bar_chart(df)

    st.subheader("Самые частые биграммы")
    bigrams = load_json(DATA_DIR / f"freq_{freq_lang}_bigram.json")
    top_bigrams = sorted(bigrams.items(), key=lambda kv: kv[1], reverse=True)[:20]
    st.dataframe(
        pd.DataFrame(top_bigrams, columns=["биграмма", "частота"]),
        hide_index=True,
    )

# ============================================================
# ГЛАВНАЯ ТОЧКА ВХОДА - ТОЛЬКО ДЛЯ ПРЯМОГО ЗАПУСКА
# ============================================================
if __name__ == "__main__":
    # Это НЕ запускает сервер!
    # Streamlit сам запускает сервер при команде streamlit run
    pass
