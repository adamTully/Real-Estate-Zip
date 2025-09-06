#!/usr/bin/env python3

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import requests
import time

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

class CompleteCleanup:
    def __init__(self):
        # MongoDB connection
        mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ['DB_NAME']]
        
        # API connection
        self.base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Target data for cleanup
        self.target_zip = "30126"
        
    async def log_action(self, action, success, details=""):
        """Log cleanup actions"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {action}")
        if details:
            print(f"   ℹ️  {details}")
    
    async def complete_zip_cleanup(self):
        """Remove ZIP 30126 from ALL users and delete ALL related data"""
        try:
            print(f"🧹 COMPLETE CLEANUP FOR ZIP {self.target_zip}")
            print("=" * 60)
            
            # Step 1: Find all users with ZIP 30126
            users_with_zip = await self.db.users.find({"owned_territories": self.target_zip}).to_list(length=None)
            print(f"🔍 Found {len(users_with_zip)} user(s) with ZIP {self.target_zip}:")
            for user in users_with_zip:
                print(f"   - Email: {user.get('email', 'N/A')}, ID: {user.get('_id', 'N/A')}")
            
            # Step 2: Remove ZIP from all users
            if users_with_zip:
                result = await self.db.users.update_many(
                    {"owned_territories": self.target_zip},
                    {"$pull": {"owned_territories": self.target_zip}}
                )
                await self.log_action("Remove ZIP from All Users", True, 
                                    f"Removed ZIP {self.target_zip} from {result.modified_count} user(s)")
            
            # Step 3: Delete all analysis data for ZIP 30126
            analysis_result = await self.db.market_intelligence.delete_many({"zip_code": self.target_zip})
            await self.log_action("Delete All Analysis Data", True, 
                                f"Deleted {analysis_result.deleted_count} analysis record(s)")
            
            # Step 4: Delete all status data for ZIP 30126
            status_result = await self.db.analysis_status.delete_many({"zip_code": self.target_zip})
            await self.log_action("Delete All Status Data", True, 
                                f"Deleted {status_result.deleted_count} status record(s)")
            
            # Step 5: Delete test users created during cleanup
            test_users_result = await self.db.users.delete_many({
                "email": {"$regex": "(newuser_|fresh_user_|cleanup_admin_|dummy_cleanup_).*@example.com"}
            })
            await self.log_action("Delete Test Users", True, 
                                f"Deleted {test_users_result.deleted_count} test user(s)")
            
            return True
            
        except Exception as e:
            await self.log_action("Complete ZIP Cleanup", False, str(e))
            return False
    
    async def verify_complete_cleanup(self):
        """Final verification that ZIP 30126 is completely available"""
        try:
            print(f"\n🔍 FINAL VERIFICATION:")
            print("=" * 40)
            
            # Check database
            analysis_count = await self.db.market_intelligence.count_documents({"zip_code": self.target_zip})
            status_count = await self.db.analysis_status.count_documents({"zip_code": self.target_zip})
            territory_refs = await self.db.users.count_documents({"owned_territories": self.target_zip})
            adamtest_count = await self.db.users.count_documents({"email": "adamtest1@gmail.com"})
            
            print(f"📊 Analysis records: {analysis_count}")
            print(f"📈 Status records: {status_count}")
            print(f"🏠 Territory assignments: {territory_refs}")
            print(f"👤 adamtest1@gmail.com: {adamtest_count}")
            
            database_clean = (analysis_count == 0 and status_count == 0 and 
                            territory_refs == 0 and adamtest_count == 0)
            
            await self.log_action("Database Verification", database_clean, 
                                f"Database completely clean: {database_clean}")
            
            return database_clean
            
        except Exception as e:
            await self.log_action("Final Verification", False, str(e))
            return False
    
    def test_fresh_registration(self):
        """Test that a completely fresh user can register and claim ZIP 30126"""
        try:
            print(f"\n🆕 TESTING FRESH REGISTRATION:")
            print("=" * 40)
            
            timestamp = int(time.time())
            fresh_user_payload = {
                "email": f"final_test_{timestamp}@example.com",
                "password": "finaltest123",
                "first_name": "Final",
                "last_name": "Test"
            }
            
            # Register user
            register_response = requests.post(f"{self.api_url}/auth/register", json=fresh_user_payload, timeout=10)
            if register_response.status_code != 200:
                print(f"❌ Registration failed: {register_response.status_code}")
                return False
            
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_email = fresh_user_payload["email"]
            
            print(f"✅ User registered: {user_email}")
            
            # Assign territory
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": self.target_zip}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            if assign_response.status_code != 200:
                print(f"❌ Territory assignment failed: {assign_response.status_code}, {assign_response.text[:100]}")
                return False
            
            print(f"✅ ZIP {self.target_zip} assigned successfully")
            
            # Verify profile
            profile_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                owned_territories = profile_data.get("owned_territories", [])
                if self.target_zip in owned_territories:
                    print(f"✅ Profile verification: User owns ZIP {self.target_zip}")
                    return True
                else:
                    print(f"❌ Profile verification failed: {owned_territories}")
                    return False
            else:
                print(f"❌ Profile check failed: {profile_response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Fresh registration test failed: {str(e)}")
            return False
    
    async def run_complete_cleanup(self):
        """Execute complete cleanup and verification"""
        print("🧹 COMPLETE USER DATA CLEANUP")
        print(f"🎯 Target: Complete clean slate for ZIP {self.target_zip}")
        print("=" * 80)
        
        # Step 1: Complete cleanup
        cleanup_success = await self.complete_zip_cleanup()
        
        # Step 2: Database verification
        db_verified = await self.verify_complete_cleanup()
        
        # Step 3: API verification
        print(f"\n🌐 API VERIFICATION:")
        api_verified = self.test_fresh_registration()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 COMPLETE CLEANUP SUMMARY")
        print("=" * 80)
        
        print(f"🧹 Database cleanup: {'✅ SUCCESS' if cleanup_success else '❌ FAILED'}")
        print(f"🗄️  Database verification: {'✅ CLEAN' if db_verified else '❌ DIRTY'}")
        print(f"🌐 API verification: {'✅ SUCCESS' if api_verified else '❌ FAILED'}")
        
        overall_success = cleanup_success and db_verified and api_verified
        
        print(f"\n🎯 Overall Result: {'✅ COMPLETE SUCCESS' if overall_success else '❌ ISSUES REMAIN'}")
        
        if overall_success:
            print(f"\n🎉 Complete cleanup successful!")
            print(f"   • All data for adamtest1@gmail.com removed")
            print(f"   • All analysis data for ZIP {self.target_zip} removed")
            print(f"   • All status data for ZIP {self.target_zip} removed")
            print(f"   • ZIP {self.target_zip} completely available")
            print(f"   • Fresh users can register and claim ZIP {self.target_zip}")
            print(f"   • System ready for enhanced prompts testing")
        else:
            print(f"\n⚠️ Cleanup issues remain. Check logs above.")
        
        # Close database connection
        self.client.close()
        
        return overall_success

async def main():
    cleanup = CompleteCleanup()
    
    try:
        success = await cleanup.run_complete_cleanup()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))