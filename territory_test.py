#!/usr/bin/env python3

import requests
import sys
import json
import time
import random

class TerritoryAssignmentTester:
    def __init__(self, base_url="http://localhost:8001"):
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
            if details:
                print(f"   Details: {details}")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def test_territory_assignment_complete(self):
        """Test complete territory assignment workflow"""
        print("🗺️ Testing Territory Assignment Functionality")
        print("=" * 60)
        
        try:
            # Use unique timestamp to avoid conflicts
            timestamp = int(time.time()) + random.randint(1000, 9999)
            test_email = f"territory{timestamp}@example.com"
            
            print(f"📧 Creating test user with email: {test_email}")
            
            # Step 1: Register the test user
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "first_name": "Territory",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            if register_response.status_code != 200:
                self.log_test("User Registration", False, f"Status: {register_response.status_code}, Response: {register_response.text[:200]}")
                return False
            
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_id = register_data["user"]["id"]
            
            self.log_test("User Registration", True, f"User ID: {user_id}")
            
            # Step 2: Test POST /api/users/assign-territory
            print("\n🎯 Testing POST /api/users/assign-territory")
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": "10001"}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            if assign_response.status_code == 200:
                assign_data = assign_response.json()
                success = assign_data.get("zip_code") == "10001"
                details = f"Response: {assign_data}"
                self.log_test("Assign Territory (ZIP 10001)", success, details)
            else:
                self.log_test("Assign Territory (ZIP 10001)", False, f"Status: {assign_response.status_code}, Response: {assign_response.text[:200]}")
                return False
            
            # Step 3: Test GET /api/auth/me to verify territory in user profile
            print("\n👤 Testing GET /api/auth/me")
            me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                owned_territories = me_data.get("owned_territories", [])
                success = "10001" in owned_territories
                details = f"Owned territories: {owned_territories}"
                self.log_test("Verify Territory in User Profile", success, details)
            else:
                self.log_test("Verify Territory in User Profile", False, f"Status: {me_response.status_code}")
                return False
            
            # Step 4: Create super admin for admin endpoint testing or use existing
            print("\n👑 Setting up Admin Access")
            admin_email = f"admin{timestamp}@example.com"
            admin_payload = {
                "email": admin_email,
                "password": "adminpass123",
                "first_name": "Super",
                "last_name": "Admin"
            }
            
            admin_response = requests.post(f"{self.api_url}/admin/create-super-admin", json=admin_payload, timeout=10)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                admin_token = admin_data["access_token"]
                self.log_test("Super Admin Creation", True, f"Admin email: {admin_email}")
            elif admin_response.status_code == 400 and "already exists" in admin_response.text:
                # Super admin already exists, try to create and login with a regular admin
                self.log_test("Super Admin Creation", True, "Super admin already exists, will try to use existing or create regular user")
                
                # Try to register a regular user and then manually set them as admin in database
                # For testing purposes, let's try to login with a known admin or skip admin tests
                print("   ℹ️  Super admin already exists. Skipping admin-specific tests for now.")
                admin_token = None
            else:
                self.log_test("Super Admin Creation", False, f"Status: {admin_response.status_code}, Response: {admin_response.text[:200]}")
                admin_token = None
            
            # Step 5: Test GET /api/admin/users to verify territory data
            print("\n🔍 Testing GET /api/admin/users")
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            users_response = requests.get(f"{self.api_url}/admin/users", headers=admin_headers, timeout=10)
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                
                # Find our test user
                test_user = None
                for user in users_data:
                    if user.get("email") == test_email:
                        test_user = user
                        break
                
                if test_user:
                    territories_count = test_user.get("total_territories", 0)
                    owned_territories = test_user.get("owned_territories", [])
                    success = territories_count == 1 and "10001" in owned_territories
                    details = f"User: {test_user['email']}, Total territories: {territories_count}, Owned: {owned_territories}"
                    self.log_test("Admin Dashboard - Territory Count", success, details)
                    
                    # Also check if we can find user by the pattern mentioned in the request
                    pattern_found = False
                    for user in users_data:
                        if "territory" in user.get("email", "").lower():
                            pattern_found = True
                            pattern_details = f"Found user with 'territory' pattern: {user['email']}, territories: {user.get('owned_territories', [])}"
                            print(f"   📋 {pattern_details}")
                    
                    if pattern_found:
                        self.log_test("Admin Dashboard - Pattern Search", True, "Found users with 'territory' pattern in email")
                    
                else:
                    self.log_test("Admin Dashboard - Territory Count", False, f"Test user not found in admin list. Available users: {[u.get('email') for u in users_data[:3]]}")
                    return False
            else:
                self.log_test("Admin Dashboard - Territory Count", False, f"Status: {users_response.status_code}")
                return False
            
            # Step 6: Test duplicate territory assignment
            print("\n🔄 Testing Duplicate Territory Assignment")
            duplicate_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            if duplicate_response.status_code == 200:
                duplicate_data = duplicate_response.json()
                success = "already assigned" in duplicate_data.get("message", "").lower()
                details = f"Response: {duplicate_data}"
                self.log_test("Duplicate Territory Assignment", success, details)
            else:
                self.log_test("Duplicate Territory Assignment", False, f"Status: {duplicate_response.status_code}")
            
            # Step 7: Test assigning a different territory
            print("\n🆕 Testing Additional Territory Assignment")
            territory_payload2 = {"zip_code": "90210"}
            
            assign_response2 = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload2, 
                headers=headers, 
                timeout=10
            )
            
            if assign_response2.status_code == 200:
                assign_data2 = assign_response2.json()
                success = assign_data2.get("zip_code") == "90210"
                details = f"Response: {assign_data2}"
                self.log_test("Assign Additional Territory (ZIP 90210)", success, details)
                
                # Verify both territories are now in user profile
                me_response2 = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                if me_response2.status_code == 200:
                    me_data2 = me_response2.json()
                    owned_territories2 = me_data2.get("owned_territories", [])
                    success = "10001" in owned_territories2 and "90210" in owned_territories2
                    details = f"All owned territories: {owned_territories2}"
                    self.log_test("Verify Multiple Territories", success, details)
                
            else:
                self.log_test("Assign Additional Territory (ZIP 90210)", False, f"Status: {assign_response2.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Territory Assignment - General Error", False, str(e))
            return False
    
    def run_tests(self):
        """Run all territory assignment tests"""
        print("🚀 Starting Territory Assignment Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API availability first
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code != 200:
                print("❌ API is not accessible. Stopping tests.")
                return False
            print("✅ API is accessible")
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
        
        # Run territory assignment tests
        success = self.test_territory_assignment_complete()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if success and self.tests_passed == self.tests_run:
            print("🎉 All territory assignment tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    tester = TerritoryAssignmentTester()
    success = tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())