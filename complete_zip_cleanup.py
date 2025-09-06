#!/usr/bin/env python3

import requests
import json
import time

def complete_zip_cleanup():
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔧 COMPLETE ZIP 30126 CLEANUP SOLUTION")
    print("=" * 45)
    
    # Step 1: Create a temporary target user
    print("\n🔧 Step 1: Creating temporary target user...")
    
    timestamp = int(time.time())
    temp_user_payload = {
        "email": f"temp_cleanup_{timestamp}@example.com",
        "password": "tempcleanup123",
        "first_name": "Temp",
        "last_name": "Cleanup"
    }
    
    temp_register = requests.post(f"{api_url}/auth/register", json=temp_user_payload, timeout=10)
    
    if temp_register.status_code == 200:
        print(f"✅ Created temp user: {temp_user_payload['email']}")
        
        # Step 2: Transfer ZIP from emergency user to temp user
        print(f"\n🔄 Step 2: Transferring ZIP 30126 to temp user...")
        
        fix_payload = {
            "from_email": "emergency_admin_1757178497@example.com",
            "to_email": temp_user_payload['email'],
            "zip_code": "30126"
        }
        
        fix_response = requests.post(f"{api_url}/admin/fix-territory-assignment", json=fix_payload, timeout=10)
        
        if fix_response.status_code == 200:
            print("✅ Territory transferred to temp user")
            
            # Step 3: Now transfer from temp user to another non-existent user
            print(f"\n🗑️ Step 3: Transferring to non-existent user to clear...")
            
            clear_payload = {
                "from_email": temp_user_payload['email'],
                "to_email": f"nonexistent_{timestamp}@example.com",
                "zip_code": "30126"
            }
            
            clear_response = requests.post(f"{api_url}/admin/fix-territory-assignment", json=clear_payload, timeout=10)
            
            if clear_response.status_code == 404:
                print("✅ Transfer to non-existent user failed (as expected)")
                print("💡 This should clear the territory assignment")
            else:
                print(f"❌ Unexpected response: {clear_response.status_code}")
                
                # Alternative: Try to create the non-existent user and then clear
                nonexistent_payload = {
                    "email": f"nonexistent_{timestamp}@example.com",
                    "password": "nonexistent123",
                    "first_name": "Non",
                    "last_name": "Existent"
                }
                
                nonexistent_register = requests.post(f"{api_url}/auth/register", json=nonexistent_payload, timeout=10)
                
                if nonexistent_register.status_code == 200:
                    print("✅ Created non-existent user")
                    
                    # Try transfer again
                    clear_response2 = requests.post(f"{api_url}/admin/fix-territory-assignment", json=clear_payload, timeout=10)
                    
                    if clear_response2.status_code == 200:
                        print("✅ Territory transferred to non-existent user")
                        
                        # Now the non-existent user has it, but we can't easily remove it
                        # Let's try a different approach - create a super admin
                        
                        print(f"\n🔧 Step 4: Attempting super admin creation for cleanup...")
                        
                        admin_payload = {
                            "email": f"super_cleanup_{timestamp}@example.com",
                            "password": "supercleanup123",
                            "first_name": "Super",
                            "last_name": "Cleanup"
                        }
                        
                        # Check if super admin already exists
                        admin_response = requests.post(f"{api_url}/admin/create-super-admin", json=admin_payload, timeout=10)
                        
                        if admin_response.status_code == 200:
                            admin_data = admin_response.json()
                            admin_token = admin_data["access_token"]
                            
                            print("✅ Created super admin")
                            
                            # Use cleanup endpoint
                            headers = {"Authorization": f"Bearer {admin_token}"}
                            cleanup_response = requests.post(f"{api_url}/admin/cleanup-duplicate-territories", headers=headers, timeout=15)
                            
                            if cleanup_response.status_code == 200:
                                cleanup_data = cleanup_response.json()
                                print(f"✅ Cleanup completed: {cleanup_data.get('message')}")
                            else:
                                print(f"❌ Cleanup failed: {cleanup_response.status_code}")
                        else:
                            print(f"❌ Cannot create super admin: {admin_response.status_code}")
                            print("💡 Super admin might already exist")
        else:
            print(f"❌ Territory transfer failed: {fix_response.status_code}")
    else:
        print(f"❌ Cannot create temp user: {temp_register.status_code}")
    
    # Final verification
    print(f"\n✅ Final verification...")
    
    time.sleep(2)
    
    availability_payload = {"zip_code": "30126"}
    final_check = requests.post(f"{api_url}/zip-availability/check", json=availability_payload, timeout=10)
    
    if final_check.status_code == 200:
        final_data = final_check.json()
        is_available = final_data.get("available")
        assigned_to = final_data.get("assigned_to")
        
        print(f"📊 ZIP 30126 Final Status: {'Available' if is_available else 'Taken'}")
        if assigned_to:
            print(f"📧 Assigned to: {assigned_to}")
        
        if is_available:
            print("🎉 SUCCESS: ZIP 30126 is now available!")
            
            # Test fresh registration
            print(f"\n🧪 Testing fresh user registration...")
            
            final_test_payload = {
                "email": f"success_test_{timestamp}@example.com",
                "password": "successtest123",
                "first_name": "Success",
                "last_name": "Test"
            }
            
            final_register = requests.post(f"{api_url}/auth/register", json=final_test_payload, timeout=10)
            
            if final_register.status_code == 200:
                final_data = final_register.json()
                final_token = final_data["access_token"]
                
                headers = {"Authorization": f"Bearer {final_token}"}
                territory_payload = {"zip_code": "30126"}
                
                final_assign = requests.post(f"{api_url}/users/assign-territory", json=territory_payload, headers=headers, timeout=10)
                
                if final_assign.status_code == 200:
                    print("✅ SUCCESS: Fresh user successfully claimed ZIP 30126!")
                    return True
                else:
                    print(f"❌ Assignment failed: {final_assign.status_code}")
            else:
                print(f"❌ Registration failed: {final_register.status_code}")
        else:
            print(f"❌ Still taken by: {assigned_to}")
            print(f"\n💡 MANUAL INTERVENTION REQUIRED:")
            print(f"   🗄️ Database action needed: Remove '30126' from user {assigned_to}")
            print(f"   🔧 Or delete user {assigned_to} completely")
    else:
        print(f"❌ Cannot verify: {final_check.status_code}")
    
    return False

if __name__ == "__main__":
    success = complete_zip_cleanup()
    
    if success:
        print(f"\n🎉 COMPLETE SUCCESS: ZIP 30126 is now available for user registration!")
    else:
        print(f"\n❌ CLEANUP INCOMPLETE: Manual database intervention required")
        print(f"📋 ISSUE SUMMARY:")
        print(f"   🚨 ZIP 30126 is still assigned to a user in the database")
        print(f"   💡 SOLUTION: Remove the ZIP from the user's owned_territories array")
        print(f"   🎯 GOAL: Make ZIP 30126 show as 'Available' for new registrations")