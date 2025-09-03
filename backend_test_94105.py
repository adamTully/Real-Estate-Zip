#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ZipIntel94105Tester:
    def __init__(self):
        # Use the exact URL from frontend/.env
        self.base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.test_zip = "94105"  # Specific ZIP requested for testing
        self.tests_run = 0
        self.tests_passed = 0
        
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
        
    def test_post_zip_analysis_94105(self):
        """Test POST /api/zip-analysis for ZIP 94105 - Check for rate limits and analysis_content"""
        try:
            print(f"\n🔍 Testing POST /api/zip-analysis for ZIP {self.test_zip}")
            payload = {"zip_code": self.test_zip}
            
            # Make the request with longer timeout for LLM processing
            response = requests.post(
                f"{self.api_url}/zip-analysis", 
                json=payload,
                timeout=60  # Longer timeout for OpenAI processing
            )
            
            print(f"Response Status: {response.status_code}")
            
            # Check for HTTP 200 response
            if response.status_code != 200:
                error_details = f"Status: {response.status_code}, Response: {response.text[:500]}"
                # Check specifically for rate limit or quota errors
                if "rate" in response.text.lower() or "quota" in response.text.lower() or "limit" in response.text.lower():
                    error_details += " - RATE LIMIT/QUOTA ERROR DETECTED"
                self.log_test("POST /api/zip-analysis HTTP 200", False, error_details)
                return False, None
            
            self.log_test("POST /api/zip-analysis HTTP 200", True, "Successful HTTP 200 response")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("POST Response JSON Parse", False, f"Invalid JSON: {str(e)}")
                return False, None
            
            self.log_test("POST Response JSON Parse", True, "Valid JSON response")
            
            # Verify required schema fields
            required_fields = [
                "id", "zip_code", "buyer_migration", "seo_youtube_trends",
                "content_strategy", "hidden_listings", "market_hooks", 
                "content_assets", "created_at", "updated_at"
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Schema Validation", False, f"Missing fields: {missing_fields}")
                return False, None
            
            self.log_test("Schema Validation", True, f"All required fields present: {len(required_fields)} fields")
            
            # Verify ZIP code matches
            if data.get("zip_code") != self.test_zip:
                self.log_test("ZIP Code Match", False, f"Expected {self.test_zip}, got {data.get('zip_code')}")
                return False, None
            
            self.log_test("ZIP Code Match", True, f"Correct ZIP code: {self.test_zip}")
            
            # Check for analysis_content strings in all sections
            sections_to_check = ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "content_assets"]
            analysis_content_results = []
            
            for section in sections_to_check:
                if section in data and isinstance(data[section], dict):
                    if "analysis_content" in data[section]:
                        content = data[section]["analysis_content"]
                        if isinstance(content, str) and len(content) > 50:  # Substantial content
                            analysis_content_results.append(f"✅ {section}: {len(content)} chars")
                            
                            # Check for rate limit indicators in content
                            if any(term in content.lower() for term in ["rate limit", "quota", "temporarily unavailable", "try again"]):
                                self.log_test(f"Analysis Content Quality - {section}", False, f"Rate limit/quota error in content: {content[:200]}...")
                                return False, None
                        else:
                            analysis_content_results.append(f"❌ {section}: Empty or too short")
                            self.log_test(f"Analysis Content - {section}", False, f"Content too short or empty: {len(content) if isinstance(content, str) else 'Not string'}")
                            return False, None
                    else:
                        analysis_content_results.append(f"❌ {section}: Missing analysis_content")
                        self.log_test(f"Analysis Content - {section}", False, "Missing analysis_content field")
                        return False, None
                else:
                    analysis_content_results.append(f"❌ {section}: Section missing or invalid")
                    self.log_test(f"Section Structure - {section}", False, "Section missing or not a dict")
                    return False, None
            
            # Log all analysis_content results
            self.log_test("All Sections Have analysis_content", True, "; ".join(analysis_content_results))
            
            # Check market_hooks for detailed_analysis (special case)
            if "market_hooks" in data and isinstance(data["market_hooks"], dict):
                if "detailed_analysis" in data["market_hooks"]:
                    detailed_content = data["market_hooks"]["detailed_analysis"]
                    if isinstance(detailed_content, str) and len(detailed_content) > 100:
                        self.log_test("Market Hooks detailed_analysis", True, f"Present with {len(detailed_content)} chars")
                    else:
                        self.log_test("Market Hooks detailed_analysis", False, "Too short or not string")
                        return False, None
                else:
                    self.log_test("Market Hooks detailed_analysis", False, "Missing detailed_analysis field")
                    return False, None
            
            # Verify UUID format for ID
            try:
                import uuid
                uuid.UUID(data["id"])
                self.log_test("ID UUID Format", True, f"Valid UUID: {data['id']}")
            except ValueError:
                self.log_test("ID UUID Format", False, f"Invalid UUID: {data['id']}")
                return False, None
            
            # Verify timestamps
            for timestamp_field in ["created_at", "updated_at"]:
                if timestamp_field in data:
                    try:
                        # Try to parse the timestamp
                        if isinstance(data[timestamp_field], str):
                            datetime.fromisoformat(data[timestamp_field].replace('Z', '+00:00'))
                        self.log_test(f"Timestamp {timestamp_field}", True, f"Valid timestamp format")
                    except ValueError:
                        self.log_test(f"Timestamp {timestamp_field}", False, f"Invalid timestamp format: {data[timestamp_field]}")
                        return False, None
            
            print(f"\n📊 POST Analysis Summary:")
            print(f"   ZIP Code: {data.get('zip_code')}")
            print(f"   Record ID: {data.get('id')}")
            print(f"   Created: {data.get('created_at')}")
            print(f"   All sections with analysis_content: ✅")
            print(f"   No rate limit/quota errors detected: ✅")
            
            return True, data
            
        except requests.exceptions.Timeout:
            self.log_test("POST /api/zip-analysis", False, "Request timeout - possible server overload")
            return False, None
        except requests.exceptions.ConnectionError as e:
            self.log_test("POST /api/zip-analysis", False, f"Connection error: {str(e)}")
            return False, None
        except Exception as e:
            self.log_test("POST /api/zip-analysis", False, f"Unexpected error: {str(e)}")
            return False, None
    
    def test_get_zip_analysis_94105(self):
        """Test GET /api/zip-analysis/{zip} for ZIP 94105"""
        try:
            print(f"\n🔍 Testing GET /api/zip-analysis/{self.test_zip}")
            
            response = requests.get(f"{self.api_url}/zip-analysis/{self.test_zip}", timeout=30)
            
            print(f"Response Status: {response.status_code}")
            
            # Check for HTTP 200 response
            if response.status_code != 200:
                self.log_test("GET /api/zip-analysis HTTP 200", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
            
            self.log_test("GET /api/zip-analysis HTTP 200", True, "Successful HTTP 200 response")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("GET Response JSON Parse", False, f"Invalid JSON: {str(e)}")
                return False
            
            self.log_test("GET Response JSON Parse", True, "Valid JSON response")
            
            # Verify ZIP code matches
            if data.get("zip_code") != self.test_zip:
                self.log_test("GET ZIP Code Match", False, f"Expected {self.test_zip}, got {data.get('zip_code')}")
                return False
            
            self.log_test("GET ZIP Code Match", True, f"Correct ZIP code: {self.test_zip}")
            
            # Verify same structure as POST response
            required_fields = ["id", "zip_code", "buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "market_hooks", "content_assets"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("GET Schema Validation", False, f"Missing fields: {missing_fields}")
                return False
            
            self.log_test("GET Schema Validation", True, f"All required fields present")
            
            print(f"\n📊 GET Analysis Summary:")
            print(f"   ZIP Code: {data.get('zip_code')}")
            print(f"   Record ID: {data.get('id')}")
            print(f"   Retrieved successfully: ✅")
            
            return True
            
        except Exception as e:
            self.log_test("GET /api/zip-analysis", False, f"Error: {str(e)}")
            return False
    
    def run_focused_test(self):
        """Run focused test for ZIP 94105 as requested"""
        print("🚀 ZIP Intel Generator - Focused Backend Test for ZIP 94105")
        print("📋 Testing after OpenAI funds added - checking for rate limit/quota resolution")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Step 1: POST /api/zip-analysis for ZIP 94105
        post_success, analysis_data = self.test_post_zip_analysis_94105()
        
        if not post_success:
            print("\n❌ POST test failed. Cannot proceed with GET test.")
            self.print_final_results()
            return False
        
        # Brief pause to ensure data is available
        time.sleep(2)
        
        # Step 2: GET /api/zip-analysis/{zip} for ZIP 94105
        get_success = self.test_get_zip_analysis_94105()
        
        # Print final results
        self.print_final_results()
        
        return post_success and get_success
    
    def print_final_results(self):
        """Print final test results"""
        print("\n" + "=" * 80)
        print(f"📊 Final Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            print("✅ No rate limit or quota errors detected")
            print("✅ All sections include analysis_content strings")
            print("✅ HTTP 200 responses confirmed")
            print("✅ Correct schema validation passed")
            print("✅ Backend API is fully functional after OpenAI funds addition")
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed.")
            print("❌ Issues detected - see details above")

def main():
    tester = ZipIntel94105Tester()
    success = tester.run_focused_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())