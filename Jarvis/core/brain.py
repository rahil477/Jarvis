import os
import json
import re
import datetime
import random
import time
import ollama
import psutil
import pyautogui
from Jarvis.utils.logger import logger
from Jarvis.core.config import config
from Jarvis.prompts import UNIFIED_SYSTEM_PROMPT

class JarvisBrain:
    def __init__(self):
        self.memory = self.load_memory()
        self.episodic_memory = self.load_episodic_memory()
        self.collection = self._init_chroma()
        
    def _init_chroma(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=config.CHROMA_PATH)
            return client.get_or_create_collection(name="jarvis_semantic_memory")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            return None

    def load_memory(self):
        if os.path.exists(config.MEMORY_FILE):
            try:
                with open(config.MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Memory load error: {e}")
        
        return {
            "xp": 0, "level": 1,
            "user": {"name": "Rahil Menefzade", "location": "Azerbaijan"},
            "patterns": [],
            "reward_score": 0.5,
            "ab_test_variants": {"metrics": {"A": {"success": 0, "total": 0}, "B": {"success": 0, "total": 0}}},
            "performance_metrics": {"avg_latency": 0, "total_interactions": 0}
        }

    def save_memory(self):
        with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def load_episodic_memory(self):
        if os.path.exists(config.EPISODIC_MEMORY_FILE):
            try:
                with open(config.EPISODIC_MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return []

    def save_episodic_memory(self):
        with open(config.EPISODIC_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.episodic_memory[-100:], f, ensure_ascii=False, indent=4)

    def get_context(self, query):
        context = ""
        if self.collection:
            try:
                results = self.collection.query(query_texts=[query], n_results=3)
                if results['documents']:
                    context = "\nBENZER GEÇMİŞ TECRÜBELER:\n" + "\n".join(results['documents'][0])
            except: pass
        return context

    def log_interaction(self, query, response, tools_used, status="Success", latency=0, ab_variant="A"):
        now = datetime.datetime.now()
        interaction_data = {
            "timestamp": now.isoformat(),
            "query": query,
            "response": response,
            "tools": tools_used,
            "status": status,
            "context": {
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "latency": latency,
                "ab_variant": ab_variant
            }
        }
        
        # Layer 6 Update
        self._update_ab_metrics(ab_variant, status == "Success")
        self._update_performance_metrics(latency)
        
        # Append to master log
        with open(config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(interaction_data, ensure_ascii=False) + "\n")
            
        logger.info(f"Interaction logged. Status: {status}, Latency: {latency:.2f}s")

    def _update_ab_metrics(self, variant, success):
        abs = self.memory.get("ab_test_variants", {"metrics": {"A": {"success": 0, "total": 0}, "B": {"success": 0, "total": 0}}})
        if variant in abs["metrics"]:
            abs["metrics"][variant]["total"] += 1
            if success: abs["metrics"][variant]["success"] += 1
        self.memory["ab_test_variants"] = abs
        self.save_memory()

    def _update_performance_metrics(self, latency):
        pm = self.memory.get("performance_metrics", {"avg_latency": 0, "total_interactions": 0})
        total = pm["total_interactions"]
        avg = pm["avg_latency"]
        new_total = total + 1
        pm["total_interactions"] = new_total
        pm["avg_latency"] = ((avg * total) + latency) / new_total
        self.memory["performance_metrics"] = pm
        self.save_memory()

    def add_to_episodic_memory(self, query, response, outcome):
        self.episodic_memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query, "response": response, "outcome": outcome
        })
        self.save_episodic_memory()

    def mine_patterns(self):
        if not os.path.exists(config.LOG_FILE): return
        try:
            with open(config.LOG_FILE, "r", encoding="utf-8") as f:
                logs = [json.loads(line) for line in f][-20:]
            
            prompt = f"Analyze these recent interactions and detect recurring patterns, user preferences, or habits. Return a list of patterns in JSON format.\nLogs: {json.dumps(logs)}"
            resp = ollama.chat(model=config.OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], format='json')
            patterns = json.loads(resp['message']['content'])
            
            if isinstance(patterns, list):
                self.memory["patterns"] = patterns[:10]
                self.save_memory()
                logger.info(f"Mined {len(patterns)} new behavior patterns.")
        except Exception as e:
            logger.error(f"Pattern mining failed: {e}")
