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

class FinalCleanup:
    def __init__(self):
        # MongoDB connection
        mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ['DB_NAME']]
        
        # Target data for cleanup
        self.target_zip = "30126"
        
    async def log_action(self, action, success, details=""):
        """Log cleanup actions"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {action}")
        if details:
            print(f"   ℹ️  {details}")
    
    async def remove_all_territory_assignments(self):
        """Remove ZIP 30126 from all users"""
        try:
            # Find all users with ZIP 30126
            users_with_zip = await self.db.users.find({"owned_territories": self.target_zip}).to_list(length=None)
            
            print(f"🔍 Found {len(users_with_zip)} user(s) with ZIP {self.target_zip}:")
            for user in users_with_zip:
                print(f"   - Email: {user.get('email', 'N/A')}, ID: {user.get('_id', 'N/A')}")
            
            # Remove ZIP from all users
            result = await self.db.users.update_many(
                {"owned_territories": self.target_zip},
                {"$pull": {"owned_territories": self.target_zip}}
            )
            
            success = True
            details = f"Removed ZIP {self.target_zip} from {result.modified_count} user(s)"
            await self.log_action("Remove All Territory Assignments", success, details)
            
            return success
            
        except Exception as e:
            await self.log_action("Remove All Territory Assignments", False, str(e))
            return False
    
    async def delete_dummy_users(self):
        """Delete any dummy cleanup users"""
        try:
            # Find and delete dummy users created during cleanup
            result = await self.db.users.delete_many({"email": {"$regex": "dummy_cleanup_.*@example.com"}})
            
            success = True
            details = f"Deleted {result.deleted_count} dummy cleanup user(s)"
            await self.log_action("Delete Dummy Users", success, details)
            
            return success
            
        except Exception as e:
            await self.log_action("Delete Dummy Users", False, str(e))
            return False
    
    async def verify_complete_cleanup(self):
        """Final verification that ZIP 30126 is completely clean"""
        try:
            print("\n🔍 FINAL CLEANUP VERIFICATION:")
            print("=" * 50)
            
            # Check market_intelligence collection
            analysis_count = await self.db.market_intelligence.count_documents({"zip_code": self.target_zip})
            print(f"📊 Analysis records for ZIP {self.target_zip}: {analysis_count}")
            
            # Check analysis_status collection
            status_count = await self.db.analysis_status.count_documents({"zip_code": self.target_zip})
            print(f"📈 Status records for ZIP {self.target_zip}: {status_count}")
            
            # Check for any territory assignments of ZIP 30126
            territory_refs = await self.db.users.count_documents({"owned_territories": self.target_zip})
            print(f"🏠 Territory assignments for ZIP {self.target_zip}: {territory_refs}")
            
            # Check for adamtest1@gmail.com user
            adamtest_count = await self.db.users.count_documents({"email": "adamtest1@gmail.com"})
            print(f"👤 adamtest1@gmail.com user records: {adamtest_count}")
            
            # Check for dummy users
            dummy_count = await self.db.users.count_documents({"email": {"$regex": "dummy_cleanup_.*@example.com"}})
            print(f"🤖 Dummy cleanup users: {dummy_count}")
            
            cleanup_complete = (analysis_count == 0 and status_count == 0 and 
                              territory_refs == 0 and adamtest_count == 0 and dummy_count == 0)
            
            await self.log_action("Final Cleanup Verification", cleanup_complete, 
                                f"ZIP {self.target_zip} completely clean: {cleanup_complete}")
            
            return cleanup_complete
            
        except Exception as e:
            await self.log_action("Final Cleanup Verification", False, str(e))
            return False
    
    async def run_final_cleanup(self):
        """Execute the final cleanup steps"""
        print("🧹 EXECUTING FINAL CLEANUP")
        print(f"🎯 Target: Complete cleanup of ZIP {self.target_zip}")
        print("=" * 60)
        
        # Step 1: Remove all territory assignments
        print(f"\n🗑️  Step 1: Remove All Territory Assignments")
        territories_removed = await self.remove_all_territory_assignments()
        
        # Step 2: Delete dummy users
        print(f"\n🗑️  Step 2: Delete Dummy Users")
        dummies_deleted = await self.delete_dummy_users()
        
        # Step 3: Final verification
        print(f"\n✅ Step 3: Final Verification")
        cleanup_verified = await self.verify_complete_cleanup()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 FINAL CLEANUP SUMMARY")
        print("=" * 60)
        
        print(f"🏠 Territory assignments removed: {'✅ SUCCESS' if territories_removed else '❌ FAILED'}")
        print(f"🤖 Dummy users deleted: {'✅ SUCCESS' if dummies_deleted else '❌ FAILED'}")
        print(f"✅ Final verification: {'✅ COMPLETE' if cleanup_verified else '❌ INCOMPLETE'}")
        
        overall_success = territories_removed and dummies_deleted and cleanup_verified
        
        print(f"\n🎯 Overall Result: {'✅ CLEANUP SUCCESSFUL' if overall_success else '❌ CLEANUP FAILED'}")
        
        if overall_success:
            print(f"\n🎉 Final cleanup completed successfully!")
            print(f"   • ZIP {self.target_zip} is completely clean")
            print(f"   • No analysis data remains")
            print(f"   • No status data remains")
            print(f"   • No user owns ZIP {self.target_zip}")
            print(f"   • adamtest1@gmail.com user removed")
            print(f"   • All dummy users removed")
            print(f"   • ZIP {self.target_zip} is now available for new registration")
        else:
            print(f"\n⚠️ Final cleanup encountered issues. Please check the logs above.")
        
        # Close database connection
        self.client.close()
        
        return overall_success

async def main():
    cleanup = FinalCleanup()
    
    try:
        # Execute the final cleanup
        success = await cleanup.run_final_cleanup()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))