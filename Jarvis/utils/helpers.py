import os
import shutil
import time
from Jarvis.utils.logger import logger

def cleanup_temp_files(directory=".", extension=".mp3"):
    """Remove temporary files like speech recordings"""
    try:
        for file in os.listdir(directory):
            if file.endswith(extension) and file.startswith("speech_"):
                os.remove(os.path.join(directory, file))
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def format_time(seconds):
    """Helper to format seconds into readable time"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

def get_system_info():
    import psutil
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "N/A"
    }
