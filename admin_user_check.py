#!/usr/bin/env python3

import requests
import json

def check_user_with_zip_30126():
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Try to login with existing test user to get some access
    login_payload = {
        "email": "territory1756780976@example.com",
        "password": "testpass123"
    }
    
    print("🔑 Attempting to login with test user...")
    login_response = requests.post(f"{api_url}/auth/login", json=login_payload, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    token = login_data["access_token"]
    user_data = login_data["user"]
    
    print(f"✅ Logged in as: {user_data['email']}")
    print(f"👤 User territories: {user_data.get('owned_territories', [])}")
    
    # Check if we can access admin endpoints
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 Attempting to access admin users endpoint...")
    users_response = requests.get(f"{api_url}/admin/users", headers=headers, timeout=15)
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        print(f"✅ Found {len(users_data)} users in database")
        
        # Look for users with ZIP 30126
        users_with_30126 = []
        for user in users_data:
            if "30126" in user.get("owned_territories", []):
                users_with_30126.append(user)
        
        if users_with_30126:
            print(f"\n🚨 Found {len(users_with_30126)} user(s) with ZIP 30126:")
            for user in users_with_30126:
                print(f"   📧 Email: {user.get('email')}")
                print(f"   👤 Name: {user.get('first_name')} {user.get('last_name')}")
                print(f"   🆔 ID: {user.get('id')}")
                print(f"   🗺️ Territories: {user.get('owned_territories')}")
                print(f"   ✅ Active: {user.get('is_active')}")
                print(f"   📅 Created: {user.get('created_at')}")
                print()
        else:
            print("✅ No users found with ZIP 30126 in database")
            
        # Look for the specific user mentioned in the availability check
        target_email = "final_test_1757173779@example.com"
        target_user = None
        for user in users_data:
            if user.get('email') == target_email:
                target_user = user
                break
        
        if target_user:
            print(f"\n🎯 Found target user {target_email}:")
            print(f"   👤 Name: {target_user.get('first_name')} {target_user.get('last_name')}")
            print(f"   🆔 ID: {target_user.get('id')}")
            print(f"   🗺️ Territories: {target_user.get('owned_territories')}")
            print(f"   ✅ Active: {target_user.get('is_active')}")
            print(f"   📅 Created: {target_user.get('created_at')}")
        else:
            print(f"\n❌ Target user {target_email} NOT found in database")
            print("🔍 This suggests a database inconsistency!")
            
    elif users_response.status_code == 403:
        print("❌ Access denied to admin endpoint (user is not admin)")
        print("🔍 Will try alternative approach...")
        
        # Try to check if the target user exists by attempting to create it
        target_email = "final_test_1757173779@example.com"
        test_register = {
            "email": target_email,
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        register_response = requests.post(f"{api_url}/auth/register", json=test_register, timeout=10)
        
        if register_response.status_code == 400:
            register_data = register_response.json()
            if "already registered" in register_data.get("detail", "").lower():
                print(f"✅ User {target_email} EXISTS in database")
                
                # Try to login with this user
                login_test = {
                    "email": target_email,
                    "password": "testpass123"  # Try common password
                }
                
                login_test_response = requests.post(f"{api_url}/auth/login", json=login_test, timeout=10)
                if login_test_response.status_code == 200:
                    login_test_data = login_test_response.json()
                    test_user_data = login_test_data["user"]
                    print(f"✅ Successfully logged in as {target_email}")
                    print(f"🗺️ User territories: {test_user_data.get('owned_territories', [])}")
                else:
                    print(f"❌ Cannot login as {target_email} (wrong password or account issue)")
            else:
                print(f"❌ Registration failed for other reason: {register_data.get('detail')}")
        else:
            print(f"❌ User {target_email} does NOT exist in database")
            print("🔍 This confirms database inconsistency!")
    else:
        print(f"❌ Admin endpoint error: {users_response.status_code}")

if __name__ == "__main__":
    check_user_with_zip_30126()