#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class AuthTester:
    def __init__(self, base_url="https://territory-hub-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
    
    def test_auth_register_valid(self):
        """Test user registration with valid data"""
        try:
            timestamp = int(time.time())
            payload = {
                "email": f"test{timestamp}@example.com",
                "password": "testpass123",
                "first_name": "John",
                "last_name": "Doe"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    user_data = data["user"]
                    user_required_fields = ["id", "email", "first_name", "last_name", "role", "created_at", "is_active"]
                    missing_user_fields = [field for field in user_required_fields if field not in user_data]
                    
                    if missing_user_fields:
                        success = False
                        details = f"Missing user fields: {missing_user_fields}"
                    else:
                        self.auth_token = data["access_token"]
                        details = f"User registered with ID: {user_data['id']}, Token type: {data['token_type']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("POST /api/auth/register - Valid Data", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST /api/auth/register - Valid Data", False, str(e))
            return False
    
    def test_auth_register_duplicate_email(self):
        """Test user registration with duplicate email"""
        try:
            timestamp = int(time.time())
            email = f"duplicate{timestamp}@example.com"
            payload = {
                "email": email,
                "password": "testpass123",
                "first_name": "First",
                "last_name": "User"
            }
            
            response1 = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            if response1.status_code != 200:
                self.log_test("POST /api/auth/register - Duplicate Email", False, f"First registration failed: {response1.status_code}")
                return False
            
            payload2 = {
                "email": email,
                "password": "testpass123",
                "first_name": "Second",
                "last_name": "User"
            }
            
            response2 = requests.post(f"{self.api_url}/auth/register", json=payload2, timeout=10)
            success = response2.status_code == 400
            
            if success:
                data = response2.json()
                success = "already registered" in data.get("detail", "").lower()
                details = f"Correctly rejected duplicate email: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response2.status_code}, Expected: 400"
            
            self.log_test("POST /api/auth/register - Duplicate Email", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST /api/auth/register - Duplicate Email", False, str(e))
            return False
    
    def test_auth_register_weak_password(self):
        """Test user registration with weak password"""
        try:
            timestamp = int(time.time())
            payload = {
                "email": f"weak{timestamp}@example.com",
                "password": "123",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            success = response.status_code == 422
            
            if success:
                data = response.json()
                error_detail = str(data.get("detail", ""))
                success = "password" in error_detail.lower() and ("6 characters" in error_detail or "length" in error_detail)
                details = f"Correctly rejected weak password: {error_detail}" if success else f"Unexpected validation error: {error_detail}"
            else:
                details = f"Status: {response.status_code}, Expected: 422"
            
            self.log_test("POST /api/auth/register - Weak Password", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST /api/auth/register - Weak Password", False, str(e))
            return False
    
    def test_auth_login_valid(self):
        """Test user login with correct credentials"""
        try:
            timestamp = int(time.time())
            register_payload = {
                "email": f"login{timestamp}@example.com",
                "password": "testpass123",
                "first_name": "Login",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            if register_response.status_code != 200:
                self.log_test("POST /api/auth/login - Valid Credentials", False, "Failed to register test user")
                return False
            
            login_payload = {
                "email": register_payload["email"],
                "password": register_payload["password"]
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    user_data = data["user"]
                    success = user_data["email"] == login_payload["email"]
                    details = f"Login successful for {user_data['email']}, Token: {data['access_token'][:20]}..." if success else "Email mismatch in response"
                    
                    if success:
                        self.auth_token = data["access_token"]
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("POST /api/auth/login - Valid Credentials", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST /api/auth/login - Valid Credentials", False, str(e))
            return False
    
    def test_auth_login_wrong_password(self):
        """Test user login with wrong password"""
        try:
            login_payload = {
                "email": "test@example.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 401
            
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower()
                details = f"Correctly rejected wrong password: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 401"
            
            self.log_test("POST /api/auth/login - Wrong Password", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST /api/auth/login - Wrong Password", False, str(e))
            return False
    
    def test_auth_login_nonexistent_email(self):
        """Test user login with non-existent email"""
        try:
            login_payload = {
                "email": "nonexistent@example.com",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 401
            
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower()
                details = f"Correctly rejected non-existent email: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 401"
            
            self.log_test("POST /api/auth/login - Non-existent Email", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST /api/auth/login - Non-existent Email", False, str(e))
            return False
    
    def test_auth_me_valid_token(self):
        """Test /auth/me endpoint with valid JWT token"""
        try:
            if not self.auth_token:
                self.log_test("GET /api/auth/me - Valid Token", False, "No auth token available from previous tests")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["id", "email", "first_name", "last_name", "role", "owned_territories", "created_at", "is_active"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Profile retrieved for {data['email']}, Role: {data['role']}, Active: {data['is_active']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("GET /api/auth/me - Valid Token", success, details)
            return success
            
        except Exception as e:
            self.log_test("GET /api/auth/me - Valid Token", False, str(e))
            return False
    
    def test_auth_me_invalid_token(self):
        """Test /auth/me endpoint with invalid JWT token"""
        try:
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success = response.status_code == 401
            
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower() or "token" in data.get("detail", "").lower()
                details = f"Correctly rejected invalid token: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 401"
            
            self.log_test("GET /api/auth/me - Invalid Token", success, details)
            return success
            
        except Exception as e:
            self.log_test("GET /api/auth/me - Invalid Token", False, str(e))
            return False
    
    def test_auth_me_no_token(self):
        """Test /auth/me endpoint with no authorization header"""
        try:
            response = requests.get(f"{self.api_url}/auth/me", timeout=10)
            success = response.status_code == 403
            
            if success:
                details = "Correctly rejected request without authorization header"
            else:
                details = f"Status: {response.status_code}, Expected: 403"
            
            self.log_test("GET /api/auth/me - No Token", success, details)
            return success
            
        except Exception as e:
            self.log_test("GET /api/auth/me - No Token", False, str(e))
            return False
    
    def run_auth_tests(self):
        """Run all authentication tests"""
        print("🔐 Testing Authentication System")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        print("\n📝 Testing User Registration...")
        self.test_auth_register_valid()
        self.test_auth_register_duplicate_email()
        self.test_auth_register_weak_password()
        
        print("\n🔑 Testing User Login...")
        self.test_auth_login_valid()
        self.test_auth_login_wrong_password()
        self.test_auth_login_nonexistent_email()
        
        print("\n👤 Testing User Profile Endpoint...")
        self.test_auth_me_valid_token()
        self.test_auth_me_invalid_token()
        self.test_auth_me_no_token()
        
        print("\n" + "=" * 60)
        print(f"📊 Authentication Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All authentication tests passed! JWT authentication system is fully functional.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} authentication test(s) failed.")
            return False

def main():
    tester = AuthTester()
    success = tester.run_auth_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())