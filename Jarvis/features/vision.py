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
        """Tier 2: Multi-modal - Image Analysis with v5.0 Protocol"""
        try:
            # Injecting Vision Engine System Prompt instructions into the call
            full_prompt = f"System: Sen JARVIS Vision Engine modulusan. Protocol: Describe, Identify actionable items, Suggest next steps.\nUser: {prompt}"
            resp = ollama.chat(model=config.OLLAMA_VISION_MODEL, messages=[{
                'role': 'user', 'content': full_prompt, 'images': [image_path]
            }])
            return resp['message']['content']
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return f"Error: {e}"

    def analyze_ui(self, image_path):
        """Tier 2: Specific UI Element Detection"""
        prompt = "Identify all clickable UI elements, input fields, and potential error messages on this screen. Provide coordinates if possible."
        return self.analyze_image(image_path, prompt)

    def extract_code(self, image_path):
        """Tier 2: Code Screenshot Extraction"""
        prompt = "Extract any visible code from this image. Return ONLY the clean code without explanation."
        return self.analyze_image(image_path, prompt)

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
