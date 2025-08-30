#!/usr/bin/env python3

import requests
import json
import time

def test_backend_94105():
    """Simple test for ZIP 94105 backend functionality"""
    
    print("🚀 Backend Test for ZIP 94105 - Post OpenAI Funding")
    print("=" * 60)
    
    api_url = "http://localhost:8001/api"
    test_zip = "94105"
    
    # Test 1: API Root
    print("1️⃣ Testing API root...")
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ API root accessible")
        else:
            print(f"❌ API root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API root error: {str(e)}")
        return False
    
    # Test 2: Check for existing analysis
    print(f"\n2️⃣ Checking existing analysis for {test_zip}...")
    try:
        response = requests.get(f"{api_url}/zip-analysis/{test_zip}", timeout=10)
        if response.status_code == 200:
            print("✅ Found existing analysis for 94105")
            data = response.json()
            
            # Verify schema
            required_fields = ["id", "zip_code", "buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "market_hooks", "content_assets"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ Missing fields: {missing}")
                return False
            else:
                print("✅ Complete schema present")
            
            # Check analysis_content in sections
            sections = ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "content_assets"]
            analysis_check = []
            
            for section in sections:
                if section in data and isinstance(data[section], dict):
                    if "analysis_content" in data[section]:
                        content = data[section]["analysis_content"]
                        if isinstance(content, str) and len(content) > 20:
                            # Check for error indicators
                            if any(term in content.lower() for term in ["quota", "rate limit", "temporarily unavailable", "try again"]):
                                analysis_check.append(f"❌ {section}: Error detected")
                            else:
                                analysis_check.append(f"✅ {section}: OK ({len(content)} chars)")
                        else:
                            analysis_check.append(f"❌ {section}: Too short")
                    else:
                        analysis_check.append(f"❌ {section}: No analysis_content")
                else:
                    analysis_check.append(f"❌ {section}: Missing/invalid")
            
            print("📊 Analysis Content Check:")
            for check in analysis_check:
                print(f"   {check}")
            
            # Check market_hooks detailed_analysis
            if "market_hooks" in data and "detailed_analysis" in data["market_hooks"]:
                detailed = data["market_hooks"]["detailed_analysis"]
                if isinstance(detailed, str) and len(detailed) > 50:
                    print("✅ market_hooks detailed_analysis: Present")
                else:
                    print("❌ market_hooks detailed_analysis: Missing/short")
            else:
                print("❌ market_hooks detailed_analysis: Missing")
            
            # Check for any error indicators
            has_errors = any("❌" in check for check in analysis_check)
            if not has_errors:
                print("\n🎉 GET /api/zip-analysis/94105 - ALL CHECKS PASSED")
                print("✅ No quota/rate limit errors detected")
                print("✅ All sections have analysis_content strings")
                print("✅ HTTP 200 response confirmed")
                print("✅ Correct schema validation passed")
                return True
            else:
                print("\n❌ Some checks failed - see details above")
                return False
                
        elif response.status_code == 404:
            print("ℹ️ No existing analysis found - need to create new one")
            
            # Test 3: Create new analysis
            print(f"\n3️⃣ Creating new analysis for {test_zip}...")
            try:
                payload = {"zip_code": test_zip}
                response = requests.post(f"{api_url}/zip-analysis", json=payload, timeout=60)
                
                if response.status_code == 200:
                    print("✅ POST /api/zip-analysis successful")
                    data = response.json()
                    
                    # Quick validation
                    if data.get("zip_code") == test_zip and "id" in data:
                        print(f"✅ Created analysis with ID: {data['id']}")
                        
                        # Check for analysis_content
                        sections = ["buyer_migration", "seo_youtube_trends", "content_strategy", "hidden_listings", "content_assets"]
                        all_good = True
                        
                        for section in sections:
                            if section in data and isinstance(data[section], dict) and "analysis_content" in data[section]:
                                content = data[section]["analysis_content"]
                                if isinstance(content, str) and len(content) > 20:
                                    if any(term in content.lower() for term in ["quota", "rate limit", "temporarily unavailable"]):
                                        print(f"❌ {section}: Quota/rate limit error detected")
                                        all_good = False
                                    else:
                                        print(f"✅ {section}: analysis_content OK")
                                else:
                                    print(f"❌ {section}: analysis_content too short")
                                    all_good = False
                            else:
                                print(f"❌ {section}: Missing analysis_content")
                                all_good = False
                        
                        if all_good:
                            print("\n🎉 POST /api/zip-analysis - ALL CHECKS PASSED")
                            print("✅ No quota/rate limit errors detected")
                            print("✅ All sections have analysis_content strings")
                            return True
                        else:
                            print("\n❌ POST analysis has issues - see details above")
                            return False
                    else:
                        print("❌ Invalid response structure")
                        return False
                else:
                    error_text = response.text[:300]
                    if any(term in error_text.lower() for term in ["quota", "rate limit", "billing"]):
                        print(f"❌ QUOTA/RATE LIMIT ERROR: {error_text}")
                    else:
                        print(f"❌ POST failed: {response.status_code} - {error_text}")
                    return False
                    
            except requests.exceptions.Timeout:
                print("❌ POST request timed out - OpenAI processing may be slow")
                return False
            except Exception as e:
                print(f"❌ POST error: {str(e)}")
                return False
        else:
            print(f"❌ GET failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GET error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_backend_94105()
    if success:
        print("\n🎯 BACKEND TEST RESULT: SUCCESS")
        print("Backend API is working correctly after OpenAI funds were added")
    else:
        print("\n🎯 BACKEND TEST RESULT: FAILED")
        print("Issues detected - see details above")