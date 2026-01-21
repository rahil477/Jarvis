import os
import json
import datetime
import chromadb
from transformers import pipeline
import ollama

# --- 1. CONFIG ---
CHROMA_PATH = "./jarvis_chroma"
MEMORY_FILE = "assistant_memory.json"
LOG_DIR = "experience_logs"

def run_diagnostics():
    print("\n" + "="*50)
    print("   J.A.R.V.İ.S. TITAN v5.0 ADVANCED DIAGNOSTICS")
    print("="*50 + "\n")

    # --- Test 1: ChromaDB (Layer 3: Semantic Memory) ---
    print("--- 1. SEMANTIC MEMORY (ChromaDB) ---")
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name="jarvis_semantic_memory")
        collection.add(
            documents=["TEST_ENTRY: Diagnostics run at " + str(datetime.datetime.now())],
            ids=["diag_" + str(datetime.datetime.now().timestamp())],
            metadatas=[{"type": "diag"}]
        )
        results = collection.query(query_texts=["TEST_ENTRY"], n_results=1)
        if results['documents']:
            print("✅ ChromaDB: OK (Write/Read successful)")
        else:
            print("❌ ChromaDB: FAILED (No results returned)")
    except Exception as e:
        print(f"❌ ChromaDB: ERROR ({e})")

    # --- Test 2: Sentiment Analysis (Self-Learning Mood Context) ---
    print("\n--- 2. SENTIMENT ANALYSIS (Transformers) ---")
    try:
        sentiment_model = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")
        result = sentiment_model("I am very happy with my AI assistant!")[0]
        print(f"✅ Sentiment: OK (Detected: {result['label']} score: {result['score']:.2f})")
    except Exception as e:
        print(f"❌ Sentiment: ERROR ({e})")

    # --- Test 3: Experience Collector (Layer 1: Logging) ---
    print("\n--- 3. EXPERIENCE COLLECTOR (Logging Structure) ---")
    if os.path.exists(LOG_DIR):
        files = os.listdir(LOG_DIR)
        print(f"✅ Experience Logs: OK ({len(files)} log files found)")
    else:
        print("❌ Experience Logs: FAILED (Directory not found)")

    # --- Test 4: Autonomy & Reasoning (Layer 4: ReAct Loop) ---
    print("\n--- 4. AUTONOMOUS REASONING (Ollama ReAct) ---")
    try:
        prompt = "Geçen hafta ne öğrendiğini kısaca özetle."
        resp = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
        content = resp['message']['content']
        print(f"✅ Reasoning Engine: OK (Model response received)")
        print(f"--- PREVIEW --- \n{content[:200]}...")
    except Exception as e:
        print(f"❌ Reasoning Engine: ERROR ({e})")

    print("\n" + "="*50)
    print("   DIAGNOSTICS COMPLETE")
    print("="*50)

if __name__ == "__main__":
    run_diagnostics()
