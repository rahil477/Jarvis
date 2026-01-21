#!/usr/bin/env python3
"""
Vosk STT Test Aracı
Vosk veya Google API ile ses tanımasını test et
"""

import sys
import os
import subprocess

# Python 3.11 venv yolunu belirle
venv_path = os.path.join(os.path.dirname(__file__), ".venv11", "Scripts", "python.exe")

if not os.path.exists(venv_path):
    print("[HATA] Python 3.11 venv bulunamadı")
    sys.exit(1)

test_code = """
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Jarvis"))

print("[1/3] Vosk modulu kontrol ediliyor...")
try:
    import vosk
    print("[TAMAM] Vosk yüklü")
except:
    print("[UYARI] Vosk yüklü değil - Google API kullanılacak")

print("[2/3] PyAudio kontrol ediliyor...")
try:
    import pyaudio
    p = pyaudio.PyAudio()
    print(f"[TAMAM] PyAudio yüklü ({p.get_device_count()} cihaz)")
    p.terminate()
except Exception as e:
    print(f"[HATA] PyAudio hatası: {e}")

print("[3/3] SpeechRecognition kontrol ediliyor...")
try:
    import speech_recognition as sr
    print("[TAMAM] SpeechRecognition yüklü")
except:
    print("[HATA] SpeechRecognition yüklü değil")

print()
print("[TEST] Mikrofon test edilecek...")
print("Lütfen 3 saniye içinde konuşun...")
"""

# Testi çalıştır
result = subprocess.run([venv_path, "-c", test_code], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
