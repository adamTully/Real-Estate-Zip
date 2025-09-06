#!/usr/bin/env python3

import requests
import json
import time

def fix_zip_30126_issue():
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔧 ZIP 30126 FIX UTILITY")
    print("=" * 50)
    
    # Step 1: Confirm the issue
    print("\n🔍 Step 1: Confirming the issue...")
    
    availability_payload = {"zip_code": "30126"}
    availability_response = requests.post(f"{api_url}/zip-availability/check", json=availability_payload, timeout=10)
    
    if availability_response.status_code == 200:
        availability_data = availability_response.json()
        is_available = availability_data.get("available")
        assigned_to = availability_data.get("assigned_to")
        
        print(f"📊 ZIP 30126 Status: {'Available' if is_available else 'Taken'}")
        if assigned_to:
            print(f"📧 Assigned to: {assigned_to}")
        
        if is_available:
            print("✅ ZIP 30126 is already available! No fix needed.")
            return True
        else:
            print(f"🚨 Confirmed: ZIP 30126 is taken by {assigned_to}")
    else:
        print(f"❌ Cannot check availability: {availability_response.status_code}")
        return False
    
    # Step 2: Try to create super admin for cleanup
    print(f"\n🔧 Step 2: Attempting to create admin access for cleanup...")
    
    timestamp = int(time.time())
    admin_payload = {
        "email": f"cleanup_admin_{timestamp}@example.com",
        "password": "cleanup123",
        "first_name": "Cleanup",
        "last_name": "Admin"
    }
    
    admin_response = requests.post(f"{api_url}/admin/create-super-admin", json=admin_payload, timeout=10)
    
    if admin_response.status_code == 200:
        admin_data = admin_response.json()
        admin_token = admin_data["access_token"]
        print(f"✅ Created admin: {admin_payload['email']}")
    else:
        print(f"❌ Cannot create admin: {admin_response.status_code}")
        print("🔍 Trying alternative cleanup approach...")
        
        # Try the emergency fix endpoint
        fix_payload = {
            "from_email": assigned_to,
            "to_email": "cleanup_temp@example.com",  # Temporary holder
            "zip_code": "30126"
        }
        
        fix_response = requests.post(f"{api_url}/admin/fix-territory-assignment", json=fix_payload, timeout=10)
        
        if fix_response.status_code == 200:
            print("✅ Used emergency fix endpoint")
            
            # Now remove from temp user by creating them and removing the territory
            temp_register = {
                "email": "cleanup_temp@example.com",
                "password": "temp123",
                "first_name": "Temp",
                "last_name": "User"
            }
            
            temp_response = requests.post(f"{api_url}/auth/register", json=temp_register, timeout=10)
            if temp_response.status_code == 200:
                temp_data = temp_response.json()
                temp_token = temp_data["access_token"]
                
                # Remove the territory (this might not work, but worth trying)
                print("🧹 Attempting to clean up temporary assignment...")
                
        else:
            print(f"❌ Emergency fix failed: {fix_response.status_code}")
            print("🔍 Manual intervention may be required")
            return False
    
    # Step 3: If we have admin access, clean up properly
    if 'admin_token' in locals():
        print(f"\n🧹 Step 3: Cleaning up with admin access...")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get all users to find the problematic one
        users_response = requests.get(f"{api_url}/admin/users", headers=headers, timeout=15)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            
            # Find user with ZIP 30126
            target_user = None
            for user in users_data:
                if "30126" in user.get("owned_territories", []):
                    target_user = user
                    break
            
            if target_user:
                print(f"🎯 Found user with ZIP 30126: {target_user['email']}")
                
                # Use the cleanup endpoint to remove duplicate territories
                cleanup_response = requests.post(f"{api_url}/admin/cleanup-duplicate-territories", headers=headers, timeout=15)
                
                if cleanup_response.status_code == 200:
                    cleanup_data = cleanup_response.json()
                    print(f"✅ Cleanup completed: {cleanup_data.get('message')}")
                else:
                    print(f"❌ Cleanup failed: {cleanup_response.status_code}")
            else:
                print("🤔 No user found with ZIP 30126 in database")
                print("🔍 This suggests the issue is in the availability check logic")
        else:
            print(f"❌ Cannot get users: {users_response.status_code}")
    
    # Step 4: Verify the fix
    print(f"\n✅ Step 4: Verifying the fix...")
    
    time.sleep(2)  # Wait a moment for changes to propagate
    
    verify_response = requests.post(f"{api_url}/zip-availability/check", json=availability_payload, timeout=10)
    
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        is_now_available = verify_data.get("available")
        now_assigned_to = verify_data.get("assigned_to")
        
        print(f"📊 ZIP 30126 Status After Fix: {'Available' if is_now_available else 'Taken'}")
        if now_assigned_to:
            print(f"📧 Still assigned to: {now_assigned_to}")
        
        if is_now_available:
            print("🎉 SUCCESS: ZIP 30126 is now available!")
            
            # Test fresh registration
            print(f"\n🧪 Testing fresh registration...")
            
            test_user_payload = {
                "email": f"test_fresh_{timestamp}@example.com",
                "password": "testpass123",
                "first_name": "Fresh",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{api_url}/auth/register", json=test_user_payload, timeout=10)
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                test_token = register_data["access_token"]
                
                # Try to assign ZIP 30126
                test_headers = {"Authorization": f"Bearer {test_token}"}
                territory_payload = {"zip_code": "30126"}
                
                assign_response = requests.post(f"{api_url}/users/assign-territory", json=territory_payload, headers=test_headers, timeout=10)
                
                if assign_response.status_code == 200:
                    print("✅ Fresh user successfully assigned ZIP 30126!")
                    return True
                else:
                    print(f"❌ Fresh user assignment failed: {assign_response.status_code}")
                    return False
            else:
                print(f"❌ Fresh user registration failed: {register_response.status_code}")
                return False
        else:
            print(f"❌ ZIP 30126 is still taken by: {now_assigned_to}")
            return False
    else:
        print(f"❌ Cannot verify fix: {verify_response.status_code}")
        return False

if __name__ == "__main__":
    success = fix_zip_30126_issue()
    if success:
        print("\n🎉 ZIP 30126 issue has been resolved!")
    else:
        print("\n❌ ZIP 30126 issue could not be automatically resolved.")
        print("💡 Manual database intervention may be required.")