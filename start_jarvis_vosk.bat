@echo off
REM Vosk STT ile JARVIS Başlatıcı
cd /d "%~dp0"
echo [JARVIS] Desktop Voice Assistant - Python 3.11
echo.
echo [1] Checking Python 3.11 environment...
if not exist ".venv11\Scripts\python.exe" (
    echo [ERROR] .venv11 not found!
    exit /b 1
)
echo [OK] Python 3.11 environment found
echo.
echo [2] Checking dependencies...
".venv11\Scripts\python.exe" -c "import vosk, pyaudio, speech_recognition as sr; print('[OK] All dependencies ready')" 2>nul || (
    echo [WARNING] Some dependencies missing, installing...
    ".venv11\Scripts\python.exe" -m pip install -q vosk pocketsphinx 2>nul
)
echo.
echo [3] Starting JARVIS...
echo.
".venv11\Scripts\python.exe" "Jarvis\jarvis.py"
pause
