@echo off
REM Vosk STT Hızlı Test
cd /d "%~dp0"
echo [TEST] Vosk STT ile ses tanimas testi
echo.

REM Model kontrol
if exist "model\vosk-model-small-en-us-0.15" (
    echo [OK] Vosk model bulundu (English)
) else if exist "model\tr" (
    echo [OK] Vosk Turkce model bulundu
) else (
    echo [UYARI] Vosk model bulunamadi - Google API kullanilacak
)

echo.
echo [TEST] Python ortami kontrol ediliyor...
".venv11\Scripts\python.exe" -c "import vosk, pyaudio; print('[OK] Vosk ve PyAudio hazir')" 2>&1

echo.
echo [TEST] Jarvis baslatiliyor... (Gir: salam jarvis)
echo.
".venv11\Scripts\python.exe" "Jarvis\jarvis.py"
pause
