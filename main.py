import os
import sys
from dotenv import load_dotenv
from core.brain import JarvisBrain
from core.listener import VoiceListener
from core.speaker import VoiceSpeaker
from Jarvis.utils.voice_identifier import VoiceIdentifier
import yaml
import time

load_dotenv()

# Load config safely
if os.path.exists('config.yaml'):
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
else:
    # Default config if file missing
    config = {'user': {'name': 'Rahil efendim'}}

print('🦾 JARVIS ULTIMATE v5.0 Başladılır...')
print('=' * 50)

# Initialize
try:
    speaker = VoiceSpeaker()
    listener = VoiceListener(config)
    brain = JarvisBrain(config, speaker)
    voice_analyzer = VoiceIdentifier()
except Exception as e:
    print(f"❌ Initialization Error: {e}")
    sys.exit(1)

speaker.speak(f'Sistemlər aktiv, {config.get("user", {}).get("name", "Efendim")}.')

print('\n✓ JARVIS hazırdır!')
print('🎤 Danışın (Ctrl+C ilə çıxış)')
print('=' * 50 + '\n')

while True:
    try:
        print('🎤 Dinləyirəm...')
        voice_text, audio_data = listener.listen()
        
        if voice_text:
            print(f'👤 Siz: {voice_text}')
            
            # Analyze Voice
            identity = voice_analyzer.identify_speaker(audio_data)
            emotion = voice_analyzer.detect_emotion(audio_data)
            
            print(f'� Analiz: Natiq={identity}, Emosiya={emotion}')
            
            # Special command to register voice
            if "mənim səsimi yadda saxla" in voice_text.lower() or "səsimi tanıt" in voice_text.lower():
                response = voice_analyzer.save_profile(audio_data)
                print(f'🤖 JARVIS: {response}')
                speaker.speak(response)
                continue

            response = brain.process(voice_text, identity=identity, emotion=emotion)
            print(f'🤖 JARVIS: {response}')
            speaker.speak(response)
        
    except KeyboardInterrupt:
        print('\n\n👋 Görüşənədək, efendim.')
        speaker.speak('Görüşənədək, efendim.')
        break
    except Exception as e:
        print(f'❌ Xəta: {e}')
        time.sleep(1)
