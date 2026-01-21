import os
import json
import ast
import ollama
import datetime
import random
from Jarvis.utils.logger import logger
from Jarvis.core.config import config

class SelfEvolution:
    def __init__(self):
        self.learned_tools_dir = config.JARVIS_DIR / "learned_tools"
        os.makedirs(self.learned_tools_dir, exist_ok=True)
        self.evolution_log = config.BASE_DIR / "evolution_log.json"

    def generate_new_tool(self, requirement):
        """Tier 4: Self-Coding Agent - Tool Generation"""
        prompt = f"""
        Sen JARVIS asistanının gelişim modülüsün. Aşağıdaki gereksinime uygun bir Python fonksiyonu yaz.
        Gereksinim: {requirement}
        
        Kurallar:
        1. Fonksiyonun adı gereksinimle ilgili ve açıklayıcı olmalı.
        2. SADECE Python kodunu döndür, başka açıklama yazma.
        3. Fonksiyonun adı 'learned_tool_' ile başlamalı.
        4. Bir string sonuç dönmeli.
        """
        
        try:
            logger.info(f"Generating new tool for: {requirement}")
            response = ollama.chat(model=config.OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
            code = response['message']['content'].strip()
            
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].strip()
            
            # Validate and Save
            success, func_name = self._validate_and_save(code)
            if success:
                self._log_evolution(func_name, f"Automatically generated for: {requirement}")
                return f"Uğurla tamamlandı. Yeni bacarıq əlavə edildi: {func_name}"
            return f"Xəta baş verdi: {func_name}"
        except Exception as e:
            logger.error(f"Tool generation failed: {e}")
            return f"Error: {e}"

    def _validate_and_save(self, code):
        try:
            ast.parse(code)
            tree = ast.parse(code)
            func_name = next((node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)), None)
            
            if not func_name: return False, "No function name found."

            file_path = self.learned_tools_dir / f"{func_name}.py"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            return True, func_name
        except Exception as e:
            return False, str(e)

    def _log_evolution(self, item, detail):
        log_data = []
        if os.path.exists(self.evolution_log):
            try:
                with open(self.evolution_log, "r") as f:
                    log_data = json.load(f)
            except: pass
        
        log_data.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "item": item,
            "detail": detail
        })
        
        with open(self.evolution_log, "w") as f:
            json.dump(log_data, f, indent=4)

    def get_learned_report(self):
        if not os.path.exists(self.evolution_log):
            return "Henüz bir şey öğrenmedim."
        with open(self.evolution_log, "r") as f:
            log_data = json.load(f)
        return json.dumps(log_data[-5:], indent=2)
