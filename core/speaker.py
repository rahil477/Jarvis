import pyttsx3

class VoiceSpeaker:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            
            voices = self.engine.getProperty('voices')
            
            for voice in voices:
                if 'turkish' in voice.name.lower() or 'tr' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
        except Exception as e:
             print(f'❌ TTS init failed: {e}')
             self.engine = None
    
    def speak(self, text):
        if not self.engine:
            print(f"🔊 (No TTS): {text}")
            return
        try:
            # print(f'🔊 {text}') 
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f'❌ TTS xətası: {e}')
