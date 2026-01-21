
import speech_recognition as sr
try:
    with sr.Microphone() as source:
        print("Microphone accessed successfully!")
except Exception as e:
    print(f"Error accessing microphone: {e}")
