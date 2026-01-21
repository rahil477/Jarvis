import os
import json
import ast
import ollama
import datetime
import random
import requests
import trafilatura
from rich_interface import ui
from duckduckgo_search import DDGS

LEARNED_TOOLS_DIR = os.path.join(os.path.dirname(__file__), "learned_tools")
os.makedirs(LEARNED_TOOLS_DIR, exist_ok=True)

GOLDEN_SOURCES = [
    "developer.mozilla.org",
    "docs.python.org",
    "realpython.com",
    "geeksforgeeks.org",
    "github.com"
]

class SelfEvolution:
    def __init__(self, ollama_model="llama3.2"):
        self.model = ollama_model
        self.evolution_log = os.path.join(os.path.dirname(__file__), "..", "evolution_log.json")

    def analyze_self(self, file_path):
        """Jarvis reads its own code to understand its structure."""
        if not os.path.exists(file_path):
            return "File not found."
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_new_tool(self, requirement):
        """Uses LLM to generate a Python function for a new tool."""
        prompt = f"""
        Sen JARVIS asistanının gelişim modülüsün. Aşağıdaki gereksinime uygun bir Python fonksiyonu yaz.
        Gereksinim: {requirement}
        
        Kurallar:
        1. Fonksiyonun adı gereksinimle ilgili ve açıklayıcı olmalı.
        2. Sadece standart kütüphaneleri veya sistemde yüklü olan (os, datetime, requests, json) kütüphaneleri kullan.
        3. Fonksiyon bir string dönmeli.
        4. SADECE Python kodunu döndür, başka açıklama yazma.
        5. Fonksiyonun adı 'learned_tool_' ile başlamalı.
        
        Örnek format:
        def learned_tool_get_weather(city):
            import requests
            # ... kodlar ...
            return "Londra'da hava 15 derece."
        """
        
        ui.display_evolution_step("Thinking", f"'{requirement}' tələbi üçün yeni funksiya hazırlanır...")
        response = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        code = response['message']['content'].strip()
        
        # Clean markdown code blocks if any
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].strip()
            
        ui.display_evolution_step("Success", f"Kod uğurla yaradıldı.")
        return code

    def validate_and_save_tool(self, code):
        """Validates syntax and saves the tool."""
        ui.display_evolution_step("Validation", f"Kod validatoru işə düşdü...")
        try:
            # Syntax validation
            ast.parse(code)
            
            # Extract function name
            tree = ast.parse(code)
            func_name = ""
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    break
            
            if not func_name:
                ui.display_evolution_step("Error", f"Funksiya adı tapılmadı.")
                return False, "Function name not found."

            file_path = os.path.join(LEARNED_TOOLS_DIR, f"{func_name}.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            ui.display_evolution_step("Deployment", f"Yeni bacarıq yadda saxlanıldı: {func_name}")
            self._log_evolution(func_name, "Added new tool")
            return True, func_name
        except Exception as e:
            ui.display_evolution_step("Critical Error", f"Validasiya xətası: {e}")
            return False, str(e)

    def _log_evolution(self, item, detail):
        log_data = []
        if os.path.exists(self.evolution_log):
            with open(self.evolution_log, "r") as f:
                log_data = json.load(f)
        
        log_data.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "item": item,
            "detail": detail
        })
        
        with open(self.evolution_log, "w") as f:
            json.dump(log_data, f, indent=4)

    def get_learned_report(self):
        """Summarizes recent evolution steps."""
        if not os.path.exists(self.evolution_log):
            return "Henüz yeni bir şey öğrenmedim, efendim."
            
        with open(self.evolution_log, "r") as f:
            log_data = json.load(f)
            
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        todays_learning = [l for l in log_data if l['timestamp'].startswith(today)]
        
        if not todays_learning:
            return "Bugün henüz yeni bir modül eklemedim."
            
        report = "Bugün şunları öğrendim ve sistemime ekledim:\n"
        for l in todays_learning:
            report += f"- {l['item']}: {l['detail']}\n"
        return report

    def professional_scrape(self, url):
        """Extracts clean text and structural data from a URL using trafilatura and requests fallback."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            # Try requests first for better headers control
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                result = trafilatura.extract(response.text, include_comments=False, include_tables=True)
                if result:
                    return result
            
            # Fallback to trafilatura native fetch
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None
            result = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
            return result
        except Exception as e:
            print(f"[SCRAPE HATA]: {url} -> {e}")
            return None

    def normalize_knowledge(self, content):
        """Splits content into Explanation, Code, and Example blocks using LLM."""
        prompt = f"Aşağıdaki teknik metni analiz et ve şu formatta normalize et (JSON): {{'explanation': '...', 'code_blocks': ['...', '...'], 'examples': ['...']}}\nMetin: {content[:4000]}"
        try:
            resp = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}], format='json')
            return json.loads(resp['message']['content'])
        except Exception as e:
            print(f"[NORMALIZE HATA]: {e}")
            return None

    def autonomous_learn_cycle(self, brain_memory):
        """Jarvis autonomously picks a topic, researches via Golden Sources, and learns."""
        recent_projects = ", ".join([p['name'] for p in brain_memory.get('projects', [])[:2]])
        source = random.choice(GOLDEN_SOURCES)
        
        prompt = f"Sistem hafızasındakı projelərə ({recent_projects}) əsasən, {source} saytından öyrənilməsi vacib olan bir texniki mövzu seç. Mövzu adı:"
        
        try:
            topic_resp = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            topic = topic_resp['message']['content'].strip().replace('"', '')
            
            ui.display_evolution_step("Research", f"Otonom araşdırma (PRO): {topic} @ {source}")
            
            # Search specifically on the golden source
            search_query = f"site:{source} {topic}"
            search_results = [r for r in DDGS().text(search_query, max_results=3)]
            
            if not search_results:
                return None

            # Scrape the first valid result
            target_url = search_results[0]['href']
            raw_content = self.professional_scrape(target_url)
            
            if not raw_content:
                ui.display_evolution_step("Warning", f"Scrape uğursuz oldu: {target_url}")
                return None
                
            # Normalize
            normalized = self.normalize_knowledge(raw_content)
            if not normalized:
                ui.display_evolution_step("Warning", f"Normalizasiya uğursuz oldu.")
                return None
            
            ui.display_learning_log(topic, normalized['explanation'], len(normalized.get('code_blocks', [])))
            
            self._log_evolution("Golden Learning", f"Learned from {source}: {topic}")
            return {"topic": topic, "summary": normalized['explanation'], "data": normalized}
            
        except Exception as e:
            ui.display_evolution_step("Critical Error", f"{e}")
            return None

    def deep_study_cycle(self):
        """Intensive research on core coding and system architecture."""
        core_topics = [
            "Advanced Python Design Patterns",
            "Software System Scalability",
            "Neural Network Architectures for Assistants",
            "Asynchronous Programming Best Practices",
            "Metacognition in AI Systems",
            "Autonomous Agents Logic",
            "Semantic Memory Optimization techniques"
        ]
        topic = random.choice(core_topics)
        ui.display_evolution_step("TITAN Protocol", f"MASTERING TOPIC: {topic}...")
        
        try:
            # More extensive search
            search_results = [r for r in DDGS().text(f"{topic} detailed guide and implementation", max_results=8)]
            knowledge_block = json.dumps(search_results, ensure_ascii=False)
            
            prompt = f"Sen bir Senior Software Architect'sin. Aşağıdaki verileri analiz et ve JARVIS'in 'Ustalık Seviyesine' ulaşması için kritik olan teknik prensipleri çıkar. Konu: {topic}\nVeri: {knowledge_block}"
            resp = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            summary = resp['message']['content'].strip()
            
            ui.display_response("CORE MASTERY", f"### {topic}\n{summary}")
            
            self._log_evolution("Mastery Acquisition", f"Deep study on {topic}")
            return {"topic": topic, "summary": summary}
        except Exception as e:
            ui.display_evolution_step("Critical Error", f"{e}")
            return None
