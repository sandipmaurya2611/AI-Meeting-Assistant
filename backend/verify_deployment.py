import requests
import time
import sys
import json

BASE_URL = "http://localhost:8000/api/rag"

def wait_for_server():
    print("Waiting for server...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/stats")
            print("Server is ready!")
            return True
        except:
            time.sleep(2)
            print(".", end="", flush=True)
    print("\nServer not responding.")
    return False

def verify_system():
    if not wait_for_server():
        sys.exit(1)

    print("\n1. Re-indexing documents (New Embeddings)...")
    try:
        resp = requests.post(f"{BASE_URL}/index/sync")
        if resp.status_code == 200:
            print("✓ Indexing successful")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"✗ Indexing failed: {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

    print("\n2. Testing Search & Generation (Groq)...")
    try:
        query = "What is the pricing for the standard plan?"
        resp = requests.post(
            f"{BASE_URL}/search",
            json={"query": query, "top_k": 3}
        )
        if resp.status_code == 200:
            result = resp.json()
            print("✓ Search successful")
            print(f"Answer: {result['answer']}")
            print(f"Sources: {[c['source'] for c in result['retrieved_chunks']]}")
        else:
            print(f"✗ Search failed: {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_system()
