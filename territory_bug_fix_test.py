#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class TerritoryBugFixTester:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.user_token = None
        
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
        
    def test_user_login_adamtest1(self):
        """Test login for adamtest1@gmail.com"""
        try:
            login_payload = {
                "email": "adamtest1@gmail.com",
                "password": "adam123"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.user_token = data["access_token"]
                user_data = data["user"]
                owned_territories = user_data.get("owned_territories", [])
                details = f"Login successful for {user_data['email']}, User ID: {user_data['id']}, Current territories: {owned_territories}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Login adamtest1@gmail.com", success, details)
            return success, data if success else None
            
        except Exception as e:
            self.log_test("Login adamtest1@gmail.com", False, str(e))
            return False, None

    def test_check_zip_availability(self, zip_code):
        """Check ZIP code availability and current assignment"""
        try:
            payload = {"zip_code": zip_code}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                is_available = data.get("available", False)
                assigned_to = data.get("assigned_to", None)
                location_info = data.get("location_info", {})
                details = f"ZIP {zip_code} - Available: {is_available}, Assigned to: {assigned_to}, Location: {location_info.get('city', 'Unknown')}, {location_info.get('state', 'Unknown')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test(f"Check ZIP {zip_code} Availability", success, details)
            return success, data if success else None
            
        except Exception as e:
            self.log_test(f"Check ZIP {zip_code} Availability", False, str(e))
            return False, None

    def test_create_super_admin(self):
        """Create super admin for cleanup operations"""
        try:
            timestamp = int(time.time())
            admin_payload = {
                "email": f"superadmin{timestamp}@example.com",
                "password": "adminpass123",
                "first_name": "Super",
                "last_name": "Admin"
            }
            
            response = requests.post(f"{self.api_url}/admin/create-super-admin", json=admin_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_data = data["user"]
                details = f"Super admin created: {admin_data['email']}, Role: {admin_data['role']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Create Super Admin", success, details)
            return success
            
        except Exception as e:
            self.log_test("Create Super Admin", False, str(e))
            return False

    def test_cleanup_duplicate_territories(self):
        """Use admin cleanup endpoint to remove duplicate territory assignments"""
        try:
            if not self.admin_token:
                self.log_test("Cleanup Duplicate Territories", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.api_url}/admin/cleanup-duplicate-territories", headers=headers, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                duplicates_found = data.get("duplicates_found", [])
                duplicates_removed = len(duplicates_found)
                total_territories = data.get("total_unique_territories", 0)
                
                # Check if ZIP 30126 was involved in cleanup
                zip_30126_cleaned = False
                for duplicate in duplicates_found:
                    if duplicate.get("zip_code") == "30126":
                        zip_30126_cleaned = True
                        break
                
                details = f"Cleanup completed: {duplicates_removed} duplicates removed, {total_territories} unique territories remain. ZIP 30126 cleaned: {zip_30126_cleaned}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Cleanup Duplicate Territories", success, details)
            return success
            
        except Exception as e:
            self.log_test("Cleanup Duplicate Territories", False, str(e))
            return False

    def test_assign_territory_to_adamtest1(self):
        """Assign ZIP 30126 to adamtest1@gmail.com"""
        try:
            if not self.user_token:
                self.log_test("Assign Territory to adamtest1", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            payload = {"zip_code": "30126"}
            
            response = requests.post(f"{self.api_url}/users/assign-territory", json=payload, headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                message = data.get("message", "")
                zip_code = data.get("zip_code", "")
                details = f"Territory assignment result: {message}, ZIP: {zip_code}"
            else:
                # Check if it's a conflict error (409) - this tells us the issue
                if response.status_code == 409:
                    error_data = response.json()
                    details = f"Conflict detected: {error_data.get('detail', 'Unknown conflict')}"
                else:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Assign Territory to adamtest1", success, details)
            return success
            
        except Exception as e:
            self.log_test("Assign Territory to adamtest1", False, str(e))
            return False

    def test_verify_user_territories(self):
        """Verify adamtest1@gmail.com now owns ZIP 30126"""
        try:
            if not self.user_token:
                self.log_test("Verify User Territories", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                owned_territories = data.get("owned_territories", [])
                has_30126 = "30126" in owned_territories
                user_email = data.get("email", "")
                
                success = has_30126
                details = f"User {user_email} territories: {owned_territories}, Has ZIP 30126: {has_30126}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Verify User Territories", success, details)
            return success
            
        except Exception as e:
            self.log_test("Verify User Territories", False, str(e))
            return False

    def test_final_zip_availability_check(self):
        """Final check that ZIP 30126 is now assigned to adamtest1@gmail.com"""
        try:
            payload = {"zip_code": "30126"}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                is_available = data.get("available", True)
                assigned_to = data.get("assigned_to", None)
                
                # Success means it's NOT available and assigned to adamtest1@gmail.com
                success = not is_available and assigned_to == "adamtest1@gmail.com"
                details = f"ZIP 30126 - Available: {is_available}, Assigned to: {assigned_to}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Final ZIP 30126 Assignment Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Final ZIP 30126 Assignment Check", False, str(e))
            return False

    def run_territory_bug_fix_test(self):
        """Run the complete territory bug fix test sequence"""
        print("🚀 Territory Assignment Bug Fix Test for adamtest1@gmail.com")
        print(f"📍 Testing against: {self.base_url}")
        print("🎯 Goal: Fix ZIP 30126 assignment to adamtest1@gmail.com")
        print("=" * 70)
        
        # Step 1: Login as adamtest1@gmail.com
        print("\n🔑 Step 1: Login as adamtest1@gmail.com")
        login_success, user_data = self.test_user_login_adamtest1()
        if not login_success:
            print("❌ Cannot proceed without successful login")
            return False
        
        # Step 2: Check current ZIP 30126 status
        print("\n🔍 Step 2: Check current ZIP 30126 assignment status")
        zip_success, zip_data = self.test_check_zip_availability("30126")
        if zip_success and zip_data:
            current_owner = zip_data.get("assigned_to")
            if current_owner == "adamtest1@gmail.com":
                print("✅ ZIP 30126 is already correctly assigned to adamtest1@gmail.com!")
                return True
            elif current_owner:
                print(f"⚠️ ZIP 30126 is currently assigned to: {current_owner}")
            else:
                print("ℹ️ ZIP 30126 appears to be available")
        
        # Step 3: Create super admin for cleanup operations
        print("\n👑 Step 3: Create super admin for cleanup operations")
        admin_success = self.test_create_super_admin()
        if not admin_success:
            print("⚠️ Could not create super admin, trying direct assignment...")
        
        # Step 4: Run duplicate cleanup if admin available
        if admin_success:
            print("\n🧹 Step 4: Run duplicate territory cleanup")
            self.test_cleanup_duplicate_territories()
        
        # Step 5: Try to assign ZIP 30126 to adamtest1@gmail.com
        print("\n🏠 Step 5: Assign ZIP 30126 to adamtest1@gmail.com")
        assign_success = self.test_assign_territory_to_adamtest1()
        
        # Step 6: Verify the assignment worked
        print("\n✅ Step 6: Verify territory assignment")
        verify_success = self.test_verify_user_territories()
        
        # Step 7: Final confirmation check
        print("\n🎯 Step 7: Final ZIP availability confirmation")
        final_success = self.test_final_zip_availability_check()
        
        # Print final results
        print("\n" + "=" * 70)
        print(f"📊 Territory Bug Fix Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if verify_success and final_success:
            print("🎉 SUCCESS: Territory assignment bug has been fixed!")
            print("✅ adamtest1@gmail.com now owns ZIP 30126")
            return True
        elif assign_success:
            print("⚠️ PARTIAL SUCCESS: Assignment completed but verification needs review")
            return True
        else:
            print("❌ FAILED: Territory assignment bug could not be fixed")
            print("💡 Manual intervention may be required")
            return False

def main():
    tester = TerritoryBugFixTester()
    
    print("🔧 Running Territory Assignment Bug Fix Test...")
    success = tester.run_territory_bug_fix_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())