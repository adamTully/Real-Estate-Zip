#!/usr/bin/env python3

import requests
import sys
import json
import time

def run_zip_analysis_for_30126():
    """Run ZIP analysis for 30126 to enable Content Generation Hub"""
    
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    zip_code = "30126"
    
    print(f"🚀 Running ZIP Analysis for {zip_code}")
    print(f"📍 API: {api_url}")
    print("=" * 60)
    
    try:
        # Step 1: Start ZIP analysis
        print(f"\n📝 Step 1: Starting ZIP analysis for {zip_code}")
        payload = {"zip_code": zip_code}
        response = requests.post(f"{api_url}/zip-analysis/start", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print(f"✅ Analysis started successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   State: {data.get('state')}")
            print(f"   Progress: {data.get('overall_percent', 0)}%")
        else:
            print(f"❌ Failed to start analysis: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        # Step 2: Monitor progress
        print(f"\n📊 Step 2: Monitoring analysis progress...")
        max_wait_time = 300  # 5 minutes
        check_interval = 15  # 15 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            time.sleep(check_interval)
            elapsed_time += check_interval
            
            # Check status
            status_response = requests.get(f"{api_url}/zip-analysis/status/{zip_code}", timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                state = status_data.get("state", "unknown")
                progress = status_data.get("overall_percent", 0)
                
                print(f"   ⏳ Progress: {progress}%, State: {state} (elapsed: {elapsed_time}s)")
                
                if state == "done":
                    print(f"✅ Analysis completed successfully!")
                    break
                elif state == "failed":
                    print(f"❌ Analysis failed!")
                    return False
            else:
                print(f"⚠️  Status check failed: {status_response.status_code}")
        
        if elapsed_time >= max_wait_time:
            print(f"⏰ Analysis taking longer than expected ({max_wait_time}s)")
            print("   This is normal for first-time analysis with LLM generation")
        
        # Step 3: Verify analysis data exists
        print(f"\n🔍 Step 3: Verifying analysis data...")
        analysis_response = requests.get(f"{api_url}/zip-analysis/{zip_code}", timeout=10)
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()
            print(f"✅ Analysis data retrieved successfully!")
            print(f"   ZIP Code: {analysis_data.get('zip_code')}")
            print(f"   Created: {analysis_data.get('created_at')}")
            
            # Check key sections
            sections = ["buyer_migration", "seo_social_trends", "content_strategy", "content_assets"]
            for section in sections:
                if section in analysis_data:
                    section_data = analysis_data[section]
                    summary = section_data.get("summary", "No summary")
                    print(f"   ✅ {section}: {summary[:50]}...")
                else:
                    print(f"   ❌ {section}: Missing")
            
            return True
        else:
            print(f"❌ Failed to retrieve analysis data: {analysis_response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error running ZIP analysis: {str(e)}")
        return False

def test_content_generation_after_analysis():
    """Test content generation access after analysis is complete"""
    
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    zip_code = "30126"
    user_email = "adamtest3@gmail.com"
    user_password = "adamtest3"
    
    print(f"\n🎨 Testing Content Generation Hub Access")
    print("=" * 60)
    
    try:
        # Login as adamtest3@gmail.com
        print(f"🔑 Logging in as {user_email}")
        login_payload = {"email": user_email, "password": user_password}
        login_response = requests.post(f"{api_url}/auth/login", json=login_payload, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        login_data = login_response.json()
        auth_token = login_data["access_token"]
        user_data = login_data["user"]
        owned_territories = user_data.get("owned_territories", [])
        
        print(f"✅ Login successful!")
        print(f"   User: {user_data.get('email')}")
        print(f"   Owned territories: {owned_territories}")
        
        if zip_code not in owned_territories:
            print(f"❌ User doesn't own ZIP {zip_code}")
            return False
        
        # Test Instagram content generation
        print(f"\n📱 Testing Instagram content generation for ZIP {zip_code}")
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"zip_code": zip_code}
        
        content_response = requests.post(
            f"{api_url}/generate-platform-content/instagram", 
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if content_response.status_code == 200:
            content_data = content_response.json()
            instagram_posts = content_data.get("instagram_posts", [])
            print(f"✅ Content generation successful!")
            print(f"   Generated {len(instagram_posts)} Instagram posts")
            
            if instagram_posts:
                first_post = instagram_posts[0]
                print(f"   First post title: {first_post.get('title', 'No title')[:50]}...")
                print(f"   Content length: {len(first_post.get('content', ''))} characters")
            
            return True
        else:
            print(f"❌ Content generation failed: {content_response.status_code}")
            print(f"   Response: {content_response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing content generation: {str(e)}")
        return False

def main():
    print("🔧 FIXING TERRITORY ASSIGNMENT FOR adamtest3@gmail.com")
    print("🎯 Running ZIP analysis for 30126 to enable Content Generation Hub")
    print("=" * 80)
    
    # Run ZIP analysis
    analysis_success = run_zip_analysis_for_30126()
    
    if analysis_success:
        # Test content generation
        content_success = test_content_generation_after_analysis()
        
        if content_success:
            print("\n🎉 SUCCESS: Territory assignment issue completely resolved!")
            print("✅ User adamtest3@gmail.com can now:")
            print("   - See ZIP 30126 in their dashboard")
            print("   - Access Content Generation Hub for ZIP 30126")
            print("   - Generate platform-specific content")
            return 0
        else:
            print("\n⚠️  PARTIAL SUCCESS: Analysis completed but content generation needs verification")
            return 1
    else:
        print("\n❌ FAILED: Could not complete ZIP analysis")
        return 1

if __name__ == "__main__":
    sys.exit(main())