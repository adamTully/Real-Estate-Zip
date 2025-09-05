#!/usr/bin/env python3

import requests
import sys
import json
import os

class SimpleUserCreator:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Target user details from the request
        self.target_email = "territory1756780976@example.com"
        self.target_password = "testpass123"
        self.target_first_name = "Territory"
        self.target_last_name = "Test"
        
    def check_user_exists_and_login(self):
        """Check if user exists and can login"""
        try:
            login_payload = {
                "email": self.target_email,
                "password": self.target_password
            }
            
            print(f"🔍 Checking if user exists: {self.target_email}")
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User exists and credentials work!")
                print(f"   User ID: {data['user']['id']}")
                print(f"   Role: {data['user']['role']}")
                print(f"   Active: {data['user']['is_active']}")
                return True, data
            else:
                print(f"❌ User doesn't exist or credentials don't work (Status: {response.status_code})")
                return False, None
                
        except Exception as e:
            print(f"❌ Error checking user: {str(e)}")
            return False, None
    
    def create_user(self):
        """Create the test user"""
        try:
            register_payload = {
                "email": self.target_email,
                "password": self.target_password,
                "first_name": self.target_first_name,
                "last_name": self.target_last_name
            }
            
            print(f"🔨 Creating user: {self.target_email}")
            response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User created successfully!")
                print(f"   User ID: {data['user']['id']}")
                print(f"   Role: {data['user']['role']}")
                print(f"   Active: {data['user']['is_active']}")
                return True, data
            elif response.status_code == 400:
                # User already exists
                error_data = response.json()
                if "already registered" in error_data.get("detail", "").lower():
                    print(f"ℹ️  User already exists, trying to login...")
                    return self.check_user_exists_and_login()
                else:
                    print(f"❌ Registration failed: {error_data.get('detail')}")
                    return False, None
            else:
                print(f"❌ Registration failed (Status: {response.status_code}): {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return False, None
    
    def verify_login(self):
        """Final verification that login works"""
        try:
            login_payload = {
                "email": self.target_email,
                "password": self.target_password
            }
            
            print(f"🔐 Final login verification...")
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login verification successful!")
                return True, data
            else:
                print(f"❌ Login verification failed (Status: {response.status_code})")
                return False, None
                
        except Exception as e:
            print(f"❌ Error verifying login: {str(e)}")
            return False, None
    
    def run(self):
        """Main execution flow"""
        print("🚀 Simple User Creation for Manual Testing")
        print(f"📍 API URL: {self.api_url}")
        print("=" * 60)
        
        # Step 1: Check if user exists and can login
        user_exists, user_data = self.check_user_exists_and_login()
        
        if not user_exists:
            # Step 2: Create user if doesn't exist
            created, user_data = self.create_user()
            if not created:
                print("\n❌ FAILED: Could not create or verify user")
                return False
        
        # Step 3: Final verification
        verified, final_data = self.verify_login()
        
        if verified:
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! Working credentials ready:")
            print(f"✅ Email: {self.target_email}")
            print(f"✅ Password: {self.target_password}")
            print("\n📋 User Details:")
            print(f"   • Name: {final_data['user']['first_name']} {final_data['user']['last_name']}")
            print(f"   • Role: {final_data['user']['role']}")
            print(f"   • User ID: {final_data['user']['id']}")
            print(f"   • Active: {final_data['user']['is_active']}")
            print(f"   • Territories: {final_data['user']['owned_territories']}")
            print("\n🎯 Ready for manual testing of SEO & Social Media Trends features!")
            return True
        else:
            print("\n❌ FAILED: Could not verify final login")
            return False

def main():
    creator = SimpleUserCreator()
    success = creator.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())