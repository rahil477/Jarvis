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
        target = config.OLLAMA_MODEL
        
        # Routing Logic
        if any(w in query_lower for w in ["yaz", "kod", "script", "function", "debug"]):
            target = config.MODEL_MAP["code"]
        elif any(w in query_lower for w in ["izah et", "nədir", "necə", "araşdır"]):
            target = config.MODEL_MAP["complex"]
        elif any(w in query_lower for w in ["hesabla", "riyaziyyat", "məntiq"]):
            target = config.MODEL_MAP["logic"]
        elif len(query.split()) < 5:
            target = config.MODEL_MAP["fast"]

        # Fallback Check
        try:
            import ollama
            resp = ollama.list()
            # Handle both object and dict-like responses
            if hasattr(resp, 'models'):
                installed = [m.model for m in resp.models]
            elif isinstance(resp, dict) and 'models' in resp:
                installed = [m.get('name') or m.get('model') for m in resp['models']]
            else:
                installed = []

            if target not in installed and f"{target}:latest" not in installed:
                logger.warning(f"Model {target} not found. Falling back to {config.OLLAMA_MODEL}")
                return config.OLLAMA_MODEL
        except Exception as e:
            logger.error(f"Router fallback check failed: {e}")
            pass
            
        return target
