import customtkinter as ctk
import threading
import sys
import os
import math
import cv2
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
        self.webcam = None
        self.webcam_label = None
        self.is_listening = False
        
        self.title("J.A.R.V.İ.S. v5.0 - ULTIMATE")
        self.geometry("1200x800")
        self.configure(fg_color="#0a0b10")
        
        # UI Elements
        self._build_ui()
        self.siri_wave.animate()
        self._start_webcam()
        
    def _build_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=20)
        ctk.CTkLabel(self.header, text="J.A.R.V.İ.S.", font=("Orbitron", 36, "bold"), text_color="#fff").pack()
        ctk.CTkLabel(self.header, text="TITAN SYSTEM v4.0", font=("DIN", 12), text_color="#666").pack()

        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Chat and controls
        left_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True)
        
        # Wave
        self.wave_frame = ctk.CTkFrame(left_panel, fg_color="transparent", height=150)
        self.wave_frame.pack(fill="x")
        self.siri_wave = SiriWave(self.wave_frame, width=600, height=150)
        self.siri_wave.pack()
        
        # Right side - Webcam feed
        right_panel = ctk.CTkFrame(main_container, fg_color="#161b22", corner_radius=15)
        right_panel.pack(side="right", fill="both", padx=(20, 0))
        
        ctk.CTkLabel(right_panel, text="📹 Live Feed", font=("Inter", 14, "bold"), text_color="#fff").pack(pady=10)
        self.webcam_label = ctk.CTkLabel(right_panel, text="")
        self.webcam_label.pack(padx=10, pady=10)

        # Chat
        self.chat_box = ctk.CTkTextbox(left_panel, fg_color="#161b22", corner_radius=15, font=("Inter", 14))
        self.chat_box.pack(fill="both", expand=True, pady=20)
        self.chat_box.configure(state="disabled")

        # Input
        self.input_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=20)
        
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
        if self.is_listening:
            self.update_chat("SYSTEM", "Already listening...")
            return
            
        self.is_listening = True
        self.update_chat("SYSTEM", "🎤 Listening... (Speak now)")
        self.siri_wave.set_amplitude(0.7)
        self.mic_btn.configure(fg_color="#22c55e")  # Green when active
        threading.Thread(target=self._voice_listen, daemon=True).start()

    def _voice_listen(self):
        try:
            query = self.agent.voice.listen(duration=5)
            if query and query.strip():
                self.after(0, lambda: self.update_chat("YOU (voice)", query))
                self.after(0, lambda: self.entry.insert(0, query))
                self.after(0, self.send_query)
            else:
                self.after(0, lambda: self.update_chat("SYSTEM", "⚠️ No speech detected. Try again."))
        except Exception as e:
            self.after(0, lambda: self.update_chat("SYSTEM", f"❌ Voice error: {str(e)}"))
            logger.error(f"Voice listen error: {e}")
        finally:
            self.after(0, lambda: self.siri_wave.set_amplitude(0.0))
            self.after(0, lambda: self.mic_btn.configure(fg_color="#ef4444"))
            self.is_listening = False
    
    def _start_webcam(self):
        """Start webcam feed in background thread"""
        def update_frame():
            try:
                self.webcam = cv2.VideoCapture(0)
                while True:
                    ret, frame = self.webcam.read()
                    if ret:
                        # Resize and convert for display
                        frame = cv2.resize(frame, (400, 300))
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame)
                        imgtk = ImageTk.PhotoImage(image=img)
                        
                        if self.webcam_label and self.webcam_label.winfo_exists():
                            self.webcam_label.configure(image=imgtk)
                            self.webcam_label.image = imgtk
                    else:
                        break
                    
                    # Small delay to reduce CPU usage
                    threading.Event().wait(0.03)
            except Exception as e:
                logger.error(f"Webcam error: {e}")
                if self.webcam_label and self.webcam_label.winfo_exists():
                    self.after(0, lambda: self.webcam_label.configure(text="📹 Camera unavailable"))
        
        threading.Thread(target=update_frame, daemon=True).start()
    
    def destroy(self):
        """Clean up webcam on close"""
        if self.webcam:
            self.webcam.release()
        super().destroy()

if __name__ == "__main__":
    from main import JarvisAgent
    agent = JarvisAgent()
    gui = JarvisGUI(agent)
    gui.mainloop()
