"""
JARVIS v4.0 - Audio & Webcam Enhancement Module
Ses və Webcam funksiyalarını təkmilləşdirən modul
"""
import os
import cv2
import asyncio
import edge_tts
import random
import time
import threading
import ollama

# Windows Media Player COM for reliable audio playback
try:
    import win32com.client
    HAS_WMP = True
except:
    HAS_WMP = False
    from playsound import playsound

TTS_VOICE = "tr-TR-AhmetNeural"
OLLAMA_VISION_MODEL = "llava"

def speak_enhanced(text):
    """Gelişmiş ses çıkışı - Windows Media Player COM kullanır"""
    if not text: return
    
    def _play_sync():
        f = os.path.abspath(f"audio_{random.randint(1000,9999)}.mp3")
        try:
            # TTS ile MP3 oluştur
            async def _save():
                await edge_tts.Communicate(text, TTS_VOICE).save(f)
            asyncio.run(_save())
            
            # Windows Media Player ile çal
            if HAS_WMP:
                player = win32com.client.Dispatch("WMPlayer.OCX")
                player.url = f
                player.controls.play()
                # Oynatma bitene kadar bekle
                while player.playState not in [1, 8]:  # 1=Stopped, 8=MediaEnded
                    time.sleep(0.1)
                player.close()
            else:
                # Fallback: playsound
                playsound(f)
                
        except Exception as e:
            print(f"[SES HATASI]: {e}")
        finally:
            # Dosyayı temizle
            time.sleep(0.5)
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
    
    # Arka planda çalıştır
    threading.Thread(target=_play_sync, daemon=True).start()

def webcam_capture_and_analyze(prompt="Webcam'de ne görüyorsun?"):
    """
    Webcam'den görüntü yakalar ve Ollama Vision ile analiz eder.
    Returns: Analiz sonucu (string)
    """
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return "❌ Webcam açılamadı. Lütfen kamera bağlantısını kontrol edin."
    
    # Kamerayı ısıt (ilk birkaç frame genelde karanlık olur)
    for _ in range(5):
        cap.read()
    
    # Gerçek görüntüyü yakala
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "❌ Webcam'den görüntü alınamadı."
    
    # Görüntüyü kaydet
    img_path = "webcam_snapshot.png"
    cv2.imwrite(img_path, frame)
    
    try:
        # Ollama Vision ile analiz
        response = ollama.chat(
            model=OLLAMA_VISION_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [img_path]
            }]
        )
        
        analysis = response['message']['content']
        
        # Temizlik
        if os.path.exists(img_path):
            os.remove(img_path)
        
        return f"📷 Webcam Analizi:\n{analysis}"
        
    except Exception as e:
        return f"❌ Vision analiz hatası: {e}"

def webcam_live_monitor(duration_seconds=5):
    """
    Webcam'i belirli süre izler ve özet çıkarır.
    duration_seconds: Kaç saniye izlenecek
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Webcam bulunamadı."
    
    observations = []
    start_time = time.time()
    
    while (time.time() - start_time) < duration_seconds:
        ret, frame = cap.read()
        if ret:
            # Her saniye bir snapshot al
            if int(time.time() - start_time) % 1 == 0:
                cv2.imwrite(f"temp_frame_{len(observations)}.png", frame)
                observations.append(f"temp_frame_{len(observations)}.png")
        time.sleep(0.2)
    
    cap.release()
    
    # İlk ve son frame'i analiz et
    if observations:
        result = f"Webcam {duration_seconds} saniye izlendi. {len(observations)} snapshot alındı."
        # Cleanup
        for obs in observations:
            if os.path.exists(obs):
                os.remove(obs)
        return result
    
    return "İzleme başarısız."

# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Ses ve Webcam Modülü Test Ediliyor...")
    
    # Ses testi
    print("\n1. Ses Testi:")
    speak_enhanced("Salam Rahil efendim. Ses sistemi test edilir.")
    time.sleep(3)
    
    # Webcam testi
    print("\n2. Webcam Testi:")
    result = webcam_capture_and_analyze("Önünde kim var? Ne görüyorsun?")
    print(result)
