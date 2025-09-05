#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time
import os

class UserVerificationTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.target_email = "territory1756780976@example.com"
        self.target_password = "testpass123"
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
            print(f"   ℹ️  {details}")
        
    def test_user_exists(self):
        """Check if the target user exists by attempting login"""
        try:
            login_payload = {
                "email": self.target_email,
                "password": self.target_password
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            
            if response.status_code == 200:
                # User exists and credentials are correct
                data = response.json()
                user_data = data.get("user", {})
                self.log_test("User Exists Check", True, 
                    f"User exists and credentials work! User ID: {user_data.get('id')}, "
                    f"Active: {user_data.get('is_active')}, Role: {user_data.get('role')}, "
                    f"Territories: {user_data.get('owned_territories', [])}")
                return True, "exists_and_works", data
                
            elif response.status_code == 401:
                # User might exist but wrong password, or user doesn't exist
                error_detail = response.json().get("detail", "")
                if "invalid email or password" in error_detail.lower():
                    # Could be either case - need to check if user exists another way
                    self.log_test("User Exists Check", False, 
                        f"Login failed with 401: {error_detail}")
                    return False, "login_failed", None
                else:
                    self.log_test("User Exists Check", False, 
                        f"Unexpected 401 error: {error_detail}")
                    return False, "unexpected_error", None
            else:
                self.log_test("User Exists Check", False, 
                    f"Unexpected status code: {response.status_code}")
                return False, "unexpected_status", None
                
        except Exception as e:
            self.log_test("User Exists Check", False, str(e))
            return False, "exception", None
    
    def test_create_user_if_needed(self):
        """Create the target user if it doesn't exist"""
        try:
            register_payload = {
                "email": self.target_email,
                "password": self.target_password,
                "first_name": "Territory",
                "last_name": "Test"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                self.log_test("Create Test User", True, 
                    f"User created successfully! User ID: {user_data.get('id')}, "
                    f"Email: {user_data.get('email')}, Active: {user_data.get('is_active')}")
                return True, data
                
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "")
                if "already registered" in error_detail.lower():
                    self.log_test("Create Test User", True, 
                        "User already exists (which is expected)")
                    return True, None
                else:
                    self.log_test("Create Test User", False, 
                        f"Registration failed: {error_detail}")
                    return False, None
            else:
                self.log_test("Create Test User", False, 
                    f"Unexpected status code: {response.status_code}, Response: {response.text[:200]}")
                return False, None
                
        except Exception as e:
            self.log_test("Create Test User", False, str(e))
            return False, None
    
    def test_login_verification(self):
        """Verify login works with the target credentials"""
        try:
            login_payload = {
                "email": self.target_email,
                "password": self.target_password
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                token = data.get("access_token", "")
                
                # Verify user is active
                is_active = user_data.get("is_active", False)
                if not is_active:
                    self.log_test("Login Verification", False, 
                        "User exists but is not active (is_active: false)")
                    return False, None
                
                self.log_test("Login Verification", True, 
                    f"Login successful! Token received, User active: {is_active}, "
                    f"Role: {user_data.get('role')}, Territories: {user_data.get('owned_territories', [])}")
                return True, data
                
            else:
                error_detail = response.json().get("detail", "") if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("Login Verification", False, 
                    f"Login failed - Status: {response.status_code}, Error: {error_detail}")
                return False, None
                
        except Exception as e:
            self.log_test("Login Verification", False, str(e))
            return False, None
    
    def test_user_profile_access(self, auth_token):
        """Test accessing user profile with the token"""
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Profile Access", True, 
                    f"Profile accessible - Email: {data.get('email')}, "
                    f"Active: {data.get('is_active')}, Role: {data.get('role')}, "
                    f"Territories: {data.get('owned_territories', [])}")
                return True, data
            else:
                self.log_test("User Profile Access", False, 
                    f"Profile access failed - Status: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("User Profile Access", False, str(e))
            return False, None
    
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                message = data.get("message", "")
                self.log_test("API Connectivity", True, f"API accessible - {message}")
            else:
                self.log_test("API Connectivity", False, f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.log_test("API Connectivity", False, str(e))
            return False
    
    def run_verification(self):
        """Run the complete user verification process"""
        print("🔍 USER ACCESS VERIFICATION FOR MANUAL TESTING")
        print(f"📧 Target Email: {self.target_email}")
        print(f"🔑 Target Password: {self.target_password}")
        print(f"🌐 API URL: {self.api_url}")
        print("=" * 70)
        
        # Step 1: Test API connectivity
        print("\n1️⃣ Testing API Connectivity...")
        if not self.test_api_connectivity():
            print("❌ API is not accessible. Cannot proceed with user verification.")
            return False
        
        # Step 2: Check if user exists and credentials work
        print("\n2️⃣ Checking if user exists and credentials work...")
        user_exists, status, login_data = self.test_user_exists()
        
        if status == "exists_and_works":
            print("✅ User exists and credentials work perfectly!")
            auth_token = login_data.get("access_token")
            
            # Step 3: Test profile access
            print("\n3️⃣ Testing user profile access...")
            self.test_user_profile_access(auth_token)
            
        elif status == "login_failed":
            print("⚠️ User might exist but credentials don't work. Attempting to create user...")
            
            # Step 3: Try to create the user
            print("\n3️⃣ Creating test user with required credentials...")
            created, create_data = self.test_create_user_if_needed()
            
            if created:
                # Step 4: Verify login works now
                print("\n4️⃣ Verifying login works with created user...")
                login_success, login_data = self.test_login_verification()
                
                if login_success:
                    auth_token = login_data.get("access_token")
                    # Step 5: Test profile access
                    print("\n5️⃣ Testing user profile access...")
                    self.test_user_profile_access(auth_token)
                else:
                    print("❌ Failed to login even after creating user")
            else:
                print("❌ Failed to create user")
        
        else:
            print("❌ Unexpected error during user existence check")
        
        # Print final results
        print("\n" + "=" * 70)
        print(f"📊 Verification Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 USER ACCESS VERIFICATION SUCCESSFUL!")
            print(f"✅ The user can login with:")
            print(f"   📧 Email: {self.target_email}")
            print(f"   🔑 Password: {self.target_password}")
            print("✅ User is ready for manual testing of SEO & Social Media Trends features!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} test(s) failed.")
            print("❌ User access verification incomplete. Please check the issues above.")
            return False

def main():
    tester = UserVerificationTester()
    success = tester.run_verification()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())