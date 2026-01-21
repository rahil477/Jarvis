
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import threading
import json
import asyncio
import edge_tts
import random

# Add Jarvis path
sys.path.append(os.path.join(os.getcwd(), "Jarvis"))
import jarvis

app = Flask(__name__)
CORS(app)

# Override Jarvis functions to work with Web
# We don't want Jarvis filtering to speakers on server side ideally, 
# but for now we will just return the text and audio path.

LATEST_AUDIO_FILE = ""

def web_speak(text):
    global LATEST_AUDIO_FILE
    filename = f"static/response_{random.randint(1000,9999)}.mp3"
    
    # Cleanup old files
    for f in os.listdir("static"):
        if f.startswith("response_") and f.endswith(".mp3"):
            try: os.remove(os.path.join("static", f))
            except: pass

    async def _gen():
        await edge_tts.Communicate(text, jarvis.TTS_VOICE).save(filename)
    
    asyncio.run(_gen())
    LATEST_AUDIO_FILE = filename
    return filename

# Mock the GUI callback
class WebBypass:
    def GUI_CALLBACK(self, type, data):
        # We could use WebSockets to push this to frontend
        pass

jarvis.GUI_CALLBACK = lambda t, d: None # Disable local GUI callbacks

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"status": "error", "message": "Boş sorğu"})

    # Use Jarvis Brain
    # Note: ask_agent_self_learning typically runs speak() internally.
    # We need to intercept the response.
    # Since jarvis.ask_agent_self_learning is complex, we will hook into it 
    # OR we can just use the internal logic if we refactored it better.
    # For now, let's use a trick: Capture stdout or modify the speak function temporarily.
    
    captured_response = []
    
    # Monkey patch jarvis.speak for this request scope? Thread safety issue.
    # Better: Modifying jarvis.py to return response instead of printing/speaking 
    # is the architectural fix. But for now, let's just make a new wrapper here if possible
    # or rely on the global speak override.
    
    global LATEST_AUDIO_FILE
    LATEST_AUDIO_FILE = ""
    
    # Hijack speak
    original_speak = jarvis.speak
    jarvis.speak = lambda t: captured_response.append(t)
    jarvis.speak_enhanced = lambda t: captured_response.append(t) # Override enhanced too
    
    try:
        jarvis.ask_agent_self_learning(query)
    except Exception as e:
        captured_response.append(f"Xəta: {e}")
    finally:
        # Restore
        jarvis.speak = original_speak
        jarvis.speak_enhanced = original_speak
        
    full_text = " ".join(captured_response)
    
    # Generate Audio for the Web
    audio_url = ""
    if full_text:
        audio_path = web_speak(full_text)
        audio_url = "/" + audio_path
        
    return jsonify({
        "status": "success",
        "response": full_text,
        "audio_url": audio_url
    })

if __name__ == '__main__':
    # Ensure static dir exists
    if not os.path.exists("static"): os.makedirs("static")
    app.run(debug=True, port=5000)
