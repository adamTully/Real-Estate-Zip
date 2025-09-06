#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class EndToEndCleanupTest:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # Target data
        self.target_zip = "30126"
        self.new_user_token = None
        
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
    
    def test_fresh_user_registration(self):
        """Test that a fresh user can register with ZIP 30126"""
        try:
            timestamp = int(time.time())
            new_user_payload = {
                "email": f"fresh_user_{timestamp}@example.com",
                "password": "freshpass123",
                "first_name": "Fresh",
                "last_name": "User"
            }
            
            # Register new user
            response = requests.post(f"{self.api_url}/auth/register", json=new_user_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.new_user_token = data["access_token"]
                user_data = data["user"]
                details = f"Fresh user registered: {user_data['email']}, ID: {user_data['id']}"
            else:
                details = f"Registration failed: Status {response.status_code}"
            
            self.log_test("Fresh User Registration", success, details)
            return success, new_user_payload["email"] if success else None
            
        except Exception as e:
            self.log_test("Fresh User Registration", False, str(e))
            return False, None
    
    def test_territory_assignment(self, user_email):
        """Test assigning ZIP 30126 to the fresh user"""
        try:
            if not self.new_user_token:
                self.log_test("Territory Assignment", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.new_user_token}"}
            territory_payload = {"zip_code": self.target_zip}
            
            response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"ZIP {self.target_zip} assigned to {user_email}: {data.get('message', 'Success')}"
            else:
                details = f"Assignment failed: Status {response.status_code}, Response: {response.text[:100]}"
            
            self.log_test("Territory Assignment", success, details)
            return success
            
        except Exception as e:
            self.log_test("Territory Assignment", False, str(e))
            return False
    
    def test_user_profile_verification(self, user_email):
        """Verify user profile shows ZIP 30126 ownership"""
        try:
            if not self.new_user_token:
                self.log_test("User Profile Verification", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.new_user_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                owned_territories = data.get("owned_territories", [])
                success = self.target_zip in owned_territories
                details = f"User {user_email} territories: {owned_territories}, owns ZIP {self.target_zip}: {success}"
            else:
                details = f"Profile check failed: Status {response.status_code}"
            
            self.log_test("User Profile Verification", success, details)
            return success
            
        except Exception as e:
            self.log_test("User Profile Verification", False, str(e))
            return False
    
    def test_zip_analysis_creation(self):
        """Test creating new ZIP analysis for 30126"""
        try:
            payload = {"zip_code": self.target_zip}
            response = requests.post(
                f"{self.api_url}/zip-analysis/start", 
                json=payload,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                job_id = data.get("job_id", "N/A")
                state = data.get("state", "N/A")
                details = f"New analysis started for ZIP {self.target_zip}, Job ID: {job_id}, State: {state}"
            else:
                details = f"Analysis creation failed: Status {response.status_code}"
            
            self.log_test("ZIP Analysis Creation", success, details)
            return success
            
        except Exception as e:
            self.log_test("ZIP Analysis Creation", False, str(e))
            return False
    
    def test_no_old_data_exists(self):
        """Verify no old adamtest1 data exists"""
        try:
            # Try to login as adamtest1
            login_response = requests.post(f"{self.api_url}/auth/login", 
                                        json={"email": "adamtest1@gmail.com", "password": "adam123"}, 
                                        timeout=10)
            user_exists = login_response.status_code == 200
            
            # Check for old analysis data (should be 404)
            analysis_response = requests.get(f"{self.api_url}/zip-analysis/{self.target_zip}", timeout=10)
            old_analysis_exists = analysis_response.status_code == 200
            
            success = not user_exists and not old_analysis_exists
            details = f"adamtest1@gmail.com exists: {user_exists}, Old analysis exists: {old_analysis_exists}"
            
            self.log_test("No Old Data Exists", success, details)
            return success
            
        except Exception as e:
            self.log_test("No Old Data Exists", False, str(e))
            return False
    
    def run_end_to_end_test(self):
        """Run complete end-to-end cleanup verification"""
        print("🚀 END-TO-END CLEANUP VERIFICATION TEST")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🎯 Verify clean slate for ZIP {self.target_zip}")
        print("=" * 80)
        
        # Step 1: Verify no old data exists
        print("\n🔍 Step 1: Verify No Old Data Exists")
        no_old_data = self.test_no_old_data_exists()
        
        # Step 2: Register fresh user
        print("\n👤 Step 2: Register Fresh User")
        user_registered, user_email = self.test_fresh_user_registration()
        
        if not user_registered:
            print("❌ Cannot proceed without user registration")
            return False
        
        # Step 3: Assign territory
        print(f"\n🏠 Step 3: Assign ZIP {self.target_zip}")
        territory_assigned = self.test_territory_assignment(user_email)
        
        # Step 4: Verify user profile
        print("\n✅ Step 4: Verify User Profile")
        profile_verified = self.test_user_profile_verification(user_email)
        
        # Step 5: Test new analysis creation
        print("\n📊 Step 5: Test New Analysis Creation")
        analysis_created = self.test_zip_analysis_creation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 END-TO-END TEST SUMMARY")
        print("=" * 80)
        
        print(f"🔍 No old data exists: {'✅ VERIFIED' if no_old_data else '❌ OLD DATA FOUND'}")
        print(f"👤 Fresh user registration: {'✅ SUCCESS' if user_registered else '❌ FAILED'}")
        print(f"🏠 Territory assignment: {'✅ SUCCESS' if territory_assigned else '❌ FAILED'}")
        print(f"✅ User profile verification: {'✅ SUCCESS' if profile_verified else '❌ FAILED'}")
        print(f"📊 New analysis creation: {'✅ SUCCESS' if analysis_created else '❌ FAILED'}")
        
        overall_success = (no_old_data and user_registered and territory_assigned and 
                          profile_verified and analysis_created)
        
        print(f"\n🎯 Overall Result: {'✅ CLEAN SLATE VERIFIED' if overall_success else '❌ ISSUES FOUND'}")
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if overall_success:
            print(f"\n🎉 End-to-end cleanup verification successful!")
            print(f"   • No old adamtest1@gmail.com data exists")
            print(f"   • Fresh user can register and claim ZIP {self.target_zip}")
            print(f"   • User profile correctly shows territory ownership")
            print(f"   • New ZIP analysis can be created from scratch")
            print(f"   • System is ready for testing enhanced prompts")
        else:
            print(f"\n⚠️ End-to-end verification found issues:")
            if not no_old_data:
                print(f"   • Old data still exists in the system")
            if not user_registered:
                print(f"   • Fresh user registration failed")
            if not territory_assigned:
                print(f"   • Territory assignment failed")
            if not profile_verified:
                print(f"   • User profile verification failed")
            if not analysis_created:
                print(f"   • New analysis creation failed")
        
        return overall_success

def main():
    tester = EndToEndCleanupTest()
    
    # Run the end-to-end test
    success = tester.run_end_to_end_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())