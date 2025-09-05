#!/usr/bin/env python3

import requests
import json

def test_platform_generation():
    """Quick test of the individual platform generation system"""
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🚀 Quick Individual Platform Generation Test")
    print(f"📍 Testing against: {base_url}")
    print("=" * 60)
    
    # Step 1: Login with existing test user
    print("\n🔑 Step 1: Login with test user")
    login_payload = {
        "email": "territory1756780976@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/login", json=login_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            auth_token = data["access_token"]
            user_data = data["user"]
            owned_territories = user_data.get("owned_territories", [])
            print(f"✅ Login successful for {user_data['email']}")
            print(f"📍 Owned territories: {owned_territories}")
            
            if "10001" not in owned_territories:
                print("❌ User doesn't own ZIP 10001")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Test authentication requirement
    print("\n🚫 Step 2: Test authentication requirement")
    try:
        payload = {"zip_code": "10001"}
        response = requests.post(f"{api_url}/generate-platform-content/instagram", json=payload, timeout=30)
        if response.status_code in [401, 403]:
            print("✅ Correctly rejected unauthenticated request")
        else:
            print(f"❌ Unexpected status for unauthenticated request: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth test error: {e}")
    
    # Step 3: Test territory ownership validation
    print("\n🏠 Step 3: Test territory ownership validation")
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"zip_code": "90210"}  # User doesn't own this ZIP
        response = requests.post(f"{api_url}/generate-platform-content/instagram", json=payload, headers=headers, timeout=30)
        if response.status_code == 403:
            data = response.json()
            print(f"✅ Correctly rejected unowned territory: {data.get('detail', 'No detail')}")
        else:
            print(f"❌ Unexpected status for unowned territory: {response.status_code}")
    except Exception as e:
        print(f"❌ Territory test error: {e}")
    
    # Step 4: Test Instagram content generation
    print("\n📱 Step 4: Test Instagram content generation")
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"zip_code": "10001"}
        response = requests.post(f"{api_url}/generate-platform-content/instagram", json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Instagram content generation successful")
            print(f"📊 Response keys: {list(data.keys())}")
            
            if "instagram_posts" in data:
                posts = data["instagram_posts"]
                print(f"📝 Generated {len(posts)} Instagram posts")
                if posts:
                    first_post = posts[0]
                    print(f"📄 First post keys: {list(first_post.keys())}")
                    content_length = len(first_post.get("content", ""))
                    print(f"📏 Content length: {content_length} characters")
                    hashtags = first_post.get("hashtags", "")
                    print(f"🏷️ Hashtags: {hashtags[:100]}...")
            else:
                print("❌ No instagram_posts in response")
        else:
            print(f"❌ Instagram generation failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Instagram generation error: {e}")
    
    # Step 5: Test a few other platforms
    print("\n🌐 Step 5: Test other platforms")
    platforms = ["facebook", "tiktok", "linkedin"]
    
    for platform in platforms:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            payload = {"zip_code": "10001"}
            response = requests.post(f"{api_url}/generate-platform-content/{platform}", json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {platform.capitalize()} content generation successful")
                # Find the posts key (could be facebook_posts, tiktok_posts, etc.)
                posts_key = f"{platform}_posts"
                if posts_key in data:
                    posts_count = len(data[posts_key])
                    print(f"   📝 Generated {posts_count} {platform} posts")
                else:
                    # Look for any key with "posts" in it
                    posts_keys = [k for k in data.keys() if "posts" in k or "campaigns" in k]
                    if posts_keys:
                        print(f"   📝 Found content keys: {posts_keys}")
                    else:
                        print(f"   ⚠️ No posts found in response keys: {list(data.keys())}")
            else:
                print(f"❌ {platform.capitalize()} generation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {platform.capitalize()} generation error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Individual Platform Generation Test Complete!")
    return True

if __name__ == "__main__":
    test_platform_generation()