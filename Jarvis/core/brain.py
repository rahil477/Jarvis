import ollama
import os

class JarvisBrain:
    def __init__(self, config, speaker):
        self.config = config
        self.speaker = speaker
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.conversation_history = []
        
        # System prompt
        user_name = config.get('user', {}).get('name', 'User')
        location = config.get('user', {}).get('location', 'Unknown')
        
        self.system_prompt = f"""
Sen JARVIS-sən - {user_name} üçün AI köməkçisi.

PERSONALITY:
- Respectful: Həmişə "efendim" de
- Intelligent: Tony Stark'ın JARVIS kimi
- Helpful: Proaktiv və faydalı
- Concise: Qısa və aydın cavablar

CAPABILITIES:
- Sualları cavablandır
- Məlumat ver
- Tapşırıqları yerinə yetir

LANGUAGE: Azeri/Turkish qarışığı (natural)

CURRENT USER: {user_name}
LOCATION: {location}
"""
    
    def process(self, user_input):
        """Process user input and generate response"""
        try:
            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            messages.extend(self.conversation_history[-10:])  # Last 10 exchanges
            
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            assistant_response = response['message']['content']
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            return f"Bağışlayın efendim, xəta baş verdi: {str(e)}"
