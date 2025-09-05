#!/usr/bin/env python3

import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def migrate_field_names():
    """Migrate seo_youtube_trends to seo_social_trends in existing records"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = pymongo.MongoClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    collection = db.market_intelligence
    
    print("🔄 Starting field name migration...")
    
    # Find all records with the old field name
    old_records = list(collection.find({"seo_youtube_trends": {"$exists": True}}))
    print(f"📊 Found {len(old_records)} records with old field name 'seo_youtube_trends'")
    
    updated_count = 0
    
    for record in old_records:
        try:
            # Get the old field data
            old_data = record.get("seo_youtube_trends")
            
            if old_data:
                # Update the record: rename field and remove old field
                result = collection.update_one(
                    {"_id": record["_id"]},
                    {
                        "$set": {"seo_social_trends": old_data},
                        "$unset": {"seo_youtube_trends": ""}
                    }
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Updated record for ZIP {record.get('zip_code', 'unknown')}")
                else:
                    print(f"⚠️  No changes made for ZIP {record.get('zip_code', 'unknown')}")
            else:
                print(f"⚠️  Empty old field data for ZIP {record.get('zip_code', 'unknown')}")
                
        except Exception as e:
            print(f"❌ Error updating record {record.get('zip_code', 'unknown')}: {str(e)}")
    
    print(f"\n✅ Migration completed: {updated_count}/{len(old_records)} records updated")
    
    # Verify the migration
    print("\n🔍 Verifying migration...")
    remaining_old = collection.count_documents({"seo_youtube_trends": {"$exists": True}})
    new_count = collection.count_documents({"seo_social_trends": {"$exists": True}})
    
    print(f"📊 Records with old field 'seo_youtube_trends': {remaining_old}")
    print(f"📊 Records with new field 'seo_social_trends': {new_count}")
    
    if remaining_old == 0:
        print("✅ Migration successful - no old field names remaining")
        return True
    else:
        print("⚠️  Migration incomplete - some old field names remain")
        return False

if __name__ == "__main__":
    success = migrate_field_names()
    exit(0 if success else 1)