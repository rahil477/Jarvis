import sys
import os
import time
import threading
import queue
import re
import random
from Jarvis.core.brain import JarvisBrain
from Jarvis.core.config import config
from Jarvis.features.voice import VoiceEngine
from Jarvis.features.vision import VisionEngine
from Jarvis.utils.logger import logger
from Jarvis.utils.security import SecurityManager
from Jarvis.prompts import UNIFIED_SYSTEM_PROMPT

class JarvisAgent:
    def __init__(self):
        logger.info("Initializing JARVIS TITAN v4.0...")
        self.brain = JarvisBrain()
        self.voice = VoiceEngine()
        self.vision = VisionEngine()
        self.security = SecurityManager()
        self.command_queue = queue.Queue()
        self.is_running = True
        self.tools = self._init_tools()

    def _init_tools(self):
        return {
            "SEARCH_WEB": lambda q: f"Searching web for: {q}",
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

        # Feedback detection
        if any(w in query.lower() for w in ["səhv", "wrong", "sehv", "təzədən", "düzgün deyil"]):
            self.brain.update_reward(success=False)
            self.brain._update_ab_metrics(ab_variant, success=False)

        context = self.brain.get_context(query)
        messages = [
            {"role": "system", "content": UNIFIED_SYSTEM_PROMPT},
            {"role": "system", "content": f"User: Rahil. Context: {context}. Reward: {self.brain.memory.get('reward_score', 0.5):.2f}"},
            {"role": "user", "content": query}
        ]

        try:
            for step in range(config.MAX_REASONING_STEPS):
                import ollama
                resp = ollama.chat(model=config.OLLAMA_MODEL, messages=messages)
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
                
                if "CEVAP:" in content:
                    final_text = content.split("CEVAP:")[1].strip()
                    self.voice.speak(final_text)
                    latency = time.time() - start_time
                    self.brain.log_interaction(query, final_text, [], "Success", latency, ab_variant)
                    self.brain.add_to_episodic_memory(query, final_text, "Success")
                    return final_text
                    
            return content # Fallback if no CEVAP found
        except Exception as e:
            logger.error(f"Brain reasoning failed: {e}")
            return "Zihnimdə bir xəta baş verdi, üzr istəyirəm."

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
