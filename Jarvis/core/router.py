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
        
        # Coding tasks
        if any(w in query_lower for w in ["yaz", "kod", "script", "function", "debug", "python", "javascript", "html", "css"]):
            logger.info("Routing to CODE model (Mistral)")
            return config.MODEL_MAP["code"]
        
        # Complex reasoning / Long explanation
        if any(w in query_lower for w in ["izah et", "nədir", "necə", "proses", "təhlil", "araşdır"]):
            logger.info("Routing to COMPLEX model (Llama 3.2)")
            return config.MODEL_MAP["complex"]
        
        # Logic / Math tasks
        if any(w in query_lower for w in ["hesabla", "riyaziyyat", "məntiq", "isbat"]):
            logger.info("Routing to LOGIC model (DeepSeek)")
            return config.MODEL_MAP["logic"]

        # Default to fast for short or conversational queries
        if len(query.split()) < 5:
            logger.info("Routing to FAST model (Phi-3)")
            return config.MODEL_MAP["fast"]

        return config.OLLAMA_MODEL
