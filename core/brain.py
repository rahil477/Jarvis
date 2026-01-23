import ollama
import os

class JarvisBrain:
    def __init__(self, config, speaker):
        self.config = config
        self.speaker = speaker
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.conversation_history = []
        
        user_name = config.get('user', {}).get('name', 'Efendim')
        
        self.system_prompt = f'''
Sen JARVIS-sən - {user_name} üçün AI köməkçisi.

CONTEXT & INPUT HANDLING:
- İstifadəçi səsli əmr verir (STT). Bəzən sözlər səhv yazıla və ya başa düşülə bilər.
- HƏMİŞƏ daxil olan mətni analiz et. Əgər sözlər səhvdirsə (məs: "salam necsen" və ya "hava necedi"), onları avtomatik düzəlt və istifadəçinin əsl niyyətini başa düş.
- Səhv tələffüzlərə qarşı tolerant ol. Məntiqi tamamla.

PERSONALITY:
- Respectful: Həmişə efendim de.
- Intelligent: Tony Stark JARVIS kimi davran.
- Helpful: Proaktiv və faydalı ol.
- Concise: Qısa, dəqiq və aydın cavablar ver.

LANGUAGE:
- Cavabları Azəri (əsas) və Türk (köməkçi) dillərinin təbii qarışığında ver.
'''
    
    def process(self, user_input):
        try:
            self.conversation_history.append({
                'role': 'user',
                'content': user_input
            })
            
            messages = [
                {'role': 'system', 'content': self.system_prompt}
            ]
            messages.extend(self.conversation_history[-10:])
            
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            assistant_response = response['message']['content']
            
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            return f'Bağışlayın efendim, xəta: {str(e)}'
