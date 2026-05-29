@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo No se encontro el entorno virtual. Ejecuta install.bat primero.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
streamlit run app.py
