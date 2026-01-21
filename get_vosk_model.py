#!/usr/bin/env python3
"""Vosk model indir ve hazırla - basitleştirilmiş versiyon"""

import os
import sys

try:
    # Bağlantı kontrol et
    import urllib.request
    
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    tr_model_dir = os.path.join(model_dir, "tr")
    
    os.makedirs(model_dir, exist_ok=True)
    
    print("Downloading Vosk Turkish model...")
    print(f"Destination: {tr_model_dir}")
    
    # URL - Vosk Turkish small model
    url = "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip"
    zip_path = os.path.join(model_dir, "model.zip")
    
    # İndir
    urllib.request.urlretrieve(url, zip_path)
    print("Downloaded successfully")
    
    # Çıkar
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(model_dir)
    print("Extracted")
    
    # Temizle
    os.remove(zip_path)
    
    print("Ready!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
