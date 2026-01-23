import pyttsx3

class VoiceSpeaker:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice
            voices = self.engine.getProperty('voices')
            
            # Try to find Turkish/English voice
            voice_found = False
            for voice in voices:
                if 'turkish' in voice.name.lower() or 'tr' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    voice_found = True
                    break
            
            if not voice_found:
                # Fallback to English/First available
                pass
            
            # Set properties
            self.engine.setProperty('rate', 150)    # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
        except Exception as e:
            print(f"Speaker initialization failed: {e}")
            self.engine = None
    
    def speak(self, text):
        """Convert text to speech"""
        if not self.engine:
            print(f"Speaker not available. Text: {text}")
            return

        try:
            # print(f"🔊 Danışıram: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS xətası: {e}")
