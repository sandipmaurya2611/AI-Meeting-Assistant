import requests
import json

BASE_URL = "http://localhost:8000/api/rag"

print("="*70)
print("COMPREHENSIVE RAG SYSTEM VERIFICATION")
print("="*70)

# Test 1: Check server stats
print("\n[TEST 1] Checking Server Stats...")
try:
    resp = requests.get(f"{BASE_URL}/stats")
    if resp.status_code == 200:
        print("✓ Server is running")
        stats = resp.json()
        print(f"  - Vector DB: {stats['vector_db_type']}")
        print(f"  - Chunk Size: {stats['chunk_size']}")
        print(f"  - Top K: {stats['top_k_default']}")
    else:
        print(f"✗ Failed: {resp.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 2: Index documents
print("\n[TEST 2] Indexing Documents...")
try:
    resp = requests.post(f"{BASE_URL}/index/sync")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Indexed successfully")
        print(f"  - Documents: {result['details']['total_documents']}")
        print(f"  - Chunks: {result['details']['total_chunks']}")
        print(f"  - Folders: {len(result['details']['folders_indexed'])}")
    else:
        print(f"✗ Failed: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Search (context only)
print("\n[TEST 3] Testing Search (Context Retrieval)...")
try:
    resp = requests.post(
        f"{BASE_URL}/search/context-only",
        json={"query": "What is the pricing?", "top_k": 3}
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Search successful")
        print(f"  - Results: {result['total_results']}")
        if result['chunks']:
            print(f"  - Top source: {result['chunks'][0]['source']}")
    else:
        print(f"✗ Failed: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Full RAG (Search + Generate)
print("\n[TEST 4] Testing Full RAG Pipeline (Groq Generation)...")
try:
    resp = requests.post(
        f"{BASE_URL}/search",
        json={"query": "What are the payment terms?", "top_k": 3}
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ RAG pipeline successful")
        print(f"  - Retrieved: {result['total_chunks_retrieved']} chunks")
        print(f"  - Answer: {result['answer'][:200]}...")
    else:
        print(f"✗ Failed: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Meeting endpoint
print("\n[TEST 5] Testing Meeting Endpoint...")
try:
    resp = requests.post(
        f"{BASE_URL}/meeting",
        json={
            "transcript": "The client is asking about our pricing structure and volume discounts",
            "meeting_id": "demo_001"
        }
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ Meeting endpoint successful")
        print(f"  - Retrieved: {result['total_chunks_retrieved']} chunks")
        print(f"  - Answer: {result['answer'][:150]}...")
    else:
        print(f"✗ Failed: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE!")
print("="*70)
