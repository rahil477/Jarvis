import cv2
import mediapipe as mp
import threading
from Jarvis.utils.logger import logger

class GestureEngine:
    def __init__(self):
        # Temporarily disabled due to mediapipe compatibility issues
        self.mp_hands = None
        self.hands = None
        self.mp_draw = None
        self.is_running = False
        self.callback = None
        logger.info("Gesture Engine initialized (DISABLED - mediapipe compatibility issue)")

    def start(self, callback):
        self.callback = callback
        self.is_running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.is_running = False

    def _run(self):
        cap = cv2.VideoCapture(0)
        logger.info("Gesture Detection Started...")
        
        while self.is_running and cap.isOpened():
            success, img = cap.read()
            if not success: continue

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if not self.hands: continue
            results = self.hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    gesture = self._classify_gesture(hand_lms)
                    if gesture and self.callback:
                        self.callback(gesture)
            
            # Low frequency to save CPU
            cv2.waitKey(100) 
            
        cap.release()

    def _classify_gesture(self, landmarks):
        # Basic gesture logic based on landmark positions
        # index 8: Index tip, index 4: Thumb tip
        lms = landmarks.landmark
        
        # Thumbs up check (Simplified)
        if lms[4].y < lms[3].y < lms[2].y < lms[1].y:
            # Thumb is above other thumb joints
            if all(lms[i].y > lms[2].y for i in [8, 12, 16, 20]):
                return "THUMBS_UP"

        # Open Palm check
        if all(lms[i].y < lms[i-2].y for i in [8, 12, 16, 20]):
            return "OPEN_PALM"

        # Peace sign (index and middle up)
        if lms[8].y < lms[6].y and lms[12].y < lms[10].y:
            if lms[16].y > lms[14].y and lms[20].y > lms[18].y:
                return "PEACE_SIGN"

        return None
