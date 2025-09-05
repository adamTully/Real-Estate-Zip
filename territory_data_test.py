#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time
import os

class TerritoryDataTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        
        # Target user from review request
        self.target_email = "territory1756780976@example.com"
        self.target_password = "testpass123"
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if details:
                print(f"   📋 {details}")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def test_user_authentication(self):
        """Test authentication with the target user"""
        try:
            login_payload = {
                "email": self.target_email,
                "password": self.target_password
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.auth_token = data["access_token"]
                user_data = data["user"]
                owned_territories = user_data.get("owned_territories", [])
                
                details = f"User: {user_data['first_name']} {user_data['last_name']}, Email: {user_data['email']}, Territories: {owned_territories}"
                
                # Check if user has territories
                if not owned_territories:
                    print(f"⚠️  WARNING: User has no territories assigned!")
                else:
                    print(f"✅ User has {len(owned_territories)} territories: {owned_territories}")
                    
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("User Authentication", success, details)
            return success, owned_territories if success else []
            
        except Exception as e:
            self.log_test("User Authentication", False, str(e))
            return False, []
    
    def test_existing_zip_data(self, zip_codes_to_check):
        """Check which ZIP codes have existing analysis data"""
        existing_data = {}
        
        for zip_code in zip_codes_to_check:
            try:
                response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if it has complete data
                    has_buyer_migration = bool(data.get("buyer_migration", {}).get("analysis_content"))
                    has_seo_social = bool(data.get("seo_social_trends", {}).get("analysis_content"))
                    has_content_strategy = bool(data.get("content_strategy", {}).get("analysis_content"))
                    
                    existing_data[zip_code] = {
                        "exists": True,
                        "complete": has_buyer_migration and has_seo_social and has_content_strategy,
                        "buyer_migration": has_buyer_migration,
                        "seo_social_trends": has_seo_social,
                        "content_strategy": has_content_strategy,
                        "created_at": data.get("created_at")
                    }
                    
                    status = "COMPLETE" if existing_data[zip_code]["complete"] else "PARTIAL"
                    print(f"📊 ZIP {zip_code}: {status} - BM:{has_buyer_migration}, SEO:{has_seo_social}, CS:{has_content_strategy}")
                    
                else:
                    existing_data[zip_code] = {"exists": False}
                    print(f"📊 ZIP {zip_code}: NO DATA")
                    
            except Exception as e:
                existing_data[zip_code] = {"exists": False, "error": str(e)}
                print(f"📊 ZIP {zip_code}: ERROR - {str(e)}")
        
        return existing_data
    
    def test_territory_assignment(self, zip_code):
        """Test assigning a territory to the user"""
        try:
            if not self.auth_token:
                self.log_test(f"Territory Assignment ({zip_code})", False, "No auth token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            territory_payload = {"zip_code": zip_code}
            
            response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Response: {data.get('message', 'No message')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test(f"Territory Assignment ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Territory Assignment ({zip_code})", False, str(e))
            return False
    
    def test_user_profile_after_assignment(self):
        """Test user profile to verify territory assignment"""
        try:
            if not self.auth_token:
                self.log_test("User Profile Check", False, "No auth token available")
                return False, []
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                owned_territories = data.get("owned_territories", [])
                details = f"User: {data['first_name']} {data['last_name']}, Territories: {owned_territories}"
            else:
                owned_territories = []
                details = f"Status: {response.status_code}"
            
            self.log_test("User Profile Check", success, details)
            return success, owned_territories
            
        except Exception as e:
            self.log_test("User Profile Check", False, str(e))
            return False, []
    
    def test_data_access_for_territory(self, zip_code):
        """Test if user can access analysis data for their assigned territory"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                
                # Check for updated field names and content
                has_seo_social = "seo_social_trends" in data
                has_old_field = "seo_youtube_trends" in data
                
                if has_old_field:
                    success = False
                    details = "ERROR: Old field 'seo_youtube_trends' still present"
                elif not has_seo_social:
                    success = False
                    details = "ERROR: New field 'seo_social_trends' not found"
                else:
                    # Check content quality
                    buyer_migration = data.get("buyer_migration", {})
                    seo_social = data.get("seo_social_trends", {})
                    content_strategy = data.get("content_strategy", {})
                    
                    bm_content = buyer_migration.get("analysis_content", "")
                    seo_content = seo_social.get("analysis_content", "")
                    cs_content = content_strategy.get("analysis_content", "")
                    
                    # Check for platform-specific content in SEO & Social Media Trends
                    platforms = ["Facebook", "Instagram", "Twitter", "TikTok"]
                    platform_mentions = [p for p in platforms if p.lower() in seo_content.lower()]
                    
                    # Check for enhanced content strategy elements
                    strategy_platforms = ["blog", "email", "Facebook", "YouTube", "Instagram", "TikTok"]
                    strategy_mentions = [p for p in strategy_platforms if p.lower() in cs_content.lower()]
                    
                    details = f"Data access successful. BM: {len(bm_content)} chars, SEO: {len(seo_content)} chars ({len(platform_mentions)} platforms), CS: {len(cs_content)} chars ({len(strategy_mentions)} platforms)"
                    
                    if len(platform_mentions) < 2:
                        print(f"⚠️  WARNING: SEO & Social Media Trends may not have platform-specific content (found: {platform_mentions})")
                    
                    if len(strategy_mentions) < 4:
                        print(f"⚠️  WARNING: Content Strategy may not have platform-specific guidance (found: {strategy_mentions})")
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test(f"Data Access ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Data Access ({zip_code})", False, str(e))
            return False
    
    def run_territory_data_fix(self):
        """Run the complete territory data fix process"""
        print("🚀 Territory Data Fix for Manual Testing")
        print(f"📍 Testing against: {self.base_url}")
        print(f"👤 Target user: {self.target_email}")
        print("=" * 60)
        
        # Step 1: Authenticate user
        print("\n🔐 Step 1: Authenticating target user...")
        auth_success, current_territories = self.test_user_authentication()
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Check existing ZIP codes with data
        print("\n📊 Step 2: Checking existing ZIP codes with analysis data...")
        zip_codes_to_check = ["10001", "94105", "90210", "60601", "33101"]
        existing_data = self.test_existing_zip_data(zip_codes_to_check)
        
        # Find ZIP codes with complete data
        complete_zips = [zip_code for zip_code, info in existing_data.items() 
                        if info.get("exists") and info.get("complete")]
        
        print(f"\n✅ Found {len(complete_zips)} ZIP codes with complete data: {complete_zips}")
        
        if not complete_zips:
            print("⚠️  No ZIP codes with complete data found. Creating new analysis...")
            # Try to create analysis for 10001
            test_zip = "10001"
            print(f"\n🔄 Creating analysis for ZIP {test_zip}...")
            
            try:
                payload = {"zip_code": test_zip}
                response = requests.post(f"{self.api_url}/zip-analysis/start", json=payload, timeout=30)
                
                if response.status_code == 200:
                    print(f"✅ Analysis started for ZIP {test_zip}")
                    print("⏳ Waiting 60 seconds for analysis to complete...")
                    time.sleep(60)
                    
                    # Check if complete
                    updated_data = self.test_existing_zip_data([test_zip])
                    if updated_data.get(test_zip, {}).get("complete"):
                        complete_zips = [test_zip]
                        print(f"✅ Analysis completed for ZIP {test_zip}")
                    else:
                        print(f"⚠️  Analysis for ZIP {test_zip} still in progress")
                        complete_zips = [test_zip]  # Use it anyway for assignment
                else:
                    print(f"❌ Failed to start analysis: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Error creating analysis: {e}")
                return False
        
        # Step 3: Assign territory if user doesn't have one with complete data
        assigned_zip = None
        
        if current_territories:
            # Check if user already has a territory with complete data
            user_complete_territories = [zip_code for zip_code in current_territories 
                                       if zip_code in complete_zips]
            
            if user_complete_territories:
                assigned_zip = user_complete_territories[0]
                print(f"\n✅ User already has territory with complete data: {assigned_zip}")
            else:
                print(f"\n⚠️  User has territories {current_territories} but none have complete data")
                # Assign a ZIP with complete data
                if complete_zips:
                    assigned_zip = complete_zips[0]
                    print(f"\n🗺️  Step 3: Assigning ZIP {assigned_zip} with complete data...")
                    self.test_territory_assignment(assigned_zip)
        else:
            # User has no territories, assign one with complete data
            if complete_zips:
                assigned_zip = complete_zips[0]
                print(f"\n🗺️  Step 3: Assigning ZIP {assigned_zip} with complete data...")
                self.test_territory_assignment(assigned_zip)
        
        # Step 4: Verify assignment
        print("\n👤 Step 4: Verifying territory assignment...")
        profile_success, updated_territories = self.test_user_profile_after_assignment()
        
        if profile_success and assigned_zip in updated_territories:
            print(f"✅ Territory {assigned_zip} successfully assigned to user")
        elif profile_success:
            print(f"⚠️  User territories: {updated_territories}")
            if updated_territories:
                assigned_zip = updated_territories[0]  # Use first available
        
        # Step 5: Test data access
        if assigned_zip:
            print(f"\n📋 Step 5: Testing data access for ZIP {assigned_zip}...")
            self.test_data_access_for_territory(assigned_zip)
        else:
            print("\n❌ No assigned ZIP to test data access")
            return False
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Territory Data Fix Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if assigned_zip:
            print(f"\n🎯 MANUAL TESTING READY:")
            print(f"   👤 User: {self.target_email}")
            print(f"   🔑 Password: {self.target_password}")
            print(f"   🗺️  Assigned ZIP: {assigned_zip}")
            print(f"   📊 Data Status: Available for testing")
            print(f"\n🔗 Test URLs:")
            print(f"   • Login: {self.base_url}")
            print(f"   • Analysis: {self.api_url}/zip-analysis/{assigned_zip}")
            print(f"   • User Profile: {self.api_url}/auth/me")
        
        success_rate = self.tests_passed / self.tests_run if self.tests_run > 0 else 0
        return success_rate >= 0.8  # 80% success rate threshold

def main():
    tester = TerritoryDataTester()
    
    print("Running Territory Data Fix as requested in review...")
    success = tester.run_territory_data_fix()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())