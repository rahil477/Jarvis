import os
import requests
import zipfile
from Jarvis.core.config import config
from Jarvis.utils.logger import logger

def download_model():
    model_path = config.VOSK_MODEL_PATH
    if os.path.exists(model_path):
        logger.info("Vosk model already exists.")
        return

    url = "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip"
    logger.info(f"Downloading Vosk model from {url}...")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    zip_path = "model.zip"
    
    response = requests.get(url, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    logger.info("Extracting model...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(model_path))
    
    os.remove(zip_path)
    # Rename extracted folder to 'tr' if needed
    extracted_name = "vosk-model-small-tr-0.3"
    if os.path.exists(os.path.join(os.path.dirname(model_path), extracted_name)):
        os.rename(os.path.join(os.path.dirname(model_path), extracted_name), model_path)
    
    logger.info("Vosk model setup complete.")

if __name__ == "__main__":
    download_model()
