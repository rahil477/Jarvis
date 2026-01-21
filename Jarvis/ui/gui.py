import customtkinter as ctk
import threading
import sys
import os
import math
from PIL import Image, ImageTk
from Jarvis.core.brain import JarvisBrain
from Jarvis.features.voice import VoiceEngine
from Jarvis.utils.logger import logger

class SiriWave(ctk.CTkCanvas):
    def __init__(self, master, width=800, height=200, bg_color="#0a0b10"):
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.width = width
        self.height = height
        self.amplitude = 0
        self.target_amplitude = 0
        self.phase = 0
        self.speed = 0.2
        self.colors = ["#00d2ff", "#ff0099", "#00ff99"]
        
    def set_amplitude(self, val):
        self.target_amplitude = min(1.0, max(0.0, val))

    def animate(self):
        if not self.winfo_exists(): return
        self.delete("all")
        
        # Smooth interpolation
        if self.target_amplitude > self.amplitude:
            self.amplitude += 0.05
        else:
            self.amplitude -= 0.02
        self.amplitude = max(0.0, self.amplitude)

        center_y = self.height / 2
        if self.amplitude > 0.01:
            for i, color in enumerate(self.colors):
                offset = i * (math.pi / 4)
                points = []
                for x in range(0, self.width, 5):
                    norm_x = x / self.width
                    envelope = 4 * norm_x * (1 - norm_x) 
                    y = center_y + math.sin(x * 0.02 + self.phase + offset) * self.amplitude * envelope * 60
                    points.append((x, y))
                if len(points) > 2:
                    self.create_line(points, fill=color, width=2, smooth=True)

        self.phase += self.speed
        self.after(20, self.animate)

class JarvisGUI(ctk.CTk):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        
        self.title("J.A.R.V.İ.S. v4.0")
        self.geometry("900x700")
        self.configure(fg_color="#0a0b10")
        
        # UI Elements
        self._build_ui()
        self.siri_wave.animate()
        
    def _build_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=20)
        ctk.CTkLabel(self.header, text="J.A.R.V.İ.S.", font=("Orbitron", 36, "bold"), text_color="#fff").pack()
        ctk.CTkLabel(self.header, text="TITAN SYSTEM v4.0", font=("DIN", 12), text_color="#666").pack()

        # Wave
        self.wave_frame = ctk.CTkFrame(self, fg_color="transparent", height=150)
        self.wave_frame.pack(fill="x", padx=20)
        self.siri_wave = SiriWave(self.wave_frame, width=860, height=150)
        self.siri_wave.pack()

        # Chat
        self.chat_box = ctk.CTkTextbox(self, fg_color="#161b22", corner_radius=15, font=("Inter", 14))
        self.chat_box.pack(fill="both", expand=True, padx=40, pady=20)
        self.chat_box.configure(state="disabled")

        # Input
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=40, pady=20)
        
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Command...", height=50, corner_radius=25, fg_color="#0d1117")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_query())
        
        self.mic_btn = ctk.CTkButton(self.input_frame, text="🎤", width=50, height=50, corner_radius=25, 
                                     fg_color="#ef4444", command=self.toggle_voice)
        self.mic_btn.pack(side="right")

    def update_chat(self, sender, text):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"\n{sender}: ", "bold")
        self.chat_box.insert("end", f"{text}\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def send_query(self):
        query = self.entry.get()
        if not query: return
        self.entry.delete(0, "end")
        self.update_chat("USER", query)
        
        # Process in thread
        self.siri_wave.set_amplitude(0.3) # Thinking
        threading.Thread(target=self._process_query, args=(query,), daemon=True).start()

    def _process_query(self, query):
        response = self.agent.ask(query)
        self.after(0, lambda: self.update_chat("JARVIS", response))
        self.after(0, lambda: self.siri_wave.set_amplitude(0.0))

    def toggle_voice(self):
        # Implementation for voice toggle
        self.update_chat("SYSTEM", "Voice input activated.")
        self.siri_wave.set_amplitude(0.7)
        threading.Thread(target=self._voice_listen, daemon=True).start()

    def _voice_listen(self):
        query = self.agent.voice.listen()
        if query:
            self.after(0, lambda: self.entry.insert(0, query))
            self.after(0, self.send_query)
        self.after(0, lambda: self.siri_wave.set_amplitude(0.0))

if __name__ == "__main__":
    from main import JarvisAgent
    agent = JarvisAgent()
    gui = JarvisGUI(agent)
    gui.mainloop()
