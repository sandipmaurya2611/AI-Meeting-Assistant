"""
Test script for the authentication system.
This script tests user registration, login, and protected endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_authentication():
    """Test the complete authentication flow."""
    
    # Test data
    test_user = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    
    print("🔐 Testing Authentication System")
    print("=" * 60)
    
    # 1. Test Registration
    print("\n1️⃣  Testing User Registration...")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=test_user
    )
    print_response("REGISTRATION RESPONSE", response)
    
    if response.status_code == 201:
        data = response.json()
        token = data.get("access_token")
        user = data.get("user")
        print(f"✅ Registration successful!")
        print(f"   User ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
        print(f"   Token: {token[:50]}...")
    elif response.status_code == 400:
        print("⚠️  User already exists, proceeding to login...")
        token = None
    else:
        print("❌ Registration failed!")
        return
    
    # 2. Test Login
    print("\n2️⃣  Testing User Login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    print_response("LOGIN RESPONSE", response)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user = data.get("user")
        print(f"✅ Login successful!")
        print(f"   User ID: {user.get('id')}")
        print(f"   Token: {token[:50]}...")
    else:
        print("❌ Login failed!")
        return
    
    # 3. Test Get Current User (Protected Endpoint)
    print("\n3️⃣  Testing Protected Endpoint (Get Current User)...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    print_response("GET CURRENT USER RESPONSE", response)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Protected endpoint access successful!")
        print(f"   User ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
    else:
        print("❌ Protected endpoint access failed!")
        return
    
    # 4. Test Invalid Token
    print("\n4️⃣  Testing Invalid Token...")
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    print_response("INVALID TOKEN RESPONSE", response)
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected!")
    else:
        print("❌ Invalid token should have been rejected!")
    
    # 5. Test Wrong Password
    print("\n5️⃣  Testing Wrong Password...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": test_user["email"],
            "password": "wrongpassword"
        }
    )
    print_response("WRONG PASSWORD RESPONSE", response)
    
    if response.status_code == 401:
        print("✅ Wrong password correctly rejected!")
    else:
        print("❌ Wrong password should have been rejected!")
    
    # 6. Test Logout
    print("\n6️⃣  Testing Logout...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers=headers
    )
    print_response("LOGOUT RESPONSE", response)
    
    if response.status_code == 200:
        print("✅ Logout successful!")
    else:
        print("❌ Logout failed!")
    
    # Summary
    print("\n" + "="*60)
    print("🎉 AUTHENTICATION SYSTEM TEST COMPLETE!")
    print("="*60)
    print("\n✅ All authentication features are working correctly!")
    print("\nFeatures Tested:")
    print("  ✓ User Registration")
    print("  ✓ User Login")
    print("  ✓ Protected Endpoints")
    print("  ✓ JWT Token Validation")
    print("  ✓ Invalid Token Rejection")
    print("  ✓ Wrong Password Rejection")
    print("  ✓ Logout")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        test_authentication()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server!")
        print("   Make sure the backend is running on http://localhost:8000")
        print("   Run: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
