#!/usr/bin/env python3
"""
JARVIS Ses Diagnostik Aləti
Ses sisteminizin işlərə qoyulmasını kontrol edir
"""

import sys
import time
import os

print("="*70)
print(" "*15 + "JARVIS SES DIAGNOSTIKI - KONTROL ETMƏ")
print("="*70)
print()

# Test 1: PyAudio
print("[1/6] PyAudio modulunu yoxlayıram...")
try:
    import pyaudio
    p = pyaudio.PyAudio()
    mic_count = p.get_device_count()
    print(f"  ✓ PyAudio tapıldı")
    print(f"  ✓ {mic_count} səs cihazı tapıldı")
    p.terminate()
except Exception as e:
    print(f"  ✗ PyAudio xətası: {e}")
    sys.exit(1)

# Test 2: SpeechRecognition
print("\n[2/6] SpeechRecognition modulunu yoxlayıram...")
try:
    import speech_recognition as sr
    print(f"  ✓ SpeechRecognition tapıldı")
except Exception as e:
    print(f"  ✗ SpeechRecognition xətası: {e}")
    sys.exit(1)

# Test 3: Mikrofon Siyahısı
print("\n[3/6] Mikrofon cihazlarını sıralayıram...")
try:
    import pyaudio
    p = pyaudio.PyAudio()
    print(f"  Mövcud mikrofon cihazları:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['max_input_channels'] > 0:
            print(f"    [{i}] {info['name']} (Input kanalları: {info['max_input_channels']})")
    p.terminate()
except Exception as e:
    print(f"  ✗ Xəta: {e}")

# Test 4: Səs Tənzimlənməsi
print("\n[4/6] Səs kalibrasyonunu sınayıram (3 saniyə)...")
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("  Sust qalın, kalibrə edilir...")
        r.adjust_for_ambient_noise(source, duration=3)
        print("  ✓ Kalibrə edildi")
except Exception as e:
    print(f"  ✗ Kalibrə xətası: {e}")

# Test 5: Səs Qeydi
print("\n[5/6] Səs qeydi sınayıram (5 saniyə dinləyin)...")
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("  >>> DANIŞIN! (5 saniyə)...")
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        print("  ✓ Səs qeyd edildi")
except sr.WaitTimeoutError:
    print("  ✗ Vaxt bitdi - səs alınmadı")
except sr.UnknownValueError:
    print("  ✓ Səs alındı amma sözlər tanınmadı (bunun problem yoxdur)")
except Exception as e:
    print(f"  ✗ Xəta: {e}")

# Test 6: İnternet Bağlantısı
print("\n[6/6] İnternet bağlantısını yoxlayıram...")
try:
    import urllib.request
    urllib.request.urlopen('http://8.8.8.8', timeout=3)
    print("  ✓ İnternet bağlantısı var")
    
    # Google API testi
    print("  Google Speech API'sini sınayıram...")
    import speech_recognition as sr
    r = sr.Recognizer()
    
    # Test audio (sessiz)
    with sr.Microphone() as source:
        print("    >>> Bir söz DANIŞIN (tez!)...")
        audio = r.listen(source, timeout=3, phrase_time_limit=3)
    
    try:
        text = r.recognize_google(audio, language="tr-TR")
        print(f"  ✓ Tanıdı: '{text}'")
    except sr.UnknownValueError:
        print("  ⚠ Səs oldu ama sözlər tanınmadı (bağlantı OK)")
    except sr.RequestError as e:
        print(f"  ✗ Google API Xətası: {e}")
        
except urllib.error.URLError:
    print("  ✗ İnternet bağlantısı yoxdur!")
    print("     Google Speech API'sine bağlanmaq üçün internet lazımdır")
except Exception as e:
    print(f"  ⚠ Xəta: {e}")

print("\n" + "="*70)
print("SONUÇLAR:")
print("="*70)
print("""
✓ Hər şey OK görünür!

Əgər "Səs oldu ama sözlər tanınmadı" görürsünüzsə:
  - Daha AYDINCA danışın
  - Mikrofonu kalibrə etdikdən sonra danışın
  - Arxa planı səsini azaldın

Əgər "İnternet bağlantısı yoxdur" görürsünüzsə:
  - Kabel internet bağlayın
  - WiFi-ə bağlanın
  - Router'ə klik edin

Əgər "PyAudio" xətası varsa:
  - Python 3.11 istifadə edir misiniz? (.venv11)
  - Yenidən quraşdırın: pip install pyaudio
""")
print("="*70)
