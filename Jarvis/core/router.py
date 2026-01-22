import re
from Jarvis.core.config import config
from Jarvis.utils.logger import logger

class TaskRouter:
    @staticmethod
    def route(query: str) -> str:
        """
        Determines the best model for the given query.
        TIER 1: Core Intelligence - Multi-model Orchestration
        """
        query_lower = query.lower()
        
        # Routing Logic (Re-enabled after model installation)
        if any(w in query_lower for w in ["yaz", "kod", "script", "function", "debug"]):
            return config.MODEL_MAP.get("code", config.OLLAMA_MODEL)
        elif any(w in query_lower for w in ["izah et", "nədir", "necə", "araşdır"]):
            return config.MODEL_MAP.get("complex", config.OLLAMA_MODEL)
        elif any(w in query_lower for w in ["hesabla", "riyaziyyat", "məntiq"]):
            return config.MODEL_MAP.get("logic", config.OLLAMA_MODEL)
        elif len(query.split()) < 5:
            return config.MODEL_MAP.get("fast", config.OLLAMA_MODEL)
        
        return config.OLLAMA_MODEL
