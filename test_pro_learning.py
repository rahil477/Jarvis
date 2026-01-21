import sys
import os

# Add Jarvis directory to path
sys.path.append(os.path.join(os.getcwd(), "Jarvis"))

from self_evolution import SelfEvolution

def test_pro_learning():
    print("Testing JARVIS Professional Learning Pipeline...")
    evolver = SelfEvolution(ollama_model="llama3.2")
    
    urls = [
        "https://docs.python.org/3/tutorial/controlflow.html",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions",
        "https://realpython.com/python-functions/"
    ]
    
    for test_url in urls:
        print(f"\n--- Testing: {test_url} ---")
        try:
            content = evolver.professional_scrape(test_url)
            if content:
                print(f"Success! Scraped {len(content)} characters.")
                print("Normalizing knowledge...")
                normalized = evolver.normalize_knowledge(content)
                if normalized:
                    print("--- Normalized Data ---")
                    print(f"Explanation: {normalized.get('explanation', '')[:100]}...")
                    print(f"Code Blocks: {len(normalized.get('code_blocks', []))}")
                    break
            else:
                print("Scraping failed.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_pro_learning()
