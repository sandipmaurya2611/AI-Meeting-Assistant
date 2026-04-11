import requests
import json

BASE_URL = "http://localhost:8000/api/meetings"

print("="*70)
print("TESTING MULTI-PARTICIPANT MEETING SYSTEM")
print("="*70)

# Test 1: Create a meeting
print("\n[TEST 1] Creating a new meeting...")
try:
    response = requests.post(
        BASE_URL,
        json={
            "host_id": "user-123",
            "title": "Test Meeting"
        }
    )
    
    if response.status_code == 200:
        meeting = response.json()
        print("✓ Meeting created successfully")
        print(f"  ID: {meeting['id']}")
        print(f"  Room: {meeting['room_name']}")
        print(f"  URL: {meeting['meeting_url']}")
        
        room_name = meeting['room_name']
    else:
        print(f"✗ Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 2: Get meeting by room name (simulating join link)
print("\n[TEST 2] Fetching meeting by room name...")
try:
    response = requests.get(f"{BASE_URL}/room/{room_name}")
    
    if response.status_code == 200:
        meeting = response.json()
        print("✓ Meeting fetched successfully")
        print(f"  Title: {meeting['title']}")
        print(f"  Room: {meeting['room_name']}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE!")
print("="*70)
