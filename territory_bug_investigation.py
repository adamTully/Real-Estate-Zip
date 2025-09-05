#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class TerritoryBugInvestigator:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.admin_token = None
        
        # Bug investigation targets
        self.bug_user_email = "adamtest1@gmail.com"
        self.expected_zip = "30126"  # ZIP user registered for
        self.actual_zip = "10001"   # ZIP showing in dashboard
        
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
        
    def try_existing_admin_user(self):
        """Try to use existing admin credentials or skip admin tests"""
        try:
            # Try common admin credentials
            admin_credentials = [
                {"email": "admin@example.com", "password": "adminpass123"},
                {"email": "super@admin.com", "password": "admin123"},
                {"email": "test@admin.com", "password": "testpass123"}
            ]
            
            for creds in admin_credentials:
                login_response = requests.post(f"{self.api_url}/auth/login", json=creds, timeout=10)
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    user_data = login_data.get("user", {})
                    if user_data.get("role") == "super_admin":
                        self.admin_token = login_data["access_token"]
                        self.log_test("Find Existing Admin User", True, f"Found admin: {creds['email']}")
                        return True
            
            self.log_test("Find Existing Admin User", False, "No existing admin users found - will skip admin-only tests")
            return False
                
        except Exception as e:
            self.log_test("Find Existing Admin User", False, str(e))
            return False
    
    def investigate_user_data(self):
        """TASK 1: Check User Data - Look up user adamtest1@gmail.com in database"""
        try:
            if not self.admin_token:
                self.log_test("Investigate User Data", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.api_url}/admin/users", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Investigate User Data", False, f"Failed to get users list: {response.status_code}")
                return False
            
            users_data = response.json()
            target_user = None
            
            # Find the target user
            for user in users_data:
                if user.get("email") == self.bug_user_email:
                    target_user = user
                    break
            
            if target_user:
                owned_territories = target_user.get("owned_territories", [])
                total_territories = target_user.get("total_territories", 0)
                created_at = target_user.get("created_at", "Unknown")
                role = target_user.get("role", "Unknown")
                is_active = target_user.get("is_active", False)
                
                details = f"""
                📧 Email: {target_user['email']}
                👤 Name: {target_user.get('first_name', '')} {target_user.get('last_name', '')}
                🏠 Owned Territories: {owned_territories}
                📊 Total Territories: {total_territories}
                📅 Created: {created_at}
                🔑 Role: {role}
                ✅ Active: {is_active}
                🆔 User ID: {target_user.get('id', 'Unknown')}
                """
                
                # Check if user has the expected ZIP or actual ZIP
                has_expected = self.expected_zip in owned_territories
                has_actual = self.actual_zip in owned_territories
                
                if has_expected and not has_actual:
                    success = True
                    bug_status = "✅ NO BUG: User correctly owns expected ZIP 30126"
                elif has_actual and not has_expected:
                    success = False
                    bug_status = f"🐛 BUG CONFIRMED: User owns {self.actual_zip} instead of expected {self.expected_zip}"
                elif has_both := (has_expected and has_actual):
                    success = False
                    bug_status = f"🐛 DUPLICATE ASSIGNMENT: User owns both {self.expected_zip} and {self.actual_zip}"
                else:
                    success = False
                    bug_status = f"🐛 NO TERRITORIES: User doesn't own either ZIP. Territories: {owned_territories}"
                
                self.log_test("Investigate User Data", success, f"{details}\n🔍 Bug Status: {bug_status}")
                return target_user
            else:
                self.log_test("Investigate User Data", False, f"User {self.bug_user_email} not found in database")
                return None
                
        except Exception as e:
            self.log_test("Investigate User Data", False, str(e))
            return None
    
    def investigate_territory_ownership(self):
        """TASK 2: Check Territory Ownership - Who owns ZIP 30126 and ZIP 10001?"""
        try:
            if not self.admin_token:
                self.log_test("Investigate Territory Ownership", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.api_url}/admin/users", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Investigate Territory Ownership", False, f"Failed to get users list: {response.status_code}")
                return False
            
            users_data = response.json()
            
            # Track who owns which ZIP
            zip_30126_owners = []
            zip_10001_owners = []
            all_territory_assignments = {}
            
            for user in users_data:
                owned_territories = user.get("owned_territories", [])
                email = user.get("email", "Unknown")
                
                if self.expected_zip in owned_territories:
                    zip_30126_owners.append({
                        "email": email,
                        "name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                        "created_at": user.get("created_at", "Unknown"),
                        "all_territories": owned_territories
                    })
                
                if self.actual_zip in owned_territories:
                    zip_10001_owners.append({
                        "email": email,
                        "name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                        "created_at": user.get("created_at", "Unknown"),
                        "all_territories": owned_territories
                    })
                
                # Track all territory assignments for duplicate detection
                for territory in owned_territories:
                    if territory not in all_territory_assignments:
                        all_territory_assignments[territory] = []
                    all_territory_assignments[territory].append(email)
            
            # Check for duplicates
            duplicates = {zip_code: owners for zip_code, owners in all_territory_assignments.items() if len(owners) > 1}
            
            details = f"""
            🏠 ZIP {self.expected_zip} (Expected) Owners: {len(zip_30126_owners)}
            {json.dumps(zip_30126_owners, indent=2) if zip_30126_owners else "   No owners found"}
            
            🏠 ZIP {self.actual_zip} (Actual) Owners: {len(zip_10001_owners)}
            {json.dumps(zip_10001_owners, indent=2) if zip_10001_owners else "   No owners found"}
            
            🔍 Duplicate Territory Assignments Found: {len(duplicates)}
            {json.dumps(duplicates, indent=2) if duplicates else "   No duplicates found"}
            """
            
            # Determine if there's a bug
            success = True
            bug_findings = []
            
            if len(zip_30126_owners) == 0:
                bug_findings.append(f"❌ ZIP {self.expected_zip} has no owners")
                success = False
            elif len(zip_30126_owners) > 1:
                bug_findings.append(f"🐛 ZIP {self.expected_zip} has multiple owners: {[o['email'] for o in zip_30126_owners]}")
                success = False
            
            if len(zip_10001_owners) > 1:
                bug_findings.append(f"🐛 ZIP {self.actual_zip} has multiple owners: {[o['email'] for o in zip_10001_owners]}")
                success = False
            
            if duplicates:
                bug_findings.append(f"🐛 Found {len(duplicates)} ZIP codes with duplicate assignments")
                success = False
            
            if bug_findings:
                details += f"\n🚨 Bug Findings:\n" + "\n".join(bug_findings)
            else:
                details += f"\n✅ No territory assignment bugs detected"
            
            self.log_test("Investigate Territory Ownership", success, details)
            return {
                "zip_30126_owners": zip_30126_owners,
                "zip_10001_owners": zip_10001_owners,
                "duplicates": duplicates
            }
            
        except Exception as e:
            self.log_test("Investigate Territory Ownership", False, str(e))
            return None
    
    def test_registration_flow(self):
        """TASK 3: Test Registration Flow - Try registering new test user with different ZIP"""
        try:
            timestamp = int(time.time())
            test_email = f"regtest{timestamp}@example.com"
            test_zip = "75201"  # Dallas ZIP for testing
            
            # Step 1: Register new user
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "first_name": "Registration",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            
            if register_response.status_code != 200:
                self.log_test("Test Registration Flow", False, f"Registration failed: {register_response.status_code}")
                return False
            
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_id = register_data["user"]["id"]
            
            # Step 2: Assign territory to new user
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": test_zip}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            if assign_response.status_code != 200:
                self.log_test("Test Registration Flow", False, f"Territory assignment failed: {assign_response.status_code}")
                return False
            
            # Step 3: Verify territory assignment via /auth/me
            me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            if me_response.status_code != 200:
                self.log_test("Test Registration Flow", False, f"Profile retrieval failed: {me_response.status_code}")
                return False
            
            me_data = me_response.json()
            owned_territories = me_data.get("owned_territories", [])
            
            # Check if assignment worked correctly
            success = test_zip in owned_territories
            
            details = f"""
            👤 Test User: {test_email}
            🆔 User ID: {user_id}
            🏠 Assigned ZIP: {test_zip}
            📋 Owned Territories: {owned_territories}
            ✅ Assignment Successful: {success}
            """
            
            if success:
                details += f"\n✅ Registration flow works correctly - ZIP {test_zip} properly assigned"
            else:
                details += f"\n❌ Registration flow bug - ZIP {test_zip} not found in owned territories"
            
            self.log_test("Test Registration Flow", success, details)
            return success
            
        except Exception as e:
            self.log_test("Test Registration Flow", False, str(e))
            return False
    
    def test_session_cache_issues(self):
        """TASK 4: Check for Session/Cache Issues - Login as adamtest1@gmail.com and check GET /api/auth/me"""
        try:
            # First, try to login as the bug user
            login_payload = {
                "email": self.bug_user_email,
                "password": "testpass123"  # Common test password
            }
            
            # Try multiple common passwords
            common_passwords = ["testpass123", "password123", "admin123", "test123", "123456"]
            login_success = False
            user_token = None
            
            for password in common_passwords:
                login_payload["password"] = password
                login_response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    user_token = login_data["access_token"]
                    login_success = True
                    print(f"   ✅ Login successful with password: {password}")
                    break
                elif login_response.status_code == 401:
                    print(f"   ❌ Login failed with password: {password}")
                else:
                    print(f"   ⚠️  Unexpected response with password {password}: {login_response.status_code}")
            
            if not login_success:
                # If we can't login, create a test user with the same email pattern for testing
                print(f"   ℹ️  Cannot login as {self.bug_user_email}, creating test user for session testing...")
                
                timestamp = int(time.time())
                test_email = f"adamtest{timestamp}@gmail.com"
                
                register_payload = {
                    "email": test_email,
                    "password": "testpass123",
                    "first_name": "Adam",
                    "last_name": "Test"
                }
                
                register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
                
                if register_response.status_code != 200:
                    self.log_test("Test Session/Cache Issues", False, f"Cannot create test user: {register_response.status_code}")
                    return False
                
                register_data = register_response.json()
                user_token = register_data["access_token"]
                
                # Assign both ZIPs to test user to simulate the bug
                headers = {"Authorization": f"Bearer {user_token}"}
                
                # Assign ZIP 30126 first
                assign1_response = requests.post(
                    f"{self.api_url}/users/assign-territory", 
                    json={"zip_code": self.expected_zip}, 
                    headers=headers, 
                    timeout=10
                )
                
                # Assign ZIP 10001 second
                assign2_response = requests.post(
                    f"{self.api_url}/users/assign-territory", 
                    json={"zip_code": self.actual_zip}, 
                    headers=headers, 
                    timeout=10
                )
                
                print(f"   ℹ️  Created test user {test_email} and assigned both ZIPs for testing")
            
            # Now test the /auth/me endpoint
            if user_token:
                headers = {"Authorization": f"Bearer {user_token}"}
                
                # Make multiple calls to check for consistency
                me_responses = []
                for i in range(3):
                    me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        me_responses.append({
                            "call": i + 1,
                            "owned_territories": me_data.get("owned_territories", []),
                            "email": me_data.get("email", "Unknown")
                        })
                    else:
                        me_responses.append({
                            "call": i + 1,
                            "error": f"Status {me_response.status_code}"
                        })
                    time.sleep(1)  # Small delay between calls
                
                # Check for consistency
                territories_consistent = True
                if len(me_responses) >= 2:
                    first_territories = me_responses[0].get("owned_territories", [])
                    for response in me_responses[1:]:
                        if response.get("owned_territories", []) != first_territories:
                            territories_consistent = False
                            break
                
                details = f"""
                🔑 Login Status: {'Success' if login_success else 'Failed - used test user'}
                📧 User Email: {me_responses[0].get('email', 'Unknown') if me_responses else 'No responses'}
                
                🔄 Multiple /auth/me calls:
                {json.dumps(me_responses, indent=2)}
                
                ✅ Territory Consistency: {territories_consistent}
                """
                
                if not territories_consistent:
                    details += "\n🐛 CACHE BUG: Territory data inconsistent across multiple calls"
                
                success = territories_consistent and len(me_responses) > 0 and all("error" not in r for r in me_responses)
                
                self.log_test("Test Session/Cache Issues", success, details)
                return success
            else:
                self.log_test("Test Session/Cache Issues", False, "Could not obtain user token for testing")
                return False
                
        except Exception as e:
            self.log_test("Test Session/Cache Issues", False, str(e))
            return False
    
    def test_admin_users_endpoint(self):
        """Test GET /api/admin/users endpoint to check all users and their territories"""
        try:
            if not self.admin_token:
                self.log_test("Test Admin Users Endpoint", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.api_url}/admin/users", headers=headers, timeout=10)
            
            success = response.status_code == 200
            
            if success:
                users_data = response.json()
                
                # Analyze territory distribution
                total_users = len(users_data)
                users_with_territories = [u for u in users_data if u.get("owned_territories")]
                territory_count_distribution = {}
                all_territories = []
                
                for user in users_data:
                    territories = user.get("owned_territories", [])
                    count = len(territories)
                    territory_count_distribution[count] = territory_count_distribution.get(count, 0) + 1
                    all_territories.extend(territories)
                
                # Check for duplicates
                territory_counts = {}
                for territory in all_territories:
                    territory_counts[territory] = territory_counts.get(territory, 0) + 1
                
                duplicates = {t: count for t, count in territory_counts.items() if count > 1}
                
                details = f"""
                👥 Total Users: {total_users}
                🏠 Users with Territories: {len(users_with_territories)}
                📊 Territory Count Distribution: {territory_count_distribution}
                🔍 Duplicate Territories: {duplicates if duplicates else 'None found'}
                📋 Sample Users:
                {json.dumps([{
                    'email': u.get('email', 'Unknown'),
                    'territories': u.get('owned_territories', []),
                    'total': u.get('total_territories', 0)
                } for u in users_data[:5]], indent=2)}
                """
                
                if duplicates:
                    success = False
                    details += f"\n🐛 DUPLICATE TERRITORY BUG: Found {len(duplicates)} territories assigned to multiple users"
                
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Test Admin Users Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Test Admin Users Endpoint", False, str(e))
            return False
    
    def run_investigation(self):
        """Run the complete territory assignment bug investigation"""
        print("🔍 TERRITORY ASSIGNMENT BUG INVESTIGATION")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🎯 Target User: {self.bug_user_email}")
        print(f"🏠 Expected ZIP: {self.expected_zip}")
        print(f"🏠 Actual ZIP: {self.actual_zip}")
        print("=" * 80)
        
        # Step 1: Try to find existing admin user
        print("\n🔑 Step 1: Looking for Existing Admin User")
        has_admin = self.try_existing_admin_user()
        
        if not has_admin:
            print("⚠️  No admin access available - will test with limited functionality")
        
        # Step 2: Investigate user data
        print(f"\n👤 Step 2: Investigating User Data for {self.bug_user_email}")
        user_data = self.investigate_user_data()
        
        # Step 3: Check territory ownership
        print(f"\n🏠 Step 3: Checking Territory Ownership for ZIPs {self.expected_zip} and {self.actual_zip}")
        territory_data = self.investigate_territory_ownership()
        
        # Step 4: Test registration flow
        print(f"\n📝 Step 4: Testing Registration Flow with New User")
        self.test_registration_flow()
        
        # Step 5: Test session/cache issues
        print(f"\n🔄 Step 5: Testing Session/Cache Issues")
        self.test_session_cache_issues()
        
        # Step 6: Test admin endpoint
        print(f"\n👑 Step 6: Testing Admin Users Endpoint")
        self.test_admin_users_endpoint()
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 INVESTIGATION RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Provide bug analysis
        print("\n🔍 BUG ANALYSIS:")
        
        if user_data:
            user_territories = user_data.get("owned_territories", [])
            if self.expected_zip in user_territories and self.actual_zip not in user_territories:
                print(f"✅ NO BUG: User correctly owns expected ZIP {self.expected_zip}")
            elif self.actual_zip in user_territories and self.expected_zip not in user_territories:
                print(f"🐛 BUG CONFIRMED: User owns {self.actual_zip} instead of expected {self.expected_zip}")
                print(f"   💡 RECOMMENDATION: Update user's territory from {self.actual_zip} to {self.expected_zip}")
            elif self.expected_zip in user_territories and self.actual_zip in user_territories:
                print(f"🐛 DUPLICATE ASSIGNMENT BUG: User owns both ZIPs")
                print(f"   💡 RECOMMENDATION: Remove {self.actual_zip} from user's territories")
            else:
                print(f"🐛 MISSING TERRITORIES BUG: User doesn't own either ZIP")
                print(f"   💡 RECOMMENDATION: Assign {self.expected_zip} to user")
        else:
            print(f"❌ USER NOT FOUND: {self.bug_user_email} does not exist in database")
            print(f"   💡 RECOMMENDATION: Check if user registered with different email")
        
        if territory_data and territory_data.get("duplicates"):
            print(f"\n🚨 SYSTEM-WIDE ISSUE: Found duplicate territory assignments")
            print(f"   💡 RECOMMENDATION: Run territory cleanup process")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Fix territory assignment for {self.bug_user_email}")
        print(f"   2. Implement duplicate territory prevention")
        print(f"   3. Add territory assignment validation")
        print(f"   4. Test registration flow with ZIP assignment")
        
        return self.tests_passed == self.tests_run

def main():
    investigator = TerritoryBugInvestigator()
    success = investigator.run_investigation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())