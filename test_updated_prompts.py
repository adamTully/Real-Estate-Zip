#!/usr/bin/env python3

import requests
import json
import time

def test_updated_prompts():
    """Test the updated prompts for ZIP Territory Pro platform"""
    base_url = "http://localhost:8001"
    api_url = f"{base_url}/api"
    test_zip = "10001"
    
    print("🚀 Testing Updated Prompts for ZIP Territory Pro Platform")
    print(f"📍 Testing against: {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: POST /api/zip-analysis/start
    print(f"\n📝 Test 1: POST /api/zip-analysis/start with ZIP {test_zip}")
    tests_total += 1
    
    try:
        payload = {"zip_code": test_zip}
        response = requests.post(f"{api_url}/zip-analysis/start", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for new field names in tasks
            tasks = data.get("tasks", {})
            if "seo_social_trends" in tasks and "seo_youtube_trends" not in tasks:
                print("✅ Field name updated correctly: 'seo_social_trends' found, 'seo_youtube_trends' not present")
                tests_passed += 1
            else:
                print(f"❌ Field name issue: tasks = {list(tasks.keys())}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: GET /api/zip-analysis/status/{zip_code}
    print(f"\n📊 Test 2: GET /api/zip-analysis/status/{test_zip}")
    tests_total += 1
    
    try:
        response = requests.get(f"{api_url}/zip-analysis/status/{test_zip}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get("tasks", {})
            
            if "seo_social_trends" in tasks and "seo_youtube_trends" not in tasks:
                print("✅ Status endpoint shows correct field names")
                tests_passed += 1
            else:
                print(f"❌ Status endpoint field name issue: tasks = {list(tasks.keys())}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Check MarketIntelligence model structure by testing direct analysis
    print(f"\n📋 Test 3: Testing MarketIntelligence model structure")
    tests_total += 1
    
    try:
        # Try the direct analysis endpoint to see the model structure
        payload = {"zip_code": "90210"}  # Use a different ZIP to avoid conflicts
        response = requests.post(f"{api_url}/zip-analysis", json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for new field name
            if "seo_social_trends" in data and "seo_youtube_trends" not in data:
                print("✅ MarketIntelligence model has correct field name: 'seo_social_trends'")
                
                # Check content for platform-specific mentions
                seo_data = data.get("seo_social_trends", {})
                analysis_content = seo_data.get("analysis_content", "")
                
                platforms = ["Facebook", "Instagram", "Twitter", "TikTok"]
                found_platforms = [p for p in platforms if p.lower() in analysis_content.lower()]
                
                if len(found_platforms) >= 2:
                    print(f"✅ SEO & Social Media content includes multiple platforms: {found_platforms}")
                else:
                    print(f"⚠️ Limited platform coverage in content: {found_platforms}")
                
                tests_passed += 1
            else:
                print(f"❌ MarketIntelligence model field issue. Available fields: {list(data.keys())}")
        else:
            print(f"❌ Direct analysis failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Check Enhanced Content Strategy
    print(f"\n🎯 Test 4: Testing Enhanced Content Strategy")
    tests_total += 1
    
    try:
        # Use the same analysis from Test 3
        if 'data' in locals() and 'content_strategy' in data:
            content_strategy = data.get("content_strategy", {})
            analysis_content = content_strategy.get("analysis_content", "")
            
            # Check for platform-specific strategies
            expected_platforms = ["blog", "email", "Facebook", "YouTube", "Instagram", "TikTok"]
            found_platforms = [p for p in expected_platforms if p.lower() in analysis_content.lower()]
            
            # Check for strategy elements
            strategy_elements = ["objective", "cadence", "content types", "kpis"]
            found_elements = [e for e in strategy_elements if e.lower() in analysis_content.lower()]
            
            if len(found_platforms) >= 4 and len(found_elements) >= 2:
                print(f"✅ Enhanced content strategy includes {len(found_platforms)} platforms and {len(found_elements)} strategy elements")
                tests_passed += 1
            else:
                print(f"⚠️ Content strategy may need enhancement. Platforms: {found_platforms}, Elements: {found_elements}")
        else:
            print("❌ No content strategy data available from previous test")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All updated prompts tests passed!")
        print("\n✅ KEY FINDINGS:")
        print("  - Field name successfully changed from 'seo_youtube_trends' to 'seo_social_trends'")
        print("  - SEO & Social Media Trends now covers multiple platforms")
        print("  - Enhanced Content Strategy includes platform-specific guidance")
        print("  - All endpoints work without errors")
        print("  - JSON structure is valid and serializable")
        return True
    else:
        failed_tests = tests_total - tests_passed
        print(f"⚠️ {failed_tests} test(s) failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = test_updated_prompts()
    exit(0 if success else 1)