import cv2
import pyautogui
import ollama
from Jarvis.utils.logger import logger
from Jarvis.core.config import config

class VisionEngine:
    def capture_screen(self, filename="vision_tmp.png"):
        try:
            img = pyautogui.screenshot()
            img.save(filename)
            return filename
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None

    def analyze_image(self, image_path, prompt="Gördüğünü anlat"):
        try:
            resp = ollama.chat(model=config.OLLAMA_VISION_MODEL, messages=[{
                'role': 'user', 'content': prompt, 'images': [image_path]
            }])
            return resp['message']['content']
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return f"Error: {e}"

    def capture_webcam(self, filename="webcam_tmp.png"):
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(filename, frame)
                cap.release()
                return filename
            cap.release()
        except Exception as e:
            logger.error(f"Webcam capture failed: {e}")
        return None
