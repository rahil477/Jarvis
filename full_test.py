import ollama
import asyncio
import edge_tts
import os
from playsound import playsound

async def test_brain():
    print("--- 1. BEYİN TESTİ (Ollama) ---")
    try:
        resp = ollama.chat(model="llama3.2", messages=[{'role': 'user', 'content': 'Merhaba, sesimi duyuyor musun?'}])
        print(f"Ollama Yanıtı: {resp['message']['content']}")
        return True
    except Exception as e:
        print(f"Ollama Hatası: {e}")
        return False

async def test_voice():
    print("\n--- 2. SES TESTİ (Edge-TTS) ---")
    try:
        text = "Sistem testi başarılı. Sesimi duyabiliyorsanız her şey yolunda demektir."
        voice = "tr-TR-AhmetNeural"
        output = "test_run.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output)
        playsound(output)
        os.remove(output)
        print("Səs başarıyla çalındı.")
        return True
    except Exception as e:
        print(f"Ses Hatası: {e}")
        return False

if __name__ == "__main__":
    print("J.A.R.V.İ.S. TAM SİSTEM TANILAMA BAŞLATILIYOR...\n")
    brain_ok = asyncio.run(test_brain())
    voice_ok = asyncio.run(test_voice())
    
    print("\n--- SONUÇ ---")
    print(f"Beyin (Ollama): {'TAMAM' if brain_ok else 'HATA'}")
    print(f"Ses (TTS): {'TAMAM' if voice_ok else 'HATA'}")
    
    if brain_ok and voice_ok:
        print("\nSistem çekirdeği sağlıklı. Sorun mikrofon veya internet bağlantısında olabilir.")
    else:
        print("\nSistemde kritik bir hata var. Lütfen yukarıdaki hata mesajlarını inceleyin.")
