#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time
import socket

class ZipAvailabilityTester:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if details:
                print(f"   📝 {details}")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def test_nominatim_connectivity(self):
        """Test if nominatim.openstreetmap.org is accessible"""
        try:
            # Test DNS resolution
            socket.gethostbyname("nominatim.openstreetmap.org")
            
            # Test HTTP connectivity
            response = requests.get(
                "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=30126,USA",
                timeout=10,
                headers={'User-Agent': 'zip-intel-generator'}
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = len(data) > 0
                details = f"Nominatim accessible, returned {len(data)} results for ZIP 30126" if success else "Nominatim accessible but no results for ZIP 30126"
            else:
                details = f"HTTP Status: {response.status_code}"
                
            self.log_test("Nominatim Connectivity Check", success, details)
            return success
            
        except socket.gaierror as e:
            self.log_test("Nominatim Connectivity Check", False, f"DNS resolution failed: {e}")
            return False
        except requests.exceptions.Timeout:
            self.log_test("Nominatim Connectivity Check", False, "Connection timeout to nominatim.openstreetmap.org")
            return False
        except Exception as e:
            self.log_test("Nominatim Connectivity Check", False, f"Connection error: {e}")
            return False

    def test_zip_availability_30126(self):
        """Test ZIP availability check for ZIP 30126 specifically"""
        try:
            payload = {"zip_code": "30126"}
            response = requests.post(
                f"{self.api_url}/zip-availability/check", 
                json=payload,
                timeout=15
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                
                # Verify required fields exist
                required_fields = ["zip_code", "available", "location_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Verify location info structure
                    location_info = data.get("location_info", {})
                    location_required = ["city", "state", "latitude", "longitude"]
                    missing_location = [field for field in location_required if field not in location_info]
                    
                    if missing_location:
                        success = False
                        details = f"Missing location fields: {missing_location}"
                    else:
                        # Check if we got real location data
                        city = location_info.get("city", "")
                        state = location_info.get("state", "")
                        lat = location_info.get("latitude", 0)
                        lng = location_info.get("longitude", 0)
                        
                        if city == "Unknown" or state == "Unknown" or (lat == 0 and lng == 0):
                            success = False
                            details = f"Geocoding failed - got placeholder data: city={city}, state={state}, lat={lat}, lng={lng}"
                        else:
                            available = data.get("available", False)
                            assigned_to = data.get("assigned_to")
                            details = f"ZIP 30126 geocoded successfully: {city}, {state} (lat: {lat:.4f}, lng: {lng:.4f}). Available: {available}"
                            if not available and assigned_to:
                                details += f", assigned to: {assigned_to}"
            else:
                # Check for specific error messages
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    if "Failed to lookup ZIP code location" in error_detail:
                        details = f"Geocoding service error: {error_detail}"
                    else:
                        details = f"Status: {response.status_code}, Error: {error_detail}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                
            self.log_test("ZIP Availability Check - 30126", success, details)
            return success, response.json() if response.status_code == 200 else None
            
        except requests.exceptions.Timeout:
            self.log_test("ZIP Availability Check - 30126", False, "Request timeout - possible geocoding service delay")
            return False, None
        except Exception as e:
            self.log_test("ZIP Availability Check - 30126", False, str(e))
            return False, None

    def test_zip_availability_alternative_zips(self):
        """Test ZIP availability with other ZIP codes to check if issue is system-wide"""
        test_zips = ["10001", "90210", "60601"]
        successful_zips = []
        failed_zips = []
        
        for zip_code in test_zips:
            try:
                payload = {"zip_code": zip_code}
                response = requests.post(
                    f"{self.api_url}/zip-availability/check", 
                    json=payload,
                    timeout=15
                )
                
                success = response.status_code == 200
                if success:
                    data = response.json()
                    location_info = data.get("location_info", {})
                    city = location_info.get("city", "Unknown")
                    state = location_info.get("state", "Unknown")
                    
                    if city != "Unknown" and state != "Unknown":
                        successful_zips.append(f"{zip_code} ({city}, {state})")
                        self.log_test(f"ZIP Availability Check - {zip_code}", True, f"Geocoded to {city}, {state}")
                    else:
                        failed_zips.append(f"{zip_code} (geocoding failed)")
                        self.log_test(f"ZIP Availability Check - {zip_code}", False, "Geocoding returned placeholder data")
                else:
                    failed_zips.append(f"{zip_code} (HTTP {response.status_code})")
                    self.log_test(f"ZIP Availability Check - {zip_code}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                failed_zips.append(f"{zip_code} (error: {str(e)[:50]})")
                self.log_test(f"ZIP Availability Check - {zip_code}", False, str(e))
        
        # Overall assessment
        overall_success = len(successful_zips) >= 2  # At least 2 out of 3 should work
        details = f"Successful: {successful_zips}, Failed: {failed_zips}"
        
        self.log_test("ZIP Availability - Alternative ZIPs", overall_success, details)
        return overall_success, successful_zips, failed_zips

    def test_zip_availability_invalid_format(self):
        """Test ZIP availability with invalid ZIP format"""
        try:
            payload = {"zip_code": "invalid"}
            response = requests.post(
                f"{self.api_url}/zip-availability/check", 
                json=payload,
                timeout=10
            )
            
            # Should return 400 for invalid format
            success = response.status_code == 400
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower() or "format" in data.get("detail", "").lower()
                details = f"Correctly rejected invalid ZIP format: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 400"
            
            self.log_test("ZIP Availability - Invalid Format", success, details)
            return success
            
        except Exception as e:
            self.log_test("ZIP Availability - Invalid Format", False, str(e))
            return False

    def check_backend_logs_for_geocoding_errors(self):
        """Check backend logs for geocoding-related errors"""
        try:
            # This is a simulation since we can't directly access logs in this environment
            # In a real scenario, you would check supervisor logs or application logs
            print("\n🔍 Checking backend logs for geocoding errors...")
            print("   📝 Note: In production, check these log locations:")
            print("   📝 - /var/log/supervisor/backend.*.log")
            print("   📝 - Application logs for geopy/nominatim errors")
            print("   📝 - Look for: 'Geolocation error', 'Connection timeout', 'nominatim'")
            
            # We can try to trigger an error and see the response
            payload = {"zip_code": "00000"}  # Non-existent ZIP
            response = requests.post(
                f"{self.api_url}/zip-availability/check", 
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    print(f"   📝 Sample error response: {error_detail}")
                    
                    if "Failed to lookup ZIP code location" in error_detail:
                        print("   ⚠️  Confirmed: Geocoding service connectivity issue detected")
                        return False
                    elif "ZIP code not found" in error_detail:
                        print("   ✅ Normal behavior: Non-existent ZIP properly handled")
                        return True
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error checking logs: {e}")
            return False

    def suggest_fix_for_zip_30126(self, zip_30126_success, alternative_zips_success):
        """Suggest fixes based on test results"""
        print("\n🔧 SUGGESTED FIXES:")
        
        if not zip_30126_success and not alternative_zips_success:
            print("   🚨 SYSTEM-WIDE GEOCODING ISSUE:")
            print("   📝 1. Check if nominatim.openstreetmap.org is accessible from server")
            print("   📝 2. Verify geopy library is installed and up to date")
            print("   📝 3. Check for rate limiting from OpenStreetMap")
            print("   📝 4. Consider implementing fallback geocoding service")
            print("   📝 5. Add manual location data for common ZIPs as temporary fix")
            
        elif not zip_30126_success and alternative_zips_success:
            print("   🎯 ZIP 30126 SPECIFIC ISSUE:")
            print("   📝 1. Add manual location data for ZIP 30126:")
            print("   📝    - City: Kennesaw")
            print("   📝    - State: Georgia (GA)")
            print("   📝    - County: Cobb County")
            print("   📝    - Latitude: ~34.0234")
            print("   📝    - Longitude: ~-84.6155")
            print("   📝 2. Implement fallback data dictionary for problematic ZIPs")
            
        else:
            print("   ✅ GEOCODING WORKING:")
            print("   📝 ZIP availability system is functioning correctly")
            print("   📝 If user still reports issues, check:")
            print("   📝 1. User's network connectivity")
            print("   📝 2. Browser cache/cookies")
            print("   📝 3. Frontend error handling")

    def run_comprehensive_zip_availability_test(self):
        """Run comprehensive ZIP availability testing as requested in review"""
        print("🚀 Testing ZIP Availability Check for ZIP 30126")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Step 1: Test nominatim connectivity
        print("\n🌐 Step 1: Testing nominatim.openstreetmap.org connectivity...")
        nominatim_success = self.test_nominatim_connectivity()
        
        # Step 2: Test ZIP 30126 specifically
        print("\n🎯 Step 2: Testing ZIP availability for 30126...")
        zip_30126_success, zip_30126_data = self.test_zip_availability_30126()
        
        # Step 3: Test alternative ZIPs
        print("\n🔄 Step 3: Testing alternative ZIP codes...")
        alt_success, successful_zips, failed_zips = self.test_zip_availability_alternative_zips()
        
        # Step 4: Test invalid ZIP format
        print("\n❌ Step 4: Testing invalid ZIP format handling...")
        self.test_zip_availability_invalid_format()
        
        # Step 5: Check backend logs (simulated)
        print("\n📋 Step 5: Checking backend logs...")
        self.check_backend_logs_for_geocoding_errors()
        
        # Step 6: Provide fix suggestions
        print("\n💡 Step 6: Analysis and recommendations...")
        self.suggest_fix_for_zip_30126(zip_30126_success, alt_success)
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 ZIP Availability Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Specific analysis for ZIP 30126
        if zip_30126_success:
            print("🎉 ZIP 30126 availability check is working correctly!")
            if zip_30126_data:
                location = zip_30126_data.get("location_info", {})
                print(f"   📍 Location: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")
                print(f"   📊 Available: {zip_30126_data.get('available', 'Unknown')}")
        else:
            print("❌ ZIP 30126 availability check is failing!")
            if not nominatim_success:
                print("   🚨 Root cause: Nominatim geocoding service connectivity issue")
            elif not alt_success:
                print("   🚨 Root cause: System-wide geocoding failure")
            else:
                print("   🎯 Root cause: ZIP 30126 specific geocoding issue")
        
        return zip_30126_success

def main():
    tester = ZipAvailabilityTester()
    
    # Run the ZIP availability test as requested in the review
    print("Running ZIP Availability Test for ZIP 30126 as requested in review...")
    success = tester.run_comprehensive_zip_availability_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())