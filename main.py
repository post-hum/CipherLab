#!/usr/bin/env python3
"""Обёртка для запуска Streamlit-приложения из собранного бинарника."""
import sys
import os
from streamlit.web import cli as stcli

if __name__ == '__main__':
    # Если запущено из PyInstaller
    if getattr(sys, 'frozen', False):
        # Путь к скрипту внутри временной папки _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            script_path = os.path.join(sys._MEIPASS, 'app', 'streamlit_app.py')
        else:
            script_path = 'app/streamlit_app.py'
    else:
        script_path = 'app/streamlit_app.py'

    # Эмулируем команду: streamlit run <script> --server.headless true --server.port 8501
    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--server.headless", "true",
        "--server.port", "8501"
    ]
    sys.exit(stcli.main())
