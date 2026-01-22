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

    def speak(self, text, mode="default", emotion="neutral"):
        """Asynchronous TTS with emotional adaptation placeholders"""
        def _run():
            self.is_speaking = True
            logger.info(f"Speaking (Mode: {mode}, Emotion: {emotion}): {text[:50]}...")
            
            # Tier 2: Emotional Adaptation (Simulation)
            adjusted_text = text
            if emotion == "urgent":
                adjusted_text = f"Efendim, diqqət! {text}"
            elif emotion == "happy":
                adjusted_text = f"Əla xəbər! {text}"

            try:
                communicate = edge_tts.Communicate(adjusted_text, config.TTS_VOICE)
                # Use unique filename to prevent permission errors
                file_path = f"speech_{int(time.time())}_{threading.get_ident()}.mp3"
                asyncio.run(communicate.save(file_path))
                
                pygame.mixer.music.load(file_path)
                # Adaptive volume
                volume = 0.6 if mode == "soft" else 1.0
                pygame.mixer.music.set_volume(volume)
                
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Cleanup after playing
                pygame.mixer.music.unload()
                
            except Exception as e:
                logger.error(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
                # Try to clean up file with a small delay
                try:
                    if 'file_path' in locals() and os.path.exists(file_path):
                        # Background cleanup to not block
                        def cleanup(path):
                            time.sleep(1)
                            try: os.remove(path)
                            except: pass
                        threading.Thread(target=cleanup, args=(file_path,)).start()
                except: pass

        threading.Thread(target=_run, daemon=True).start()

    def listen(self, duration=10):
        """Offline STT using Vosk with sounddevice (alternative to pyaudio)"""
        if not self.vosk_model:
            logger.warning("Vosk model not loaded, cannot listen.")
            return ""

        try:
            import numpy as np
            import sounddevice as sd
            
            samplerate = 16000
            rec = vosk.KaldiRecognizer(self.vosk_model, samplerate)
            
            logger.info("Listening (via sounddevice)...")
            
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                                   channels=1) as stream:
                start_time = time.time()
                while time.time() - start_time < duration:
                    data, overflowed = stream.read(4000)
                    if overflowed:
                        logger.warning("Audio input overflowed.")
                    
                    if rec.AcceptWaveform(bytes(data)):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            # TIER 1: Phonetic Correction
                            # Vosk often mishears 'Jarvis' in Turkish/Azeri models
                            corrections = {
                                "yavuz": "jarvis",
                                "havuç": "jarvis",
                                "servis": "jarvis",
                                "yalnız": "jarvis",
                                "kabus": "jarvis",
                                "kabusu": "jarvis",
                                "masası": "jarvis" # often 'jarvis masası' -> 'havuç masası'
                            }
                            text_lower = text.lower()
                            for wrong, right in corrections.items():
                                text_lower = text_lower.replace(wrong, right)
                                
                            return text_lower
                            
        except Exception as e:
            logger.error(f"STT Error: {e}")
        return ""
