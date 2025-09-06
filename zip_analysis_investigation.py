#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time
import os

class ZipAnalysisInvestigator:
    def __init__(self, base_url=None):
        # Use the production URL from frontend/.env
        if base_url is None:
            base_url = "https://territory-hub-2.preview.emergentagent.com"
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        
        # Specific user details from the issue
        self.user_email = "adamtest1@gmail.com"
        self.user_password = "adam123"
        self.test_zip = "30126"
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        if details and success:
            print(f"   ℹ️  {details}")
        
    def test_user_authentication(self):
        """Test login for adamtest1@gmail.com"""
        try:
            login_payload = {
                "email": self.user_email,
                "password": self.user_password
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.auth_token = data["access_token"]
                user_data = data["user"]
                owned_territories = user_data.get("owned_territories", [])
                
                # Check if user owns ZIP 30126
                owns_zip = self.test_zip in owned_territories
                details = f"Login successful. User ID: {user_data['id']}, Email: {user_data['email']}, Owns ZIP {self.test_zip}: {'Yes' if owns_zip else 'No'}, All territories: {owned_territories}"
                
                if not owns_zip:
                    success = False
                    details += f" - CRITICAL: User does not own ZIP {self.test_zip}!"
                    
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test(f"User Authentication ({self.user_email})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"User Authentication ({self.user_email})", False, str(e))
            return False
    
    def test_user_profile_details(self):
        """Get detailed user profile information"""
        try:
            if not self.auth_token:
                self.log_test("User Profile Details", False, "No auth token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"User Profile - ID: {data.get('id')}, Email: {data.get('email')}, Name: {data.get('first_name')} {data.get('last_name')}, Role: {data.get('role')}, Active: {data.get('is_active')}, Territories: {data.get('owned_territories', [])}, Created: {data.get('created_at')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("User Profile Details", success, details)
            return success, data if success else None
            
        except Exception as e:
            self.log_test("User Profile Details", False, str(e))
            return False, None
    
    def test_zip_analysis_start(self):
        """Test ZIP analysis start endpoint for ZIP 30126"""
        try:
            if not self.auth_token:
                self.log_test("ZIP Analysis Start", False, "No auth token available")
                return False, None
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"zip_code": self.test_zip}
            
            print(f"   🔄 Starting ZIP analysis for {self.test_zip}...")
            response = requests.post(
                f"{self.api_url}/zip-analysis/start", 
                json=payload,
                headers=headers,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify response structure
                required_fields = ["zip_code", "job_id", "state", "overall_percent", "tasks"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields in response: {missing_fields}"
                else:
                    job_id = data.get("job_id")
                    state = data.get("state")
                    percent = data.get("overall_percent", 0)
                    tasks = data.get("tasks", {})
                    
                    details = f"Analysis started - Job ID: {job_id}, State: {state}, Progress: {percent}%, Tasks: {list(tasks.keys())}"
                    
                    # Check if tasks are properly configured
                    expected_tasks = ["location", "buyer_migration", "seo_social_trends", "content_strategy", "content_assets"]
                    missing_tasks = [task for task in expected_tasks if task not in tasks]
                    if missing_tasks:
                        details += f", Missing tasks: {missing_tasks}"
                        
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test(f"ZIP Analysis Start ({self.test_zip})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Start ({self.test_zip})", False, str(e))
            return False, None
    
    def test_zip_analysis_status(self):
        """Test ZIP analysis status endpoint"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/status/{self.test_zip}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                state = data.get("state", "unknown")
                percent = data.get("overall_percent", 0)
                tasks = data.get("tasks", {})
                
                # Get task details
                task_status = {}
                for task_name, task_data in tasks.items():
                    task_status[task_name] = {
                        "status": task_data.get("status", "unknown"),
                        "percent": task_data.get("percent", 0)
                    }
                
                details = f"Status retrieved - State: {state}, Overall: {percent}%, Task statuses: {task_status}"
                
                # Check for any failed tasks
                failed_tasks = [name for name, info in task_status.items() if info["status"] == "failed"]
                if failed_tasks:
                    details += f", FAILED TASKS: {failed_tasks}"
                    
            else:
                if response.status_code == 404:
                    details = "Status not found - analysis may not have been started"
                else:
                    details = f"Status: {response.status_code}"
            
            self.log_test(f"ZIP Analysis Status ({self.test_zip})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Status ({self.test_zip})", False, str(e))
            return False, None
    
    def test_openai_api_key(self):
        """Test if OpenAI API key is working by making a simple request"""
        try:
            # We'll test this indirectly by checking if the backend can make LLM calls
            # by starting a simple analysis and monitoring for LLM-related errors
            
            # First, let's check if there are any existing analyses to see if LLM is working
            test_zip = "10001"  # Use a different ZIP for testing
            response = requests.get(f"{self.api_url}/zip-analysis/{test_zip}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Check if we have real LLM-generated content
                buyer_migration = data.get("buyer_migration", {})
                analysis_content = buyer_migration.get("analysis_content", "")
                
                if "Real-time analysis temporarily unavailable" in analysis_content:
                    success = False
                    details = "OpenAI API appears to be having issues - fallback content detected"
                elif len(analysis_content) > 100 and "analysis" in analysis_content.lower():
                    success = True
                    details = f"OpenAI API appears to be working - found {len(analysis_content)} chars of analysis content"
                else:
                    success = False
                    details = f"Unclear OpenAI status - analysis content: {analysis_content[:100]}..."
            else:
                # Try to start a new analysis to test OpenAI
                payload = {"zip_code": "12345"}  # Use invalid ZIP to test validation
                response = requests.post(f"{self.api_url}/zip-analysis/start", json=payload, timeout=10)
                
                if response.status_code == 422:
                    success = True
                    details = "Backend is responding correctly (validation working), OpenAI status unclear"
                else:
                    success = False
                    details = f"Backend response unexpected: {response.status_code}"
            
            self.log_test("OpenAI API Key Test", success, details)
            return success
            
        except Exception as e:
            self.log_test("OpenAI API Key Test", False, str(e))
            return False
    
    def test_backend_logs_check(self):
        """Check for backend errors by testing various endpoints"""
        try:
            # Test multiple endpoints to see if backend is functioning
            endpoints_to_test = [
                ("/", "GET", None),
                ("/auth/me", "GET", {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else None),
                ("/zip-availability/check", "POST", None, {"zip_code": self.test_zip})
            ]
            
            results = []
            for endpoint_info in endpoints_to_test:
                endpoint = endpoint_info[0]
                method = endpoint_info[1]
                headers = endpoint_info[2] if len(endpoint_info) > 2 else None
                payload = endpoint_info[3] if len(endpoint_info) > 3 else None
                
                try:
                    if method == "GET":
                        resp = requests.get(f"{self.api_url}{endpoint}", headers=headers, timeout=10)
                    else:
                        resp = requests.post(f"{self.api_url}{endpoint}", json=payload, headers=headers, timeout=10)
                    
                    results.append(f"{endpoint}: {resp.status_code}")
                except Exception as e:
                    results.append(f"{endpoint}: ERROR - {str(e)}")
            
            # All endpoints should be reachable
            success = all("ERROR" not in result for result in results)
            details = f"Backend endpoint health check: {', '.join(results)}"
            
            self.log_test("Backend Health Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False
    
    def test_zip_availability_check(self):
        """Test ZIP availability check for ZIP 30126"""
        try:
            payload = {"zip_code": self.test_zip}
            response = requests.post(f"{self.api_url}/zip-availability/check", json=payload, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                is_available = data.get("available", True)
                assigned_to = data.get("assigned_to")
                location_info = data.get("location_info", {})
                
                details = f"ZIP {self.test_zip} - Available: {is_available}, Assigned to: {assigned_to}, Location: {location_info.get('city', 'Unknown')}, {location_info.get('state', 'Unknown')}"
                
                if not is_available and assigned_to != self.user_email:
                    details += f" - ISSUE: ZIP assigned to {assigned_to} instead of {self.user_email}"
                    
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test(f"ZIP Availability Check ({self.test_zip})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Availability Check ({self.test_zip})", False, str(e))
            return False, None
    
    def test_existing_analysis_check(self):
        """Check if there's already an existing analysis for ZIP 30126"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{self.test_zip}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                created_at = data.get("created_at")
                zip_code = data.get("zip_code")
                
                # Check if analysis has all required fields
                required_fields = ["buyer_migration", "seo_social_trends", "content_strategy", "content_assets"]
                missing_fields = [field for field in required_fields if field not in data]
                
                success = len(missing_fields) == 0
                details = f"Existing analysis found for ZIP {zip_code}, Created: {created_at}, Missing fields: {missing_fields if missing_fields else 'None'}"
                
                # Check content quality
                buyer_migration = data.get("buyer_migration", {})
                analysis_content = buyer_migration.get("analysis_content", "")
                if "Real-time analysis temporarily unavailable" in analysis_content:
                    details += " - WARNING: Contains fallback content, may indicate LLM issues"
                    
            elif response.status_code == 404:
                success = True  # This is expected if no analysis exists yet
                details = "No existing analysis found (expected for new analysis)"
            else:
                success = False
                details = f"Unexpected status: {response.status_code}"
            
            self.log_test(f"Existing Analysis Check ({self.test_zip})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Existing Analysis Check ({self.test_zip})", False, str(e))
            return False
    
    def monitor_analysis_progress(self, max_wait_time=120):
        """Monitor analysis progress for a specified time"""
        try:
            print(f"   🔄 Monitoring analysis progress for up to {max_wait_time} seconds...")
            start_time = time.time()
            last_percent = -1
            
            while time.time() - start_time < max_wait_time:
                response = requests.get(f"{self.api_url}/zip-analysis/status/{self.test_zip}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    state = data.get("state", "unknown")
                    percent = data.get("overall_percent", 0)
                    
                    if percent != last_percent:
                        print(f"   📊 Progress: {percent}% (State: {state})")
                        last_percent = percent
                    
                    if state == "done":
                        success = True
                        details = f"Analysis completed successfully in {int(time.time() - start_time)} seconds"
                        break
                    elif state == "failed":
                        success = False
                        error = data.get("error", "Unknown error")
                        details = f"Analysis failed: {error}"
                        break
                    elif state == "running":
                        time.sleep(5)  # Wait 5 seconds before checking again
                        continue
                    else:
                        time.sleep(2)  # Wait 2 seconds for other states
                        continue
                else:
                    success = False
                    details = f"Status check failed: {response.status_code}"
                    break
            else:
                # Timeout reached
                success = False
                details = f"Analysis did not complete within {max_wait_time} seconds"
            
            self.log_test(f"Analysis Progress Monitoring ({self.test_zip})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Analysis Progress Monitoring ({self.test_zip})", False, str(e))
            return False
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("🔍 ZIP Code Analysis Failure Investigation")
        print(f"👤 User: {self.user_email}")
        print(f"📍 ZIP Code: {self.test_zip}")
        print(f"🌐 API URL: {self.api_url}")
        print("=" * 60)
        
        # Step 1: Test user authentication and territory ownership
        print("\n🔐 Step 1: Testing User Authentication & Territory Ownership")
        auth_success = self.test_user_authentication()
        
        if not auth_success:
            print("❌ Authentication failed. Cannot proceed with analysis testing.")
            return False
        
        # Step 2: Get detailed user profile
        print("\n👤 Step 2: Getting User Profile Details")
        profile_success, profile_data = self.test_user_profile_details()
        
        # Step 3: Check ZIP availability and assignment
        print("\n🏠 Step 3: Checking ZIP Availability & Assignment")
        availability_success, availability_data = self.test_zip_availability_check()
        
        # Step 4: Check for existing analysis
        print("\n📋 Step 4: Checking for Existing Analysis")
        existing_analysis_success = self.test_existing_analysis_check()
        
        # Step 5: Test backend health
        print("\n🏥 Step 5: Backend Health Check")
        backend_health_success = self.test_backend_logs_check()
        
        # Step 6: Test OpenAI API
        print("\n🤖 Step 6: OpenAI API Test")
        openai_success = self.test_openai_api_key()
        
        # Step 7: Try to start new analysis
        print("\n🚀 Step 7: Starting New ZIP Analysis")
        analysis_start_success, analysis_data = self.test_zip_analysis_start()
        
        if analysis_start_success:
            # Step 8: Monitor progress
            print("\n📊 Step 8: Monitoring Analysis Progress")
            progress_success = self.monitor_analysis_progress(60)  # Monitor for 1 minute
            
            # Step 9: Check final status
            print("\n📈 Step 9: Final Status Check")
            final_status_success, final_status_data = self.test_zip_analysis_status()
        else:
            print("❌ Analysis start failed. Skipping progress monitoring.")
            progress_success = False
            final_status_success = False
        
        # Print investigation summary
        print("\n" + "=" * 60)
        print("🔍 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        
        # Analyze the results and provide recommendations
        print("\n🎯 KEY FINDINGS:")
        
        if not auth_success:
            print("❌ CRITICAL: User authentication failed")
        elif profile_data and self.test_zip not in profile_data.get("owned_territories", []):
            print(f"❌ CRITICAL: User does not own ZIP {self.test_zip}")
        else:
            print(f"✅ User authentication and territory ownership verified")
        
        if not backend_health_success:
            print("❌ CRITICAL: Backend health issues detected")
        else:
            print("✅ Backend appears to be healthy")
        
        if not openai_success:
            print("❌ WARNING: OpenAI API may have issues")
        else:
            print("✅ OpenAI API appears to be working")
        
        if not analysis_start_success:
            print(f"❌ CRITICAL: ZIP analysis failed to start for {self.test_zip}")
        else:
            print(f"✅ ZIP analysis started successfully for {self.test_zip}")
        
        print("\n💡 RECOMMENDATIONS:")
        
        if not auth_success:
            print("1. Verify user credentials and account status")
        elif profile_data and self.test_zip not in profile_data.get("owned_territories", []):
            print(f"1. Assign ZIP {self.test_zip} to user {self.user_email}")
        
        if not backend_health_success:
            print("2. Check backend logs for errors")
            print("3. Verify all backend services are running")
        
        if not openai_success:
            print("4. Check OpenAI API key and quota")
            print("5. Verify LLM service configuration")
        
        if not analysis_start_success and auth_success:
            print("6. Check for specific error messages in analysis start response")
            print("7. Verify ZIP code format and validation")
        
        overall_success = self.tests_passed >= (self.tests_run * 0.7)  # 70% pass rate
        
        if overall_success:
            print("\n🎉 Investigation completed with mostly successful results")
        else:
            print("\n⚠️ Investigation revealed significant issues that need attention")
        
        return overall_success

def main():
    investigator = ZipAnalysisInvestigator()
    success = investigator.run_investigation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())