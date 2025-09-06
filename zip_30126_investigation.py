#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ZIP30126Investigator:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.investigation_zip = "30126"
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
            print(f"   📋 Details: {details}")
        
    def test_zip_availability_check(self):
        """Test 1: Check ZIP Availability Response for ZIP 30126"""
        try:
            payload = {"zip_code": self.investigation_zip}
            response = requests.post(
                f"{self.api_url}/zip-availability/check", 
                json=payload,
                timeout=15
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                
                # Extract key information
                is_available = data.get("available", None)
                assigned_to = data.get("assigned_to", None)
                location_info = data.get("location_info", {})
                city = location_info.get("city", "Unknown")
                state = location_info.get("state", "Unknown")
                
                # Log detailed findings
                availability_status = "Available" if is_available else "Taken"
                owner_info = f"Assigned to: {assigned_to}" if assigned_to else "No owner found"
                
                details = f"ZIP {self.investigation_zip} status: {availability_status}. Location: {city}, {state}. {owner_info}"
                
                # This test always passes if we get a response, we're just gathering info
                success = True
                
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:300]}"
                
            self.log_test(f"ZIP Availability Check for {self.investigation_zip}", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Availability Check for {self.investigation_zip}", False, str(e))
            return False, None

    def test_user_database_search(self):
        """Test 2: Search User Database for ZIP 30126 ownership"""
        try:
            # We need to create a super admin to access user data
            timestamp = int(time.time())
            admin_payload = {
                "email": f"investigator{timestamp}@example.com",
                "password": "investigator123",
                "first_name": "ZIP",
                "last_name": "Investigator"
            }
            
            # Try to create super admin (might fail if one exists)
            admin_response = requests.post(f"{self.api_url}/admin/create-super-admin", json=admin_payload, timeout=10)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                admin_token = admin_data["access_token"]
            else:
                # If super admin creation fails, try to login with existing test user
                login_payload = {
                    "email": "territory1756780976@example.com",
                    "password": "testpass123"
                }
                login_response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    admin_token = login_data["access_token"]
                else:
                    self.log_test("User Database Search", False, "Cannot authenticate to access user data")
                    return False, []
            
            # Get all users
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            users_response = requests.get(f"{self.api_url}/admin/users", headers=admin_headers, timeout=15)
            
            if users_response.status_code != 200:
                self.log_test("User Database Search", False, f"Failed to get users: {users_response.status_code}")
                return False
            
            users_data = users_response.json()
            
            # Search for users with ZIP 30126
            users_with_zip = []
            for user in users_data:
                owned_territories = user.get("owned_territories", [])
                if self.investigation_zip in owned_territories:
                    users_with_zip.append({
                        "email": user.get("email"),
                        "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                        "id": user.get("id"),
                        "territories": owned_territories,
                        "created_at": user.get("created_at"),
                        "is_active": user.get("is_active")
                    })
            
            # Report findings
            if len(users_with_zip) == 0:
                success = True
                details = f"✅ GOOD: No users found with ZIP {self.investigation_zip} in owned_territories. Database appears clean."
            else:
                success = True  # Still successful test, just reporting findings
                details = f"🚨 FOUND: {len(users_with_zip)} user(s) with ZIP {self.investigation_zip}: "
                for user in users_with_zip:
                    details += f"\n   - {user['email']} ({user['name']}) - Active: {user['is_active']} - All territories: {user['territories']}"
            
            self.log_test("User Database Search", success, details)
            return success, users_with_zip
            
        except Exception as e:
            self.log_test("User Database Search", False, str(e))
            return False, []

    def test_analysis_data_check(self):
        """Test 3: Check Analysis Data for ZIP 30126"""
        try:
            # Check if analysis exists for ZIP 30126
            analysis_response = requests.get(f"{self.api_url}/zip-analysis/{self.investigation_zip}", timeout=15)
            
            if analysis_response.status_code == 404:
                success = True
                details = f"✅ GOOD: No analysis data found for ZIP {self.investigation_zip}. Analysis collection appears clean."
            elif analysis_response.status_code == 200:
                analysis_data = analysis_response.json()
                success = True  # Still successful test, just reporting findings
                details = f"🚨 FOUND: Analysis data exists for ZIP {self.investigation_zip}. Created: {analysis_data.get('created_at', 'Unknown')}, ID: {analysis_data.get('id', 'Unknown')}"
            else:
                success = False
                details = f"Unexpected response: {analysis_response.status_code}"
            
            # Also check analysis status
            status_response = requests.get(f"{self.api_url}/zip-analysis/status/{self.investigation_zip}", timeout=10)
            
            if status_response.status_code == 404:
                status_details = "✅ No analysis status found"
            elif status_response.status_code == 200:
                status_data = status_response.json()
                status_details = f"🚨 Analysis status exists: {status_data.get('state', 'Unknown')} - {status_data.get('overall_percent', 0)}%"
            else:
                status_details = f"Status check error: {status_response.status_code}"
            
            details += f"\n   Status check: {status_details}"
            
            self.log_test("Analysis Data Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Analysis Data Check", False, str(e))
            return False

    def test_fresh_registration(self):
        """Test 4: Try registering a completely new user with ZIP 30126"""
        try:
            # Create a completely new user
            timestamp = int(time.time())
            new_user_email = f"fresh_test_{timestamp}@example.com"
            
            register_payload = {
                "email": new_user_email,
                "password": "freshtest123",
                "first_name": "Fresh",
                "last_name": "Tester"
            }
            
            # Register new user
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            
            if register_response.status_code != 200:
                self.log_test("Fresh Registration", False, f"Failed to register new user: {register_response.status_code}")
                return False
            
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_id = register_data["user"]["id"]
            
            # Try to assign ZIP 30126 to this new user
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": self.investigation_zip}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            if assign_response.status_code == 200:
                assign_data = assign_response.json()
                success = True
                details = f"✅ SUCCESS: New user {new_user_email} successfully assigned ZIP {self.investigation_zip}. Message: {assign_data.get('message', 'No message')}"
            elif assign_response.status_code == 409:
                # Conflict - ZIP already assigned
                assign_data = assign_response.json()
                success = True  # Test successful, just reporting the conflict
                details = f"🚨 CONFLICT: ZIP {self.investigation_zip} already assigned. Error: {assign_data.get('detail', 'No details')}"
            else:
                success = False
                details = f"Unexpected assignment response: {assign_response.status_code} - {assign_response.text[:200]}"
            
            # Verify user profile
            me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            if me_response.status_code == 200:
                me_data = me_response.json()
                owned_territories = me_data.get("owned_territories", [])
                if self.investigation_zip in owned_territories:
                    details += f"\n   ✅ Verification: User profile shows ZIP {self.investigation_zip} in owned_territories: {owned_territories}"
                else:
                    details += f"\n   ❌ Verification: User profile does NOT show ZIP {self.investigation_zip}. Territories: {owned_territories}"
            
            self.log_test("Fresh Registration", success, details)
            return success
            
        except Exception as e:
            self.log_test("Fresh Registration", False, str(e))
            return False

    def test_zip_availability_vs_database_consistency(self, availability_data, users_with_zip):
        """Test 5: Check consistency between availability API and database"""
        try:
            if not availability_data:
                self.log_test("Availability vs Database Consistency", False, "No availability data to compare")
                return False
            
            api_says_available = availability_data.get("available", None)
            api_assigned_to = availability_data.get("assigned_to", None)
            
            database_has_owners = len(users_with_zip) > 0
            
            # Check for consistency
            if api_says_available and database_has_owners:
                # Inconsistency: API says available but database has owners
                success = False
                details = f"🚨 INCONSISTENCY: API says ZIP {self.investigation_zip} is AVAILABLE but database shows {len(users_with_zip)} owner(s): {[u['email'] for u in users_with_zip]}"
            elif not api_says_available and not database_has_owners:
                # Inconsistency: API says taken but no database owners
                success = False
                details = f"🚨 INCONSISTENCY: API says ZIP {self.investigation_zip} is TAKEN (assigned to: {api_assigned_to}) but database shows NO owners"
            elif not api_says_available and database_has_owners:
                # Check if the assigned_to matches database
                db_emails = [u['email'] for u in users_with_zip]
                if api_assigned_to in db_emails:
                    success = True
                    details = f"✅ CONSISTENT: API says TAKEN (assigned to: {api_assigned_to}) and database confirms this user owns the ZIP"
                else:
                    success = False
                    details = f"🚨 INCONSISTENCY: API says TAKEN (assigned to: {api_assigned_to}) but database shows different owners: {db_emails}"
            elif api_says_available and not database_has_owners:
                # Perfect consistency
                success = True
                details = f"✅ CONSISTENT: API says ZIP {self.investigation_zip} is AVAILABLE and database confirms no owners"
            else:
                success = False
                details = f"🚨 UNKNOWN STATE: API available={api_says_available}, assigned_to={api_assigned_to}, DB owners={len(users_with_zip)}"
            
            self.log_test("Availability vs Database Consistency", success, details)
            return success
            
        except Exception as e:
            self.log_test("Availability vs Database Consistency", False, str(e))
            return False

    def run_investigation(self):
        """Run the complete ZIP 30126 investigation"""
        print("🔍 ZIP 30126 INVESTIGATION - Why does it show as 'taken' after cleanup?")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        print(f"\n🎯 INVESTIGATION TARGET: ZIP {self.investigation_zip}")
        print("📋 INVESTIGATION TASKS:")
        print("   1. Check ZIP Availability Response")
        print("   2. Search User Database for ownership")
        print("   3. Check Analysis Data existence")
        print("   4. Test Fresh Registration")
        print("   5. Verify consistency between API and database")
        
        # Task 1: Check ZIP Availability
        print(f"\n🔍 TASK 1: Checking ZIP availability for {self.investigation_zip}...")
        availability_success, availability_data = self.test_zip_availability_check()
        
        # Task 2: Search User Database
        print(f"\n👥 TASK 2: Searching user database for ZIP {self.investigation_zip} ownership...")
        database_success, users_with_zip = self.test_user_database_search()
        
        # Task 3: Check Analysis Data
        print(f"\n📊 TASK 3: Checking analysis data for ZIP {self.investigation_zip}...")
        analysis_success = self.test_analysis_data_check()
        
        # Task 4: Test Fresh Registration
        print(f"\n🆕 TASK 4: Testing fresh user registration with ZIP {self.investigation_zip}...")
        registration_success = self.test_fresh_registration()
        
        # Task 5: Check Consistency
        print(f"\n🔄 TASK 5: Checking consistency between availability API and database...")
        if availability_success and database_success:
            consistency_success = self.test_zip_availability_vs_database_consistency(availability_data, users_with_zip)
        else:
            print("❌ Cannot check consistency - missing availability or database data")
            consistency_success = False
        
        # Summary and Diagnosis
        print("\n" + "=" * 80)
        print("🔍 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        print(f"📊 Tests completed: {self.tests_run}")
        print(f"✅ Tests passed: {self.tests_passed}")
        print(f"❌ Tests failed: {self.tests_run - self.tests_passed}")
        
        # Provide diagnosis
        print(f"\n🩺 DIAGNOSIS FOR ZIP {self.investigation_zip}:")
        
        if availability_data:
            is_available = availability_data.get("available")
            assigned_to = availability_data.get("assigned_to")
            
            if not is_available and assigned_to:
                print(f"🚨 ROOT CAUSE IDENTIFIED: ZIP {self.investigation_zip} shows as TAKEN")
                print(f"   📧 Assigned to: {assigned_to}")
                print(f"   🔍 This explains why users see it as 'taken'")
                
                if users_with_zip:
                    print(f"   ✅ Database confirms: {len(users_with_zip)} user(s) own this ZIP")
                    for user in users_with_zip:
                        print(f"      - {user['email']} ({user['name']}) - Active: {user['is_active']}")
                else:
                    print(f"   ❌ Database inconsistency: No users found with this ZIP")
                    print(f"   💡 SOLUTION: Remove ghost assignment or fix database inconsistency")
            elif is_available:
                print(f"✅ ZIP {self.investigation_zip} shows as AVAILABLE")
                print(f"   💡 If user still sees 'taken', check for caching issues")
            else:
                print(f"❓ Unclear availability status")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not availability_success:
            print("   1. ❌ Fix ZIP availability endpoint - it's not responding correctly")
        
        if users_with_zip:
            print(f"   2. 🧹 Clean up database: Remove ZIP {self.investigation_zip} from these users:")
            for user in users_with_zip:
                print(f"      - {user['email']}")
        
        if not registration_success:
            print("   3. 🔧 Fix territory assignment endpoint - new users cannot claim the ZIP")
        
        if availability_data and not availability_data.get("available"):
            print(f"   4. 🔄 Make ZIP {self.investigation_zip} available by removing current assignment")
        
        print(f"\n🎯 EXPECTED RESULT: ZIP {self.investigation_zip} should show as 'Available' with no assigned user")
        
        return self.tests_passed == self.tests_run

def main():
    investigator = ZIP30126Investigator()
    
    print("🚀 Starting ZIP 30126 Investigation...")
    success = investigator.run_investigation()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())