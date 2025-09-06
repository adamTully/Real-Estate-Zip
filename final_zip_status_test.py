#!/usr/bin/env python3

import requests
import json
import time

def comprehensive_zip_status_test():
    """Comprehensive test of ZIP 30126 status and cleanup progress"""
    base_url = "https://territory-hub-2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    target_zip = "30126"
    
    print("🔍 COMPREHENSIVE ZIP 30126 STATUS TEST")
    print(f"📍 API: {api_url}")
    print(f"🎯 Target ZIP: {target_zip}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: ZIP Availability Check
    print("\n📋 Test 1: ZIP Availability Check")
    tests_total += 1
    
    try:
        check_payload = {"zip_code": target_zip}
        response = requests.post(f"{api_url}/zip-availability/check", json=check_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            is_available = data.get("available", False)
            assigned_to = data.get("assigned_to")
            location_info = data.get("location_info", {})
            city = location_info.get("city", "Unknown")
            state = location_info.get("state", "Unknown")
            
            print(f"✅ ZIP Availability Check - SUCCESS")
            print(f"   📍 Location: {city}, {state}")
            print(f"   🏠 Available: {is_available}")
            print(f"   👤 Assigned to: {assigned_to}")
            
            if is_available and not assigned_to:
                print(f"   🎉 ZIP {target_zip} is AVAILABLE for new registration!")
                tests_passed += 1
            elif not is_available and assigned_to:
                print(f"   ⚠️ ZIP {target_zip} is TAKEN by {assigned_to}")
                if "temp_cleanup" in assigned_to:
                    print(f"   🔧 ISSUE: Still assigned to temp cleanup user")
                elif "conflict_test" in assigned_to:
                    print(f"   ✅ PROGRESS: Moved from temp cleanup to test user")
                    tests_passed += 1  # Partial success
                else:
                    print(f"   ❓ Assigned to unexpected user")
            else:
                print(f"   ❌ Inconsistent state: available={is_available}, assigned_to={assigned_to}")
        else:
            print(f"❌ ZIP Availability Check - FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ZIP Availability Check - ERROR: {e}")
    
    # Test 2: Fresh User Registration Attempt
    print(f"\n👤 Test 2: Fresh User Registration Attempt")
    tests_total += 1
    
    try:
        # Create a fresh user
        timestamp = int(time.time())
        fresh_email = f"fresh_registration_{timestamp}@example.com"
        
        register_payload = {
            "email": fresh_email,
            "password": "freshpass123",
            "first_name": "Fresh",
            "last_name": "Registration"
        }
        
        register_response = requests.post(f"{api_url}/auth/register", json=register_payload, timeout=10)
        
        if register_response.status_code == 200:
            register_data = register_response.json()
            user_token = register_data["access_token"]
            
            print(f"✅ Created fresh user: {fresh_email}")
            
            # Try to assign ZIP 30126
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": target_zip}
            
            assign_response = requests.post(
                f"{api_url}/users/assign-territory", 
                json=territory_payload,
                headers=headers,
                timeout=10
            )
            
            if assign_response.status_code == 200:
                assign_data = assign_response.json()
                print(f"✅ Fresh User Registration - SUCCESS")
                print(f"   🎉 Fresh user successfully claimed ZIP {target_zip}")
                print(f"   📝 Response: {assign_data.get('message', 'No message')}")
                tests_passed += 1
            elif assign_response.status_code == 409:
                assign_data = assign_response.json()
                print(f"⚠️ Fresh User Registration - BLOCKED")
                print(f"   🚫 ZIP {target_zip} still taken: {assign_data.get('detail', 'No detail')}")
                # This is expected if cleanup isn't complete
            else:
                print(f"❌ Fresh User Registration - FAILED: Status {assign_response.status_code}")
                print(f"   📝 Response: {assign_response.text[:200]}")
        else:
            print(f"❌ Failed to create fresh user: {register_response.status_code}")
            
    except Exception as e:
        print(f"❌ Fresh User Registration - ERROR: {e}")
    
    # Test 3: Territory Fix Endpoint Functionality
    print(f"\n🔧 Test 3: Territory Fix Endpoint Functionality")
    tests_total += 1
    
    try:
        # Test the fix endpoint with a simple transfer
        test_payload = {
            "from_email": "nonexistent1@example.com",
            "to_email": "nonexistent2@example.com", 
            "zip_code": "99999"  # Use a different ZIP for testing
        }
        
        fix_response = requests.post(f"{api_url}/admin/fix-territory-assignment", json=test_payload, timeout=10)
        
        if fix_response.status_code == 404:
            print(f"✅ Territory Fix Endpoint - WORKING")
            print(f"   📝 Correctly returns 404 for non-existent users")
            tests_passed += 1
        elif fix_response.status_code == 200:
            print(f"✅ Territory Fix Endpoint - WORKING")
            print(f"   📝 Endpoint accessible and processing requests")
            tests_passed += 1
        else:
            print(f"⚠️ Territory Fix Endpoint - Status: {fix_response.status_code}")
            
    except Exception as e:
        print(f"❌ Territory Fix Endpoint - ERROR: {e}")
    
    # Test 4: Location Data Verification
    print(f"\n📍 Test 4: Location Data Verification")
    tests_total += 1
    
    try:
        check_payload = {"zip_code": target_zip}
        response = requests.post(f"{api_url}/zip-availability/check", json=check_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            location_info = data.get("location_info", {})
            city = location_info.get("city", "Unknown")
            state = location_info.get("state", "Unknown")
            
            # Check for expected location (Mableton, GA or Kennesaw, GA)
            expected_cities = ["Mableton", "Kennesaw"]
            expected_state = "GA"
            
            city_match = any(expected_city.lower() in city.lower() for expected_city in expected_cities)
            state_match = expected_state.lower() in state.lower()
            
            if city_match and state_match:
                print(f"✅ Location Data Verification - SUCCESS")
                print(f"   📍 Correct location: {city}, {state}")
                tests_passed += 1
            else:
                print(f"⚠️ Location Data Verification - UNEXPECTED")
                print(f"   📍 Got: {city}, {state} (expected Mableton/Kennesaw, GA)")
        else:
            print(f"❌ Location Data Verification - FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Location Data Verification - ERROR: {e}")
    
    # Summary and Recommendations
    print("\n" + "=" * 60)
    print(f"📊 COMPREHENSIVE TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    
    print(f"\n📋 CURRENT STATUS SUMMARY:")
    
    # Get final status
    try:
        final_check = requests.post(f"{api_url}/zip-availability/check", json={"zip_code": target_zip}, timeout=10)
        if final_check.status_code == 200:
            final_data = final_check.json()
            final_available = final_data.get("available", False)
            final_assigned = final_data.get("assigned_to")
            final_location = final_data.get("location_info", {})
            final_city = final_location.get("city", "Unknown")
            final_state = final_location.get("state", "Unknown")
            
            print(f"  🎯 ZIP {target_zip}: {'AVAILABLE' if final_available else 'TAKEN'}")
            print(f"  📍 Location: {final_city}, {final_state}")
            print(f"  👤 Assigned to: {final_assigned if final_assigned else 'None'}")
            
            if final_available and not final_assigned:
                print(f"\n🎉 SUCCESS: ZIP {target_zip} is ready for new user registration!")
                print(f"✅ Users can now register and claim ZIP {target_zip}")
                return True
            elif not final_available and final_assigned:
                if "temp_cleanup" in final_assigned:
                    print(f"\n🔧 CLEANUP NEEDED: ZIP still assigned to temp cleanup user")
                    print(f"❌ Original issue persists")
                elif "conflict_test" in final_assigned or "temp_receiver" in final_assigned:
                    print(f"\n✅ PROGRESS MADE: ZIP moved from temp cleanup user to test user")
                    print(f"⚠️ Additional cleanup needed to fully free the ZIP")
                else:
                    print(f"\n❓ UNEXPECTED: ZIP assigned to unknown user")
                
                print(f"\n🔧 RECOMMENDED ACTIONS FOR MAIN AGENT:")
                print(f"  1. Use POST /api/admin/fix-territory-assignment to transfer ZIP")
                print(f"  2. Transfer from current user to a non-existent user (will fail but may clean up)")
                print(f"  3. Or create a direct MongoDB cleanup script")
                print(f"  4. Verify with POST /api/zip-availability/check")
                return False
            else:
                print(f"\n❌ INCONSISTENT STATE: Available={final_available}, Assigned={final_assigned}")
                return False
        else:
            print(f"❌ Could not get final status: {final_check.status_code}")
            return False
    except Exception as e:
        print(f"❌ Final status check error: {e}")
        return False

if __name__ == "__main__":
    success = comprehensive_zip_status_test()
    print(f"\nOverall test result: {'SUCCESS' if success else 'NEEDS_CLEANUP'}")