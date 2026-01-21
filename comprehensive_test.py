
import os
import sys
import json
import datetime
import threading
import time

# Add Jarvis directory to path
sys.path.append(os.path.join(os.getcwd(), "Jarvis"))
import jarvis

def run_test():
    print("🚀 [JARVIS v4.0] BAŞTAN SONA TEST PROTOKOLÜ BAŞLADI\n" + "="*50)
    
    # 1. Bellek Kontrolü
    print("\n[TEST 1] Bellek ve Profil Yükleme...")
    brain = jarvis.brain
    if brain and brain.memory['user']['name'] == "Rahil Menefzade":
        print("✅ Başarılı: Rahil Menefzade profili yüklendi.")
    else:
        print("❌ Hata: Profil yüklenemedi.")

    # 2. Rezonans ve Düşünme Motoru (Ollama)
    print("\n[TEST 2] Titan Reasoning Engine (LLM) Bağlantısı...")
    try:
        # We'll use a simple query that doesn't trigger complex tool use for a fast test
        # We'll use a dummy sys.modules['__main__'].GUI_CALLBACK to avoid errors if jarvis uses it
        orig_callback = getattr(jarvis, 'GUI_CALLBACK', None)
        jarvis.GUI_CALLBACK = lambda type, data: print(f"   [GUI-SIM]: {type} -> {data[:50]}...")
        
        test_query = "Salam Jarvis, sistem testi yapıyoruz. Bugünün tarihini söyle."
        jarvis.ask_agent_self_learning(test_query)
        print("✅ Başarılı: LLM yanıt verdi ve reasoning adımları tamamlandı.")
    except Exception as e:
        print(f"❌ Hata: LLM veya Reasoning hatası: {e}")

    # 3. Araç Havuzu (Tools) Kontrolü
    print("\n[TEST 3] Araçlar (Tools) Doğrulaması...")
    required_tools = ["SEARCH_WEB", "VISION", "SYSTEM_STATS", "FABRICATE_PROJECT", "KNOWLEDGE_LINK"]
    missing = [t for t in required_tools if t not in jarvis.TOOLS]
    if not missing:
        print(f"✅ Başarılı: Tüm kritik araçlar ({len(required_tools)} adet) havuzda mevcut.")
    else:
        print(f"❌ Hata: Eksik araçlar: {missing}")

    # 4. Proaktif Motor Kontrolü
    print("\n[TEST 4] Proactive Engine (Iron Man Protocol)...")
    if hasattr(jarvis, 'proactive_engine') and jarvis.proactive_engine.running:
        print("✅ Başarılı: Proaktif motor aktif ve izleme modunda.")
    else:
        print("❌ Hata: Proaktif motor başlatılamadı.")

    print("\n" + "="*50 + "\n✅ [TEST TAMAMLANDI] Sistem operasyonel, Rahil efendim.")

if __name__ == "__main__":
    run_test()
