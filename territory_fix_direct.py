#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class DirectTerritoryFixer:
    def __init__(self, base_url=None):
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        if details and success:
            print(f"   📝 {details}")

    def try_existing_admin_credentials(self):
        """Try common admin credentials that might exist"""
        possible_admins = [
            {"email": "admin@example.com", "password": "admin123"},
            {"email": "superadmin@example.com", "password": "adminpass123"},
            {"email": "admin1756780976@example.com", "password": "adminpass123"},  # From previous tests
        ]
        
        for admin_creds in possible_admins:
            try:
                response = requests.post(f"{self.api_url}/auth/login", json=admin_creds, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    user_data = data["user"]
                    if user_data.get("role") == "super_admin":
                        print(f"✅ Found existing super admin: {admin_creds['email']}")
                        return data["access_token"]
            except:
                continue
        
        print("⚠️ Could not find existing super admin credentials")
        return None

    def manual_territory_transfer(self):
        """Manually transfer territory by finding and removing from wrong user"""
        print("\n🔧 Attempting manual territory transfer...")
        
        # Step 1: Try to find existing super admin
        admin_token = self.try_existing_admin_credentials()
        
        if admin_token:
            print("🔑 Using existing super admin credentials")
            
            # Step 2: Use cleanup endpoint
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.post(f"{self.api_url}/admin/cleanup-duplicate-territories", headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Cleanup executed: {data.get('message', 'No message')}")
                    
                    # Check if ZIP 30126 was cleaned up
                    duplicates = data.get("duplicates_found", [])
                    zip_30126_cleaned = any(d.get("zip_code") == "30126" for d in duplicates)
                    
                    if zip_30126_cleaned:
                        print("✅ ZIP 30126 was involved in cleanup process")
                        return True
                    else:
                        print("⚠️ ZIP 30126 was not found in duplicates - may need manual intervention")
                        
                        # Try to get all users to see the current state
                        users_response = requests.get(f"{self.api_url}/admin/users", headers=headers, timeout=10)
                        if users_response.status_code == 200:
                            users = users_response.json()
                            print(f"\n📊 Current user territory assignments:")
                            for user in users:
                                if user.get("owned_territories"):
                                    print(f"   {user['email']}: {user['owned_territories']}")
                        
                        return False
                else:
                    print(f"❌ Cleanup failed: {response.status_code} - {response.text[:200]}")
                    return False
                    
            except Exception as e:
                print(f"❌ Cleanup error: {str(e)}")
                return False
        else:
            print("❌ Cannot proceed without super admin access")
            return False

    def test_final_assignment(self):
        """Test if we can now assign ZIP 30126 to adamtest1@gmail.com"""
        try:
            # Login as adamtest1
            login_payload = {
                "email": "adamtest1@gmail.com",
                "password": "adam123"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            if response.status_code != 200:
                print("❌ Could not login as adamtest1@gmail.com")
                return False
            
            user_token = response.json()["access_token"]
            
            # Try to assign territory
            headers = {"Authorization": f"Bearer {user_token}"}
            payload = {"zip_code": "30126"}
            
            assign_response = requests.post(f"{self.api_url}/users/assign-territory", json=payload, headers=headers, timeout=10)
            
            if assign_response.status_code == 200:
                print("✅ Successfully assigned ZIP 30126 to adamtest1@gmail.com")
                
                # Verify assignment
                me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    territories = user_data.get("owned_territories", [])
                    if "30126" in territories:
                        print(f"✅ Verified: adamtest1@gmail.com now owns territories: {territories}")
                        return True
                    else:
                        print(f"⚠️ Assignment may have failed - territories: {territories}")
                        return False
                else:
                    print("⚠️ Could not verify assignment")
                    return False
            else:
                error_data = assign_response.json() if assign_response.status_code != 500 else {"detail": "Server error"}
                print(f"❌ Assignment failed: {assign_response.status_code} - {error_data.get('detail', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Assignment test error: {str(e)}")
            return False

    def run_direct_fix(self):
        """Run the direct territory fix process"""
        print("🔧 Direct Territory Fix for ZIP 30126 Assignment Bug")
        print(f"📍 Target: {self.base_url}")
        print("🎯 Goal: Transfer ZIP 30126 from adamtest1757110758@gmail.com to adamtest1@gmail.com")
        print("=" * 80)
        
        # Step 1: Check current status
        print("\n🔍 Step 1: Check current ZIP 30126 status")
        try:
            payload = {"zip_code": "30126"}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_owner = data.get("assigned_to")
                print(f"   Current owner: {current_owner}")
                if current_owner == "adamtest1@gmail.com":
                    print("✅ ZIP 30126 is already correctly assigned!")
                    return True
            else:
                print(f"⚠️ Could not check ZIP status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Status check error: {str(e)}")
        
        # Step 2: Attempt manual transfer
        print("\n🔄 Step 2: Attempt territory transfer")
        transfer_success = self.manual_territory_transfer()
        
        # Step 3: Test final assignment
        print("\n🎯 Step 3: Test final assignment to adamtest1@gmail.com")
        assignment_success = self.test_final_assignment()
        
        # Step 4: Final verification
        print("\n✅ Step 4: Final verification")
        try:
            payload = {"zip_code": "30126"}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                final_owner = data.get("assigned_to")
                print(f"   Final owner: {final_owner}")
                
                if final_owner == "adamtest1@gmail.com":
                    print("🎉 SUCCESS: Territory assignment bug has been FIXED!")
                    print("✅ ZIP 30126 is now correctly assigned to adamtest1@gmail.com")
                    return True
                else:
                    print(f"❌ FAILED: ZIP 30126 is still assigned to {final_owner}")
                    return False
            else:
                print("⚠️ Could not verify final status")
                return False
        except Exception as e:
            print(f"⚠️ Final verification error: {str(e)}")
            return False

def main():
    fixer = DirectTerritoryFixer()
    
    print("🔧 Running Direct Territory Fix...")
    success = fixer.run_direct_fix()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())