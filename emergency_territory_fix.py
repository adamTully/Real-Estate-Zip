#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class EmergencyTerritoryFixer:
    def __init__(self, base_url=None):
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
    def log_step(self, step, message):
        print(f"{step} {message}")

    def check_current_status(self):
        """Check current ZIP 30126 assignment"""
        self.log_step("🔍", "Checking current ZIP 30126 assignment...")
        try:
            payload = {"zip_code": "30126"}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_owner = data.get("assigned_to")
                available = data.get("available", True)
                location = data.get("location_info", {})
                
                print(f"   📍 ZIP 30126 Status:")
                print(f"   📧 Currently assigned to: {current_owner}")
                print(f"   🏠 Available: {available}")
                print(f"   🌍 Location: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")
                
                return current_owner
            else:
                print(f"   ❌ Error checking status: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None

    def use_emergency_fix(self):
        """Use the emergency territory fix endpoint"""
        self.log_step("🚨", "Using emergency territory fix endpoint...")
        try:
            payload = {
                "from_email": "adamtest1757110758@gmail.com",
                "to_email": "adamtest1@gmail.com", 
                "zip_code": "30126"
            }
            
            response = requests.post(f"{self.api_url}/admin/fix-territory-assignment", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {data.get('message', 'Fix completed')}")
                return True
            else:
                error_data = response.json() if response.status_code != 500 else {"detail": "Server error"}
                print(f"   ❌ Fix failed: {response.status_code} - {error_data.get('detail', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

    def verify_fix(self):
        """Verify the fix worked"""
        self.log_step("✅", "Verifying the fix...")
        
        # Check 1: ZIP availability check
        try:
            payload = {"zip_code": "30126"}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                new_owner = data.get("assigned_to")
                print(f"   📧 ZIP 30126 now assigned to: {new_owner}")
                
                if new_owner == "adamtest1@gmail.com":
                    print("   ✅ ZIP assignment is now correct!")
                else:
                    print(f"   ❌ ZIP still assigned to wrong user: {new_owner}")
                    return False
            else:
                print(f"   ❌ Could not verify ZIP status: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Verification error: {str(e)}")
            return False
        
        # Check 2: User profile check
        try:
            login_payload = {
                "email": "adamtest1@gmail.com",
                "password": "adam123"
            }
            
            login_response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            if login_response.status_code == 200:
                user_token = login_response.json()["access_token"]
                
                headers = {"Authorization": f"Bearer {user_token}"}
                me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    territories = user_data.get("owned_territories", [])
                    print(f"   🏠 adamtest1@gmail.com territories: {territories}")
                    
                    if "30126" in territories:
                        print("   ✅ User profile confirms ZIP 30126 ownership!")
                        return True
                    else:
                        print("   ❌ User profile does not show ZIP 30126 ownership")
                        return False
                else:
                    print(f"   ❌ Could not get user profile: {me_response.status_code}")
                    return False
            else:
                print(f"   ❌ Could not login as adamtest1@gmail.com: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ User verification error: {str(e)}")
            return False

    def run_emergency_fix(self):
        """Run the complete emergency fix process"""
        print("🚨 EMERGENCY TERRITORY ASSIGNMENT FIX")
        print(f"📍 Target: {self.base_url}")
        print("🎯 Goal: Fix ZIP 30126 assignment for adamtest1@gmail.com")
        print("=" * 70)
        
        # Step 1: Check current status
        print("\n📋 STEP 1: Current Status Check")
        current_owner = self.check_current_status()
        
        if current_owner == "adamtest1@gmail.com":
            print("🎉 ZIP 30126 is already correctly assigned to adamtest1@gmail.com!")
            return True
        elif current_owner == "adamtest1757110758@gmail.com":
            print("⚠️ Confirmed: ZIP 30126 is incorrectly assigned to test user")
        else:
            print(f"⚠️ Unexpected owner: {current_owner}")
        
        # Step 2: Apply emergency fix
        print("\n🔧 STEP 2: Apply Emergency Fix")
        fix_success = self.use_emergency_fix()
        
        if not fix_success:
            print("❌ Emergency fix failed. Manual intervention required.")
            return False
        
        # Step 3: Verify fix
        print("\n🔍 STEP 3: Verify Fix")
        verify_success = self.verify_fix()
        
        # Final result
        print("\n" + "=" * 70)
        if verify_success:
            print("🎉 SUCCESS: Territory assignment bug has been FIXED!")
            print("✅ adamtest1@gmail.com now correctly owns ZIP 30126")
            print("✅ User can now see their correct territory in the dashboard")
            return True
        else:
            print("❌ FAILED: Fix could not be completed")
            print("💡 Manual database intervention may be required")
            return False

def main():
    fixer = EmergencyTerritoryFixer()
    
    print("🚨 Running Emergency Territory Assignment Fix...")
    success = fixer.run_emergency_fix()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())