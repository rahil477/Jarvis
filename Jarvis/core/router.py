import re
from Jarvis.core.config import config
from Jarvis.utils.logger import logger

class TaskRouter:
    @staticmethod
    def route(query: str) -> str:
        """
        Determines the best model for the given query.
        TIER 1: Core Intelligence - Multi-model Orchestration (Enhanced)
        """
        query_lower = query.lower()
        
        # Priority 1: Math/Logic (most specific)
        math_keywords = ["hesabla", "riyaziyyat", "məntiq", "isbat", "hesab et", "toplama", "çıxma", "vurma", "bölmə"]
        if any(w in query_lower for w in math_keywords):
            return config.MODEL_MAP.get("logic", config.OLLAMA_MODEL)
        
        # Priority 2: Code (specific technical terms)
        code_keywords = ["yaz", "kod", "script", "function", "debug", "python", "javascript", "html", "css", "bug", "error"]
        if any(w in query_lower for w in code_keywords):
            return config.MODEL_MAP.get("code", config.OLLAMA_MODEL)
        
        # Priority 3: Complex explanations (longer queries with explanation keywords)
        explanation_keywords = ["izah et", "nədir", "araşdır", "təhlil", "anlat", "explain"]
        if any(w in query_lower for w in explanation_keywords):
            return config.MODEL_MAP.get("complex", config.OLLAMA_MODEL)
        
        # Priority 4: Short conversational (very short queries, excluding "necə" which means "how")
        # Exclude "necə" from short queries as it usually requires explanation
        if len(query.split()) < 5 and "necə" not in query_lower:
            return config.MODEL_MAP.get("fast", config.OLLAMA_MODEL)
        
        # Default: Use base model for everything else
        return config.OLLAMA_MODEL
