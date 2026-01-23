import sounddevice as sd
import vosk
import json
import queue
import sys
import os

class VoiceListener:
    def __init__(self, config):
        self.config = config
        self.sample_rate = config.get('audio', {}).get('sample_rate', 16000)
        
        # Load Vosk model
        model_path = config.get('models', {}).get('stt_model_path', 'models/vosk-model-tr')
        
        # Check relative to current working directory
        if not os.path.isabs(model_path):
            model_path = os.path.join(os.getcwd(), model_path)

        if not os.path.exists(model_path):
            print(f"❌ Vosk model tapılmadı: {model_path}")
            print("📥 Model yükləyin: https://alphacephei.com/vosk/models")
            print("Yüklədikdən sonra 'models' qovluğuna çıxarın.")
            # For robustness, don't exit hard if possible, but here it's core functionality
            # creating a dummy model object might fail later, so cleaner to raise
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
        
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
        self.audio_queue = queue.Queue()
        
    def audio_callback(self, indata, frames, time, status):
        """Audio stream callback"""
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(bytes(indata))
    
    def listen(self, timeout=10):
        """Listen for voice input"""
        try:
            # Get device index if specified
            device = self.config.get('audio', {}).get('device_index', None)
            
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                device=device,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            ):
                # print("🎤 Danışın...", end="\r")
                
                silence_threshold = 30  # 30 * blocksize/sample_rate ~ seconds
                silence_count = 0
                
                while True:
                    data = self.audio_queue.get()
                    
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '')
                        
                        if text:
                            return text
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get('partial', '')
                        
                        if partial_text:
                            print(f"🔊 {partial_text}", end='\r')
                            silence_count = 0
                        else:
                            silence_count += 1
                            # Can implement silence timeout here if needed
                            pass
        
        except Exception as e:
            print(f"❌ Dinləmə xətası: {e}")
            return None
