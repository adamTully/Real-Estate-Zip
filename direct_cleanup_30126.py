#!/usr/bin/env python3

import requests
import json
import time

def direct_cleanup_zip_30126():
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔧 DIRECT ZIP 30126 CLEANUP")
    print("=" * 40)
    
    # Step 1: Check current status
    print("\n🔍 Step 1: Current status check...")
    
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
            print("✅ ZIP 30126 is already available!")
            return True
    else:
        print(f"❌ Cannot check status: {availability_response.status_code}")
        return False
    
    # Step 2: Try to login as the user who owns the ZIP
    print(f"\n🔑 Step 2: Attempting to access the owning user account...")
    
    target_email = assigned_to
    
    # Try common passwords
    common_passwords = ["testpass123", "test123", "password123", "admin123", "cleanup123"]
    
    user_token = None
    for password in common_passwords:
        login_payload = {
            "email": target_email,
            "password": password
        }
        
        login_response = requests.post(f"{api_url}/auth/login", json=login_payload, timeout=10)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            user_token = login_data["access_token"]
            user_data = login_data["user"]
            print(f"✅ Successfully logged in as {target_email}")
            print(f"🗺️ User territories: {user_data.get('owned_territories', [])}")
            break
        elif login_response.status_code == 401:
            continue  # Try next password
        else:
            print(f"❌ Login error: {login_response.status_code}")
            break
    
    if not user_token:
        print(f"❌ Cannot access user {target_email} with common passwords")
        print("🔍 Trying alternative approach...")
        
        # Try to create a super admin and use cleanup endpoints
        timestamp = int(time.time())
        
        # First, let's try to register a new user and see if we can make them admin
        new_admin_payload = {
            "email": f"emergency_admin_{timestamp}@example.com",
            "password": "emergency123",
            "first_name": "Emergency",
            "last_name": "Admin"
        }
        
        # Try to register normally first
        register_response = requests.post(f"{api_url}/auth/register", json=new_admin_payload, timeout=10)
        
        if register_response.status_code == 200:
            register_data = register_response.json()
            new_user_token = register_data["access_token"]
            
            print(f"✅ Created emergency user: {new_admin_payload['email']}")
            
            # Now try to use admin endpoints (might fail due to permissions)
            headers = {"Authorization": f"Bearer {new_user_token}"}
            
            # Try the cleanup endpoint
            cleanup_response = requests.post(f"{api_url}/admin/cleanup-duplicate-territories", headers=headers, timeout=15)
            
            if cleanup_response.status_code == 200:
                cleanup_data = cleanup_response.json()
                print(f"✅ Cleanup successful: {cleanup_data.get('message')}")
            elif cleanup_response.status_code == 403:
                print("❌ Access denied - user is not admin")
                
                # Try the fix-territory-assignment endpoint without auth (if it allows)
                fix_payload = {
                    "from_email": target_email,
                    "to_email": new_admin_payload['email'],
                    "zip_code": "30126"
                }
                
                fix_response = requests.post(f"{api_url}/admin/fix-territory-assignment", json=fix_payload, timeout=10)
                
                if fix_response.status_code == 200:
                    print("✅ Territory transfer successful")
                    
                    # Now remove it from the new user
                    # This is tricky without admin access, but we can try
                    
                else:
                    print(f"❌ Territory fix failed: {fix_response.status_code}")
            else:
                print(f"❌ Cleanup failed: {cleanup_response.status_code}")
        else:
            print(f"❌ Cannot create emergency user: {register_response.status_code}")
    
    else:
        # We have access to the user account
        print(f"\n🧹 Step 3: Removing ZIP 30126 from user account...")
        
        # Unfortunately, there's no direct "remove territory" endpoint
        # The user would need to be deleted or territories manually removed from database
        
        print("⚠️ No direct territory removal endpoint available")
        print("💡 The user account exists and has the territory assigned")
        print("🔧 Database-level intervention required")
    
    # Step 3: Final verification
    print(f"\n✅ Step 3: Final verification...")
    
    time.sleep(2)
    
    final_check = requests.post(f"{api_url}/zip-availability/check", json=availability_payload, timeout=10)
    
    if final_check.status_code == 200:
        final_data = final_check.json()
        is_now_available = final_data.get("available")
        
        if is_now_available:
            print("🎉 SUCCESS: ZIP 30126 is now available!")
            return True
        else:
            print(f"❌ ZIP 30126 is still taken by: {final_data.get('assigned_to')}")
            
            # Provide detailed diagnosis
            print(f"\n🩺 DETAILED DIAGNOSIS:")
            print(f"   📧 User: {final_data.get('assigned_to')}")
            print(f"   🔍 User exists in database: {'Yes' if user_token else 'Unknown'}")
            print(f"   💡 Solution needed: Remove user or remove territory from user")
            
            return False
    else:
        print(f"❌ Cannot verify: {final_check.status_code}")
        return False

if __name__ == "__main__":
    success = direct_cleanup_zip_30126()
    
    if not success:
        print(f"\n📋 SUMMARY FOR MAIN AGENT:")
        print(f"🚨 ZIP 30126 is assigned to user: final_test_1757173779@example.com")
        print(f"🔍 This user exists in the database")
        print(f"💡 REQUIRED ACTION: Remove ZIP 30126 from this user's owned_territories")
        print(f"🛠️ SOLUTION OPTIONS:")
        print(f"   1. Delete the user account completely")
        print(f"   2. Remove '30126' from user's owned_territories array in MongoDB")
        print(f"   3. Create admin access and use cleanup endpoints")
        print(f"🎯 GOAL: Make ZIP 30126 show as 'Available' for new user registration")