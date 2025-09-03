#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid
import time

class FocusedZipIntelAPITester:
    def __init__(self, base_url="https://territory-hub-2.preview.emergentagent.com"):
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
    
    def test_post_zip_analysis(self):
        """Test POST /api/zip-analysis with valid zip 94105"""
        try:
            payload = {"zip_code": self.test_zip}
            response = requests.post(
                f"{self.api_url}/zip-analysis", 
                json=payload,
                timeout=60  # Longer timeout for LLM processing
            )
            
            success = response.status_code == 200
            if not success:
                self.log_test("POST /api/zip-analysis", False, f"Status: {response.status_code}, Response: {response.text[:500]}")
                return False, None
            
            data = response.json()
            
            # Check if response is JSON serializable
            if not self.is_json_serializable(data):
                self.log_test("POST /api/zip-analysis", False, "Response is not JSON serializable")
                return False, None
            
            # Verify MarketIntelligence shape - required keys
            required_keys = ["buyer_migration", "seo_youtube_trends", "content_strategy", 
                           "hidden_listings", "market_hooks", "content_assets"]
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                self.log_test("POST /api/zip-analysis", False, f"Missing required keys: {missing_keys}")
                return False, None
            
            # Verify ID is UUID string
            if "id" not in data or not self.is_valid_uuid(data["id"]):
                self.log_test("POST /api/zip-analysis", False, f"ID is not a valid UUID: {data.get('id')}")
                return False, None
            
            # Verify created_at and updated_at are present
            if "created_at" not in data or "updated_at" not in data:
                self.log_test("POST /api/zip-analysis", False, "Missing created_at or updated_at fields")
                return False, None
            
            # Verify analysis_content for first four categories
            analysis_content_categories = ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings"]
            for category in analysis_content_categories:
                if not isinstance(data[category], dict):
                    self.log_test("POST /api/zip-analysis", False, f"{category} is not a dict")
                    return False, None
                if "analysis_content" not in data[category]:
                    self.log_test("POST /api/zip-analysis", False, f"{category} missing analysis_content")
                    return False, None
                if not isinstance(data[category]["analysis_content"], str):
                    self.log_test("POST /api/zip-analysis", False, f"{category} analysis_content is not a string")
                    return False, None
            
            # Verify market_hooks structure (may include detailed_analysis string and lists)
            market_hooks = data["market_hooks"]
            if not isinstance(market_hooks, dict):
                self.log_test("POST /api/zip-analysis", False, "market_hooks is not a dict")
                return False, None
            
            # Check if market_hooks has detailed_analysis (optional but mentioned in requirements)
            if "detailed_analysis" in market_hooks and not isinstance(market_hooks["detailed_analysis"], str):
                self.log_test("POST /api/zip-analysis", False, "market_hooks detailed_analysis is not a string")
                return False, None
            
            self.log_test("POST /api/zip-analysis", True, f"Successfully created analysis for {self.test_zip}")
            return True, data
            
        except Exception as e:
            self.log_test("POST /api/zip-analysis", False, str(e))
            return False, None
    
    def test_get_zip_analysis(self):
        """Test GET /api/zip-analysis/{zip} returns the same record"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{self.test_zip}", timeout=30)
            
            success = response.status_code == 200
            if not success:
                self.log_test("GET /api/zip-analysis/{zip}", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            
            # Verify same structure as POST
            required_keys = ["buyer_migration", "seo_youtube_trends", "content_strategy", 
                           "hidden_listings", "market_hooks", "content_assets"]
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                self.log_test("GET /api/zip-analysis/{zip}", False, f"Missing required keys: {missing_keys}")
                return False
            
            # Verify ID is UUID string
            if "id" not in data or not self.is_valid_uuid(data["id"]):
                self.log_test("GET /api/zip-analysis/{zip}", False, f"ID is not a valid UUID: {data.get('id')}")
                return False
            
            # Verify zip_code matches
            if data.get("zip_code") != self.test_zip:
                self.log_test("GET /api/zip-analysis/{zip}", False, f"ZIP code mismatch: expected {self.test_zip}, got {data.get('zip_code')}")
                return False
            
            self.log_test("GET /api/zip-analysis/{zip}", True, f"Successfully retrieved analysis for {self.test_zip}")
            return True
            
        except Exception as e:
            self.log_test("GET /api/zip-analysis/{zip}", False, str(e))
            return False
    
    def test_cors_and_api_prefix(self):
        """Test CORS and /api prefix are respected"""
        try:
            # Test CORS headers
            response = requests.options(f"{self.api_url}/zip-analysis", timeout=10)
            
            # Check if CORS headers are present (basic check)
            cors_headers = [
                'access-control-allow-origin',
                'access-control-allow-methods',
                'access-control-allow-headers'
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            
            # Test /api prefix works
            api_response = requests.get(f"{self.api_url}/", timeout=10)
            api_prefix_works = api_response.status_code == 200
            
            # Test that non-/api prefix doesn't work for our endpoints
            try:
                non_api_response = requests.get(f"{self.base_url}/zip-analysis/{self.test_zip}", timeout=5)
                non_api_blocked = non_api_response.status_code == 404
            except:
                non_api_blocked = True  # If it fails to connect, that's also good
            
            success = has_cors and api_prefix_works and non_api_blocked
            details = f"CORS headers: {has_cors}, API prefix works: {api_prefix_works}, Non-API blocked: {non_api_blocked}"
            
            self.log_test("CORS and /api prefix", success, details)
            return success
            
        except Exception as e:
            self.log_test("CORS and /api prefix", False, str(e))
            return False
    
    def test_invalid_zip_errors(self):
        """Test errors for invalid zip codes"""
        invalid_zips = ["123", "abcde", "99999", "00000"]
        
        all_passed = True
        for invalid_zip in invalid_zips:
            try:
                payload = {"zip_code": invalid_zip}
                response = requests.post(f"{self.api_url}/zip-analysis", json=payload, timeout=10)
                
                # Should return 422 for validation error or 500 for processing error
                success = response.status_code in [422, 500]
                details = f"Status: {response.status_code}" if success else f"Unexpected status: {response.status_code}"
                
                self.log_test(f"Invalid ZIP Error ({invalid_zip})", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Invalid ZIP Error ({invalid_zip})", False, str(e))
                all_passed = False
        
        return all_passed
    
    def run_focused_test(self):
        """Run focused tests as per review request"""
        print("🎯 Starting Focused ZIP Intel API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🏠 Focus ZIP: {self.test_zip}")
        print("=" * 60)
        
        # Test 1: CORS and API prefix
        print("\n🌐 Testing CORS and /api prefix...")
        self.test_cors_and_api_prefix()
        
        # Test 2: Invalid ZIP errors
        print("\n❌ Testing invalid ZIP error handling...")
        self.test_invalid_zip_errors()
        
        # Test 3: POST /api/zip-analysis with valid zip
        print(f"\n📤 Testing POST /api/zip-analysis with {self.test_zip}...")
        post_success, post_data = self.test_post_zip_analysis()
        
        if post_success:
            # Wait a moment for data to be available
            time.sleep(2)
            
            # Test 4: GET /api/zip-analysis/{zip}
            print(f"\n📥 Testing GET /api/zip-analysis/{self.test_zip}...")
            self.test_get_zip_analysis()
        else:
            print(f"❌ POST failed, skipping GET test")
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All focused tests passed! API meets requirements.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    tester = FocusedZipIntelAPITester()
    success = tester.run_focused_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())