import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("="*70)
print("TESTING REAL-TIME AI WEBSOCKET SYSTEM")
print("="*70)

# Test 1: Send transcript for processing
print("\n[TEST 1] Sending transcript for processing...")
try:
    response = requests.post(
        f"{BASE_URL}/process-transcript",
        json={
            "transcript": "The client is asking about our pricing plans and whether we offer any volume discounts.",
            "meeting_id": "test_meeting_001",
            "speaker": "Client",
            "use_rag": True,
            "top_k": 3
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Transcript processed successfully")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        print(f"  Preview: {result['preview']['suggestion']}")
        print("\n  → AI suggestion has been pushed to WebSocket queue")
        print("  → All connected WebSocket clients will receive it automatically")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Another transcript (confusion detection)
print("\n" + "="*70)
print("[TEST 2] Testing confusion detection...")
time.sleep(2)

try:
    response = requests.post(
        f"{BASE_URL}/process-transcript",
        json={
            "transcript": "Wait, I'm not sure I understand. Can you explain that again? I'm confused.",
            "meeting_id": "test_meeting_001",
            "speaker": "Client",
            "use_rag": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Confusion transcript processed")
        print(f"  Preview: {result['preview']['suggestion']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Task creation
print("\n" + "="*70)
print("[TEST 3] Testing task creation...")
time.sleep(2)

try:
    response = requests.post(
        f"{BASE_URL}/process-transcript",
        json={
            "transcript": "This sounds perfect! Can you send me a detailed proposal and pricing breakdown?",
            "meeting_id": "test_meeting_001",
            "speaker": "Client",
            "use_rag": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Task creation transcript processed")
        print(f"  Preview: {result['preview']['suggestion']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE!")
print("="*70)
print("\nℹ️  To see the WebSocket in action:")
print("1. Open http://localhost:3000 in your browser")
print("2. Connect to the AI WebSocket")
print("3. Run this script again")
print("4. Watch the AI suggestions appear in real-time!")
