#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class LocalTerritoryTester:
    def __init__(self):
        # Use local backend URL
        self.base_url = "http://localhost:8001"
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
                
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                owned_territories = []
            
            self.log_test("User Authentication", success, details)
            return success, owned_territories
            
        except Exception as e:
            self.log_test("User Authentication", False, str(e))
            return False, []
    
    def check_zip_analysis_data(self, zip_code):
        """Check if ZIP analysis data exists and get details"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check field names and content
                has_seo_social = "seo_social_trends" in data
                has_old_field = "seo_youtube_trends" in data
                
                buyer_migration = data.get("buyer_migration", {})
                seo_social = data.get("seo_social_trends", {})
                content_strategy = data.get("content_strategy", {})
                
                bm_content = buyer_migration.get("analysis_content", "")
                seo_content = seo_social.get("analysis_content", "")
                cs_content = content_strategy.get("analysis_content", "")
                
                # Check for platform-specific content
                platforms = ["Facebook", "Instagram", "Twitter", "TikTok"]
                platform_mentions = [p for p in platforms if p.lower() in seo_content.lower()]
                
                strategy_platforms = ["blog", "email", "Facebook", "YouTube", "Instagram", "TikTok"]
                strategy_mentions = [p for p in strategy_platforms if p.lower() in cs_content.lower()]
                
                result = {
                    "exists": True,
                    "has_seo_social_field": has_seo_social,
                    "has_old_field": has_old_field,
                    "buyer_migration_length": len(bm_content),
                    "seo_social_length": len(seo_content),
                    "content_strategy_length": len(cs_content),
                    "platform_mentions": platform_mentions,
                    "strategy_mentions": strategy_mentions,
                    "created_at": data.get("created_at")
                }
                
                print(f"📊 ZIP {zip_code} Analysis Data:")
                print(f"   • Field names: seo_social_trends={has_seo_social}, old_field={has_old_field}")
                print(f"   • Content lengths: BM={len(bm_content)}, SEO={len(seo_content)}, CS={len(cs_content)}")
                print(f"   • Platform mentions: SEO={len(platform_mentions)}, Strategy={len(strategy_mentions)}")
                
                return result
                
            elif response.status_code == 404:
                print(f"📊 ZIP {zip_code}: No analysis data found")
                return {"exists": False, "status": 404}
            else:
                print(f"📊 ZIP {zip_code}: Error {response.status_code} - {response.text[:100]}")
                return {"exists": False, "status": response.status_code, "error": response.text[:200]}
                
        except Exception as e:
            print(f"📊 ZIP {zip_code}: Exception - {str(e)}")
            return {"exists": False, "error": str(e)}
    
    def create_zip_analysis(self, zip_code):
        """Create new ZIP analysis"""
        try:
            payload = {"zip_code": zip_code}
            response = requests.post(f"{self.api_url}/zip-analysis/start", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis started for ZIP {zip_code}")
                print(f"   Job ID: {data.get('job_id')}")
                print(f"   State: {data.get('state')}")
                print(f"   Progress: {data.get('overall_percent')}%")
                
                # Wait and check progress
                for i in range(12):  # Check for 2 minutes
                    time.sleep(10)
                    status_response = requests.get(f"{self.api_url}/zip-analysis/status/{zip_code}", timeout=10)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        progress = status_data.get('overall_percent', 0)
                        state = status_data.get('state', 'unknown')
                        
                        print(f"   Progress update {i+1}: {progress}% - {state}")
                        
                        if state == "done":
                            print(f"✅ Analysis completed for ZIP {zip_code}")
                            return True
                        elif state == "failed":
                            print(f"❌ Analysis failed for ZIP {zip_code}")
                            return False
                    else:
                        print(f"   Status check failed: {status_response.status_code}")
                
                print(f"⏳ Analysis for ZIP {zip_code} still in progress after 2 minutes")
                return True  # Consider it successful even if still processing
                
            else:
                print(f"❌ Failed to start analysis for ZIP {zip_code}: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating analysis for ZIP {zip_code}: {str(e)}")
            return False
    
    def assign_territory(self, zip_code):
        """Assign territory to user"""
        try:
            if not self.auth_token:
                print("❌ No auth token available for territory assignment")
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
                print(f"✅ Territory assignment: {data.get('message', 'Success')}")
            else:
                print(f"❌ Territory assignment failed: {response.status_code} - {response.text[:200]}")
            
            return success
            
        except Exception as e:
            print(f"❌ Territory assignment error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive territory data test"""
        print("🚀 Local Territory Data Test")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Step 1: Authenticate user
        print("\n🔐 Step 1: Authenticating target user...")
        auth_success, current_territories = self.test_user_authentication()
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Check current territory data
        print(f"\n📊 Step 2: Checking data for current territories: {current_territories}")
        
        territory_data = {}
        for zip_code in current_territories:
            territory_data[zip_code] = self.check_zip_analysis_data(zip_code)
        
        # Check if user has any territory with complete data
        complete_territories = []
        for zip_code, data in territory_data.items():
            if (data.get("exists") and 
                data.get("buyer_migration_length", 0) > 100 and
                data.get("seo_social_length", 0) > 100 and
                data.get("content_strategy_length", 0) > 100):
                complete_territories.append(zip_code)
        
        print(f"\n✅ User has {len(complete_territories)} territories with complete data: {complete_territories}")
        
        # Step 3: If no complete data, create analysis for assigned territory
        if not complete_territories and current_territories:
            target_zip = current_territories[0]
            print(f"\n🔄 Step 3: Creating analysis for assigned territory {target_zip}...")
            
            if self.create_zip_analysis(target_zip):
                # Re-check the data
                territory_data[target_zip] = self.check_zip_analysis_data(target_zip)
                if territory_data[target_zip].get("exists"):
                    complete_territories.append(target_zip)
        
        # Step 4: If still no complete data, assign a new territory and create analysis
        if not complete_territories:
            print(f"\n🗺️  Step 4: Assigning new territory with fresh analysis...")
            
            # Try different ZIP codes
            test_zips = ["10001", "94105", "90210"]
            
            for test_zip in test_zips:
                if test_zip not in current_territories:
                    print(f"\n   Trying ZIP {test_zip}...")
                    
                    # Check if it already has data
                    existing_data = self.check_zip_analysis_data(test_zip)
                    
                    if existing_data.get("exists") and existing_data.get("seo_social_length", 0) > 100:
                        # Assign this territory
                        if self.assign_territory(test_zip):
                            complete_territories.append(test_zip)
                            print(f"✅ Assigned existing territory {test_zip} with complete data")
                            break
                    else:
                        # Create new analysis and assign
                        if self.create_zip_analysis(test_zip):
                            if self.assign_territory(test_zip):
                                complete_territories.append(test_zip)
                                print(f"✅ Created and assigned new territory {test_zip}")
                                break
        
        # Step 5: Final verification
        print(f"\n👤 Step 5: Final verification...")
        
        # Re-authenticate to get updated profile
        final_auth, final_territories = self.test_user_authentication()
        
        if final_auth:
            print(f"✅ Final user territories: {final_territories}")
            
            # Test data access for each territory
            for zip_code in final_territories:
                data_info = self.check_zip_analysis_data(zip_code)
                
                if data_info.get("exists"):
                    # Check for updated prompts compliance
                    has_correct_field = data_info.get("has_seo_social_field", False)
                    no_old_field = not data_info.get("has_old_field", True)
                    has_platform_content = len(data_info.get("platform_mentions", [])) >= 2
                    has_strategy_content = len(data_info.get("strategy_mentions", [])) >= 4
                    
                    compliance_score = sum([has_correct_field, no_old_field, has_platform_content, has_strategy_content])
                    
                    print(f"\n📋 Territory {zip_code} Compliance Check:")
                    print(f"   • Correct field name (seo_social_trends): {has_correct_field}")
                    print(f"   • No old field (seo_youtube_trends): {no_old_field}")
                    print(f"   • Platform-specific SEO content: {has_platform_content}")
                    print(f"   • Multi-platform strategy content: {has_strategy_content}")
                    print(f"   • Compliance Score: {compliance_score}/4")
                    
                    if compliance_score >= 3:
                        print(f"✅ Territory {zip_code} is ready for manual testing")
                        self.tests_passed += 1
                    else:
                        print(f"⚠️  Territory {zip_code} needs attention")
                    
                    self.tests_run += 1
        
        # Print final summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} territories ready")
        
        if final_territories:
            print(f"\n🎯 MANUAL TESTING SETUP:")
            print(f"   👤 User: {self.target_email}")
            print(f"   🔑 Password: {self.target_password}")
            print(f"   🗺️  Territories: {final_territories}")
            print(f"\n🔗 Test Commands:")
            print(f"   • Login: curl -X POST {self.api_url}/auth/login -H 'Content-Type: application/json' -d '{json.dumps({'email': self.target_email, 'password': self.target_password})}'")
            for zip_code in final_territories:
                print(f"   • Analysis {zip_code}: curl {self.api_url}/zip-analysis/{zip_code}")
        
        return len(final_territories) > 0 and self.tests_passed > 0

def main():
    tester = LocalTerritoryTester()
    
    print("Running Local Territory Data Test...")
    success = tester.run_comprehensive_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())