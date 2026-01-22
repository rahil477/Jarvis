import re
from Jarvis.core.config import config
from Jarvis.utils.logger import logger

class TaskRouter:
    @staticmethod
    def route(query: str) -> str:
        """
        Determines the best model for the given query.
        TIER 1: Core Intelligence - Multi-model Orchestration
        
        Simplified version: Uses llama3.2 for all queries until other models are installed.
        """
        # For now, always use the base model (llama3.2)
        # This prevents "model not found" warnings
        return config.OLLAMA_MODEL
        
        # Future: Uncomment below when you install specialized models
        # query_lower = query.lower()
        # 
        # if any(w in query_lower for w in ["yaz", "kod", "script", "function", "debug"]):
        #     return config.MODEL_MAP.get("code", config.OLLAMA_MODEL)
        # elif any(w in query_lower for w in ["izah et", "nədir", "necə", "araşdır"]):
        #     return config.MODEL_MAP.get("complex", config.OLLAMA_MODEL)
        # elif any(w in query_lower for w in ["hesabla", "riyaziyyat", "məntiq"]):
        #     return config.MODEL_MAP.get("logic", config.OLLAMA_MODEL)
        # 
        # return config.OLLAMA_MODEL
