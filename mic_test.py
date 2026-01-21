import speech_recognition as sr
import time

def debug_mic():
    r = sr.Recognizer()
    print("--- MİKROFON TESTİ BAŞLADI ---")
    print("Mevcut Cihazlar:")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Index {i}: {name}")
    
    # Varsayılan mikrofonu dene
    with sr.Microphone() as source:
        print("\nSessiz durun, gürültü seviyesi ölçülüyor...")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"Enerji Eşiği: {r.energy_threshold}")
        
        print("\nŞimdi konuşun (5 saniye kayıt yapılacak)...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Ses algılandı! Google'a gönderiliyor...")
            text = r.recognize_google(audio, language="tr-TR")
            print(f"BAŞARILI! Duyulan: {text}")
        except sr.WaitTimeoutError:
            print("HATA: Hiç ses duyulmadı (Timeout). Mikrofonunuzun açık olduğundan emin olun.")
        except sr.UnknownValueError:
            print("HATA: Ses algılandı ama kelimeye dönüştürülemedi (Anlaşılamadı).")
        except Exception as e:
            print(f"SİSTEM HATASI: {e}")

if __name__ == "__main__":
    debug_mic()
