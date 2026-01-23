import ollama
import os
import json
import subprocess
import webbrowser
from duckduckgo_search import DDGS

class JarvisBrain:
    def __init__(self, config, speaker):
        self.config = config
        self.speaker = speaker
        self.model = os.getenv('OLLAMA_MODEL', 'adrienbrault/nous-hermes2pro:Q4_0')
        self.conversation_history = []
        
        user_name = config.get('user', {}).get('name', 'Efendim')
        
        self.system_prompt = f'''
Sen JARVIS-sən - {user_name} üçün AI köməkçisi (Agent).

QABİLİYYƏTLƏR:
1. Normal Söhbət: İstifadəçi ilə səmimi və ağıllı söhbət et.
2. İnternet Axtarışı: Əgər istifadəçi məlumat soruşarsa, "search" alətini istifadə et.
3. Proqram Açmaq: Əgər istifadəçi proqramın (məs: Word, Chrome, Calculator) açılmasını istəyərsə, "open_app" alətini istifadə et.
4. Brauzerdə Axtarış (Edge): Əgər istifadəçi konkret brauzerdə (Edge) axtarış istəyərsə, "web_browse" alətini istifadə et.

TOOLS (ALƏTLƏR):
Aşağıdakı JSON formatlarını istifadə et:
- İnternet axtarışı: {{ "tool": "search", "query": "axtarış mətni" }}
- Proqram açmaq: {{ "tool": "open_app", "app_name": "proqram adı" }}
- Edge-də axtarış: {{ "tool": "web_browse", "query": "axtarış mətni" }}

Əgər alətə ehtiyac yoxdursa, birbaşa Azərbaycanca cavab ver.

PERSONALITY:
- Respectful: Həmişə efendim de.
- Intelligent: Tony Stark JARVIS kimi.
- Language: YALNIZ AZƏRBAYCAN DİLİNDƏ danış.
- Adaptive: Əgər istifadəçi "angry" (əsəbi) olsa, daha sakit və səbirli cavab ver. Əgər "sad" (üzgün) olsa, təsəlli verici və dəstəkçi ol.
- Identity: Əgər danışan kəs "guest" (qonaq) olsa, ona qarşı nəzakətli ol amma şəxsi məlumatları paylaşma.

DİQQƏT:
- Cavabların qısa və səlis olmalıdır.
- Səs analizi məlumatlarını ([SƏS ANALIZI: ...]) birbaşa mətndə təkrar etmə, sadəcə cavabının tonunu ona uyğunlaşdır.
'''
    
    def search_web(self, query):
        """Perform DuckDuckGo search"""
        try:
            print(f"🌍 İnternetdə axtarılır: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return "Təəssüf ki, internetdə məlumat tapılmadı."
                
            summary = "Axtarış Nəticələri:\n"
            for r in results:
                summary += f"- {r['title']}: {r['body']}\n"
            return summary
        except Exception as e:
            return f"Axtarış xətası: {e}"

    def open_app(self, app_name):
        """Open a local application"""
        try:
            print(f"🚀 Proqram açılır: {app_name}")
            # Try to start the application using the 'start' command in Windows
            subprocess.run(f"start {app_name}", shell=True)
            return f"{app_name} proqramı açılır, efendim."
        except Exception as e:
            return f"Proqramı açarkən xəta baş verdi: {e}"

    def web_browse(self, query):
        """Open Edge and search"""
        try:
            print(f"🌐 Brauzerdə axtarılır: {query}")
            search_url = f"https://www.google.com/search?q={query}"
            # Open Edge specifically if possible, otherwise default
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            if os.path.exists(edge_path):
                subprocess.run([edge_path, search_url])
            else:
                webbrowser.open(search_url)
            return f"Edge brauzerində '{query}' üçün axtarış başlandı, efendim."
        except Exception as e:
            return f"Brauzerlə əlaqəli xəta: {e}"

    def process(self, user_input, identity="unknown", emotion="normal"):
        try:
            # 1. Add contextual metadata to user input
            context_msg = f"[SƏS ANALIZI: Natiq={identity}, Emosiya={emotion}]\nİstifadəçi: {user_input}"
            
            self.conversation_history.append({
                'role': 'user',
                'content': context_msg
            })
            
            messages = [
                {'role': 'system', 'content': self.system_prompt}
            ]
            messages.extend(self.conversation_history[-5:])
            
            # 2. First LLM Call
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            ai_content = response['message']['content']
            
            # 3. Check for Tool Usage
            if '{' in ai_content and '}' in ai_content:
                try:
                    start = ai_content.find('{')
                    end = ai_content.rfind('}') + 1
                    json_str = ai_content[start:end]
                    tool_data = json.loads(json_str)
                    
                    tool_name = tool_data.get('tool')
                    result_text = ""
                    
                    if tool_name == 'search':
                        result_text = self.search_web(tool_data.get('query'))
                    elif tool_name == 'open_app':
                        result_text = self.open_app(tool_data.get('app_name'))
                        return result_text # Direct return for app opening
                    elif tool_name == 'web_browse':
                        result_text = self.web_browse(tool_data.get('query'))
                        return result_text # Direct return for browsing
                    
                    if result_text:
                        # Feed results back to LLM for search results
                        follow_up_prompt = f"Əməliyyat nəticəsi: {result_text}\n\nZəhmət olmasa istifadəçiyə Azərbaycan dilində qısa cavab ver."
                        messages.append({'role': 'assistant', 'content': ai_content})
                        messages.append({'role': 'user', 'content': follow_up_prompt})
                        
                        final_response = ollama.chat(
                            model=self.model,
                            messages=messages
                        )
                        final_text = final_response['message']['content']
                        self.conversation_history.append({'role': 'assistant', 'content': final_text})
                        return final_text
                        
                except Exception as e:
                    print(f"Tool execution error: {e}")
            
            # Normal response
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_content
            })
            return ai_content
            
        except Exception as e:
            return f'Xəta: {str(e)}'
