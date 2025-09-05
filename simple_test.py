#!/usr/bin/env python3

import requests
import json

def test_user_and_data():
    base_url = "http://localhost:8001/api"
    
    # Test 1: Login user
    print("🔐 Testing user login...")
    login_data = {
        "email": "territory1756780976@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            user = data["user"]
            territories = user.get("owned_territories", [])
            
            print(f"✅ Login successful!")
            print(f"   User: {user['first_name']} {user['last_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Territories: {territories}")
            
            # Test 2: Check user profile
            print(f"\n👤 Testing user profile...")
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=15)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"✅ Profile retrieved: {profile_data['owned_territories']}")
            else:
                print(f"❌ Profile failed: {profile_response.status_code}")
            
            # Test 3: Check existing analysis data
            print(f"\n📊 Checking analysis data...")
            for zip_code in ["10001", "94105", "90210"]:
                try:
                    analysis_response = requests.get(f"{base_url}/zip-analysis/{zip_code}", timeout=15)
                    if analysis_response.status_code == 200:
                        analysis_data = analysis_response.json()
                        has_seo_social = "seo_social_trends" in analysis_data
                        has_old_field = "seo_youtube_trends" in analysis_data
                        
                        seo_content = analysis_data.get("seo_social_trends", {}).get("analysis_content", "")
                        
                        print(f"✅ ZIP {zip_code}: Data exists")
                        print(f"   • seo_social_trends field: {has_seo_social}")
                        print(f"   • old seo_youtube_trends field: {has_old_field}")
                        print(f"   • Content length: {len(seo_content)} chars")
                        
                        if has_seo_social and not has_old_field and len(seo_content) > 100:
                            print(f"   ✅ ZIP {zip_code} is ready for testing!")
                            
                            # Test 4: Assign this territory if not already assigned
                            if zip_code not in territories:
                                print(f"\n🗺️  Assigning territory {zip_code}...")
                                assign_data = {"zip_code": zip_code}
                                assign_response = requests.post(
                                    f"{base_url}/users/assign-territory", 
                                    json=assign_data, 
                                    headers=headers, 
                                    timeout=15
                                )
                                
                                if assign_response.status_code == 200:
                                    assign_result = assign_response.json()
                                    print(f"✅ Territory assigned: {assign_result.get('message')}")
                                else:
                                    print(f"❌ Assignment failed: {assign_response.status_code} - {assign_response.text[:100]}")
                            else:
                                print(f"   ✅ Territory {zip_code} already assigned to user")
                            
                            return True  # Found good data
                        
                    elif analysis_response.status_code == 404:
                        print(f"📊 ZIP {zip_code}: No data")
                    else:
                        print(f"❌ ZIP {zip_code}: Error {analysis_response.status_code}")
                        
                except Exception as e:
                    print(f"❌ ZIP {zip_code}: Exception - {str(e)}")
            
            # Test 5: Create new analysis if needed
            print(f"\n🔄 Creating new analysis for ZIP 10001...")
            create_data = {"zip_code": "10001"}
            create_response = requests.post(f"{base_url}/zip-analysis/start", json=create_data, timeout=30)
            
            if create_response.status_code == 200:
                create_result = create_response.json()
                print(f"✅ Analysis started: {create_result.get('state')} - {create_result.get('overall_percent')}%")
                return True
            else:
                print(f"❌ Analysis creation failed: {create_response.status_code}")
                return False
            
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_user_and_data()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")