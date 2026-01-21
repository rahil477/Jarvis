import re
import os
from Jarvis.utils.logger import logger

class SecurityManager:
    @staticmethod
    def validate_input(text):
        """Basic input sanitization"""
        if not text: return False
        # Remove potentially dangerous characters for shell/command injection
        sanitized = re.sub(r'[;&|`$]', '', text)
        return sanitized

    @staticmethod
    def check_api_keys():
        """Check if required API keys are present in environment"""
        required = ["OLLAMA_MODEL"]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            logger.warning(f"Missing configuration keys: {missing}")
            return False
        return True

    @staticmethod
    def is_safe_command(command):
        """Whitelist for system commands if needed"""
        whitelist = ["ls", "dir", "date", "time", "echo"]
        base_cmd = command.split()[0].lower()
        return base_cmd in whitelist
