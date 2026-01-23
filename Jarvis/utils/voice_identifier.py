import numpy as np
import librosa
import os
import pickle
from scipy.spatial.distance import cosine

class VoiceIdentifier:
    """
    Handles Speaker Identification and Emotion Detection using audio features.
    """
    def __init__(self, data_path="data/voice_profiles"):
        self.data_path = data_path
        os.makedirs(self.data_path, exist_ok=True)
        self.user_profile_path = os.path.join(self.data_path, "user_voice.pkl")
        self.user_fingerprint = self._load_profile()

    def _load_profile(self):
        if os.path.exists(self.user_profile_path):
            with open(self.user_profile_path, 'rb') as f:
                return pickle.load(f)
        return None

    def save_profile(self, audio_data, sr=16000):
        """Register the user's voice."""
        try:
            # Ensure audio_data is a flat numpy array
            if hasattr(audio_data, 'flatten'):
                audio_data = audio_data.flatten()
            
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfccs.T, axis=0)
            with open(self.user_profile_path, 'wb') as f:
                pickle.dump(mfcc_mean, f)
            self.user_fingerprint = mfcc_mean
            return "Səsiniz uğurla qeydiyyata alındı, efendim."
        except Exception as e:
            return f"Qeydiyyat xətası: {e}"

    def identify_speaker(self, audio_data, sr=16000):
        """Identify if the speaker is the registered user."""
        if self.user_fingerprint is None:
            return "unknown" # No profile set yet
        
        try:
            if hasattr(audio_data, 'flatten'):
                audio_data = audio_data.flatten()
                
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            current_mfcc = np.mean(mfccs.T, axis=0)
            
            # Calculate similarity (1 - cosine distance)
            similarity = 1 - cosine(self.user_fingerprint, current_mfcc)
            
            # Threshold (can be tuned)
            if similarity > 0.85:
                return "user"
            else:
                return "guest"
        except Exception as e:
            print(f"Identification error: {e}")
            return "unknown"

    def detect_emotion(self, audio_data, sr=16000):
        """
        Detect emotion based on pitch, energy and spectral features.
        Returns: 'normal', 'angry', 'sad'
        """
        try:
            if hasattr(audio_data, 'flatten'):
                audio_data = audio_data.flatten()
                
            # 1. Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
            # Filter zero pitches
            valid_pitches = pitches[pitches > 0]
            pitch_mean = np.mean(valid_pitches) if len(valid_pitches) > 0 else 0
            
            # 2. Energy (RMS)
            rms = librosa.feature.rms(y=audio_data)
            energy_mean = np.mean(rms)

            # Basic Heuristics
            # These values are approximate and might need calibration per mic
            if energy_mean > 0.04: # High energy
                return "angry"
            elif energy_mean < 0.002: # Very low energy
                return "sad"
            else:
                return "normal"
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return "normal"
