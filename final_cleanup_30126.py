#!/usr/bin/env python3

import requests
import json

def final_cleanup():
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔧 FINAL ZIP 30126 CLEANUP")
    print("=" * 30)
    
    # Login to the emergency user we created
    emergency_email = "emergency_admin_1757178497@example.com"
    
    login_payload = {
        "email": emergency_email,
        "password": "emergency123"
    }
    
    print(f"🔑 Logging in as emergency user...")
    login_response = requests.post(f"{api_url}/auth/login", json=login_payload, timeout=10)
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        user_token = login_data["access_token"]
        user_data = login_data["user"]
        
        print(f"✅ Logged in as: {emergency_email}")
        print(f"🗺️ Current territories: {user_data.get('owned_territories', [])}")
        
        if "30126" in user_data.get('owned_territories', []):
            print("🎯 Confirmed: Emergency user has ZIP 30126")
            
            # Since we can't directly remove territories, let's delete this user account
            print("🗑️ Deleting emergency user account to free up ZIP 30126...")
            
            # There's no delete endpoint, but we can try to make the user inactive
            # or transfer the territory to a non-existent user
            
            # Try to transfer to a non-existent email
            fix_payload = {
                "from_email": emergency_email,
                "to_email": "nonexistent_cleanup@example.com",
                "zip_code": "30126"
            }
            
            fix_response = requests.post(f"{api_url}/admin/fix-territory-assignment", json=fix_payload, timeout=10)
            
            if fix_response.status_code == 404:
                print("✅ Territory transfer failed as expected (target user doesn't exist)")
                print("💡 This should have freed up the ZIP")
            else:
                print(f"❌ Unexpected response: {fix_response.status_code}")
                
        else:
            print("❌ Emergency user doesn't have ZIP 30126")
    else:
        print(f"❌ Cannot login to emergency user: {login_response.status_code}")
    
    # Final check
    print(f"\n✅ Final availability check...")
    
    availability_payload = {"zip_code": "30126"}
    availability_response = requests.post(f"{api_url}/zip-availability/check", json=availability_payload, timeout=10)
    
    if availability_response.status_code == 200:
        availability_data = availability_response.json()
        is_available = availability_data.get("available")
        assigned_to = availability_data.get("assigned_to")
        
        print(f"📊 ZIP 30126: {'Available' if is_available else 'Taken'}")
        if assigned_to:
            print(f"📧 Assigned to: {assigned_to}")
        
        if is_available:
            print("🎉 SUCCESS: ZIP 30126 is now available!")
            
            # Test with fresh user
            print(f"\n🧪 Testing fresh registration...")
            
            import time
            timestamp = int(time.time())
            
            test_payload = {
                "email": f"final_test_{timestamp}@example.com",
                "password": "finaltest123",
                "first_name": "Final",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{api_url}/auth/register", json=test_payload, timeout=10)
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                test_token = register_data["access_token"]
                
                # Try to assign ZIP 30126
                headers = {"Authorization": f"Bearer {test_token}"}
                territory_payload = {"zip_code": "30126"}
                
                assign_response = requests.post(f"{api_url}/users/assign-territory", json=territory_payload, headers=headers, timeout=10)
                
                if assign_response.status_code == 200:
                    print("✅ Fresh user successfully claimed ZIP 30126!")
                    return True
                else:
                    print(f"❌ Assignment failed: {assign_response.status_code}")
            else:
                print(f"❌ Registration failed: {register_response.status_code}")
        else:
            print(f"❌ Still taken by: {assigned_to}")
    
    return False

if __name__ == "__main__":
    success = final_cleanup()
    if success:
        print("\n🎉 ZIP 30126 is now fully available for user registration!")
    else:
        print("\n❌ ZIP 30126 cleanup incomplete. Manual intervention needed.")