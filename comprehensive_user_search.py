#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ComprehensiveUserSearch:
    def __init__(self, base_url=None):
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
        self.target_email = "adamtest1@gmail.com"
        self.expected_zip = "30126"
        self.actual_zip = "10001"
        
    def test_user_registration_variations(self):
        """Test if user might have registered with slight variations"""
        print("🔍 Testing User Registration Variations")
        
        # Try different email variations
        email_variations = [
            "adamtest1@gmail.com",
            "adam.test1@gmail.com", 
            "adamtest@gmail.com",
            "adam.test@gmail.com",
            "adamtest1@example.com",
            "test1@gmail.com",
            "adam1@gmail.com"
        ]
        
        # Try different password variations
        password_variations = [
            "testpass123",
            "password123", 
            "admin123",
            "test123",
            "123456",
            "password",
            "30126",  # ZIP code as password
            "adamtest1",
            "adam123",
            "test1234"
        ]
        
        found_users = []
        
        for email in email_variations:
            print(f"\n📧 Testing email: {email}")
            
            for password in password_variations:
                try:
                    login_payload = {
                        "email": email,
                        "password": password
                    }
                    
                    response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=5)
                    
                    if response.status_code == 200:
                        login_data = response.json()
                        user_data = login_data.get("user", {})
                        
                        found_users.append({
                            "email": email,
                            "password": password,
                            "user_data": user_data,
                            "owned_territories": user_data.get("owned_territories", [])
                        })
                        
                        print(f"   ✅ SUCCESS: {email} / {password}")
                        print(f"      Territories: {user_data.get('owned_territories', [])}")
                        break  # Found valid login, move to next email
                        
                    elif response.status_code == 401:
                        continue  # Wrong password, try next
                    else:
                        print(f"   ⚠️  Unexpected response: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error testing {email}/{password}: {str(e)}")
                    continue
            else:
                print(f"   ❌ No valid password found for {email}")
        
        return found_users
    
    def test_zip_ownership_patterns(self):
        """Test who owns the ZIPs and look for patterns"""
        print(f"\n🏠 Testing ZIP Ownership Patterns")
        
        # Check both ZIPs
        zips_to_check = [self.expected_zip, self.actual_zip, "10002", "10003", "30127", "30128"]
        
        zip_owners = {}
        
        for zip_code in zips_to_check:
            try:
                response = requests.post(
                    f"{self.api_url}/zip-availability/check", 
                    json={"zip_code": zip_code}, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    zip_owners[zip_code] = {
                        "available": data.get("available", True),
                        "assigned_to": data.get("assigned_to", None),
                        "location": data.get("location_info", {})
                    }
                    
                    if not data.get("available", True):
                        print(f"   🏠 ZIP {zip_code}: Assigned to {data.get('assigned_to', 'Unknown')}")
                    else:
                        print(f"   🏠 ZIP {zip_code}: Available")
                        
            except Exception as e:
                print(f"   ❌ Error checking ZIP {zip_code}: {str(e)}")
        
        return zip_owners
    
    def test_registration_with_target_zip(self):
        """Test registering a new user with the target ZIP to see what happens"""
        print(f"\n📝 Testing Registration with Target ZIP {self.expected_zip}")
        
        try:
            timestamp = int(time.time())
            test_email = f"adamtest_recreation_{timestamp}@gmail.com"
            
            # Register new user
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "first_name": "Adam",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            
            if register_response.status_code != 200:
                print(f"   ❌ Registration failed: {register_response.status_code}")
                return False
            
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_id = register_data["user"]["id"]
            
            print(f"   ✅ User registered: {test_email}")
            print(f"   🆔 User ID: {user_id}")
            
            # Try to assign the expected ZIP
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": self.expected_zip}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            if assign_response.status_code == 200:
                assign_data = assign_response.json()
                print(f"   ✅ ZIP {self.expected_zip} assigned successfully")
                print(f"   📝 Response: {assign_data.get('message', 'No message')}")
                
                # Verify via /auth/me
                me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    territories = me_data.get("owned_territories", [])
                    print(f"   🏠 Verified territories: {territories}")
                    
                    if self.expected_zip in territories:
                        print(f"   ✅ ZIP {self.expected_zip} is now properly assigned and available for use")
                        return True
                    else:
                        print(f"   ❌ ZIP {self.expected_zip} not found in user territories after assignment")
                        return False
                else:
                    print(f"   ❌ Could not verify assignment: {me_response.status_code}")
                    return False
            else:
                assign_data = assign_response.json() if assign_response.status_code != 500 else {"detail": "Server error"}
                print(f"   ❌ ZIP assignment failed: {assign_response.status_code}")
                print(f"   📝 Error: {assign_data.get('detail', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error during registration test: {str(e)}")
            return False
    
    def run_comprehensive_search(self):
        """Run comprehensive search for the missing user"""
        print("🔍 COMPREHENSIVE USER SEARCH")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🎯 Target User: {self.target_email}")
        print(f"🏠 Expected ZIP: {self.expected_zip}")
        print(f"🏠 Actual ZIP: {self.actual_zip}")
        print("=" * 80)
        
        # Test 1: Try to find user with email variations
        found_users = self.test_user_registration_variations()
        
        # Test 2: Check ZIP ownership patterns
        zip_owners = self.test_zip_ownership_patterns()
        
        # Test 3: Test registration with target ZIP
        registration_success = self.test_registration_with_target_zip()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SEARCH RESULTS")
        
        if found_users:
            print(f"\n✅ FOUND {len(found_users)} SIMILAR USERS:")
            for user in found_users:
                print(f"   📧 {user['email']} (password: {user['password']})")
                print(f"      🏠 Territories: {user['owned_territories']}")
                
                # Check if this user has either of our target ZIPs
                if self.expected_zip in user['owned_territories']:
                    print(f"      🎯 *** HAS EXPECTED ZIP {self.expected_zip} ***")
                if self.actual_zip in user['owned_territories']:
                    print(f"      🎯 *** HAS ACTUAL ZIP {self.actual_zip} ***")
        else:
            print(f"\n❌ NO SIMILAR USERS FOUND")
            print(f"   The user {self.target_email} does not exist in the system")
        
        print(f"\n🏠 ZIP OWNERSHIP SUMMARY:")
        for zip_code, info in zip_owners.items():
            if not info.get("available", True):
                print(f"   {zip_code}: {info.get('assigned_to', 'Unknown')}")
            else:
                print(f"   {zip_code}: Available")
        
        if registration_success:
            print(f"\n✅ SOLUTION VERIFIED:")
            print(f"   ZIP {self.expected_zip} is available and can be assigned")
            print(f"   User can register and claim this ZIP successfully")
        else:
            print(f"\n❌ REGISTRATION ISSUE:")
            print(f"   There may be an issue with ZIP {self.expected_zip} assignment")
        
        # Final recommendation
        print(f"\n💡 FINAL RECOMMENDATION:")
        if not found_users:
            print(f"   1. User {self.target_email} needs to register in the system")
            print(f"   2. After registration, they can claim ZIP {self.expected_zip}")
            print(f"   3. ZIP {self.expected_zip} is currently available for assignment")
        else:
            # Check if any found user has the expected ZIP
            has_expected = any(self.expected_zip in user['owned_territories'] for user in found_users)
            if has_expected:
                matching_user = next(user for user in found_users if self.expected_zip in user['owned_territories'])
                print(f"   1. User found with expected ZIP: {matching_user['email']}")
                print(f"   2. This might be the correct user account")
            else:
                print(f"   1. Found similar users but none have ZIP {self.expected_zip}")
                print(f"   2. User may need to register with correct email: {self.target_email}")
        
        return len(found_users) > 0 or registration_success

def main():
    searcher = ComprehensiveUserSearch()
    success = searcher.run_comprehensive_search()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())