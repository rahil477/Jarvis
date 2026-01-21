import asyncio
import edge_tts
from playsound import playsound
import os

async def test_speak():
    TEXT = "Merhaba, ben Jarvis. Sesimi nasıl buldun?"
    VOICE = "tr-TR-AhmetNeural"
    OUTPUT_FILE = "test_audio.mp3"
    
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    
    print("Ses dosyası oluşturuldu, çalınıyor...")
    playsound(OUTPUT_FILE)
    os.remove(OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(test_speak())
