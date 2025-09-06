#!/usr/bin/env python3

import requests
import json
import time

def direct_zip_cleanup():
    """Direct cleanup of ZIP 30126 from temp cleanup user"""
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    target_zip = "30126"
    temp_cleanup_user = "temp_cleanup_1757178567@example.com"
    
    print("🔧 DIRECT ZIP 30126 CLEANUP")
    print(f"📍 API: {api_url}")
    print(f"🎯 Target ZIP: {target_zip}")
    print(f"👤 Cleanup User: {temp_cleanup_user}")
    print("=" * 50)
    
    # Method 1: Try to transfer ZIP to a non-existent user (this should remove it)
    print("\n🔄 Method 1: Transfer ZIP to non-existent user")
    try:
        fix_payload = {
            "from_email": temp_cleanup_user,
            "to_email": "nonexistent_cleanup_target@example.com",
            "zip_code": target_zip
        }
        
        response = requests.post(
            f"{api_url}/admin/fix-territory-assignment", 
            json=fix_payload,
            timeout=15
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Successfully transferred ZIP to cleanup target")
            else:
                print("⚠️ Transfer response received but success unclear")
        elif response.status_code == 404:
            print("⚠️ User or ZIP assignment not found - may already be cleaned")
        else:
            print(f"❌ Transfer failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Method 1 error: {e}")
    
    # Method 2: Try different approach - create a temporary user and transfer
    print("\n🔄 Method 2: Create temp user and transfer ZIP")
    try:
        # Create a temporary user to receive the ZIP
        temp_receiver_email = f"temp_receiver_{int(time.time())}@example.com"
        
        register_payload = {
            "email": temp_receiver_email,
            "password": "temppass123",
            "first_name": "Temp",
            "last_name": "Receiver"
        }
        
        register_response = requests.post(
            f"{api_url}/auth/register", 
            json=register_payload,
            timeout=10
        )
        
        if register_response.status_code == 200:
            print(f"✅ Created temporary receiver user: {temp_receiver_email}")
            
            # Now transfer ZIP from cleanup user to temp receiver
            fix_payload = {
                "from_email": temp_cleanup_user,
                "to_email": temp_receiver_email,
                "zip_code": target_zip
            }
            
            transfer_response = requests.post(
                f"{api_url}/admin/fix-territory-assignment", 
                json=fix_payload,
                timeout=15
            )
            
            print(f"Transfer Status: {transfer_response.status_code}")
            print(f"Transfer Response: {transfer_response.text}")
            
            if transfer_response.status_code == 200:
                transfer_data = transfer_response.json()
                if transfer_data.get("success"):
                    print(f"✅ Successfully transferred ZIP from {temp_cleanup_user} to {temp_receiver_email}")
                    
                    # Now remove ZIP from temp receiver by transferring to another non-existent user
                    final_fix_payload = {
                        "from_email": temp_receiver_email,
                        "to_email": "final_nonexistent@example.com",
                        "zip_code": target_zip
                    }
                    
                    final_response = requests.post(
                        f"{api_url}/admin/fix-territory-assignment", 
                        json=final_fix_payload,
                        timeout=15
                    )
                    
                    print(f"Final cleanup Status: {final_response.status_code}")
                    print(f"Final cleanup Response: {final_response.text}")
                    
                else:
                    print("⚠️ Transfer response unclear")
            else:
                print(f"❌ Transfer failed: {transfer_response.status_code}")
        else:
            print(f"❌ Failed to create temp receiver user: {register_response.status_code}")
            
    except Exception as e:
        print(f"❌ Method 2 error: {e}")
    
    # Verify final status
    print("\n✅ Verifying final ZIP status")
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
            location_info = data.get("location_info", {})
            city = location_info.get("city", "Unknown")
            state = location_info.get("state", "Unknown")
            
            print(f"ZIP {target_zip} Status:")
            print(f"  Available: {is_available}")
            print(f"  Assigned to: {assigned_to}")
            print(f"  Location: {city}, {state}")
            
            if is_available and not assigned_to:
                print("🎉 SUCCESS: ZIP 30126 is now available!")
                return True
            else:
                print("⚠️ ZIP 30126 is still not available")
                return False
        else:
            print(f"❌ Status check failed: {check_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

if __name__ == "__main__":
    success = direct_zip_cleanup()
    print(f"\nCleanup {'SUCCESSFUL' if success else 'FAILED'}")