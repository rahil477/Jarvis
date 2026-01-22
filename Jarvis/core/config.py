import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    JARVIS_DIR = BASE_DIR / "Jarvis"
    
    # Models
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")
    
    # Tier 1: Multi-model Orchestration
    MODEL_MAP = {
        "complex": "llama3.2:latest",
        "fast": "phi3:mini",
        "code": "mistral:latest",
        "logic": "deepseek-r1:7b",
        "vision": "llava:latest"
    }
    
    # Audio
    TTS_VOICE = os.getenv("TTS_VOICE", "tr-TR-AhmetNeural")
    VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", str(BASE_DIR / "model" / "tr"))
    
    # Files
    MEMORY_FILE = str(BASE_DIR / os.getenv("MEMORY_FILE", "assistant_memory.json"))
    EPISODIC_MEMORY_FILE = str(BASE_DIR / os.getenv("EPISODIC_MEMORY_FILE", "episodic_memory.json"))
    LOG_FILE = str(BASE_DIR / os.getenv("LOG_FILE", "experience_log.jsonl"))
    CHROMA_PATH = str(BASE_DIR / os.getenv("CHROMA_PATH", "jarvis_chroma"))
    
    # Logic
    MAX_REASONING_STEPS = int(os.getenv("MAX_REASONING_STEPS", "5"))
    WAKE_WORDS = ["salam jarvis", "selam jarvis", "jarvis"]

    @classmethod
    def load_from_yaml(cls, yaml_path):
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                for key, value in data.items():
                    if hasattr(cls, key.upper()):
                        setattr(cls, key.upper(), value)

# Instance for use
config = Config()
