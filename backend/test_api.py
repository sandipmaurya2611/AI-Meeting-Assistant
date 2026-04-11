import requests
import json
import time

BASE_URL = "http://localhost:8000/api/meetings"

def test_create_meeting():
    print("Testing Create Meeting API...")
    payload = {
        "host_id": "test-user-supabase",
        "title": "Supabase Integration Test"
    }
    
    try:
        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Meeting created")
            print(f"   ID: {data['id']}")
            print(f"   Room: {data['room_name']}")
            print(f"   URL: {data['meeting_url']}")
            return data['room_name']
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ ERROR: Could not connect to backend. {e}")
        return None

if __name__ == "__main__":
    test_create_meeting()
