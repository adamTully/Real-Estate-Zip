#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid
import time

class ComprehensiveZipIntelAPITester:
    def __init__(self, base_url="https://realestate-ai-41.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_zip = "94105"  # Focus on this specific ZIP as requested
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if details:
                print(f"   Details: {details}")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def is_valid_uuid(self, uuid_string):
        """Check if string is a valid UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    def is_json_serializable(self, obj):
        """Check if object is JSON serializable"""
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False
    
    def test_post_zip_analysis_comprehensive(self):
        """Test POST /api/zip-analysis with comprehensive validation"""
        try:
            payload = {"zip_code": self.test_zip}
            response = requests.post(
                f"{self.api_url}/zip-analysis", 
                json=payload,
                timeout=60  # Longer timeout for LLM processing
            )
            
            success = response.status_code == 200
            if not success:
                self.log_test("POST /api/zip-analysis - Status Code", False, f"Status: {response.status_code}, Response: {response.text[:500]}")
                return False, None
            
            data = response.json()
            
            # Test 1: JSON Serializable
            if not self.is_json_serializable(data):
                self.log_test("POST /api/zip-analysis - JSON Serializable", False, "Response is not JSON serializable")
                return False, None
            self.log_test("POST /api/zip-analysis - JSON Serializable", True)
            
            # Test 2: Required MarketIntelligence keys
            required_keys = ["buyer_migration", "seo_youtube_trends", "content_strategy", 
                           "hidden_listings", "market_hooks", "content_assets"]
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                self.log_test("POST /api/zip-analysis - Required Keys", False, f"Missing required keys: {missing_keys}")
                return False, None
            self.log_test("POST /api/zip-analysis - Required Keys", True, f"All required keys present: {required_keys}")
            
            # Test 3: UUID ID
            if "id" not in data or not self.is_valid_uuid(data["id"]):
                self.log_test("POST /api/zip-analysis - UUID ID", False, f"ID is not a valid UUID: {data.get('id')}")
                return False, None
            self.log_test("POST /api/zip-analysis - UUID ID", True, f"Valid UUID: {data['id']}")
            
            # Test 4: Timestamps
            if "created_at" not in data or "updated_at" not in data:
                self.log_test("POST /api/zip-analysis - Timestamps", False, "Missing created_at or updated_at fields")
                return False, None
            self.log_test("POST /api/zip-analysis - Timestamps", True, f"created_at: {data['created_at']}, updated_at: {data['updated_at']}")
            
            # Test 5: Analysis content for first four categories
            analysis_content_categories = ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings"]
            for category in analysis_content_categories:
                if not isinstance(data[category], dict):
                    self.log_test(f"POST /api/zip-analysis - {category} Structure", False, f"{category} is not a dict")
                    return False, None
                if "analysis_content" not in data[category]:
                    self.log_test(f"POST /api/zip-analysis - {category} Analysis Content", False, f"{category} missing analysis_content")
                    return False, None
                if not isinstance(data[category]["analysis_content"], str):
                    self.log_test(f"POST /api/zip-analysis - {category} Analysis Content Type", False, f"{category} analysis_content is not a string")
                    return False, None
                self.log_test(f"POST /api/zip-analysis - {category} Analysis Content", True, f"Valid string content ({len(data[category]['analysis_content'])} chars)")
            
            # Test 6: Market hooks structure
            market_hooks = data["market_hooks"]
            if not isinstance(market_hooks, dict):
                self.log_test("POST /api/zip-analysis - Market Hooks Structure", False, "market_hooks is not a dict")
                return False, None
            
            # Check for detailed_analysis (should be present based on code)
            if "detailed_analysis" not in market_hooks:
                self.log_test("POST /api/zip-analysis - Market Hooks Detailed Analysis", False, "market_hooks missing detailed_analysis")
                return False, None
            
            if not isinstance(market_hooks["detailed_analysis"], str):
                self.log_test("POST /api/zip-analysis - Market Hooks Detailed Analysis Type", False, "market_hooks detailed_analysis is not a string")
                return False, None
            
            self.log_test("POST /api/zip-analysis - Market Hooks Structure", True, f"Valid structure with detailed_analysis ({len(market_hooks['detailed_analysis'])} chars)")
            
            # Test 7: Content assets structure
            content_assets = data["content_assets"]
            if not isinstance(content_assets, dict):
                self.log_test("POST /api/zip-analysis - Content Assets Structure", False, "content_assets is not a dict")
                return False, None
            self.log_test("POST /api/zip-analysis - Content Assets Structure", True)
            
            return True, data
            
        except Exception as e:
            self.log_test("POST /api/zip-analysis - Exception", False, str(e))
            return False, None
    
    def test_get_zip_analysis_comprehensive(self):
        """Test GET /api/zip-analysis/{zip} comprehensive validation"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{self.test_zip}", timeout=30)
            
            success = response.status_code == 200
            if not success:
                self.log_test("GET /api/zip-analysis/{zip} - Status Code", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            
            # Test same structure as POST
            required_keys = ["buyer_migration", "seo_youtube_trends", "content_strategy", 
                           "hidden_listings", "market_hooks", "content_assets"]
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                self.log_test("GET /api/zip-analysis/{zip} - Required Keys", False, f"Missing required keys: {missing_keys}")
                return False
            
            # Verify ID is UUID string
            if "id" not in data or not self.is_valid_uuid(data["id"]):
                self.log_test("GET /api/zip-analysis/{zip} - UUID ID", False, f"ID is not a valid UUID: {data.get('id')}")
                return False
            
            # Verify zip_code matches
            if data.get("zip_code") != self.test_zip:
                self.log_test("GET /api/zip-analysis/{zip} - ZIP Match", False, f"ZIP code mismatch: expected {self.test_zip}, got {data.get('zip_code')}")
                return False
            
            self.log_test("GET /api/zip-analysis/{zip} - Complete", True, f"Successfully retrieved analysis for {self.test_zip}")
            return True
            
        except Exception as e:
            self.log_test("GET /api/zip-analysis/{zip} - Exception", False, str(e))
            return False
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        try:
            # Test with proper CORS preflight request
            headers = {
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            response = requests.options(f"{self.api_url}/zip-analysis", headers=headers, timeout=10)
            
            # Check for CORS headers in response
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
                'access-control-allow-credentials': response.headers.get('access-control-allow-credentials')
            }
            
            has_cors = all(value is not None for value in cors_headers.values())
            
            if has_cors:
                self.log_test("CORS Headers", True, f"All CORS headers present: {cors_headers}")
            else:
                self.log_test("CORS Headers", False, f"Missing CORS headers: {cors_headers}")
            
            return has_cors
            
        except Exception as e:
            self.log_test("CORS Headers", False, str(e))
            return False
    
    def test_api_prefix(self):
        """Test /api prefix is respected"""
        try:
            # Test that /api prefix works
            api_response = requests.get(f"{self.api_url}/", timeout=10)
            api_works = api_response.status_code == 200
            
            if api_works:
                self.log_test("API Prefix", True, "API prefix /api works correctly")
            else:
                self.log_test("API Prefix", False, f"API prefix failed with status: {api_response.status_code}")
            
            return api_works
            
        except Exception as e:
            self.log_test("API Prefix", False, str(e))
            return False
    
    def test_invalid_zip_format_validation(self):
        """Test validation for invalid ZIP formats"""
        invalid_formats = ["123", "abcde", "12345-", "123456", ""]
        
        all_passed = True
        for invalid_zip in invalid_formats:
            try:
                payload = {"zip_code": invalid_zip}
                response = requests.post(f"{self.api_url}/zip-analysis", json=payload, timeout=10)
                
                # Should return 422 for validation error
                success = response.status_code == 422
                if success:
                    self.log_test(f"Invalid ZIP Format ({invalid_zip})", True, f"Correctly rejected with 422")
                else:
                    self.log_test(f"Invalid ZIP Format ({invalid_zip})", False, f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Invalid ZIP Format ({invalid_zip})", False, str(e))
                all_passed = False
        
        return all_passed
    
    def run_comprehensive_test(self):
        """Run comprehensive tests as per review request"""
        print("🎯 Starting Comprehensive ZIP Intel API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🏠 Focus ZIP: {self.test_zip}")
        print("=" * 80)
        
        # Test 1: CORS
        print("\n🌐 Testing CORS configuration...")
        self.test_cors_headers()
        
        # Test 2: API prefix
        print("\n🔗 Testing /api prefix...")
        self.test_api_prefix()
        
        # Test 3: Invalid ZIP format validation
        print("\n❌ Testing invalid ZIP format validation...")
        self.test_invalid_zip_format_validation()
        
        # Test 4: POST /api/zip-analysis comprehensive
        print(f"\n📤 Testing POST /api/zip-analysis with {self.test_zip}...")
        post_success, post_data = self.test_post_zip_analysis_comprehensive()
        
        if post_success:
            # Wait a moment for data to be available
            time.sleep(2)
            
            # Test 5: GET /api/zip-analysis/{zip}
            print(f"\n📥 Testing GET /api/zip-analysis/{self.test_zip}...")
            self.test_get_zip_analysis_comprehensive()
        else:
            print(f"❌ POST failed, skipping GET test")
        
        # Print final results
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All comprehensive tests passed! API fully meets requirements.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    tester = ComprehensiveZipIntelAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())