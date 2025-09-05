#!/usr/bin/env python3

import requests
import json

def test_endpoints():
    """Quick test of the endpoints mentioned in the review request"""
    base_url = "https://territory-hub-2.preview.emergentagent.com/api"
    
    print("🔍 Testing endpoints mentioned in review request...")
    print("=" * 60)
    
    # Test 1: POST /api/zip-analysis/start with ZIP code "10001"
    print("\n1️⃣ Testing POST /api/zip-analysis/start with ZIP 10001...")
    try:
        payload = {"zip_code": "10001"}
        response = requests.post(f"{base_url}/zip-analysis/start", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST /api/zip-analysis/start - SUCCESS")
            print(f"   State: {data.get('state')}")
            print(f"   Progress: {data.get('overall_percent')}%")
            
            # Check for new field names in tasks
            tasks = data.get('tasks', {})
            if 'seo_social_trends' in tasks:
                print(f"   ✅ New field 'seo_social_trends' found in tasks")
            else:
                print(f"   ❌ New field 'seo_social_trends' NOT found in tasks")
                
            if 'seo_youtube_trends' in tasks:
                print(f"   ❌ Old field 'seo_youtube_trends' still present!")
            else:
                print(f"   ✅ Old field 'seo_youtube_trends' correctly removed")
        else:
            print(f"❌ POST /api/zip-analysis/start - FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ POST /api/zip-analysis/start - ERROR: {str(e)}")
    
    # Test 2: GET /api/zip-analysis/status/10001
    print("\n2️⃣ Testing GET /api/zip-analysis/status/10001...")
    try:
        response = requests.get(f"{base_url}/zip-analysis/status/10001", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/zip-analysis/status/10001 - SUCCESS")
            print(f"   State: {data.get('state')}")
            print(f"   Progress: {data.get('overall_percent')}%")
            
            # Check task progress shows new field names
            tasks = data.get('tasks', {})
            if 'seo_social_trends' in tasks:
                task_info = tasks['seo_social_trends']
                print(f"   ✅ seo_social_trends task: {task_info.get('status')} ({task_info.get('percent')}%)")
            else:
                print(f"   ❌ seo_social_trends task not found")
        else:
            print(f"❌ GET /api/zip-analysis/status/10001 - FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ GET /api/zip-analysis/status/10001 - ERROR: {str(e)}")
    
    # Test 3: GET /api/zip-analysis/10001
    print("\n3️⃣ Testing GET /api/zip-analysis/10001...")
    try:
        response = requests.get(f"{base_url}/zip-analysis/10001", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/zip-analysis/10001 - SUCCESS")
            
            # Check for new field name in response
            if 'seo_social_trends' in data:
                seo_data = data['seo_social_trends']
                print(f"   ✅ Response has 'seo_social_trends' field")
                print(f"   Summary: {seo_data.get('summary', 'No summary')[:100]}...")
                
                # Check for platform-specific content
                analysis_content = seo_data.get('analysis_content', '')
                platforms = ['Facebook', 'Instagram', 'Twitter', 'TikTok']
                found_platforms = [p for p in platforms if p.lower() in analysis_content.lower()]
                
                if len(found_platforms) >= 2:
                    print(f"   ✅ Platform-specific content found: {found_platforms}")
                else:
                    print(f"   ⚠️  Limited platform mentions: {found_platforms}")
            else:
                print(f"   ❌ Response missing 'seo_social_trends' field")
                
            if 'seo_youtube_trends' in data:
                print(f"   ❌ Old field 'seo_youtube_trends' still present!")
            else:
                print(f"   ✅ Old field 'seo_youtube_trends' correctly removed")
                
            # Check content strategy enhancements
            if 'content_strategy' in data:
                strategy_data = data['content_strategy']
                analysis_content = strategy_data.get('analysis_content', '')
                
                # Look for platform-specific strategies
                strategy_platforms = ['blog', 'email', 'Facebook', 'YouTube', 'Instagram', 'TikTok', 'Snapchat']
                found_strategy_platforms = [p for p in strategy_platforms if p.lower() in analysis_content.lower()]
                
                if len(found_strategy_platforms) >= 5:
                    print(f"   ✅ Enhanced content strategy with {len(found_strategy_platforms)} platforms")
                else:
                    print(f"   ⚠️  Content strategy may need enhancement (found {len(found_strategy_platforms)} platforms)")
        else:
            print(f"❌ GET /api/zip-analysis/10001 - FAILED (Status: {response.status_code})")
            if response.status_code == 404:
                print("   ℹ️  Analysis not found - may need to wait for completion or create new analysis")
    except Exception as e:
        print(f"❌ GET /api/zip-analysis/10001 - ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Endpoint testing complete!")

if __name__ == "__main__":
    test_endpoints()