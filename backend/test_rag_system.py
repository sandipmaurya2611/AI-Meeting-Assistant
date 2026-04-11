# Test script for RAG system
import requests
import json

BASE_URL = "http://localhost:8000/api/rag"

def test_index():
    """Test document indexing"""
    print("🔄 Testing document indexing...")
    response = requests.post(f"{BASE_URL}/index/sync")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_search():
    """Test search functionality"""
    print("🔍 Testing search...")
    
    queries = [
        "What is the pricing for the standard plan?",
        "Tell me about contract renewal",
        "What integrations do you support?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = requests.post(
            f"{BASE_URL}/search",
            json={"query": query, "top_k": 3}
        )
        result = response.json()
        
        print(f"\nAnswer: {result['answer']}")
        print(f"\nRetrieved {result['total_chunks_retrieved']} chunks:")
        for i, chunk in enumerate(result['retrieved_chunks'][:2], 1):
            print(f"\n  {i}. Source: {chunk['source']}")
            print(f"     Content: {chunk['content'][:100]}...")
        print("-" * 80)

def test_meeting():
    """Test meeting transcript processing"""
    print("\n💬 Testing meeting transcript processing...")
    
    transcript = "The customer is asking about our enterprise pricing and whether we offer volume discounts"
    
    response = requests.post(
        f"{BASE_URL}/meeting",
        json={
            "transcript": transcript,
            "meeting_id": "demo_meeting_001"
        }
    )
    
    result = response.json()
    print(f"\nTranscript: {transcript}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSources used: {[c['source'] for c in result['retrieved_chunks']]}")

if __name__ == "__main__":
    print("=" * 80)
    print("RAG SYSTEM TEST")
    print("=" * 80)
    
    try:
        # Test indexing
        test_index()
        
        # Test search
        test_search()
        
        # Test meeting
        test_meeting()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
