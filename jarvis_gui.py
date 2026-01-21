
import customtkinter as ctk
import threading
import sys
import os
import re
import math
import random
import time
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

# Jarvis Path Setup
sys.path.append(os.path.join(os.getcwd(), "Jarvis"))
import jarvis

class SiriWave(ctk.CTkCanvas):
    def __init__(self, master, width=800, height=200, bg_color="#0a0b10"):
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.width = width
        self.height = height
        self.amplitude = 0
        self.phase = 0
        self.speed = 0.2
        self.is_active = False
        self.colors = ["#00d2ff", "#ff0099", "#00ff99"] # Cyan, Magenta, Green (Siri-like neon)
        
    def set_amplitude(self, val):
        # Target amplitude (0.0 to 1.0)
        self.target_amplitude = min(1.0, max(0.0, val))

    def animate(self):
        if not self.winfo_exists(): return
        
        self.delete("all")
        
        # Smooth interpolation for amplitude
        if getattr(self, 'target_amplitude', 0) > self.amplitude:
            self.amplitude += 0.1
        else:
            self.amplitude -= 0.05
        self.amplitude = max(0.0, self.amplitude)

        # Base line
        center_y = self.height / 2
        
        if self.amplitude > 0.01:
            for i, color in enumerate(self.colors):
                offset = i * (math.pi / 4)
                points = []
                for x in range(0, self.width, 5):
                    # Siri wave formula
                    norm_x = x / self.width
                    # Gaussian window to fade edges
                    envelope = 4 * norm_x * (1 - norm_x) 
                    
                    y = center_y + math.sin(x * 0.02 + self.phase + offset) * self.amplitude * envelope * 50
                    points.append((x, y))
                
                if len(points) > 2:
                    self.create_line(points, fill=color, width=2, smooth=True)

        self.phase += self.speed
        self.after(20, self.animate)

class JarvisSiriGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("J.A.R.V.İ.S. NEXT GEN")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0a0b10")

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Chat/Content area
        
        # 1. HEADER (LOGO)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(30, 10), sticky="ew")
        
        self.logo_label = ctk.CTkLabel(self.header_frame, text="J.A.R.V.İ.S.", 
                                     font=ctk.CTkFont(family="Orbitron", size=40, weight="bold"),
                                     text_color="#ffffff")
        self.logo_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="ARTIFICIAL INTELLIGENCE", 
                                         font=ctk.CTkFont(family="DIN", size=12, weight="bold"),
                                         text_color="#636e72")
        self.subtitle_label.pack()

        # 2. SIRI WAVE VISUALIZER (Center Stage)
        self.wave_container = ctk.CTkFrame(self, fg_color="#0a0b10", height=200)
        self.wave_container.grid(row=1, column=0, sticky="nsew", padx=20)
        
        self.siri_wave = SiriWave(self.wave_container, width=860, height=200, bg_color="#0a0b10")
        self.siri_wave.pack(expand=True, fill="both")
        self.siri_wave.animate()

        # 3. TEXT FEEDBACK (Overlay or Below)
        self.status_label = ctk.CTkLabel(self, text="Listening...", font=ctk.CTkFont(size=16), text_color="#a0a0a0")
        self.status_label.grid(row=2, column=0, pady=10)

        # 4. CHAT LOG (Minimalist)
        # Using a text box that fades in/out or stays subtle
        self.chat_frame = ctk.CTkFrame(self, fg_color="#1a1c26", corner_radius=15)
        self.chat_frame.grid(row=3, column=0, padx=40, pady=(0, 20), sticky="nsew")
        self.grid_rowconfigure(3, weight=2)
        
        self.chat_log = ctk.CTkTextbox(self.chat_frame, font=ctk.CTkFont(size=14), fg_color="transparent", text_color="#ecf0f1")
        self.chat_log.pack(fill="both", expand=True, padx=15, pady=15)

        # 5. INPUT BAR (Bottom)
        self.input_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.input_frame.grid(row=4, column=0, sticky="ew", padx=40, pady=30)
        
        self.mic_btn = ctk.CTkButton(self.input_frame, text="🎤", width=50, height=50, corner_radius=25,
                                     fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(size=20),
                                     command=self.toggle_listening)
        self.mic_btn.pack(side="right", padx=10)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask Jarvis...", height=50, corner_radius=25,
                                  fg_color="#1e272e", border_width=0, font=ctk.CTkFont(size=14))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.send_text_query())

        # Logic Connections
        self.is_listening = False
        jarvis.GUI_CALLBACK = self.jarvis_callback
        self.update_status("Standby")

    def jarvis_callback(self, type, data):
        if type == "SPEAKING":
            self.update_chat("JARVIS", data)
            # Simulate wave activity while speaking
            self.siri_wave.set_amplitude(0.6)
            self.after(3000, lambda: self.siri_wave.set_amplitude(0.0))
            
        elif type == "THINKING":
            self.update_status("Processing...")
            self.siri_wave.set_amplitude(0.3)
            
        elif type == "ACTION":
            self.update_chat("SYSTEM", f"Executing: {data}")

    def update_chat(self, sender, text):
        self.chat_log.configure(state="normal")
        color = "#00d2ff" if sender == "JARVIS" else "#ffffff"
        if sender == "SYSTEM": color = "#bdc3c7"
        
        self.chat_log.insert("end", f"{sender}: ", ("bold"))
        self.chat_log.tag_config("bold", font=ctk.CTkFont(weight="bold"), foreground=color)
        self.chat_log.insert("end", f"{text}\n\n")
        self.chat_log.see("end")
        self.chat_log.configure(state="disabled")

    def update_status(self, text):
        self.status_label.configure(text=text)

    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.mic_btn.configure(fg_color="#2ecc71")
        self.update_status("Listening...")
        self.siri_wave.set_amplitude(0.8) # High amplitude for listening
        threading.Thread(target=self.listen_thread, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.mic_btn.configure(fg_color="#e74c3c")
        self.update_status("Standby")
        self.siri_wave.set_amplitude(0.0)

    def listen_thread(self):
        # Jarvis listen wrapper
        text = jarvis.listen()
        if text:
            self.after(0, lambda: self.process_input(text))
        
        # Auto stop filtering
        self.after(0, self.stop_listening)

    def send_text_query(self):
        text = self.entry.get()
        if not text: return
        self.entry.delete(0, "end")
        self.process_input(text)

    def process_input(self, text):
        self.update_chat("YOU", text)
        threading.Thread(target=lambda: jarvis.ask_agent_self_learning(text), daemon=True).start()

if __name__ == "__main__":
    app = JarvisSiriGUI()
    app.mainloop()
