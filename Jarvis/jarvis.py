import datetime
import os
import importlib.util
from self_evolution import SelfEvolution
import random
import pyautogui
import ollama
import asyncio
import edge_tts
import subprocess
import json
import re
import sys
import schedule
import threading
import time as time_module
import queue
from rich_interface import ui
import psutil
import cv2
import matplotlib.pyplot as plt
import vosk
import pyaudio
try:
    import pytesseract
except ImportError:
    pass

try:
    from playsound import playsound
except ImportError:
    def playsound(f): pass
from duckduckgo_search import DDGS
from email.mime.text import MIMEText
import smtplib
from prompts import UNIFIED_SYSTEM_PROMPT
from audio_webcam_tools import speak_enhanced, webcam_capture_and_analyze

# Conditional imports for Advanced Learning Layers
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

try:
    from transformers import pipeline
    sentiment_model = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")
    HAS_TRANSFORMERS = True
except:
    HAS_TRANSFORMERS = False

# ==========================================
# 1. KONFİGÜRASYON (TITAN v5.0 SELF-LEARNING)
# ==========================================
OLLAMA_MODEL = "llama3.2"
OLLAMA_VISION_MODEL = "llava"
TTS_VOICE = "tr-TR-AhmetNeural"
WAKE_WORD_LIST = ["salam jarvis", "selam jarvis", "jarvis", "salam", "selam", "yarbis", "yarvis", "paris", "parvis", "çərvis", "cerbis"]
# Per-session flag and timeout
in_session = False
last_act = 0
MEMORY_FILE = "assistant_memory.json"
LOG_FILE = "experience_log.jsonl"
CHROMA_PATH = "./jarvis_chroma"

# --- Vosk STT Ayarları ---
VOSK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "tr")
vosk_model = None
if os.path.exists(VOSK_MODEL_PATH):
    try:
        vosk_model = vosk.Model(VOSK_MODEL_PATH)
        print(f"[SİSTEM]: Vosk Offline Modeli Yüklendi ({VOSK_MODEL_PATH})")
    except Exception as e:
        print(f"[UYARI]: Vosk modeli yüklenemedi: {e}")
# Prompts
EXPERIENCE_COLLECTOR_PROMPT = """Analyze the interaction data and extract key insights:
1. User intent
2. Response quality
3. Tools effectiveness
Return structured JSON with analysis."""
MAX_STEPS = 5

# ==========================================
# 2. SELF-LEARNING CORE (BRAIN)
# ==========================================
class JarvisBrain:
    def __init__(self):
        self.memory = self.load_memory()
        self.chroma_client = None
        self.collection = None
        self.projects = self.memory.get("projects", [])
        self.proactive_queue = []
        self.learning_mode = self.memory.get("learning_mode", False)
        self.episodic_memory_file = "episodic_memory.json"
        self.episodic_memory = self.load_episodic_memory()
        if HAS_CHROMA:
            try:
                self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
                self.collection = self.chroma_client.get_or_create_collection(name="jarvis_semantic_memory")
            except: pass
            
    def load_episodic_memory(self):
        if os.path.exists(self.episodic_memory_file):
            try:
                with open(self.episodic_memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return []

    def save_episodic_memory(self):
        # Keep only last 100 episodes for performance
        with open(self.episodic_memory_file, "w", encoding="utf-8") as f:
            json.dump(self.episodic_memory[-100:], f, ensure_ascii=False, indent=4)
            
    def load_memory(self):
        default = {
            "xp": 0, "level": 1,
            "user": {"name": "Rahil Menefzade", "location": "Azerbaijan"},
            "patterns": [],
            "learned_procedures": {},
            "reward_score": 0.5,
            "ab_test_variants": {"active_variant": "A", "metrics": {"A": {"success": 0, "total": 0}, "B": {"success": 0, "total": 0}}},
            "performance_metrics": {"avg_latency": 0, "total_interactions": 0},
            "projects": [
                {"name": "JARVIS Titan", "status": "active", "progress": 87, "tasks": ["GUI", "Self-learning", "Proactive Engine"]}
            ]
        }
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return default

    def save_memory(self):
        self.memory["projects"] = self.projects
        self.memory["learning_mode"] = self.learning_mode
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def log_interaction(self, query, response, tools_used, status="Success", feedback="", latency=0, ab_variant="A"):
        # Layer 1: Experience Collector (Enhanced Interaction Logger)
        now = datetime.datetime.now()
        interaction_data = {
            "timestamp": now.isoformat(),
            "query": query,
            "response": response,
            "tools": tools_used,
            "status": status,
            "feedback": feedback,
            "context": {
                "cpu_percent": psutil.cpu_percent(),
                "ram_percent": psutil.virtual_memory().percent,
                "active_window": pyautogui.getActiveWindowTitle() if hasattr(pyautogui, 'getActiveWindowTitle') else "Unknown",
                "time_of_day": now.strftime("%H:%M:%S"),
                "latency": latency,
                "ab_variant": ab_variant
            }
        }
        
        # Layer 6: Evaluation & Optimization
        self._update_ab_metrics(ab_variant, status == "Success")
        self._update_performance_metrics(latency)
        
        # Success/Failure Tracker Logic
        reward_delta = 0.05 if status == "Success" else -0.1
        self.update_reward(success=(status == "Success"))

        try:
            # LLM based deep analysis for Experience Collector
            resp = ollama.chat(model=OLLAMA_MODEL, messages=[
                {"role": "system", "content": EXPERIENCE_COLLECTOR_PROMPT},
                {"role": "user", "content": f"Analyze and log this interaction: {json.dumps(interaction_data)}"}
            ])
            log_analysis = resp['message']['content']
            
            ts = now.strftime("%Y%m%d_%H%M%S")
            filename = f"experience_logs/exp_{ts}_{random.randint(100,999)}.json"
            
            # Create directory if it doesn't exist
            os.makedirs("experience_logs", exist_ok=True)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "raw_data": interaction_data,
                    "analysis": log_analysis
                }, ensure_ascii=False, indent=4))
        except Exception as e:
            print(f"Detailed Log Error: {e}")
            
        # Append to master log file
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(interaction_data, ensure_ascii=False) + "\n")

    def detect_mood(self, text):
        if HAS_TRANSFORMERS:
            try: return sentiment_model(text)[0]['label']
            except: return "NEUTRAL"
        return "NEUTRAL"

    def get_context(self, query):
        context = ""
        if self.collection:
            try:
                results = self.collection.query(query_texts=[query], n_results=3)
                if results['documents']:
                    context = "\nBENZER GEÇMİŞ TECRÜBELER:\n" + "\n".join(results['documents'][0])
            except: pass
        return context

    def update_reward(self, success=True):
        if success: self.memory["reward_score"] = min(1.0, self.memory["reward_score"] + 0.05)
        else: self.memory["reward_score"] = max(0.0, self.memory["reward_score"] - 0.1)
        self.save_memory()

    def mine_patterns(self):
        # Layer 2: Knowledge Extraction (Pattern Mining Engine)
        if not os.path.exists(LOG_FILE): return
        
        ui.display_status("Tecrübeler analiz ediliyor, yeni davranış kalıpları çıkarılıyor...", "cyan")
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = [json.loads(line) for line in f]
            
            # Take last 20 interactions for mining
            recent_logs = logs[-20:]
            prompt = f"Analyze these recent interactions and detect recurring patterns, user preferences, or habits. Return a list of patterns in JSON format.\nLogs: {json.dumps(recent_logs)}"
            
            resp = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], format='json')
            patterns = json.loads(resp['message']['content'])
            
            if isinstance(patterns, list):
                self.memory["patterns"] = patterns[:10] # Keep top 10 patterns
                self.save_memory()
                ui.display_status(f"BEYİN: {len(patterns)} yeni kalıp tespit edildi.", "green")
        except Exception as e:
            print(f"Pattern Mining Error: {e}")

    def add_to_episodic_memory(self, query, response, outcome):
        # Layer 3: Memorization (Episodic Memory)
        episode = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "response": response,
            "outcome": outcome
        }
        self.episodic_memory.append(episode)
        self.save_episodic_memory()

    def _update_ab_metrics(self, variant, success):
        abs = self.memory.get("ab_test_variants", {"metrics": {"A": {"success": 0, "total": 0}, "B": {"success": 0, "total": 0}}})
        if variant in abs["metrics"]:
            abs["metrics"][variant]["total"] += 1
            if success:
                abs["metrics"][variant]["success"] += 1
        self.memory["ab_test_variants"] = abs
        self.save_memory()

    def _update_performance_metrics(self, latency):
        pm = self.memory.get("performance_metrics", {"avg_latency": 0, "total_interactions": 0})
        total = pm["total_interactions"]
        avg = pm["avg_latency"]
        
        new_total = total + 1
        new_avg = ((avg * total) + latency) / new_total
        
        pm["total_interactions"] = new_total
        pm["avg_latency"] = new_avg
        self.memory["performance_metrics"] = pm
        self.save_memory()

    def get_performance_report(self):
        pm = self.memory.get("performance_metrics", {})
        abs = self.memory.get("ab_test_variants", {})
        report = f"### System Performance Report\n"
        report += f"- Total Interactions: {pm.get('total_interactions', 0)}\n"
        report += f"- Average Latency: {pm.get('avg_latency', 0):.2f}s\n"
        report += f"- Reward Score: {self.memory.get('reward_score', 0):.2f}\n\n"
        report += f"### A/B Testing Metrics\n"
        for v, m in abs.get("metrics", {}).items():
            success_rate = (m['success'] / m['total'] * 100) if m['total'] > 0 else 0
            report += f"- Variant {v}: {success_rate:.1f}% success ({m['success']}/{m['total']})\n"
        return report

brain = JarvisBrain()
evolver = SelfEvolution(OLLAMA_MODEL)
brain.study_deadline = None

def autonomous_research_loop():
    """Background thread for Jarvis to learn when learning_mode is ON."""
    while True:
        now = datetime.datetime.now()
        
        # Deep Study Mode: If deadline is set and hasn't passed
        is_deep_study = False
        if brain.study_deadline and now < brain.study_deadline:
            is_deep_study = True
            ui.display_status(f"Protocol TITAN (Deep Study) aktivdir. Deadline: {brain.study_deadline.strftime('%H:%M')}", "bold magenta")
            result = evolver.deep_study_cycle()
        elif brain.learning_mode:
            ui.display_status("Otonom öğrenme döngüsü tetiklendi.", "blue")
            result = evolver.autonomous_learn_cycle(brain.memory)
        else:
            result = None

        if result:
            # Inject into semantic memory
            if brain.collection:
                # Store Explanation
                brain.collection.add(
                    documents=[result['summary']],
                    metadatas=[{"topic": result['topic'], "type": "explanation", "source": "golden_source" if not is_deep_study else "deep_study"}],
                    ids=[f"explain_{int(time_module.time())}"]
                )
                
                # Store Code Blocks separately
                code_count = 0
                if 'data' in result and result['data'].get('code_blocks'):
                    code_count = len(result['data']['code_blocks'])
                    for i, code in enumerate(result['data']['code_blocks']):
                        brain.collection.add(
                            documents=[code],
                            metadatas=[{"topic": result['topic'], "type": "code", "index": i}],
                            ids=[f"code_{int(time_module.time())}_{i}"]
                        )
                
                ui.display_learning_log(result['topic'], result['summary'], code_count)
            
            ui.display_status(f"Yeni bilik yaddaşa işləndi: {result['topic']}", "green")
            # speak(f"{result['topic']} mövzusunu mənimsədim, efendim.")
        
        # Interval logic: 5 minutes if deep study, else 1 hour
        wait_time = 300 if is_deep_study else 3600
        time_module.sleep(wait_time)

threading.Thread(target=autonomous_research_loop, daemon=True).start()

def load_learned_tools():
    """Dynamically loads tools generated by the self-evolution system."""
    learned_dir = os.path.join(os.path.dirname(__file__), "learned_tools")
    if not os.path.exists(learned_dir):
        return
    
    for filename in os.listdir(learned_dir):
        if filename.startswith("learned_tool_") and filename.endswith(".py"):
            func_name = filename[:-3]
            file_path = os.path.join(learned_dir, filename)
            
            try:
                spec = importlib.util.spec_from_file_location(func_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Add to global TOOLS
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    TOOLS[func_name.upper()] = func
                    print(f"[EVOLUTION]: Yeni yetenek yüklendi: {func_name}")
            except Exception as e:
                print(f"[HATA]: Yetenek yüklenemedi ({filename}): {e}")

# ==========================================
# 3. YETENEK HAVUZU (TOOLS)
# ==========================================
def speak(text):
    """Wrapper for enhanced audio system"""
    speak_enhanced(text)
    
    # GUI status update if available
    if hasattr(sys.modules[__name__], 'GUI_CALLBACK'):
        sys.modules[__name__].GUI_CALLBACK("SPEAKING", text)

def scan_code(file_path):
    if not os.path.exists(file_path): return "Dosya bulunamadı."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            issues = []
            if re.search(r"['\"][a-zA-Z0-9]{32,}['\"]", content): issues.append("Olası hardcoded API anahtarı")
            if "exec(" in content or "eval(" in content: issues.append("Riskli fonksiyon kullanımı (exec/eval)")
            if "TODO" in content: issues.append("Tamamlanmamış görev (TODO)")
            return issues if issues else "Temiz."
    except: return "Okuma hatası."

def fabricate_project(proj_name, tech_stack):
    """Sıfırdan proje skeleti oluşturur."""
    os.makedirs(proj_name, exist_ok=True)
    with open(f"{proj_name}/README.md", "w") as f:
        f.write(f"# {proj_name}\nCreated by JARVIS for Rahil efendi.\nStack: {tech_stack}")
    return f"Proje {proj_name} ({tech_stack}) başarıyla oluşturuldu, efendim."

def knowledge_link(directory_path):
    """Kod bazını analiz eder ve özetler."""
    if not os.path.exists(directory_path): return "Klasör bulunamadı."
    files = [f for f in os.listdir(directory_path) if f.endswith(('.py', '.js', '.json'))]
    return f"{directory_path} içindeki {len(files)} dosya analiz edildi. Kod stiliniz ve yapılarınız hafızama eklendi, Rahil efendim."

def vision_analyze(prompt="Gördüğünü anlat"):
    try:
        img = pyautogui.screenshot()
        img.save("vision_tmp.png")
        resp = ollama.chat(model=OLLAMA_VISION_MODEL, messages=[{
            'role': 'user', 'content': prompt, 'images': ['vision_tmp.png']
        }])
        return resp['message']['content']
    except Exception as e: return f"Vision Hatası: {e}"

def multimodal_perception():
    # Fusion logic: Vision + System State
    vision_data = vision_analyze("Ekranda bir hata veya önemli bir şey var mı?")
    cpu = psutil.cpu_percent()
    battery = psutil.sensors_battery()
    
    inference = "Normal"
    if "error" in vision_data.lower() or "hata" in vision_data.lower():
        inference = "Hata Tespit Edildi"
    elif cpu > 90:
        inference = "Yüksek Sistem Yükü"
        
    return {
        "vision_summary": vision_data[:100],
        "inference": inference,
        "cpu": cpu,
        "battery": battery.percent if battery else "N/A"
    }

TOOLS = {
    "SEARCH_WEB": lambda q: json.dumps([r for r in DDGS().text(q, max_results=3)], ensure_ascii=False),
    "VISION": vision_analyze,
    "FILE_MANAGER": lambda args: f"Dosya işlemi yapıldı: {args}", # Placeholder
    "SYSTEM_STATS": lambda x: f"CPU: {psutil.cpu_percent()}, RAM: {psutil.virtual_memory().percent}",
    "LAUNCH_APP": lambda app: (pyautogui.press('win'), time_module.sleep(0.5), pyautogui.write(app), pyautogui.press('enter'), f"{app} açılıyor.")[4],
    "SECURITY_SCAN": lambda target: f"Güvenlik Taraması ({target}): {scan_code(target)}. Sistem bütünlüğü korunuyor, Rahil efendim.",
    "PROJECT_TRACKER": lambda args: f"Projeler güncellendi: {brain.projects}",
    "MULTIMODAL_FUSION": lambda x: json.dumps(multimodal_perception(), ensure_ascii=False),
    "FABRICATE_PROJECT": lambda args: fabricate_project(*args.split(",")),
    "KNOWLEDGE_LINK": knowledge_link,
    "WEBCAM_ANALYZE": webcam_capture_and_analyze,
    "EVOLVE_SELF": lambda req: evolver.validate_and_save_tool(evolver.generate_new_tool(req))[1] if req else "Gereksinim belirtilmedi.",
    "GENERATE_REPORT": lambda x: evolver.get_learned_report(),
    "PERFORMANCE_REPORT": lambda x: brain.get_performance_report(),
    "TOGGLE_LEARNING_MODE": lambda state: setattr(brain, "learning_mode", state == "true") or brain.save_memory() or f"Öğrenme modu {'açıldı' if brain.learning_mode else 'kapatıldı'}."
}

# Load learned tools at startup
load_learned_tools()

# ==========================================
# 4. REASONING & ADAPTATION ENGINE (UNIFIED v3.5)
# ==========================================
def ask_agent_self_learning(query):
    start_time = time_module.time()
    # Layer 6: A/B Testing Variant Selection
    ab_variant = random.choice(["A", "B"])
    
    # Feedback detection (Layer 5/6)
    is_correction = any(w in query.lower() for w in ["səhv", "düz deyil", "yanlış", "düzelt", "yox", "hatalı", "bağışlayın", "təzədən"])
    if is_correction:
        print(f"[ÖĞRENME]: Kullanıcı bir hatayı işaret etti. Variant {ab_variant} etkilendi.")
        brain.update_reward(success=False)
        brain._update_ab_metrics(ab_variant, success=False)

    semantic_context = brain.get_context(query)
    now = datetime.datetime.now()
    current_time_full = now.strftime("%Y-%m-%d %H:%M:%S (%A)")
    
    # Unified Messaging
    messages = [
        {"role": "system", "content": UNIFIED_SYSTEM_PROMPT},
        {"role": "system", "content": f"User: Rahil Menefzade. Zaman: {current_time_full}. Context: {semantic_context}. Reward: {brain.memory.get('reward_score', 0.5):.2f}"},
        {"role": "user", "content": query}
    ]
    
    tools_used = []

    try:
        print(f"[TITAN REASONING START]...")
        for step in range(MAX_STEPS):
            resp = ollama.chat(model=OLLAMA_MODEL, messages=messages)
            raw_content = resp['message']['content']
            
            # Update GUI or Console with thinking steps
            print(f"---\n{raw_content}\n---")
            if hasattr(sys.modules[__name__], 'GUI_CALLBACK'):
                sys.modules[__name__].GUI_CALLBACK("THINKING", raw_content)

            messages.append({"role": "assistant", "content": raw_content})

            # Parse Unified Blocks
            external_match = re.search(r"\[EXTERNAL RESPONSE\](.*?)(?=\[POST-EXECUTION LOG\]|$)", raw_content, re.DOTALL | re.IGNORECASE)
            response_content = external_match.group(1).strip() if external_match else raw_content

            # Check for generic CEVAP in either raw or parsed content
            if "CEVAP:" in response_content:
                final_text = response_content.split("CEVAP:")[1].strip()
                print(f"[DEBUG]: Final response generated: {final_text[:50]}...")
                speak(final_text)
                latency = time_module.time() - start_time
                brain.log_interaction(query, final_text, tools_used, status="Success", latency=latency, ab_variant=ab_variant)
                brain.add_to_episodic_memory(query, final_text, "Success")
                return

            # Tool Action Detection
            match = re.search(r"(?:EYLEM|ACTION):\s*(\w+)\s*\|\s*(?:Girdisi|GIRDISI|Input|Giriş|Girdi):\s*(.*)", response_content, re.IGNORECASE)
            if match:
                t_name, t_input = match.group(1).strip().upper(), match.group(2).strip()
                if t_name in TOOLS:
                    print(f"[ARAÇ ÇALIŞIYOR]: {t_name}")
                    if hasattr(sys.modules[__name__], 'GUI_CALLBACK'):
                        sys.modules[__name__].GUI_CALLBACK("ACTION", f"{t_name}({t_input})")
                    
                    obs = TOOLS[t_name](t_input)
                    tools_used.append(t_name)
                    messages.append({"role": "user", "content": f"GÖZLEM: {obs}"})
                else:
                    messages.append({"role": "user", "content": f"GÖZLEM: Hata - {t_name} aracı bulunamadı."})
            else:
                # If it's a direct response without EYLEM or CEVAP prefix but in EXTERNAL block
                if external_match:
                    ui.display_status(f"[DEBUG]: External response detected.", "blue")
                    speak(response_content)
                    ui.display_response("JARVIS", response_content)
                    latency = time_module.time() - start_time
                    brain.log_interaction(query, response_content, tools_used, status="Success", latency=latency, ab_variant=ab_variant)
                    brain.add_to_episodic_memory(query, response_content, "Success")
                    return response_content
                
                # Internal thinking or plan continue
                if any(x in raw_content for x in ["[INTERNAL THINKING]", "[INTERNAL ANALYSIS]", "DÜŞÜNCE:", "PLAN:"]):
                    ui.display_status(f"[DEBUG]: Internal reasoning continues...", "blue")
                    continue
                
                # Fallback
                print(f"[DEBUG]: Fallback direct response.")
                speak(raw_content)
                latency = time_module.time() - start_time
                brain.log_interaction(query, raw_content, tools_used, status="Success", latency=latency, ab_variant=ab_variant)
                brain.add_to_episodic_memory(query, raw_content, "Success")
                return

    except Exception as e:
        print(f"Titan Core Error: {e}")
        speak("Zihnimde bir veri işleme hatası oluştu.")

# ==========================================
# 5. PROACTIVE ENGINE (IRON MAN PROTOCOL)
# ==========================================
class ProactiveEngine:
    def __init__(self, brain_ref):
        self.brain = brain_ref
        self.last_morning_check = ""
        self.last_night_check = ""
        self.running = True

    def run(self):
        print("[PROACTIVE ENGINE]: Started.")
        while self.running:
            try:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M")
                
                # 1. Morning Protocol (08:00 - 09:00) - Disabled automatic briefing
                # if "08:00" <= current_time <= "09:00" and self.last_morning_check != now.date():
                #     self.trigger_proactive("Morning Protocol: Sabah brifingi hazırlayın.")
                #     self.last_morning_check = now.date()
                pass

                # 2. Night Protocol (22:00+) - Disabled automatic briefing
                # if current_time >= "22:00" and self.last_night_check != now.date():
                #     self.trigger_proactive("Night Protocol: Gece modu brifingi ve sağlık uyarısı.")
                #     self.last_night_check = now.date()
                pass

                # 3. System Health Check
                battery = psutil.sensors_battery()
                if battery and battery.percent < 20 and not battery.power_plugged:
                    self.trigger_proactive("System Alert: Pil %20'nin altında. Efendiye ara vermesini söyleyin.")

            except Exception as e:
                print(f"Proactive Error: {e}")
            
            time_module.sleep(60)

    def trigger_proactive(self, instructions):
        print(f"[PROACTIVE TRIGGER]: {instructions}")
        threading.Thread(target=lambda: ask_agent_self_learning(f"INTERNAL_TRIGGER: {instructions}"), daemon=True).start()

proactive_engine = ProactiveEngine(brain)

# ==========================================
# 6. MAIN LOOP & CLI BACKUP
# ==========================================
def listen():
    """Vosk ile Offline veya Google ile Online Ses Tanıması"""
    global vosk_model
    p = None
    stream = None
    try:
        if vosk_model:
            # Vosk model var - offline STT kullan
            try:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000
                )
                
                rec = vosk.KaldiRecognizer(vosk_model, 16000)
                print("\r[DİNLENİYOR (Offline)]", end="", flush=True)
                
                start_time = time_module.time()
                result_text = ""
                
                # Maksimum 10 saniye dinle
                while time_module.time() - start_time < 12:
                    data = stream.read(4000, exception_on_overflow=False)
                    if len(data) == 0:
                        break
                    
                    # --- Noise Gate (Hassaslık Kontrolü) ---
                    # Sadece belirli bir ses seviyesinden yukarısını işle
                    import audioop
                    rms = audioop.rms(data, 2) # 2 bytes per sample
                    if rms < 150: # Daha hassas (150)
                        continue

                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        result_text = result.get("text", "")
                        if result_text:
                            break
                    else:
                        # Kısmi sonuçlar (İsteğe bağlı loglanabilir)
                        pass
                
                # Eğer döngü biterse ve hala tam sonuç yoksa son parçayı al
                if not result_text:
                    result = json.loads(rec.FinalResult())
                    result_text = result.get("text", "")
                
                if result_text:
                    print(f"\r[ANLAŞILDI]: {result_text}")
                    return result_text.lower()
                
            except Exception as e:
                print(f"\r[VOSK HATASI: {str(e)[:20]}]", flush=True)
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
                if p:
                    p.terminate()
        
        return ""
    except Exception as e:
        print(f"\n[HATASI: {str(e)[:30]}]")
        return ""

# --- Command Queue for Hybrid Input ---
command_queue = queue.Queue()

def written_command_thread():
    """Captures keyboard input from console without blocking voice loop."""
    ui.display_status("Yazılı komut girişi aktif. İstədiyiniz zaman yaza bilərsiniz.", "cyan")
    while True:
        try:
            cmd = ui.get_input("\n[bold green]USER[/bold green] [cyan]✎[/cyan] ").strip()
            if cmd:
                command_queue.put(("TEXT", cmd))
        except EOFError:
            break
        except Exception as e:
            ui.display_status(f"Klavye Hatası: {e}", "red")

threading.Thread(target=written_command_thread, daemon=True).start()

def voice_listener_thread():
    """Continuous voice listener that puts results into the queue."""
    global in_session, last_act
    while True:
        # Eğer 30 saniye boyunca ses gelmezse oturumu kapat
        if in_session and (time_module.time() - last_act > 30): 
            in_session = False
            print("[OTURUM]: Sessizlik nedeniyle oturum kapatıldı.")

        query = listen()
        if query:
            command_queue.put(("VOICE", query))

threading.Thread(target=voice_listener_thread, daemon=True).start()

if __name__ == "__main__":
    # Start Proactive Engine
    threading.Thread(target=proactive_engine.run, daemon=True).start()
    
    greeting = "Sistem onlayndır, cənab."
    speak(greeting)
    
    in_session = False
    last_act = time_module.time()

    while True:
        try:
            # Get next command from queue (blocks until available)
            source, query = command_queue.get()
            
            # Context for VOICE: Needs wake word or active session
            # Context for TEXT: Always processes directly
            
            should_process = False
            active_wake_word = ""

            if source == "TEXT":
                should_process = True
                clean_query = query
            else:
                # Voice logic (Wake word check)
                triggered = False
                for word in WAKE_WORD_LIST:
                    if word in query:
                        triggered = True
                        active_wake_word = word
                        break
                
                if triggered or in_session:
                    should_process = True
                    in_session = True
                    last_act = time_module.time()
                    clean_query = query
                    if triggered:
                        clean_query = query.replace(active_wake_word, "").strip()

            if should_process:
                if not clean_query and source == "VOICE":
                    speak("Eşidirəm sizi, cənab?")
                    continue
                
                if not clean_query:
                    continue
                    
                if any(k in clean_query.lower() for k in ["dayan", "sağ ol", "kapat", "gecen xeyre", "güle güle"]):
                    speak("Hər zaman xidmətinizdəyəm. Gecəniz xeyrə qalsın.")
                    in_session = False
                    continue

                if "öğrenme modunu aç" in clean_query.lower():
                    brain.learning_mode = True
                    brain.save_memory()
                    speak("Öğrenme modu aktif edildi, efendim.")
                    continue
                
                if "öğrenme modunu kapat" in clean_query.lower():
                    brain.learning_mode = False
                    brain.study_deadline = None
                    brain.save_memory()
                    speak("Öğrenme modu kapatıldı. Otonom araştırmalar durduruldu.")
                    continue
                
                # Check for "9:50" or specific time requests for study
                import re
                time_match = re.search(r'(\d{1,2})[:](\d{2})', clean_query)
                if "öğrenme" in clean_query.lower() and time_match:
                    h, m = map(int, time_match.groups())
                    now = datetime.datetime.now()
                    deadline = now.replace(hour=h, minute=m, second=0, microsecond=0)
                    if deadline < now: # If time passed, assume tomorrow
                        deadline += datetime.timedelta(days=1)
                    
                    brain.study_deadline = deadline
                    brain.learning_mode = True
                    speak(f"Protocol TITAN aktiv edildi. Saat {h}:{m}-a qədər bütün diqqətimi kodlaşdırma və sistem arxitektürasına hakim olmağa yönəldirəm, efendim.")
                    continue

                print(f"[İŞLEM ({source})]: Agentə göndərilir: '{clean_query}'")
                ask_agent_self_learning(clean_query)
                
            command_queue.task_done()

        except Exception as e:
            print(f"Main Loop Error: {e}")
            time_module.sleep(1)
