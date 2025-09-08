#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class TikTokContentDebugTester:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        
        # Test user credentials from review request
        self.test_user_email = "adamtest3@gmail.com"
        self.test_user_password = "adamtest3"
        self.test_zip_code = "30126"
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        if details and success:
            print(f"   📝 {details}")
        
    def authenticate_user(self):
        """Authenticate with the test user"""
        try:
            login_payload = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.auth_token = data["access_token"]
                user_data = data["user"]
                owned_territories = user_data.get("owned_territories", [])
                success = self.test_zip_code in owned_territories
                details = f"Login successful for {user_data['email']}, owns ZIP {self.test_zip_code}: {'Yes' if success else 'No'}, territories: {owned_territories}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("User Authentication", success, details)
            return success
            
        except Exception as e:
            self.log_test("User Authentication", False, str(e))
            return False

    def test_tiktok_content_generation(self):
        """Test TikTok content generation and analyze JSON structure"""
        try:
            if not self.auth_token:
                self.log_test("TikTok Content Generation", False, "No auth token available")
                return False, None
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"zip_code": self.test_zip_code}
            
            print(f"\n🎬 Generating TikTok content for ZIP {self.test_zip_code}...")
            response = requests.post(
                f"{self.api_url}/generate-platform-content/tiktok", 
                json=payload,
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            tiktok_data = None
            
            if success:
                tiktok_data = response.json()
                
                print(f"\n📋 TikTok Response Structure Analysis:")
                print(f"   Response Keys: {list(tiktok_data.keys())}")
                
                # Check for required fields
                required_fields = ["summary"]
                content_key = None
                
                # Look for TikTok content key
                for key in tiktok_data.keys():
                    if "tiktok" in key.lower() and "post" in key.lower():
                        content_key = key
                        break
                
                if content_key:
                    print(f"   TikTok Content Key: '{content_key}'")
                    tiktok_posts = tiktok_data.get(content_key, [])
                    
                    if isinstance(tiktok_posts, list) and len(tiktok_posts) > 0:
                        first_post = tiktok_posts[0]
                        print(f"   Number of TikTok posts: {len(tiktok_posts)}")
                        print(f"   First post keys: {list(first_post.keys())}")
                        
                        # Check for required post fields
                        post_required_fields = ["name", "title", "content"]
                        missing_post_fields = [field for field in post_required_fields if field not in first_post]
                        
                        if missing_post_fields:
                            success = False
                            details = f"Missing required post fields: {missing_post_fields}"
                        else:
                            # Check for TikTok-specific fields
                            tiktok_specific_fields = ["hook", "video_concept", "duration"]
                            present_specific_fields = [field for field in tiktok_specific_fields if field in first_post]
                            
                            details = f"Generated {len(tiktok_posts)} TikTok posts. Content key: '{content_key}'. TikTok-specific fields present: {present_specific_fields}"
                    else:
                        success = False
                        details = f"No TikTok posts found or empty array in key '{content_key}'"
                else:
                    success = False
                    details = f"No TikTok content key found. Available keys: {list(tiktok_data.keys())}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("TikTok Content Generation", success, details)
            return success, tiktok_data
            
        except Exception as e:
            self.log_test("TikTok Content Generation", False, str(e))
            return False, None

    def test_instagram_content_generation(self):
        """Test Instagram content generation for comparison"""
        try:
            if not self.auth_token:
                self.log_test("Instagram Content Generation", False, "No auth token available")
                return False, None
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"zip_code": self.test_zip_code}
            
            print(f"\n📸 Generating Instagram content for ZIP {self.test_zip_code}...")
            response = requests.post(
                f"{self.api_url}/generate-platform-content/instagram", 
                json=payload,
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            instagram_data = None
            
            if success:
                instagram_data = response.json()
                
                print(f"\n📋 Instagram Response Structure Analysis:")
                print(f"   Response Keys: {list(instagram_data.keys())}")
                
                # Check for Instagram content
                content_key = None
                for key in instagram_data.keys():
                    if "instagram" in key.lower() and "post" in key.lower():
                        content_key = key
                        break
                
                if content_key:
                    print(f"   Instagram Content Key: '{content_key}'")
                    instagram_posts = instagram_data.get(content_key, [])
                    
                    if isinstance(instagram_posts, list) and len(instagram_posts) > 0:
                        first_post = instagram_posts[0]
                        print(f"   Number of Instagram posts: {len(instagram_posts)}")
                        print(f"   First post keys: {list(first_post.keys())}")
                        
                        # Check for required post fields
                        post_required_fields = ["name", "title", "content"]
                        missing_post_fields = [field for field in post_required_fields if field not in first_post]
                        
                        if missing_post_fields:
                            success = False
                            details = f"Missing required post fields: {missing_post_fields}"
                        else:
                            details = f"Generated {len(instagram_posts)} Instagram posts. Content key: '{content_key}'"
                    else:
                        success = False
                        details = f"No Instagram posts found or empty array in key '{content_key}'"
                else:
                    success = False
                    details = f"No Instagram content key found. Available keys: {list(instagram_data.keys())}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Instagram Content Generation", success, details)
            return success, instagram_data
            
        except Exception as e:
            self.log_test("Instagram Content Generation", False, str(e))
            return False, None

    def compare_content_structures(self, tiktok_data, instagram_data):
        """Compare TikTok and Instagram content structures"""
        try:
            print(f"\n🔍 Comparing TikTok vs Instagram Content Structures:")
            
            if not tiktok_data or not instagram_data:
                self.log_test("Content Structure Comparison", False, "Missing data for comparison")
                return False
            
            # Find content keys
            tiktok_content_key = None
            instagram_content_key = None
            
            for key in tiktok_data.keys():
                if "tiktok" in key.lower() and "post" in key.lower():
                    tiktok_content_key = key
                    break
            
            for key in instagram_data.keys():
                if "instagram" in key.lower() and "post" in key.lower():
                    instagram_content_key = key
                    break
            
            print(f"   TikTok Content Key: '{tiktok_content_key}'")
            print(f"   Instagram Content Key: '{instagram_content_key}'")
            
            # Compare expected vs actual keys
            expected_tiktok_key = "tiktok_posts"
            expected_instagram_key = "instagram_posts"
            
            tiktok_key_correct = tiktok_content_key == expected_tiktok_key
            instagram_key_correct = instagram_content_key == expected_instagram_key
            
            print(f"   TikTok key matches expected '{expected_tiktok_key}': {tiktok_key_correct}")
            print(f"   Instagram key matches expected '{expected_instagram_key}': {instagram_key_correct}")
            
            # Compare post structures if both have content
            structure_comparison = {}
            
            if tiktok_content_key and instagram_content_key:
                tiktok_posts = tiktok_data.get(tiktok_content_key, [])
                instagram_posts = instagram_data.get(instagram_content_key, [])
                
                if tiktok_posts and instagram_posts:
                    tiktok_post_keys = set(tiktok_posts[0].keys()) if tiktok_posts else set()
                    instagram_post_keys = set(instagram_posts[0].keys()) if instagram_posts else set()
                    
                    common_keys = tiktok_post_keys.intersection(instagram_post_keys)
                    tiktok_only_keys = tiktok_post_keys - instagram_post_keys
                    instagram_only_keys = instagram_post_keys - tiktok_post_keys
                    
                    structure_comparison = {
                        "common_keys": list(common_keys),
                        "tiktok_only_keys": list(tiktok_only_keys),
                        "instagram_only_keys": list(instagram_only_keys)
                    }
                    
                    print(f"   Common post fields: {list(common_keys)}")
                    print(f"   TikTok-only fields: {list(tiktok_only_keys)}")
                    print(f"   Instagram-only fields: {list(instagram_only_keys)}")
            
            # Determine if structures are compatible for frontend
            success = True
            issues = []
            
            if not tiktok_key_correct:
                issues.append(f"TikTok content key is '{tiktok_content_key}' but frontend expects '{expected_tiktok_key}'")
                success = False
            
            if tiktok_content_key and tiktok_data.get(tiktok_content_key):
                tiktok_posts = tiktok_data.get(tiktok_content_key, [])
                if tiktok_posts:
                    required_fields = ["name", "title", "content"]
                    first_post = tiktok_posts[0]
                    missing_fields = [field for field in required_fields if field not in first_post]
                    if missing_fields:
                        issues.append(f"TikTok posts missing required fields: {missing_fields}")
                        success = False
            
            details = f"Key compatibility: TikTok={tiktok_key_correct}, Instagram={instagram_key_correct}. Issues: {issues if issues else 'None'}"
            
            self.log_test("Content Structure Comparison", success, details)
            return success
            
        except Exception as e:
            self.log_test("Content Structure Comparison", False, str(e))
            return False

    def test_frontend_content_extraction_simulation(self, tiktok_data, instagram_data):
        """Simulate how frontend would extract content"""
        try:
            print(f"\n🖥️ Simulating Frontend Content Extraction:")
            
            # Simulate frontend logic for extracting content
            def extract_platform_content(data, platform_name):
                """Simulate frontend content extraction logic"""
                primary_key = f"{platform_name}_posts"
                fallback_keys = [
                    f"{platform_name}Posts",
                    f"{platform_name}_content", 
                    f"{platform_name}Content",
                    platform_name
                ]
                
                # Try primary key first
                if primary_key in data:
                    return data[primary_key], primary_key
                
                # Try fallback keys
                for key in fallback_keys:
                    if key in data:
                        return data[key], key
                
                # Try any key containing platform name
                for key in data.keys():
                    if platform_name.lower() in key.lower() and ("post" in key.lower() or "content" in key.lower()):
                        return data[key], key
                
                return None, None
            
            # Test TikTok extraction
            tiktok_content, tiktok_key_used = extract_platform_content(tiktok_data or {}, "tiktok")
            instagram_content, instagram_key_used = extract_platform_content(instagram_data or {}, "instagram")
            
            print(f"   TikTok extraction:")
            print(f"     Key used: '{tiktok_key_used}'")
            print(f"     Content found: {tiktok_content is not None}")
            print(f"     Content type: {type(tiktok_content)}")
            if tiktok_content and isinstance(tiktok_content, list):
                print(f"     Number of items: {len(tiktok_content)}")
            
            print(f"   Instagram extraction:")
            print(f"     Key used: '{instagram_key_used}'")
            print(f"     Content found: {instagram_content is not None}")
            print(f"     Content type: {type(instagram_content)}")
            if instagram_content and isinstance(instagram_content, list):
                print(f"     Number of items: {len(instagram_content)}")
            
            # Check if both platforms can be extracted successfully
            tiktok_success = tiktok_content is not None and isinstance(tiktok_content, list) and len(tiktok_content) > 0
            instagram_success = instagram_content is not None and isinstance(instagram_content, list) and len(instagram_content) > 0
            
            success = tiktok_success and instagram_success
            
            if not tiktok_success:
                details = f"TikTok content extraction failed. Key used: '{tiktok_key_used}', Content: {tiktok_content}"
            elif not instagram_success:
                details = f"Instagram content extraction failed. Key used: '{instagram_key_used}', Content: {instagram_content}"
            else:
                details = f"Both platforms extracted successfully. TikTok key: '{tiktok_key_used}', Instagram key: '{instagram_key_used}'"
            
            self.log_test("Frontend Content Extraction Simulation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Frontend Content Extraction Simulation", False, str(e))
            return False

    def analyze_drawer_compatibility(self, tiktok_data, instagram_data):
        """Analyze if TikTok content is compatible with drawer functionality"""
        try:
            print(f"\n🗂️ Analyzing Drawer Compatibility:")
            
            # Check if TikTok content has the same structure as Instagram for drawer display
            if not tiktok_data or not instagram_data:
                self.log_test("Drawer Compatibility Analysis", False, "Missing data for analysis")
                return False
            
            # Find content arrays
            tiktok_posts = None
            instagram_posts = None
            
            for key, value in tiktok_data.items():
                if "tiktok" in key.lower() and "post" in key.lower() and isinstance(value, list):
                    tiktok_posts = value
                    break
            
            for key, value in instagram_data.items():
                if "instagram" in key.lower() and "post" in key.lower() and isinstance(value, list):
                    instagram_posts = value
                    break
            
            if not tiktok_posts or not instagram_posts:
                self.log_test("Drawer Compatibility Analysis", False, "Could not find post arrays in both platforms")
                return False
            
            # Check if both have posts with required fields for drawer
            drawer_required_fields = ["title", "content", "name"]
            
            tiktok_compatible = True
            instagram_compatible = True
            
            if tiktok_posts:
                first_tiktok = tiktok_posts[0]
                missing_tiktok_fields = [field for field in drawer_required_fields if field not in first_tiktok]
                if missing_tiktok_fields:
                    tiktok_compatible = False
                    print(f"   TikTok missing drawer fields: {missing_tiktok_fields}")
                else:
                    print(f"   TikTok has all drawer fields: {drawer_required_fields}")
            
            if instagram_posts:
                first_instagram = instagram_posts[0]
                missing_instagram_fields = [field for field in drawer_required_fields if field not in first_instagram]
                if missing_instagram_fields:
                    instagram_compatible = False
                    print(f"   Instagram missing drawer fields: {missing_instagram_fields}")
                else:
                    print(f"   Instagram has all drawer fields: {drawer_required_fields}")
            
            success = tiktok_compatible and instagram_compatible
            
            if success:
                details = "Both TikTok and Instagram content have required fields for drawer functionality"
            else:
                details = f"Drawer compatibility issue - TikTok compatible: {tiktok_compatible}, Instagram compatible: {instagram_compatible}"
            
            self.log_test("Drawer Compatibility Analysis", success, details)
            return success
            
        except Exception as e:
            self.log_test("Drawer Compatibility Analysis", False, str(e))
            return False

    def run_tiktok_debug_investigation(self):
        """Run the complete TikTok content generation debug investigation"""
        print("🎬 TikTok Content Generation Debug Investigation")
        print(f"📍 Testing against: {self.base_url}")
        print(f"👤 User: {self.test_user_email}")
        print(f"🏠 ZIP: {self.test_zip_code}")
        print("=" * 60)
        
        # Step 1: Authenticate
        print(f"\n🔑 Step 1: Authenticating user...")
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with investigation.")
            return False
        
        # Step 2: Generate TikTok content
        print(f"\n🎬 Step 2: Generating TikTok content...")
        tiktok_success, tiktok_data = self.test_tiktok_content_generation()
        
        # Step 3: Generate Instagram content for comparison
        print(f"\n📸 Step 3: Generating Instagram content for comparison...")
        instagram_success, instagram_data = self.test_instagram_content_generation()
        
        # Step 4: Compare structures
        if tiktok_data and instagram_data:
            print(f"\n🔍 Step 4: Comparing content structures...")
            self.compare_content_structures(tiktok_data, instagram_data)
            
            # Step 5: Simulate frontend extraction
            print(f"\n🖥️ Step 5: Simulating frontend content extraction...")
            self.test_frontend_content_extraction_simulation(tiktok_data, instagram_data)
            
            # Step 6: Analyze drawer compatibility
            print(f"\n🗂️ Step 6: Analyzing drawer compatibility...")
            self.analyze_drawer_compatibility(tiktok_data, instagram_data)
        
        # Print detailed JSON structures for analysis
        if tiktok_data:
            print(f"\n📋 TikTok Content JSON Structure:")
            print(json.dumps(tiktok_data, indent=2)[:1000] + "..." if len(json.dumps(tiktok_data, indent=2)) > 1000 else json.dumps(tiktok_data, indent=2))
        
        if instagram_data:
            print(f"\n📋 Instagram Content JSON Structure:")
            print(json.dumps(instagram_data, indent=2)[:1000] + "..." if len(json.dumps(instagram_data, indent=2)) > 1000 else json.dumps(instagram_data, indent=2))
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 TikTok Debug Investigation Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Provide specific findings and recommendations
        print(f"\n🔍 KEY FINDINGS:")
        
        if tiktok_success and instagram_success:
            print("✅ Both TikTok and Instagram content generation are working")
            print("🔍 Issue likely in frontend content extraction or drawer logic")
        elif not tiktok_success and instagram_success:
            print("❌ TikTok content generation has issues")
            print("✅ Instagram content generation is working")
            print("🔍 Issue is in TikTok backend content generation")
        elif tiktok_success and not instagram_success:
            print("✅ TikTok content generation is working")
            print("❌ Instagram content generation has issues")
            print("🔍 Unexpected - Instagram should be working based on user report")
        else:
            print("❌ Both TikTok and Instagram content generation have issues")
            print("🔍 Broader platform generation system problem")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if not tiktok_success:
            print("1. Fix TikTok content generation backend issues")
            print("2. Ensure TikTok endpoint returns proper JSON structure with 'tiktok_posts' key")
            print("3. Verify TikTok posts have required fields: name, title, content")
        
        if tiktok_success and instagram_success:
            print("1. Check frontend content extraction logic for TikTok")
            print("2. Verify frontend uses correct key 'tiktok_posts' for content extraction")
            print("3. Check drawer component handles TikTok content same as Instagram")
            print("4. Verify click handlers are properly attached to TikTok cards")
        
        return self.tests_passed == self.tests_run

def main():
    tester = TikTokContentDebugTester()
    
    print("🎬 Starting TikTok Content Generation Debug Investigation...")
    success = tester.run_tiktok_debug_investigation()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())