#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class LocalZipIntelTester:
    def __init__(self):
        # Test locally first, then external if needed
        self.local_url = "http://localhost:8001"
        self.external_url = "https://realestate-ai-41.preview.emergentagent.com"
        self.test_zip = "94105"
        self.tests_run = 0
        self.tests_passed = 0
        self.api_url = None
        
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
        
    def test_api_connectivity(self):
        """Test which API endpoint is accessible"""
        print("🔍 Testing API connectivity...")
        
        # Try local first
        try:
            response = requests.get(f"{self.local_url}/api/", timeout=5)
            if response.status_code == 200:
                self.api_url = f"{self.local_url}/api"
                self.log_test("Local API Connectivity", True, f"Connected to {self.local_url}")
                return True
        except Exception as e:
            print(f"   Local API failed: {str(e)}")
        
        # Try external
        try:
            response = requests.get(f"{self.external_url}/api/", timeout=10)
            if response.status_code == 200:
                self.api_url = f"{self.external_url}/api"
                self.log_test("External API Connectivity", True, f"Connected to {self.external_url}")
                return True
        except Exception as e:
            print(f"   External API failed: {str(e)}")
        
        self.log_test("API Connectivity", False, "Neither local nor external API accessible")
        return False
    
    def test_post_zip_analysis_94105(self):
        """Test POST /api/zip-analysis for ZIP 94105"""
        try:
            print(f"\n🔍 Testing POST /api/zip-analysis for ZIP {self.test_zip}")
            payload = {"zip_code": self.test_zip}
            
            response = requests.post(
                f"{self.api_url}/zip-analysis", 
                json=payload,
                timeout=45
            )
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text[:500]
                # Check for quota/rate limit errors
                if any(term in error_text.lower() for term in ["quota", "rate limit", "billing"]):
                    self.log_test("POST - No Quota Errors", False, f"QUOTA/RATE LIMIT ERROR: {error_text}")
                else:
                    self.log_test("POST - HTTP 200", False, f"Status: {response.status_code}, Response: {error_text}")
                return False, None
            
            self.log_test("POST - HTTP 200", True, "Successful response")
            self.log_test("POST - No Quota Errors", True, "No rate limit or quota errors detected")
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("POST - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return False, None
            
            self.log_test("POST - JSON Parse", True, "Valid JSON response")
            
            # Check schema
            required_fields = ["id", "zip_code", "buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "market_hooks", "content_assets"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("POST - Schema Validation", False, f"Missing fields: {missing_fields}")
                return False, None
            
            self.log_test("POST - Schema Validation", True, f"All {len(required_fields)} required fields present")
            
            # Check analysis_content in all sections
            sections_with_analysis = ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "content_assets"]
            analysis_results = []
            
            for section in sections_with_analysis:
                if section in data and isinstance(data[section], dict):
                    if "analysis_content" in data[section]:
                        content = data[section]["analysis_content"]
                        if isinstance(content, str) and len(content) > 20:
                            # Check for error indicators in content
                            if any(term in content.lower() for term in ["temporarily unavailable", "try again", "error", "quota", "rate limit"]):
                                analysis_results.append(f"❌ {section}: Error in content")
                                self.log_test(f"POST - {section} analysis_content", False, f"Error detected in content: {content[:100]}...")
                                return False, None
                            else:
                                analysis_results.append(f"✅ {section}: {len(content)} chars")
                        else:
                            analysis_results.append(f"❌ {section}: Too short")
                            self.log_test(f"POST - {section} analysis_content", False, f"Content too short: {len(content) if isinstance(content, str) else 'Not string'}")
                            return False, None
                    else:
                        analysis_results.append(f"❌ {section}: Missing")
                        self.log_test(f"POST - {section} analysis_content", False, "Missing analysis_content field")
                        return False, None
                else:
                    analysis_results.append(f"❌ {section}: Invalid structure")
                    self.log_test(f"POST - {section} structure", False, "Section missing or invalid")
                    return False, None
            
            self.log_test("POST - All analysis_content Present", True, "; ".join(analysis_results))
            
            # Check market_hooks detailed_analysis
            if "market_hooks" in data and "detailed_analysis" in data["market_hooks"]:
                detailed_content = data["market_hooks"]["detailed_analysis"]
                if isinstance(detailed_content, str) and len(detailed_content) > 50:
                    self.log_test("POST - market_hooks detailed_analysis", True, f"{len(detailed_content)} chars")
                else:
                    self.log_test("POST - market_hooks detailed_analysis", False, "Missing or too short")
                    return False, None
            else:
                self.log_test("POST - market_hooks detailed_analysis", False, "Missing detailed_analysis")
                return False, None
            
            print(f"\n📊 POST Success Summary:")
            print(f"   ZIP: {data.get('zip_code')}")
            print(f"   ID: {data.get('id')}")
            print(f"   All sections have analysis_content: ✅")
            print(f"   No quota/rate limit errors: ✅")
            
            return True, data
            
        except requests.exceptions.Timeout:
            self.log_test("POST - Request", False, "Timeout - server may be processing")
            return False, None
        except Exception as e:
            self.log_test("POST - Request", False, f"Error: {str(e)}")
            return False, None
    
    def test_get_zip_analysis_94105(self):
        """Test GET /api/zip-analysis/{zip}"""
        try:
            print(f"\n🔍 Testing GET /api/zip-analysis/{self.test_zip}")
            
            response = requests.get(f"{self.api_url}/zip-analysis/{self.test_zip}", timeout=15)
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code != 200:
                self.log_test("GET - HTTP 200", False, f"Status: {response.status_code}")
                return False
            
            self.log_test("GET - HTTP 200", True, "Successful response")
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("GET - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return False
            
            self.log_test("GET - JSON Parse", True, "Valid JSON response")
            
            # Verify ZIP matches
            if data.get("zip_code") != self.test_zip:
                self.log_test("GET - ZIP Match", False, f"Expected {self.test_zip}, got {data.get('zip_code')}")
                return False
            
            self.log_test("GET - ZIP Match", True, f"Correct ZIP: {self.test_zip}")
            
            # Verify structure
            required_fields = ["id", "zip_code", "buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "market_hooks", "content_assets"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("GET - Schema", False, f"Missing: {missing_fields}")
                return False
            
            self.log_test("GET - Schema", True, "Complete schema")
            
            print(f"\n📊 GET Success Summary:")
            print(f"   Retrieved record for ZIP {self.test_zip}: ✅")
            print(f"   Complete schema returned: ✅")
            
            return True
            
        except Exception as e:
            self.log_test("GET - Request", False, f"Error: {str(e)}")
            return False
    
    def run_test(self):
        """Run the focused test for ZIP 94105"""
        print("🚀 ZIP Intel Generator - Backend Test for ZIP 94105")
        print("📋 Post-OpenAI funding verification")
        print("=" * 70)
        
        # Test connectivity
        if not self.test_api_connectivity():
            print("\n❌ Cannot connect to API. Test failed.")
            return False
        
        print(f"📍 Using API: {self.api_url}")
        
        # Test POST
        post_success, _ = self.test_post_zip_analysis_94105()
        
        if not post_success:
            print("\n❌ POST test failed.")
            self.print_results()
            return False
        
        # Brief pause
        time.sleep(2)
        
        # Test GET
        get_success = self.test_get_zip_analysis_94105()
        
        self.print_results()
        return post_success and get_success
    
    def print_results(self):
        """Print final results"""
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Backend API working correctly after OpenAI funds added")
            print("✅ No rate limit or quota errors")
            print("✅ All sections include analysis_content strings")
            print("✅ HTTP 200 responses confirmed")
            print("✅ Correct schema validation")
        else:
            failed = self.tests_run - self.tests_passed
            print(f"⚠️  {failed} test(s) failed - see details above")

def main():
    tester = LocalZipIntelTester()
    success = tester.run_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())