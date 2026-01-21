#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vosk Türkçe Model İndirici
Offline STT için Vosk modelini indir ve ayarla
"""

import os
import urllib.request
import zipfile
import shutil

# Model konumu
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
TR_MODEL_DIR = os.path.join(MODEL_DIR, "tr")
TR_MODEL_ZIP = os.path.join(MODEL_DIR, "model-tr.zip")

# Vosk türkçe model URL (açık kaynak repositories)
MODEL_URL = "https://alphacephei.com/vosk/models/model-tr.zip"

def download_model():
    """Vosk Türkçe modelini indir"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print("[İNDİRİLİYOR] Vosk Türkçe Model...")
    print(f"Kaynak: {MODEL_URL}")
    print(f"Hedef: {TR_MODEL_DIR}")
    
    try:
        # Model zip dosyasını indir
        urllib.request.urlretrieve(MODEL_URL, TR_MODEL_ZIP)
        print("[TAMAMLANDI] Model indirildi")
        
        # Dosyaları çıkar
        print("[ÇIKARTILIYOR] Dosyalar açılıyor...")
        with zipfile.ZipFile(TR_MODEL_ZIP, 'r') as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        
        print("[TAMAMLANDI] Dosyalar açıldı")
        
        # Zip dosyasını sil
        if os.path.exists(TR_MODEL_ZIP):
            os.remove(TR_MODEL_ZIP)
            print("[TEMİZLENDİ] Zip dosyası silindi")
        
        print("[BAŞARILI] Vosk Türkçe Model hazır!")
        return True
        
    except Exception as e:
        print(f"[HATA] Model indirilemedi: {e}")
        return False

if __name__ == "__main__":
    download_model()
