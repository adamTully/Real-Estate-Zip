#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ZipIntelAPITester:
    def __init__(self, base_url="https://market-insights-27.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_zip_codes = ["90210", "10001", "60601", "33101"]
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                expected_message = "ZIP Intel Generator API v2.0"
                success = data.get("message") == expected_message
                details = f"Got message: {data.get('message')}" if not success else ""
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("API Root Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False
    
    def test_zip_analysis_creation(self, zip_code):
        """Test ZIP analysis creation"""
        try:
            payload = {"zip_code": zip_code}
            response = requests.post(
                f"{self.api_url}/zip-analysis", 
                json=payload,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify required fields exist
                required_fields = [
                    "id", "zip_code", "buyer_migration", "seo_youtube_trends",
                    "content_strategy", "hidden_listings", "market_hooks", 
                    "content_assets", "created_at"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Verify each intelligence category has required structure
                    for category in ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "market_hooks"]:
                        if not isinstance(data[category], dict) or "summary" not in data[category]:
                            success = False
                            details = f"Invalid structure for {category}"
                            break
                    
                    if success and "content_assets" in data:
                        content_assets = data["content_assets"]
                        if not all(key in content_assets for key in ["blog_posts", "email_campaigns", "lead_magnet"]):
                            success = False
                            details = "Missing content asset types"
                        
                details = details if not success else f"Analysis created with ID: {data.get('id', 'N/A')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                
            self.log_test(f"ZIP Analysis Creation ({zip_code})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Creation ({zip_code})", False, str(e))
            return False, None
    
    def test_zip_analysis_retrieval(self, zip_code):
        """Test ZIP analysis retrieval"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get("zip_code") == zip_code
                details = f"Retrieved analysis for {data.get('zip_code')}" if success else "ZIP code mismatch"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"ZIP Analysis Retrieval ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Retrieval ({zip_code})", False, str(e))
            return False
    
    def test_pdf_generation(self, zip_code):
        """Test PDF generation"""
        try:
            response = requests.get(f"{self.api_url}/generate-pdf/{zip_code}", timeout=15)
            success = response.status_code == 200
            
            if success:
                # Check if response is actually a PDF
                content_type = response.headers.get('content-type', '')
                is_pdf = 'application/pdf' in content_type
                has_content = len(response.content) > 1000  # PDF should be substantial
                
                success = is_pdf and has_content
                details = f"PDF size: {len(response.content)} bytes, Content-Type: {content_type}" if success else f"Invalid PDF: {content_type}, Size: {len(response.content)}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"PDF Generation ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"PDF Generation ({zip_code})", False, str(e))
            return False
    
    def test_content_assets(self, zip_code):
        """Test content asset endpoints"""
        asset_tests = [
            ("blogs", "blog-post-1.txt"),
            ("emails", "email-week-1.txt"), 
            ("lead_magnet", "buyers-guide")
        ]
        
        all_passed = True
        
        for asset_type, asset_name in asset_tests:
            try:
                # For lead_magnet, we don't need asset_name in URL
                if asset_type == "lead_magnet":
                    url = f"{self.api_url}/content-asset/{zip_code}/{asset_type}/guide"
                else:
                    # Try to get the first asset from the analysis
                    analysis_response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}")
                    if analysis_response.status_code == 200:
                        analysis_data = analysis_response.json()
                        content_assets = analysis_data.get("content_assets", {})
                        
                        if asset_type == "blogs" and content_assets.get("blog_posts"):
                            asset_name = content_assets["blog_posts"][0]["name"]
                        elif asset_type == "emails" and content_assets.get("email_campaigns"):
                            asset_name = content_assets["email_campaigns"][0]["name"]
                    
                    url = f"{self.api_url}/content-asset/{zip_code}/{asset_type}/{asset_name}"
                
                response = requests.get(url, timeout=10)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    has_content = "content" in data and len(data["content"]) > 100
                    success = has_content
                    details = f"Content length: {len(data.get('content', ''))}" if success else "No content or too short"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test(f"Content Asset {asset_type} ({zip_code})", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Content Asset {asset_type} ({zip_code})", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_invalid_zip_validation(self):
        """Test ZIP code validation"""
        invalid_zips = ["123", "abcde", "12345-", "123456"]
        
        for invalid_zip in invalid_zips:
            try:
                payload = {"zip_code": invalid_zip}
                response = requests.post(f"{self.api_url}/zip-analysis", json=payload, timeout=10)
                
                # Should return 422 for validation error
                success = response.status_code == 422
                details = f"Status: {response.status_code}" if not success else "Correctly rejected invalid ZIP"
                
                self.log_test(f"Invalid ZIP Validation ({invalid_zip})", success, details)
                
            except Exception as e:
                self.log_test(f"Invalid ZIP Validation ({invalid_zip})", False, str(e))
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting ZIP Intel Generator API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API availability
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        print("\n📋 Testing ZIP Code Validation...")
        self.test_invalid_zip_validation()
        
        print("\n🏠 Testing ZIP Analysis Workflow...")
        
        # Test with one primary ZIP code for full workflow
        primary_zip = self.test_zip_codes[0]  # 90210
        
        print(f"\n🔍 Testing full workflow with ZIP: {primary_zip}")
        
        # Create analysis
        success, analysis_data = self.test_zip_analysis_creation(primary_zip)
        if not success:
            print(f"❌ Failed to create analysis for {primary_zip}. Skipping dependent tests.")
            return False
        
        # Wait a moment for data to be available
        time.sleep(2)
        
        # Test retrieval
        self.test_zip_analysis_retrieval(primary_zip)
        
        # Test PDF generation
        self.test_pdf_generation(primary_zip)
        
        # Test content assets
        self.test_content_assets(primary_zip)
        
        # Test additional ZIP codes for creation only
        print(f"\n🌍 Testing additional ZIP codes...")
        for zip_code in self.test_zip_codes[1:]:
            self.test_zip_analysis_creation(zip_code)
            time.sleep(1)  # Brief pause between requests
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! API is fully functional.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    tester = ZipIntelAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())