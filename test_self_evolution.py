import sys
import os

# Add Jarvis directory to path
sys.path.append(os.path.join(os.getcwd(), "Jarvis"))

from self_evolution import SelfEvolution

def test_evolution():
    print("Testing JARVIS Self-Evolution Logic...")
    evolver = SelfEvolution(ollama_model="llama3.2")
    
    requirement = "Sisteme basit bir döviz çevirici ekle (USD to AZN)."
    print(f"Generating tool for: {requirement}")
    
    code = evolver.generate_new_tool(requirement)
    print("--- Generated Code ---")
    print(code)
    print("----------------------")
    
    success, result = evolver.validate_and_save_tool(code)
    if success:
        print(f"Success! Tool saved as: {result}")
        print("Now checking the report...")
        print(evolver.get_learned_report())
    else:
        print(f"Failure: {result}")

if __name__ == "__main__":
    test_evolution()
