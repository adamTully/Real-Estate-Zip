#!/usr/bin/env python3

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

class DatabaseCleanup:
    def __init__(self):
        # MongoDB connection
        mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ['DB_NAME']]
        
        # Target data for cleanup
        self.target_user_email = "adamtest1@gmail.com"
        self.target_user_id = "99c94f7e-20fd-472a-85b4-6ef7caf5df1d"
        self.target_zip = "30126"
        
    async def log_action(self, action, success, details=""):
        """Log cleanup actions"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {action}")
        if details:
            print(f"   ℹ️  {details}")
    
    async def delete_analysis_data(self):
        """Delete analysis data for ZIP 30126"""
        try:
            # Find and delete from market_intelligence collection
            result = await self.db.market_intelligence.delete_many({"zip_code": self.target_zip})
            
            success = True
            details = f"Deleted {result.deleted_count} analysis record(s) for ZIP {self.target_zip}"
            await self.log_action("Delete Analysis Data", success, details)
            return success
            
        except Exception as e:
            await self.log_action("Delete Analysis Data", False, str(e))
            return False
    
    async def delete_status_data(self):
        """Delete status data for ZIP 30126"""
        try:
            # Find and delete from analysis_status collection
            result = await self.db.analysis_status.delete_many({"zip_code": self.target_zip})
            
            success = True
            details = f"Deleted {result.deleted_count} status record(s) for ZIP {self.target_zip}"
            await self.log_action("Delete Status Data", success, details)
            return success
            
        except Exception as e:
            await self.log_action("Delete Status Data", False, str(e))
            return False
    
    async def delete_user_account(self):
        """Delete user account adamtest1@gmail.com"""
        try:
            # Find and delete from users collection
            result = await self.db.users.delete_one({"email": self.target_user_email})
            
            success = result.deleted_count > 0
            details = f"Deleted {result.deleted_count} user record(s) for {self.target_user_email}"
            await self.log_action("Delete User Account", success, details)
            return success
            
        except Exception as e:
            await self.log_action("Delete User Account", False, str(e))
            return False
    
    async def verify_cleanup(self):
        """Verify that all data has been removed"""
        try:
            print("\n🔍 VERIFYING DATABASE CLEANUP:")
            print("=" * 50)
            
            # Check market_intelligence collection
            analysis_count = await self.db.market_intelligence.count_documents({"zip_code": self.target_zip})
            print(f"📊 Analysis records for ZIP {self.target_zip}: {analysis_count}")
            
            # Check analysis_status collection
            status_count = await self.db.analysis_status.count_documents({"zip_code": self.target_zip})
            print(f"📈 Status records for ZIP {self.target_zip}: {status_count}")
            
            # Check users collection
            user_count = await self.db.users.count_documents({"email": self.target_user_email})
            print(f"👤 User records for {self.target_user_email}: {user_count}")
            
            # Check for any references to the user ID
            user_id_refs = await self.db.users.count_documents({"_id": self.target_user_id})
            print(f"🔗 User ID references: {user_id_refs}")
            
            # Check for any territory assignments of ZIP 30126
            territory_refs = await self.db.users.count_documents({"owned_territories": self.target_zip})
            print(f"🏠 Territory assignments for ZIP {self.target_zip}: {territory_refs}")
            
            cleanup_complete = (analysis_count == 0 and status_count == 0 and 
                              user_count == 0 and user_id_refs == 0 and territory_refs == 0)
            
            await self.log_action("Verify Complete Cleanup", cleanup_complete, 
                                f"All data removed: {cleanup_complete}")
            
            return cleanup_complete
            
        except Exception as e:
            await self.log_action("Verify Cleanup", False, str(e))
            return False
    
    async def list_current_data(self):
        """List current data before cleanup"""
        try:
            print("🔍 CURRENT DATA BEFORE CLEANUP:")
            print("=" * 50)
            
            # Find analysis data
            analysis_docs = await self.db.market_intelligence.find({"zip_code": self.target_zip}).to_list(length=None)
            print(f"📊 Analysis records for ZIP {self.target_zip}: {len(analysis_docs)}")
            for doc in analysis_docs:
                print(f"   - ID: {doc.get('id', 'N/A')}, Created: {doc.get('created_at', 'N/A')}")
            
            # Find status data
            status_docs = await self.db.analysis_status.find({"zip_code": self.target_zip}).to_list(length=None)
            print(f"📈 Status records for ZIP {self.target_zip}: {len(status_docs)}")
            for doc in status_docs:
                print(f"   - Job ID: {doc.get('job_id', 'N/A')}, State: {doc.get('state', 'N/A')}")
            
            # Find user data
            user_docs = await self.db.users.find({"email": self.target_user_email}).to_list(length=None)
            print(f"👤 User records for {self.target_user_email}: {len(user_docs)}")
            for doc in user_docs:
                print(f"   - ID: {doc.get('_id', 'N/A')}, Territories: {doc.get('owned_territories', [])}")
            
            # Find any other users with this territory
            territory_users = await self.db.users.find({"owned_territories": self.target_zip}).to_list(length=None)
            print(f"🏠 Users with ZIP {self.target_zip}: {len(territory_users)}")
            for doc in territory_users:
                print(f"   - Email: {doc.get('email', 'N/A')}, ID: {doc.get('_id', 'N/A')}")
            
            return True
            
        except Exception as e:
            await self.log_action("List Current Data", False, str(e))
            return False
    
    async def run_cleanup(self):
        """Execute the complete database cleanup"""
        print("🗄️  EXECUTING DATABASE CLEANUP")
        print(f"🎯 Target: Remove all data for {self.target_user_email} and ZIP {self.target_zip}")
        print("=" * 80)
        
        # Step 1: List current data
        print("\n📋 Step 1: List Current Data")
        await self.list_current_data()
        
        # Step 2: Delete analysis data
        print(f"\n🗑️  Step 2: Delete Analysis Data")
        analysis_deleted = await self.delete_analysis_data()
        
        # Step 3: Delete status data
        print(f"\n🗑️  Step 3: Delete Status Data")
        status_deleted = await self.delete_status_data()
        
        # Step 4: Delete user account
        print(f"\n🗑️  Step 4: Delete User Account")
        user_deleted = await self.delete_user_account()
        
        # Step 5: Verify cleanup
        print(f"\n✅ Step 5: Verify Cleanup")
        cleanup_verified = await self.verify_cleanup()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 DATABASE CLEANUP SUMMARY")
        print("=" * 80)
        
        print(f"📊 Analysis data deletion: {'✅ SUCCESS' if analysis_deleted else '❌ FAILED'}")
        print(f"📈 Status data deletion: {'✅ SUCCESS' if status_deleted else '❌ FAILED'}")
        print(f"👤 User account deletion: {'✅ SUCCESS' if user_deleted else '❌ FAILED'}")
        print(f"✅ Cleanup verification: {'✅ COMPLETE' if cleanup_verified else '❌ INCOMPLETE'}")
        
        overall_success = analysis_deleted and status_deleted and user_deleted and cleanup_verified
        
        print(f"\n🎯 Overall Result: {'✅ CLEANUP SUCCESSFUL' if overall_success else '❌ CLEANUP FAILED'}")
        
        if overall_success:
            print(f"\n🎉 Database cleanup completed successfully!")
            print(f"   • All analysis data for ZIP {self.target_zip} removed")
            print(f"   • All status data for ZIP {self.target_zip} removed")
            print(f"   • User account {self.target_user_email} removed")
            print(f"   • ZIP {self.target_zip} is now available for new registration")
        else:
            print(f"\n⚠️ Database cleanup encountered issues. Please check the logs above.")
        
        # Close database connection
        self.client.close()
        
        return overall_success

async def main():
    cleanup = DatabaseCleanup()
    
    try:
        # Execute the cleanup
        success = await cleanup.run_cleanup()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))