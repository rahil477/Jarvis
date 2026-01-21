
import os
import sys

# Ensure we are in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("--- JARVIS SYSTEM RESTORATION ---")
print(f"Current Path: {os.getcwd()}")
print(f"Python Version: {sys.version}")

try:
    import pyaudio
    p = pyaudio.PyAudio()
    print("\n[SUCCESS] PyAudio is working correctly.")
    print("Detected Devices:")
    for i in range(p.get_device_count()):
        print(f"  [{i}] {p.get_device_info_by_index(i).get('name')}")
    p.terminate()
except Exception as e:
    print(f"\n[ERROR] PyAudio failed: {e}")
    print("Attempting to reinstall PyAudio for Python 3.11...")
    os.system(".venv11\\Scripts\\pip install --force-reinstall pyaudio")

print("\nStarting J.A.R.V.I.S. HUD...")
os.system(".venv11\\Scripts\\python.exe jarvis_gui.py")
