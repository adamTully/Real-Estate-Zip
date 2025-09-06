#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ForceReleaseZipTester:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.target_zip = "30126"  # ZIP code to force release
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if details:
                print(f"   📝 {details}")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def test_force_zip_release(self):
        """Test POST /api/admin/force-zip-release to release ZIP 30126"""
        try:
            payload = {"zip_code": self.target_zip}
            response = requests.post(
                f"{self.api_url}/admin/force-zip-release", 
                json=payload,
                timeout=15
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify response structure
                required_fields = ["message", "users_modified", "zip_code", "success"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing response fields: {missing_fields}"
                else:
                    users_modified = data.get("users_modified", 0)
                    zip_code = data.get("zip_code")
                    success_flag = data.get("success", False)
                    
                    if zip_code != self.target_zip:
                        success = False
                        details = f"ZIP code mismatch: expected {self.target_zip}, got {zip_code}"
                    elif not success_flag:
                        success = False
                        details = f"Success flag is False in response"
                    else:
                        details = f"ZIP {self.target_zip} released from {users_modified} users. Message: {data.get('message')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:300]}"
                
            self.log_test(f"Force Release ZIP {self.target_zip}", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"Force Release ZIP {self.target_zip}", False, str(e))
            return False, None

    def test_zip_availability_check(self):
        """Test POST /api/zip-availability/check to verify ZIP 30126 is available"""
        try:
            payload = {"zip_code": self.target_zip}
            response = requests.post(
                f"{self.api_url}/zip-availability/check", 
                json=payload,
                timeout=15
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify response structure
                required_fields = ["zip_code", "available", "location_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing response fields: {missing_fields}"
                else:
                    zip_code = data.get("zip_code")
                    available = data.get("available")
                    location_info = data.get("location_info", {})
                    assigned_to = data.get("assigned_to")
                    
                    if zip_code != self.target_zip:
                        success = False
                        details = f"ZIP code mismatch: expected {self.target_zip}, got {zip_code}"
                    elif not available:
                        success = False
                        details = f"ZIP {self.target_zip} still shows as taken. Assigned to: {assigned_to}"
                    else:
                        # Verify location shows as Mableton, GA as expected
                        city = location_info.get("city", "")
                        state = location_info.get("state", "")
                        
                        expected_city = "Mableton"
                        expected_state = "GA"
                        
                        if expected_city.lower() in city.lower() and expected_state in state:
                            details = f"ZIP {self.target_zip} is Available in {city}, {state} (coordinates: {location_info.get('latitude')}, {location_info.get('longitude')})"
                        else:
                            # Still success if available, but note location discrepancy
                            details = f"ZIP {self.target_zip} is Available but location shows as {city}, {state} (expected Mableton, GA)"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:300]}"
                
            self.log_test(f"ZIP Availability Check - {self.target_zip}", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Availability Check - {self.target_zip}", False, str(e))
            return False, None

    def test_fresh_user_registration(self):
        """Test fresh user registration with ZIP 30126"""
        try:
            # Create a unique test user
            timestamp = int(time.time())
            test_email = f"fresh_user_{timestamp}@example.com"
            
            # Step 1: Register new user
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "first_name": "Fresh",
                "last_name": "User"
            }
            
            register_response = requests.post(
                f"{self.api_url}/auth/register", 
                json=register_payload, 
                timeout=15
            )
            
            if register_response.status_code != 200:
                self.log_test("Fresh User Registration - User Creation", False, f"Failed to register user: {register_response.status_code}")
                return False
            
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_email = register_data["user"]["email"]
            
            # Step 2: Assign ZIP 30126 to the new user
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": self.target_zip}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=15
            )
            
            success = assign_response.status_code == 200
            if success:
                assign_data = assign_response.json()
                assigned_zip = assign_data.get("zip_code")
                message = assign_data.get("message", "")
                
                if assigned_zip != self.target_zip:
                    success = False
                    details = f"ZIP code mismatch in assignment: expected {self.target_zip}, got {assigned_zip}"
                elif "conflict" in message.lower() or "already assigned" in message.lower():
                    success = False
                    details = f"ZIP {self.target_zip} still shows conflicts: {message}"
                else:
                    # Step 3: Verify assignment via user profile
                    me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        owned_territories = me_data.get("owned_territories", [])
                        
                        if self.target_zip in owned_territories:
                            details = f"Successfully registered user {user_email} and assigned ZIP {self.target_zip}. User territories: {owned_territories}"
                        else:
                            success = False
                            details = f"ZIP {self.target_zip} not found in user territories: {owned_territories}"
                    else:
                        success = False
                        details = f"Failed to verify user profile: {me_response.status_code}"
            else:
                assign_data = assign_response.json() if assign_response.headers.get('content-type', '').startswith('application/json') else {}
                details = f"Territory assignment failed: Status {assign_response.status_code}, Response: {assign_data.get('detail', assign_response.text[:200])}"
                
            self.log_test(f"Fresh User Registration with ZIP {self.target_zip}", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Fresh User Registration with ZIP {self.target_zip}", False, str(e))
            return False

    def test_zip_availability_after_assignment(self):
        """Test that ZIP 30126 shows as taken after fresh user assignment"""
        try:
            payload = {"zip_code": self.target_zip}
            response = requests.post(
                f"{self.api_url}/zip-availability/check", 
                json=payload,
                timeout=15
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                available = data.get("available")
                assigned_to = data.get("assigned_to")
                
                # After assignment, ZIP should NOT be available
                if available:
                    success = False
                    details = f"ZIP {self.target_zip} still shows as available after assignment"
                else:
                    details = f"ZIP {self.target_zip} correctly shows as taken, assigned to: {assigned_to}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:300]}"
                
            self.log_test(f"ZIP Availability After Assignment - {self.target_zip}", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"ZIP Availability After Assignment - {self.target_zip}", False, str(e))
            return False

    def run_force_release_test(self):
        """Run the complete force release test sequence"""
        print("🚀 Testing Force Release ZIP 30126 Functionality")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🎯 Target ZIP: {self.target_zip}")
        print("=" * 60)
        
        # Step 1: Force release ZIP 30126
        print(f"\n🔧 Step 1: Force releasing ZIP {self.target_zip} from all users...")
        success_release, release_data = self.test_force_zip_release()
        
        if not success_release:
            print(f"❌ Failed to force release ZIP {self.target_zip}. Cannot proceed with verification tests.")
            return False
        
        # Brief pause to ensure database consistency
        print("⏳ Waiting 2 seconds for database consistency...")
        time.sleep(2)
        
        # Step 2: Verify ZIP shows as available
        print(f"\n✅ Step 2: Verifying ZIP {self.target_zip} shows as available...")
        success_availability, availability_data = self.test_zip_availability_check()
        
        if not success_availability:
            print(f"❌ ZIP {self.target_zip} still shows as taken after force release.")
            return False
        
        # Step 3: Test fresh user registration
        print(f"\n👤 Step 3: Testing fresh user registration with ZIP {self.target_zip}...")
        success_registration = self.test_fresh_user_registration()
        
        if not success_registration:
            print(f"❌ Failed to register fresh user with ZIP {self.target_zip}.")
            return False
        
        # Brief pause before final verification
        print("⏳ Waiting 2 seconds before final verification...")
        time.sleep(2)
        
        # Step 4: Verify ZIP shows as taken after assignment
        print(f"\n🔒 Step 4: Verifying ZIP {self.target_zip} shows as taken after assignment...")
        success_final = self.test_zip_availability_after_assignment()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Force Release Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print(f"🎉 All force release tests passed! ZIP {self.target_zip} successfully freed and reassigned.")
            print(f"✨ Expected Result Achieved: ZIP {self.target_zip} shows as 'Available in Mableton, GA' with no user assignments after force release.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    tester = ForceReleaseZipTester()
    
    print("Running Force Release ZIP 30126 Test as requested in review...")
    success = tester.run_force_release_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())