import requests
import json

BASE_URL = "http://localhost:8000/api/copilot"

print("="*70)
print("TESTING REAL-TIME AI MEETING CO-PILOT")
print("="*70)

# Test 1: Simple copilot (no context/RAG)
print("\n[TEST 1] Simple Copilot (Transcript only)...")
try:
    response = requests.post(
        f"{BASE_URL}/simple",
        json={
            "transcript": "The client just asked about our pricing plans and whether we have any discounts available."
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Copilot response received")
        print(f"\n  Suggestion: {result['suggestion']}")
        print(f"  Follow-up: {result['follow_up_question']}")
        print(f"  Confusion: {result['confusion_detected']}")
        print(f"  Talking Points:")
        for point in result['talking_points']:
            print(f"    - {point}")
        print(f"  CRM Update: {result['crm_update']}")
        print(f"  Task: {result['task_creation']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Full copilot with RAG
print("\n" + "="*70)
print("[TEST 2] Full Copilot (With RAG Knowledge Base)...")
try:
    response = requests.post(
        f"{BASE_URL}/copilot",
        json={
            "transcript": "Customer wants to know about contract renewal policies and early termination fees.",
            "meeting_id": "demo_meeting",
            "use_rag": True,
            "top_k": 3
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Copilot response received (with RAG)")
        print(f"\n  Suggestion: {result['suggestion']}")
        print(f"  Follow-up: {result['follow_up_question']}")
        print(f"  Confusion: {result['confusion_detected']}")
        print(f"  Talking Points:")
        for point in result['talking_points']:
            print(f"    - {point}")
        print(f"  CRM Update: {result['crm_update']}")
        print(f"  Task: {result['task_creation']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Confusion detection
print("\n" + "="*70)
print("[TEST 3] Confusion Detection...")
try:
    response = requests.post(
        f"{BASE_URL}/simple",
        json={
            "transcript": "Wait, I'm not sure I understand. Can you explain that again? I'm confused about the differences."
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Copilot response received")
        print(f"\n  Confusion Detected: {result['confusion_detected']}")
        print(f"  Suggestion: {result['suggestion']}")
        print(f"  Follow-up: {result['follow_up_question']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Task creation
print("\n" + "="*70)
print("[TEST 4] Task Creation Detection...")
try:
    response = requests.post(
        f"{BASE_URL}/copilot",
        json={
            "transcript": "This sounds great! Can you send me a detailed proposal and pricing breakdown?",
            "meeting_id": "demo_meeting",
            "use_rag": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Copilot response received")
        print(f"\n  Suggestion: {result['suggestion']}")
        print(f"  Task: {result['task_creation']}")
        print(f"  CRM Update: {result['crm_update']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("COPILOT TESTS COMPLETE!")
print("="*70)
