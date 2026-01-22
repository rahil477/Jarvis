import sys
import os
import time
import threading
import queue
import re
import random
import schedule
import psutil
import datetime
from Jarvis.core.brain import JarvisBrain
from Jarvis.core.config import config
from Jarvis.core.router import TaskRouter
from Jarvis.core.evolution import SelfEvolution
from Jarvis.features.voice import VoiceEngine
from Jarvis.features.vision import VisionEngine
from Jarvis.features.gestures import GestureEngine
from Jarvis.features.web import WebEngine
from Jarvis.features.api_hub import APIHub
from Jarvis.utils.logger import logger
from Jarvis.utils.security import SecurityManager
from Jarvis.prompts import (
    UNIFIED_SYSTEM_PROMPT, 
    VISION_ENGINE_PROMPT, 
    SELF_CODING_PROMPT, 
    API_HUB_PROMPT
)

class JarvisAgent:
    def __init__(self):
        logger.info("Initializing JARVIS TITAN v4.0...")
        self.brain = JarvisBrain()
        self.voice = VoiceEngine()
        self.vision = VisionEngine()
        self.gestures = GestureEngine()
        self.web = WebEngine()
        self.api = APIHub()
        self.evolution = SelfEvolution()
        self.security = SecurityManager()
        self.command_queue = queue.Queue()
        self.is_running = True
        self.tools = self._init_tools()
        
        # Start Background Jobs
        self.gestures.start(self._handle_gesture)
        threading.Thread(target=self._run_scheduler, daemon=True).start()

    def _init_tools(self):
        return {
            "SEARCH_WEB": lambda q: self.web.search(q),
            "DEEP_RESEARCH": lambda q: self.web.deep_research(q),
            "EVOLVE_SELF": lambda q: self.evolution.generate_new_tool(q),
            "GENERATE_REPORT": lambda x: self.evolution.get_learned_report(),
            "GMAIL_INBOX": lambda x: self.api.list_unread_emails(),
            "GITHUB_PUSH": lambda q: self.api.github_push("origin/main", q),
            "NOTION_LOG": lambda q: self.api.notion_save_log(q),
            "VISION": lambda p: self.vision.analyze_image(self.vision.capture_screen(), p),
            "WEBCAM": lambda p: self.vision.analyze_image(self.vision.capture_webcam(), p),
            "SYSTEM_STATS": lambda x: f"CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%",
            "PERFORMANCE_REPORT": lambda x: self.brain.get_performance_report()
        }

    def ask(self, query):
        start_time = time.time()
        ab_variant = random.choice(["A", "B"])
        
        # Security: Input validation
        query = self.security.validate_input(query)
        if not query: return "Invalid input received."

        # TIER 1: Multi-model Orchestration (Task Routing)
        target_model = TaskRouter.route(query)
        logger.info(f"Targeting model: {target_model}")
        
        context = self.brain.get_context(query)
        
        # Select appropriate prompt based on task
        system_prompt = UNIFIED_SYSTEM_PROMPT
        if "vision" in target_model.lower(): system_prompt = VISION_ENGINE_PROMPT
        elif any(w in query.lower() for w in ["kod", "yaz", "debug"]): system_prompt = SELF_CODING_PROMPT
        elif any(w in query.lower() for w in ["email", "github", "notion"]): system_prompt = API_HUB_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"User: Rahil. Context: {context}. Reward: {self.brain.memory.get('reward_score', 0.5):.2f}"},
            {"role": "user", "content": query}
        ]

        retries = 3
        for attempt in range(retries):
            try:
                for step in range(config.MAX_REASONING_STEPS):
                    import ollama
                    resp = ollama.chat(model=target_model, messages=messages)
                    content = resp['message']['content']
                    messages.append({"role": "assistant", "content": content})

                    # Tool Detection
                    match = re.search(r"(?:EYLEM|ACTION):\s*(\w+)\s*\|\s*(?:Input|Girdi):\s*(.*)", content, re.I)
                    if match:
                        t_name, t_input = match.group(1).upper(), match.group(2).strip()
                        if t_name in self.tools:
                            logger.info(f"Executing Tool: {t_name}")
                            obs = self.tools[t_name](t_input)
                            messages.append({"role": "user", "content": f"GÖZLEM: {obs}"})
                            continue
                    
                    final_text = content
                    if "CEVAP:" in content:
                        final_text = content.split("CEVAP:")[1].strip()
                    
                    # Tier 2 Voice Adaptation
                    emotion = "urgent" if "!" in final_text else "neutral"
                    mode = "soft" if datetime.datetime.now().hour > 22 else "default"
                    self.voice.speak(final_text, mode=mode, emotion=emotion)
                    
                    latency = time.time() - start_time
                    self.brain.log_interaction(query, final_text, [], "Success", latency, ab_variant)
                    self.brain.add_to_episodic_memory(query, final_text, "Success")
                    return final_text
                    
            except Exception as e:
                logger.error(f"Brain reasoning failed (Attempt {attempt+1}/{retries}): {e}")
                if attempt == retries - 1:
                    import traceback
                    logger.error(traceback.format_exc())
                    return f"Bağışlayın, sistemdə xəta baş verdi: {str(e)}"
                time.sleep(1) # Wait before retry

    def _run_scheduler(self):
        """Tier 4: Autonomous Task Execution Scheduler"""
        schedule.every().day.at("09:00").do(lambda: self.command_queue.put(("AUTO", "Günlük brifinq hazırla")))
        schedule.every(2).hours.do(lambda: logger.info("Autonomous health check..."))
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)

    def _handle_gesture(self, gesture):
        """Tier 2: Gesture Interface Handlers"""
        logger.info(f"GESTURE DETECTED: {gesture}")
        if gesture == "THUMBS_UP":
            self.command_queue.put(("GESTURE", "Confirm/Yes"))
            # Could trigger a specific confirmation in the brain
        elif gesture == "PEACE_SIGN":
            # Auto-screenshot and analyze (Tier 2 Vision)
            logger.info("Gesture-triggered screen scan.")
            self.ask("Ekranı analiz et və vacib məlumatları de.")
        elif gesture == "OPEN_PALM":
            # Pause jarvis voice
            import pygame
            pygame.mixer.music.stop()
            logger.info("Voice paused via gesture.")

    def start_gui(self):
        from Jarvis.ui.gui import JarvisGUI
        gui = JarvisGUI(self)
        gui.mainloop()

if __name__ == "__main__":
    agent = JarvisAgent()
    if "--no-gui" in sys.argv:
        agent.run() # Should implement a CLI loop in agent.run
    else:
        agent.start_gui()
