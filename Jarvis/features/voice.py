import os
import json
import time
import threading
import queue
import sounddevice as sd
import scipy.io.wavfile as wav
import edge_tts
import asyncio
import pygame
import vosk
import audioop
from Jarvis.utils.logger import logger
from Jarvis.core.config import config

class VoiceEngine:
    def __init__(self):
        self.vosk_model = self._init_vosk()
        pygame.mixer.init()
        self.is_speaking = False

    def _init_vosk(self):
        if os.path.exists(config.VOSK_MODEL_PATH):
            try:
                return vosk.Model(config.VOSK_MODEL_PATH)
            except Exception as e:
                logger.error(f"Vosk model failed to load: {e}")
        return None

    def speak(self, text):
        """Asynchronous TTS to prevent UI freezing"""
        def _run():
            self.is_speaking = True
            try:
                communicate = edge_tts.Communicate(text, config.TTS_VOICE)
                file_path = "speech.mp3"
                asyncio.run(communicate.save(file_path))
                
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
                if os.path.exists("speech.mp3"):
                    try: os.remove("speech.mp3")
                    except: pass

        threading.Thread(target=_run, daemon=True).start()

    def listen(self, duration=10):
        """Offline STT using Vosk"""
        if not self.vosk_model:
            logger.warning("Vosk model not loaded, cannot listen.")
            return ""

        try:
            import pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
            rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            
            logger.info("Listening...")
            start_time = time.time()
            while time.time() - start_time < duration:
                data = stream.read(4000, exception_on_overflow=False)
                if len(data) == 0: break
                
                # Noise gate
                rms = audioop.rms(data, 2)
                if rms < 150: continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        return text.lower()
            
            p.terminate()
        except Exception as e:
            logger.error(f"STT Error: {e}")
        return ""
