import sounddevice as sd
import queue
import sys
import os
import whisper
import numpy as np
import tempfile
import torch

class VoiceListener:
    def __init__(self, config):
        self.config = config
        self.sample_rate = 16000
        self.channels = 1
        self.blocksize = 16000 * 5  # 5 seconds buffer
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Whisper Model: base (Device: {device}) yüklənir...")
        
        try:
            # Load Whisper Base model for speed
            self.model = whisper.load_model("base", device=device)
            print("✓ Whisper Model hazırdır.")
        except Exception as e:
            print(f"❌ Model yüklənmədi: {e}")
            sys.exit(1)
            
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
    def audio_callback(self, indata, frames, time, status):
        """Capture audio and put into queue"""
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(indata.copy())
    
    def listen(self, timeout=None):
        """
        Record audio and transcribe using Whisper.
        Currently uses a simple Voice Activity Detection (VAD) logic via Energy threshold.
        """
        # Threshold for silence (adjust based on mic)
        ENERGY_THRESHOLD = 0.02
        SILENCE_DURATION = 1.5 # seconds
        
        print("🎤 Danışın...", end="\r")
        
        audio_buffer = []
        silence_start = None
        has_speech = False
        
        with sd.InputStream(samplerate=self.sample_rate, 
                          channels=self.channels, 
                          callback=None) as stream:
            
            while True:
                # Read chunk
                indata, overflow = stream.read(4000) # 0.25s chunks
                audio_data = indata.flatten()
                energy = np.sqrt(np.mean(audio_data**2))
                
                # Check for speech
                if energy > ENERGY_THRESHOLD:
                    has_speech = True
                    silence_start = None
                else:
                    if has_speech and silence_start is None:
                        silence_start = os.times().elapsed # Using system uptime or time.time
                        import time
                        silence_start = time.time()
                
                # Collect audio if speech started
                if has_speech:
                    audio_buffer.append(audio_data)
                
                # Check silence timeout
                import time
                if has_speech and silence_start and (time.time() - silence_start > SILENCE_DURATION):
                    break
        
        # Process audio
        print("🧠 Fikirləşirəm (Transcribing)...", end="\r")
        
        # Concatenate and save to temp file (Whisper expects file or numpy array)
        audio_np = np.concatenate(audio_buffer, axis=0)
        
        # Convert to float32 expected by Whisper
        audio_np = audio_np.astype(np.float32)

        # Transcribe
        # Use 'az' for Azerbaijani or None for auto-detection
        result = self.model.transcribe(audio_np, language="az", fp16=torch.cuda.is_available())
        text = result["text"].strip()
        
        if text:
            return text, audio_np
        return None, None
