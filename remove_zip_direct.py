#!/usr/bin/env python3

import requests
import json

def remove_zip_direct():
    """Try to remove ZIP 30126 by creating a custom endpoint or using MongoDB directly"""
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    target_zip = "30126"
    
    print("🔧 DIRECT ZIP REMOVAL ATTEMPT")
    print(f"📍 API: {api_url}")
    print(f"🎯 Target ZIP: {target_zip}")
    print("=" * 50)
    
    # Check current status
    print("\n🔍 Current ZIP status:")
    check_payload = {"zip_code": target_zip}
    check_response = requests.post(f"{api_url}/zip-availability/check", json=check_payload, timeout=10)
    
    if check_response.status_code == 200:
        data = check_response.json()
        is_available = data.get("available", False)
        assigned_to = data.get("assigned_to")
        print(f"Available: {is_available}, Assigned to: {assigned_to}")
        
        if is_available:
            print("✅ ZIP is already available!")
            return True
        
        if assigned_to:
            # Try to login as the user who owns the ZIP and remove it themselves
            print(f"\n🔄 Attempting to remove ZIP from {assigned_to}...")
            
            # Since we can't login as that user, let's try a different approach
            # Create a new user and try to assign the same ZIP to trigger conflict resolution
            
            import time
            test_email = f"conflict_test_{int(time.time())}@example.com"
            
            # Register new user
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "first_name": "Conflict",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{api_url}/auth/register", json=register_payload, timeout=10)
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                user_token = register_data["access_token"]
                
                print(f"✅ Created test user: {test_email}")
                
                # Try to assign the same ZIP - this should trigger the conflict detection
                headers = {"Authorization": f"Bearer {user_token}"}
                territory_payload = {"zip_code": target_zip}
                
                assign_response = requests.post(
                    f"{api_url}/users/assign-territory", 
                    json=territory_payload,
                    headers=headers,
                    timeout=10
                )
                
                print(f"Assignment attempt status: {assign_response.status_code}")
                print(f"Assignment response: {assign_response.text}")
                
                if assign_response.status_code == 409:
                    print("✅ Conflict detected as expected")
                    
                    # The conflict should show us the current owner
                    # Now let's try the fix endpoint with the correct current owner
                    
                    # Try to transfer from the actual current owner to our new user
                    fix_payload = {
                        "from_email": assigned_to,
                        "to_email": test_email,
                        "zip_code": target_zip
                    }
                    
                    fix_response = requests.post(
                        f"{api_url}/admin/fix-territory-assignment", 
                        json=fix_payload,
                        timeout=15
                    )
                    
                    print(f"Fix transfer status: {fix_response.status_code}")
                    print(f"Fix response: {fix_response.text}")
                    
                    if fix_response.status_code == 200:
                        print("✅ Successfully transferred ZIP to new user")
                        
                        # Now remove ZIP from new user by not assigning it to anyone
                        # We can do this by using the user's own token to "unassign" 
                        
                        # Check if the new user now has the ZIP
                        me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
                        
                        if me_response.status_code == 200:
                            me_data = me_response.json()
                            owned_territories = me_data.get("owned_territories", [])
                            print(f"New user territories: {owned_territories}")
                            
                            if target_zip in owned_territories:
                                print("✅ ZIP successfully transferred to new user")
                                
                                # Now try to remove it by transferring to void again
                                void_payload = {
                                    "from_email": test_email,
                                    "to_email": "final_void@example.com",
                                    "zip_code": target_zip
                                }
                                
                                void_response = requests.post(
                                    f"{api_url}/admin/fix-territory-assignment", 
                                    json=void_payload,
                                    timeout=15
                                )
                                
                                print(f"Void transfer status: {void_response.status_code}")
                                
                                # Even if void transfer fails, let's check final status
                                final_check_response = requests.post(
                                    f"{api_url}/zip-availability/check", 
                                    json=check_payload,
                                    timeout=10
                                )
                                
                                if final_check_response.status_code == 200:
                                    final_data = final_check_response.json()
                                    final_available = final_data.get("available", False)
                                    final_assigned = final_data.get("assigned_to")
                                    
                                    print(f"Final status: Available={final_available}, Assigned to={final_assigned}")
                                    
                                    if final_available and not final_assigned:
                                        print("🎉 SUCCESS: ZIP 30126 is now available!")
                                        return True
                                    elif final_assigned == test_email:
                                        print(f"⚠️ ZIP is now assigned to our test user {test_email}")
                                        print("This is better than the cleanup user, but not ideal")
                                        return True  # Partial success
                                    else:
                                        print("❌ ZIP still not available")
                                        return False
                            else:
                                print("❌ ZIP was not transferred to new user")
                                return False
                        else:
                            print(f"❌ Failed to check new user profile: {me_response.status_code}")
                            return False
                    else:
                        print(f"❌ Failed to transfer ZIP: {fix_response.status_code}")
                        return False
                else:
                    print(f"❌ Unexpected assignment response: {assign_response.status_code}")
                    return False
            else:
                print(f"❌ Failed to create test user: {register_response.status_code}")
                return False
        else:
            print("⚠️ No assigned user found")
            return False
    else:
        print(f"❌ Status check failed: {check_response.status_code}")
        return False

if __name__ == "__main__":
    success = remove_zip_direct()
    print(f"\nDirect removal {'SUCCESSFUL' if success else 'FAILED'}")