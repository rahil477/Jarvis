import logging
import os
import base64
import time
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
import pyautogui
import ollama
from ultralytics import YOLO

# Configure logging
logger = logging.getLogger(__name__)

class VisionEngine:
    """
    Handles all vision-related tasks using LLaVA, OCR, and Computer Vision models.
    
    Capabilities:
    - Screenshot analysis (LLaVA)
    - Code extraction from images (Ollama/OCR)
    - UI Element detection (YOLO/CV)
    - Visual error diagnosis
    - Real-time webcam analysis
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logger
        
        # Load settings
        self.model_name = self.config.get("models", {}).get("vision", "llava")
        self.screenshot_dir = os.path.join(os.getcwd(), "data", "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Initialize YOLO if needed (lazy load recommended due to size)
        self.yolo_model = None 

    def analyze_image(self, image_path, prompt="Describe this image in detail."):
        """
        Analyze an image using LLaVA (via Ollama).
        """
        try:
            if not os.path.exists(image_path):
                return "Error: Image file not found."

            with open(image_path, "rb") as img_file:
                image_bytes = img_file.read()

            self.logger.info(f"Analyzing image: {image_path} with model: {self.model_name}")
            
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': [image_bytes]
                }
            ])
            
            return response['message']['content']
        except Exception as e:
            self.logger.error(f"Vision analysis failed: {e}")
            return f"Error analyzing image: {str(e)}"

    def extract_text(self, image_path):
        """
        Extract text from an image using Tesseract OCR.
        Best for documents, error logs, and plain text.
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            return ""

    def capture_screen(self, filename=None):
        """
        Capture the current screen and save to disk.
        """
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        path = os.path.join(self.screenshot_dir, filename)
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            return path
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None

    def diagnose_active_error(self):
        """
        Captures the screen and analyzes it for error messages.
        Use this when the user says "What is this error?" or "Fix this bug".
        """
        self.logger.info("Diagnosing active screen error...")
        screenshot_path = self.capture_screen(filename="error_diagnosis.png")
        
        if not screenshot_path:
            return "Could not capture screen."

        # 1. Try OCR first for exact text
        ocr_text = self.extract_text(screenshot_path)
        
        # 2. Use LLaVA for context and understanding
        prompt = (
            f"Analyze this screenshot. It contains an error or bug. "
            f"Extracted Text: {ocr_text[:500]}... "
            f"1. Identify the error message. "
            f"2. Explain the likely cause. "
            f"3. Suggest a fix."
        )
        
        analysis = self.analyze_image(screenshot_path, prompt)
        return analysis

    def detect_ui_elements(self, image_path):
        """
        Detect UI elements (buttons, inputs) using YOLO.
        """
        if not self.yolo_model:
            # Load a lightweight detection model
            self.yolo_model = YOLO("yolov8n.pt") 
            
        results = self.yolo_model(image_path)
        # Process results... (simplified for now)
        return results[0].tojson()

if __name__ == "__main__":
    # Test
    vision = VisionEngine()
    print("Vision Engine Initialized.")
    # test_path = vision.capture_screen()
    # print(vision.analyze_image(test_path, "What is on my screen?"))
