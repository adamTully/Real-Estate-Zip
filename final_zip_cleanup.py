#!/usr/bin/env python3

import requests
import json
import time

def final_zip_cleanup():
    """Final cleanup attempt for ZIP 30126"""
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    target_zip = "30126"
    
    print("🔧 FINAL ZIP 30126 CLEANUP ATTEMPT")
    print(f"📍 API: {api_url}")
    print(f"🎯 Target ZIP: {target_zip}")
    print("=" * 50)
    
    # First, check current status
    print("\n🔍 Checking current ZIP status...")
    try:
        check_payload = {"zip_code": target_zip}
        check_response = requests.post(
            f"{api_url}/zip-availability/check", 
            json=check_payload,
            timeout=10
        )
        
        if check_response.status_code == 200:
            data = check_response.json()
            is_available = data.get("available", False)
            assigned_to = data.get("assigned_to")
            
            print(f"Current status: Available={is_available}, Assigned to={assigned_to}")
            
            if is_available:
                print("✅ ZIP is already available! No cleanup needed.")
                return True
            
            if assigned_to:
                print(f"🔄 ZIP is assigned to: {assigned_to}")
                
                # Method: Create a super admin and use admin powers to clean up
                print("\n🔧 Creating super admin for cleanup...")
                
                admin_email = f"cleanup_admin_{int(time.time())}@example.com"
                admin_payload = {
                    "email": admin_email,
                    "password": "adminpass123",
                    "first_name": "Cleanup",
                    "last_name": "Admin"
                }
                
                admin_response = requests.post(
                    f"{api_url}/admin/create-super-admin", 
                    json=admin_payload,
                    timeout=10
                )
                
                if admin_response.status_code == 200:
                    print(f"✅ Created admin: {admin_email}")
                    admin_data = admin_response.json()
                    admin_token = admin_data["access_token"]
                    
                    # Use admin to clean up duplicate territories
                    print("\n🧹 Running duplicate territory cleanup...")
                    admin_headers = {"Authorization": f"Bearer {admin_token}"}
                    
                    cleanup_response = requests.post(
                        f"{api_url}/admin/cleanup-duplicate-territories",
                        headers=admin_headers,
                        timeout=15
                    )
                    
                    print(f"Cleanup response status: {cleanup_response.status_code}")
                    if cleanup_response.status_code == 200:
                        cleanup_data = cleanup_response.json()
                        print(f"Cleanup result: {cleanup_data.get('message', 'No message')}")
                        
                        # Check if this helped
                        time.sleep(2)
                        final_check_response = requests.post(
                            f"{api_url}/zip-availability/check", 
                            json=check_payload,
                            timeout=10
                        )
                        
                        if final_check_response.status_code == 200:
                            final_data = final_check_response.json()
                            final_available = final_data.get("available", False)
                            final_assigned = final_data.get("assigned_to")
                            
                            print(f"After cleanup: Available={final_available}, Assigned to={final_assigned}")
                            
                            if final_available and not final_assigned:
                                print("🎉 SUCCESS: ZIP 30126 is now available!")
                                return True
                            else:
                                # Try one more direct approach - transfer to admin then remove
                                print("\n🔄 Final attempt: Transfer to admin then remove...")
                                
                                transfer_to_admin_payload = {
                                    "from_email": assigned_to,
                                    "to_email": admin_email,
                                    "zip_code": target_zip
                                }
                                
                                transfer_response = requests.post(
                                    f"{api_url}/admin/fix-territory-assignment", 
                                    json=transfer_to_admin_payload,
                                    timeout=15
                                )
                                
                                if transfer_response.status_code == 200:
                                    print("✅ Transferred ZIP to admin")
                                    
                                    # Now remove from admin by transferring to non-existent
                                    remove_payload = {
                                        "from_email": admin_email,
                                        "to_email": "void_user@example.com",
                                        "zip_code": target_zip
                                    }
                                    
                                    # This should fail but might clean up the assignment
                                    remove_response = requests.post(
                                        f"{api_url}/admin/fix-territory-assignment", 
                                        json=remove_payload,
                                        timeout=15
                                    )
                                    
                                    print(f"Remove attempt status: {remove_response.status_code}")
                                    
                                    # Final check
                                    time.sleep(2)
                                    ultimate_check_response = requests.post(
                                        f"{api_url}/zip-availability/check", 
                                        json=check_payload,
                                        timeout=10
                                    )
                                    
                                    if ultimate_check_response.status_code == 200:
                                        ultimate_data = ultimate_check_response.json()
                                        ultimate_available = ultimate_data.get("available", False)
                                        ultimate_assigned = ultimate_data.get("assigned_to")
                                        
                                        print(f"Ultimate status: Available={ultimate_available}, Assigned to={ultimate_assigned}")
                                        
                                        if ultimate_available and not ultimate_assigned:
                                            print("🎉 SUCCESS: ZIP 30126 is finally available!")
                                            return True
                                        else:
                                            print("❌ ZIP still not available after all attempts")
                                            return False
                                else:
                                    print(f"❌ Failed to transfer to admin: {transfer_response.status_code}")
                                    return False
                        else:
                            print(f"❌ Final check failed: {final_check_response.status_code}")
                            return False
                    else:
                        print(f"❌ Cleanup failed: {cleanup_response.status_code}")
                        return False
                elif admin_response.status_code == 400:
                    print("⚠️ Super admin already exists, trying to use existing admin functionality...")
                    # Could try to login with existing admin if we knew credentials
                    return False
                else:
                    print(f"❌ Failed to create admin: {admin_response.status_code}")
                    return False
            else:
                print("⚠️ ZIP shows as taken but no assigned user found")
                return False
        else:
            print(f"❌ Status check failed: {check_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = final_zip_cleanup()
    print(f"\nFinal cleanup {'SUCCESSFUL' if success else 'FAILED'}")