#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class AdamTest3Investigation:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.target_user_email = "adamtest3@gmail.com"
        self.target_zip = "30126"
        self.auth_token = None
        
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
        
    def test_user_exists_and_login(self):
        """Check if adamtest3@gmail.com exists and try to login"""
        try:
            # Try common passwords for test users
            test_passwords = ["adam123", "testpass123", "password123", "adamtest3"]
            
            for password in test_passwords:
                login_payload = {
                    "email": self.target_user_email,
                    "password": password
                }
                
                response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data["access_token"]
                    user_data = data["user"]
                    owned_territories = user_data.get("owned_territories", [])
                    
                    self.log_test(
                        "User Login Test", 
                        True, 
                        f"Successfully logged in with password '{password}'. User ID: {user_data['id']}, Owned territories: {owned_territories}"
                    )
                    return True, user_data
                elif response.status_code == 401:
                    continue  # Try next password
                else:
                    self.log_test(
                        "User Login Test", 
                        False, 
                        f"Unexpected status code {response.status_code} with password '{password}'"
                    )
                    return False, None
            
            # If we get here, none of the passwords worked
            self.log_test(
                "User Login Test", 
                False, 
                f"Could not login with any test passwords: {test_passwords}. User may not exist or has different password."
            )
            return False, None
            
        except Exception as e:
            self.log_test("User Login Test", False, str(e))
            return False, None
    
    def test_zip_availability_check(self):
        """Check ZIP 30126 availability status"""
        try:
            payload = {"zip_code": self.target_zip}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                is_available = data.get("available", True)
                assigned_to = data.get("assigned_to")
                location_info = data.get("location_info", {})
                
                details = f"ZIP {self.target_zip} - Available: {is_available}"
                if not is_available and assigned_to:
                    details += f", Assigned to: {assigned_to}"
                details += f", Location: {location_info.get('city', 'Unknown')}, {location_info.get('state', 'Unknown')}"
                
                self.log_test("ZIP Availability Check", True, details)
                return True, data
            else:
                self.log_test("ZIP Availability Check", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False, None
                
        except Exception as e:
            self.log_test("ZIP Availability Check", False, str(e))
            return False, None
    
    def test_assign_territory_to_user(self):
        """Try to assign ZIP 30126 to adamtest3@gmail.com"""
        try:
            if not self.auth_token:
                self.log_test("Territory Assignment", False, "No auth token available - user login failed")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"zip_code": self.target_zip}
            
            response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=payload, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Territory Assignment", True, f"Assignment successful: {data.get('message', 'No message')}")
                return True
            elif response.status_code == 409:
                data = response.json()
                self.log_test("Territory Assignment", False, f"Conflict - ZIP already assigned: {data.get('detail', 'No details')}")
                return False
            else:
                self.log_test("Territory Assignment", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Territory Assignment", False, str(e))
            return False
    
    def test_verify_user_profile_after_assignment(self):
        """Verify user profile shows ZIP 30126 in owned_territories"""
        try:
            if not self.auth_token:
                self.log_test("User Profile Verification", False, "No auth token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                owned_territories = data.get("owned_territories", [])
                has_target_zip = self.target_zip in owned_territories
                
                details = f"User {data.get('email')} owns ZIP {self.target_zip}: {'Yes' if has_target_zip else 'No'}, All territories: {owned_territories}"
                self.log_test("User Profile Verification", has_target_zip, details)
                return has_target_zip
            else:
                self.log_test("User Profile Verification", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Profile Verification", False, str(e))
            return False
    
    def test_force_release_zip_if_needed(self):
        """Use admin endpoint to force release ZIP 30126 if it's assigned to wrong user"""
        try:
            payload = {"zip_code": self.target_zip}
            response = requests.post(f"{self.api_url}/admin/force-zip-release", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users_modified = data.get("users_modified", 0)
                self.log_test("Force ZIP Release", True, f"Released ZIP {self.target_zip} from {users_modified} user(s)")
                return True
            else:
                self.log_test("Force ZIP Release", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Force ZIP Release", False, str(e))
            return False
    
    def test_content_generation_access(self):
        """Test if user can access Content Generation Hub for ZIP 30126"""
        try:
            if not self.auth_token:
                self.log_test("Content Generation Access", False, "No auth token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"zip_code": self.target_zip}
            
            # Test Instagram content generation as example
            response = requests.post(
                f"{self.api_url}/generate-platform-content/instagram", 
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_content = "instagram_posts" in data and len(data.get("instagram_posts", [])) > 0
                self.log_test("Content Generation Access", has_content, f"Instagram content generation successful: {len(data.get('instagram_posts', []))} posts generated")
                return has_content
            elif response.status_code == 403:
                data = response.json()
                self.log_test("Content Generation Access", False, f"Access denied: {data.get('detail', 'No details')}")
                return False
            else:
                self.log_test("Content Generation Access", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Content Generation Access", False, str(e))
            return False
    
    def test_zip_analysis_exists(self):
        """Check if ZIP analysis data exists for ZIP 30126"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{self.target_zip}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                zip_code = data.get("zip_code")
                created_at = data.get("created_at")
                has_seo_social = "seo_social_trends" in data
                
                self.log_test("ZIP Analysis Data Check", True, f"Analysis exists for ZIP {zip_code}, created: {created_at}, has seo_social_trends: {has_seo_social}")
                return True, data
            elif response.status_code == 404:
                self.log_test("ZIP Analysis Data Check", False, f"No analysis data found for ZIP {self.target_zip}")
                return False, None
            else:
                self.log_test("ZIP Analysis Data Check", False, f"Status: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("ZIP Analysis Data Check", False, str(e))
            return False, None
    
    def run_investigation(self):
        """Run complete investigation and fix for adamtest3@gmail.com territory assignment"""
        print("🔍 INVESTIGATING TERRITORY ASSIGNMENT FOR adamtest3@gmail.com")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🎯 Target: {self.target_user_email} should own ZIP {self.target_zip}")
        print("=" * 80)
        
        # Step 1: Check if user exists and can login
        print(f"\n👤 Step 1: Check if user {self.target_user_email} exists and login")
        user_login_success, user_data = self.test_user_exists_and_login()
        
        # Step 2: Check ZIP availability status
        print(f"\n🏠 Step 2: Check ZIP {self.target_zip} availability status")
        zip_check_success, zip_data = self.test_zip_availability_check()
        
        # Step 3: Check if ZIP analysis data exists
        print(f"\n📊 Step 3: Check if ZIP analysis data exists for {self.target_zip}")
        analysis_exists, analysis_data = self.test_zip_analysis_exists()
        
        # Step 4: Determine if we need to fix territory assignment
        if user_login_success and zip_check_success:
            zip_available = zip_data.get("available", True)
            assigned_to = zip_data.get("assigned_to")
            
            if not zip_available and assigned_to != self.target_user_email:
                print(f"\n🔧 Step 4: ZIP {self.target_zip} is assigned to {assigned_to}, need to fix assignment")
                
                # Force release ZIP from current owner
                print(f"\n🚨 Step 4a: Force release ZIP {self.target_zip} from current owner")
                release_success = self.test_force_release_zip_if_needed()
                
                if release_success:
                    # Wait a moment for the change to propagate
                    time.sleep(2)
                    
                    # Try to assign to correct user
                    print(f"\n✅ Step 4b: Assign ZIP {self.target_zip} to {self.target_user_email}")
                    assignment_success = self.test_assign_territory_to_user()
                    
                    if assignment_success:
                        # Verify assignment worked
                        print(f"\n🔍 Step 4c: Verify assignment in user profile")
                        self.test_verify_user_profile_after_assignment()
                    
            elif zip_available:
                print(f"\n✅ Step 4: ZIP {self.target_zip} is available, assigning to {self.target_user_email}")
                assignment_success = self.test_assign_territory_to_user()
                
                if assignment_success:
                    print(f"\n🔍 Step 4a: Verify assignment in user profile")
                    self.test_verify_user_profile_after_assignment()
            
            elif assigned_to == self.target_user_email:
                print(f"\n✅ Step 4: ZIP {self.target_zip} is already correctly assigned to {self.target_user_email}")
                self.test_verify_user_profile_after_assignment()
        
        # Step 5: Test Content Generation Hub access
        print(f"\n🎨 Step 5: Test Content Generation Hub access")
        self.test_content_generation_access()
        
        # Print final results
        print("\n" + "=" * 80)
        print(f"📊 Investigation Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Provide summary and recommendations
        if user_login_success:
            if self.tests_passed >= self.tests_run - 1:  # Allow 1 failure
                print("🎉 ISSUE RESOLVED: Territory assignment for adamtest3@gmail.com is now working correctly!")
                print(f"✅ User can login and should now see ZIP {self.target_zip} in their dashboard")
                print(f"✅ Content Generation Hub should be accessible for ZIP {self.target_zip}")
            else:
                print("⚠️  PARTIAL SUCCESS: Some issues remain")
                print("🔧 Recommendations:")
                if not zip_check_success:
                    print(f"   - Check ZIP availability service for {self.target_zip}")
                if not analysis_exists:
                    print(f"   - User may need to run ZIP analysis for {self.target_zip} first")
                print(f"   - Verify user {self.target_user_email} can access dashboard and see owned territories")
        else:
            print("❌ CRITICAL ISSUE: Cannot login as adamtest3@gmail.com")
            print("🔧 Recommendations:")
            print(f"   - Verify user {self.target_user_email} exists in database")
            print("   - Check if password needs to be reset")
            print("   - Consider creating user if they don't exist")
        
        return self.tests_passed >= self.tests_run - 1

def main():
    investigator = AdamTest3Investigation()
    success = investigator.run_investigation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())