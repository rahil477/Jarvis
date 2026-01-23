import os
import sys
from dotenv import load_dotenv
from core.brain import JarvisBrain
from core.listener import VoiceListener
from core.speaker import VoiceSpeaker
import yaml

# Load environment
load_dotenv()

# Load config
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Config yükleme xətası: {e}. Default dəyərlər istifadə olunacaq.")
    config = {
        'user': {'name': 'Developer', 'location': 'Unknown', 'language': 'en'},
        'features': {'debug': True},
        'audio': {'sample_rate': 16000},
        'models': {'stt_model_path': 'models/vosk-model-tr'}
    }

print("🦾 JARVIS ULTIMATE v5.0 Başladılır...")
print("=" * 50)

# Initialize components
try:
    print("🔊 Speaker sistemi başladı...")
    speaker = VoiceSpeaker()
    
    print("👂 Dinləmə sistemi yüklənir...")
    listener = VoiceListener(config)
    
    print("🧠 Beyin sistemi aktivləşir...")
    brain = JarvisBrain(config, speaker)
except Exception as e:
    print(f"❌ Başlatma xətası: {e}")
    sys.exit(1)

# Welcome message
speaker.speak(f"Sistemlər aktiv, {config['user']['name']} efendim. Komandalarınızı gözləyirəm.")

print("\n✓ JARVIS hazırdır!")
print("🎤 Danışın və ya yazın (quit ilə çıxış)")
print("=" * 50 + "\n")

# Main loop
while True:
    try:
        # Option 1: Voice input
        print("🎤 Dinləyirəm...")
        voice_input = listener.listen()
        
        if voice_input:
            print(f"👤 Siz: {voice_input}")
            response = brain.process(voice_input)
            print(f"🤖 JARVIS: {response}")
            speaker.speak(response)
        
    except KeyboardInterrupt:
        print("\n\n👋 Görüşənədək, efendim.")
        speaker.speak("Görüşənədək, efendim.")
        break
    except Exception as e:
        print(f"❌ Xəta: {e}")
        # Prevent rapid loop on continuous error
        import time
        time.sleep(1)
