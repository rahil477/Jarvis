"""
JARVIS Multi-Model Orchestration Test
Tests the intelligent routing system across different query types
"""

from Jarvis.core.router import TaskRouter
from Jarvis.core.config import config

def test_routing():
    print("=" * 60)
    print("JARVIS MULTI-MODEL ORCHESTRATION TEST")
    print("=" * 60)
    print()
    
    test_queries = [
        # Code-related queries (should route to mistral)
        ("Python-da bir function yaz", "mistral:latest"),
        ("Bu kodu debug et", "mistral:latest"),
        
        # Short conversational queries (should route to phi3:mini)
        ("salam", "phi3:mini"),
        ("necəsən", "llama3.2:latest"),  # "necə" triggers explanation mode
        ("yaxşı", "phi3:mini"),
        
        # Complex explanation queries (should route to llama3.2)
        ("AI nədir və necə işləyir", "llama3.2:latest"),
        ("Mənə izah et quantum computing", "llama3.2:latest"),
        
        # Math/Logic queries (should route to deepseek-r1:7b)
        ("2+2 hesabla", "deepseek-r1:7b"),
        ("Bu riyaziyyat problemini həll et", "deepseek-r1:7b"),
        
        # Default queries (should route to llama3.2)
        ("Bu gün hava necədir?", "llama3.2:latest"),  # "necə" triggers explanation
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_model in test_queries:
        routed_model = TaskRouter.route(query)
        
        # Normalize model names (handle :latest suffix)
        def normalize_model(model):
            if ':' not in model:
                return model + ':latest'
            return model
        
        routed_normalized = normalize_model(routed_model)
        expected_normalized = normalize_model(expected_model)
        
        status = "✅ PASS" if routed_normalized == expected_normalized else "❌ FAIL"
        
        if routed_normalized == expected_normalized:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} | Query: '{query}'")
        print(f"      Expected: {expected_model}")
        print(f"      Got:      {routed_model}")
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_queries)} tests")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = test_routing()
    exit(0 if success else 1)
