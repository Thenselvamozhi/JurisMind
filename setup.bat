@echo off
echo ========================================
echo   JurisMind - Setup Script (Windows)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

REM Create virtual environment
echo.
echo [*] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo.
echo [*] Installing dependencies...
pip install -r requirements.txt

REM Train ML model
echo.
echo [*] Training ML model...
python ml_model/train_model.py

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To run JurisMind:
echo   1. Add your Groq API key to .env file
echo   2. Open Terminal 1: uvicorn backend.main:app --reload --port 8000
echo   3. Open Terminal 2: streamlit run frontend/app.py
echo.
pause
