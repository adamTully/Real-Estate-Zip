#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class ZipIntelAPITester:
    def __init__(self, base_url="https://territory-hub-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_zip_codes = ["90210", "10001", "60601", "33101"]
        self.auth_token = None  # Store JWT token for authenticated requests
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                expected_message = "ZIP Intel Generator API v2.0 (buyer+seo+strategy+assets)"
                success = data.get("message") == expected_message
                details = f"Got message: {data.get('message')}" if not success else ""
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("API Root Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False
    
    def test_zip_analysis_start(self, zip_code):
        """Test ZIP analysis start endpoint (updated prompts)"""
        try:
            payload = {"zip_code": zip_code}
            response = requests.post(
                f"{self.api_url}/zip-analysis/start", 
                json=payload,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify status response structure
                required_fields = ["zip_code", "job_id", "state", "overall_percent", "tasks"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Verify tasks include the new field name
                    tasks = data.get("tasks", {})
                    expected_tasks = ["location", "buyer_migration", "seo_social_trends", "content_strategy", "content_assets"]
                    missing_tasks = [task for task in expected_tasks if task not in tasks]
                    
                    if missing_tasks:
                        success = False
                        details = f"Missing tasks: {missing_tasks}"
                    else:
                        # Check that old field name is NOT present
                        if "seo_youtube_trends" in tasks:
                            success = False
                            details = "Old field name 'seo_youtube_trends' still present in tasks"
                        else:
                            details = f"Analysis started with job_id: {data.get('job_id', 'N/A')}, state: {data.get('state')}"
                        
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                
            self.log_test(f"ZIP Analysis Start ({zip_code})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Start ({zip_code})", False, str(e))
            return False, None

    def test_zip_analysis_creation(self, zip_code):
        """Test ZIP analysis creation (legacy endpoint)"""
        try:
            payload = {"zip_code": zip_code}
            response = requests.post(
                f"{self.api_url}/zip-analysis", 
                json=payload,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify required fields exist - UPDATED to use new field name
                required_fields = [
                    "id", "zip_code", "buyer_migration", "seo_social_trends",
                    "content_strategy", "hidden_listings", "market_hooks", 
                    "content_assets", "created_at"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Verify each intelligence category has required structure
                    for category in ["buyer_migration", "seo_social_trends", "content_strategy", "hidden_listings", "market_hooks"]:
                        if not isinstance(data[category], dict) or "summary" not in data[category]:
                            success = False
                            details = f"Invalid structure for {category}"
                            break
                    
                    # Check that old field name is NOT present
                    if "seo_youtube_trends" in data:
                        success = False
                        details = "Old field name 'seo_youtube_trends' still present in response"
                    elif success and "content_assets" in data:
                        content_assets = data["content_assets"]
                        if not all(key in content_assets for key in ["blog_posts", "email_campaigns"]):
                            success = False
                            details = "Missing content asset types"
                        
                details = details if not success else f"Analysis created with ID: {data.get('id', 'N/A')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                
            self.log_test(f"ZIP Analysis Creation ({zip_code})", success, details)
            return success, response.json() if success else None
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Creation ({zip_code})", False, str(e))
            return False, None
    
    def test_zip_analysis_status(self, zip_code):
        """Test ZIP analysis status endpoint"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/status/{zip_code}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Verify status structure
                required_fields = ["zip_code", "state", "overall_percent", "tasks"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Verify tasks include the new field name
                    tasks = data.get("tasks", {})
                    expected_tasks = ["location", "buyer_migration", "seo_social_trends", "content_strategy", "content_assets"]
                    missing_tasks = [task for task in expected_tasks if task not in tasks]
                    
                    if missing_tasks:
                        success = False
                        details = f"Missing tasks: {missing_tasks}"
                    else:
                        # Check that old field name is NOT present
                        if "seo_youtube_trends" in tasks:
                            success = False
                            details = "Old field name 'seo_youtube_trends' still present in tasks"
                        else:
                            details = f"Status retrieved: state={data.get('state')}, progress={data.get('overall_percent')}%"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"ZIP Analysis Status ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Status ({zip_code})", False, str(e))
            return False

    def test_zip_analysis_retrieval(self, zip_code):
        """Test ZIP analysis retrieval"""
        try:
            response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get("zip_code") == zip_code
                
                if success:
                    # Verify new field name is present and old one is not
                    if "seo_social_trends" not in data:
                        success = False
                        details = "New field 'seo_social_trends' not found in response"
                    elif "seo_youtube_trends" in data:
                        success = False
                        details = "Old field 'seo_youtube_trends' still present in response"
                    else:
                        # Verify seo_social_trends has platform-specific content
                        seo_data = data.get("seo_social_trends", {})
                        analysis_content = seo_data.get("analysis_content", "")
                        
                        # Check for platform-specific mentions
                        platforms = ["Facebook", "Instagram", "Twitter", "TikTok"]
                        platform_mentions = [platform for platform in platforms if platform.lower() in analysis_content.lower()]
                        
                        if len(platform_mentions) >= 2:  # At least 2 platforms mentioned
                            details = f"Retrieved analysis with seo_social_trends containing {len(platform_mentions)} platforms: {platform_mentions}"
                        else:
                            details = f"Retrieved analysis but seo_social_trends may not have platform-specific content (found: {platform_mentions})"
                else:
                    details = "ZIP code mismatch"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"ZIP Analysis Retrieval ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"ZIP Analysis Retrieval ({zip_code})", False, str(e))
            return False
    
    def test_pdf_generation(self, zip_code):
        """Test PDF generation"""
        try:
            response = requests.get(f"{self.api_url}/generate-pdf/{zip_code}", timeout=15)
            success = response.status_code == 200
            
            if success:
                # Check if response is actually a PDF
                content_type = response.headers.get('content-type', '')
                is_pdf = 'application/pdf' in content_type
                has_content = len(response.content) > 1000  # PDF should be substantial
                
                success = is_pdf and has_content
                details = f"PDF size: {len(response.content)} bytes, Content-Type: {content_type}" if success else f"Invalid PDF: {content_type}, Size: {len(response.content)}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"PDF Generation ({zip_code})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"PDF Generation ({zip_code})", False, str(e))
            return False
    
    def test_content_assets(self, zip_code):
        """Test content asset endpoints"""
        asset_tests = [
            ("blogs", "blog-post-1.txt"),
            ("emails", "email-week-1.txt"), 
            ("lead_magnet", "buyers-guide")
        ]
        
        all_passed = True
        
        for asset_type, asset_name in asset_tests:
            try:
                # For lead_magnet, we don't need asset_name in URL
                if asset_type == "lead_magnet":
                    url = f"{self.api_url}/content-asset/{zip_code}/{asset_type}/guide"
                else:
                    # Try to get the first asset from the analysis
                    analysis_response = requests.get(f"{self.api_url}/zip-analysis/{zip_code}")
                    if analysis_response.status_code == 200:
                        analysis_data = analysis_response.json()
                        content_assets = analysis_data.get("content_assets", {})
                        
                        if asset_type == "blogs" and content_assets.get("blog_posts"):
                            asset_name = content_assets["blog_posts"][0]["name"]
                        elif asset_type == "emails" and content_assets.get("email_campaigns"):
                            asset_name = content_assets["email_campaigns"][0]["name"]
                    
                    url = f"{self.api_url}/content-asset/{zip_code}/{asset_type}/{asset_name}"
                
                response = requests.get(url, timeout=10)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    has_content = "content" in data and len(data["content"]) > 100
                    success = has_content
                    details = f"Content length: {len(data.get('content', ''))}" if success else "No content or too short"
                else:
                    details = f"Status: {response.status_code}"
                
                self.log_test(f"Content Asset {asset_type} ({zip_code})", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Content Asset {asset_type} ({zip_code})", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_invalid_zip_validation(self):
        """Test ZIP code validation"""
        invalid_zips = ["123", "abcde", "12345-", "123456"]
        
        for invalid_zip in invalid_zips:
            try:
                payload = {"zip_code": invalid_zip}
                response = requests.post(f"{self.api_url}/zip-analysis", json=payload, timeout=10)
                
                # Should return 422 for validation error
                success = response.status_code == 422
                details = f"Status: {response.status_code}" if not success else "Correctly rejected invalid ZIP"
                
                self.log_test(f"Invalid ZIP Validation ({invalid_zip})", success, details)
                
            except Exception as e:
                self.log_test(f"Invalid ZIP Validation ({invalid_zip})", False, str(e))
    
    def test_auth_register_valid(self):
        """Test user registration with valid data"""
        try:
            # Use unique email with timestamp to avoid conflicts
            timestamp = int(time.time())
            payload = {
                "email": f"test{timestamp}@example.com",
                "password": "testpass123",
                "first_name": "John",
                "last_name": "Doe"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Verify response structure
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Verify user data structure
                    user_data = data["user"]
                    user_required_fields = ["id", "email", "first_name", "last_name", "role", "created_at", "is_active"]
                    missing_user_fields = [field for field in user_required_fields if field not in user_data]
                    
                    if missing_user_fields:
                        success = False
                        details = f"Missing user fields: {missing_user_fields}"
                    else:
                        # Store token for later tests
                        self.auth_token = data["access_token"]
                        details = f"User registered with ID: {user_data['id']}, Token type: {data['token_type']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Auth Register - Valid Data", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Register - Valid Data", False, str(e))
            return False
    
    def test_auth_register_duplicate_email(self):
        """Test user registration with duplicate email"""
        try:
            # First register a user
            timestamp = int(time.time())
            email = f"duplicate{timestamp}@example.com"
            payload = {
                "email": email,
                "password": "testpass123",
                "first_name": "First",
                "last_name": "User"
            }
            
            # First registration should succeed
            response1 = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            if response1.status_code != 200:
                self.log_test("Auth Register - Duplicate Email", False, f"First registration failed: {response1.status_code}")
                return False
            
            # Second registration with same email should fail
            payload2 = {
                "email": email,  # Same email
                "password": "testpass123",
                "first_name": "Second",
                "last_name": "User"
            }
            
            response2 = requests.post(f"{self.api_url}/auth/register", json=payload2, timeout=10)
            # Should return 400 for duplicate email
            success = response2.status_code == 400
            
            if success:
                data = response2.json()
                success = "already registered" in data.get("detail", "").lower()
                details = f"Correctly rejected duplicate email: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response2.status_code}, Expected: 400"
            
            self.log_test("Auth Register - Duplicate Email", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Register - Duplicate Email", False, str(e))
            return False
    
    def test_auth_register_weak_password(self):
        """Test user registration with weak password"""
        try:
            timestamp = int(time.time())
            payload = {
                "email": f"weak{timestamp}@example.com",
                "password": "123",  # Too short
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            # Should return 422 for validation error
            success = response.status_code == 422
            
            if success:
                data = response.json()
                # Check if error mentions password validation
                error_detail = str(data.get("detail", ""))
                success = "password" in error_detail.lower() and ("6 characters" in error_detail or "length" in error_detail)
                details = f"Correctly rejected weak password: {error_detail}" if success else f"Unexpected validation error: {error_detail}"
            else:
                details = f"Status: {response.status_code}, Expected: 422"
            
            self.log_test("Auth Register - Weak Password", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Register - Weak Password", False, str(e))
            return False
    
    def test_auth_login_valid(self):
        """Test user login with correct credentials"""
        try:
            # First register a user to login with
            timestamp = int(time.time())
            register_payload = {
                "email": f"login{timestamp}@example.com",
                "password": "testpass123",
                "first_name": "Login",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            if register_response.status_code != 200:
                self.log_test("Auth Login - Valid Credentials", False, "Failed to register test user")
                return False
            
            # Now test login
            login_payload = {
                "email": register_payload["email"],
                "password": register_payload["password"]
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Verify response structure (same as register)
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    user_data = data["user"]
                    success = user_data["email"] == login_payload["email"]
                    details = f"Login successful for {user_data['email']}, Token: {data['access_token'][:20]}..." if success else "Email mismatch in response"
                    
                    # Store token for /me endpoint test
                    if success:
                        self.auth_token = data["access_token"]
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Auth Login - Valid Credentials", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Login - Valid Credentials", False, str(e))
            return False
    
    def test_auth_login_wrong_password(self):
        """Test user login with wrong password"""
        try:
            # Use the email from previous test but wrong password
            login_payload = {
                "email": "test@example.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            # Should return 401 for invalid credentials
            success = response.status_code == 401
            
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower()
                details = f"Correctly rejected wrong password: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 401"
            
            self.log_test("Auth Login - Wrong Password", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Login - Wrong Password", False, str(e))
            return False
    
    def test_auth_login_nonexistent_email(self):
        """Test user login with non-existent email"""
        try:
            login_payload = {
                "email": "nonexistent@example.com",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_payload, timeout=10)
            # Should return 401 for invalid credentials
            success = response.status_code == 401
            
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower()
                details = f"Correctly rejected non-existent email: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 401"
            
            self.log_test("Auth Login - Non-existent Email", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Login - Non-existent Email", False, str(e))
            return False
    
    def test_auth_me_valid_token(self):
        """Test /auth/me endpoint with valid JWT token"""
        try:
            if not self.auth_token:
                self.log_test("Auth Me - Valid Token", False, "No auth token available from previous tests")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Verify user profile structure
                required_fields = ["id", "email", "first_name", "last_name", "role", "owned_territories", "created_at", "is_active"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Profile retrieved for {data['email']}, Role: {data['role']}, Active: {data['is_active']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.log_test("Auth Me - Valid Token", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Me - Valid Token", False, str(e))
            return False
    
    def test_auth_me_invalid_token(self):
        """Test /auth/me endpoint with invalid JWT token"""
        try:
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            # Should return 401 for invalid token
            success = response.status_code == 401
            
            if success:
                data = response.json()
                success = "invalid" in data.get("detail", "").lower() or "token" in data.get("detail", "").lower()
                details = f"Correctly rejected invalid token: {data.get('detail')}" if success else f"Unexpected error message: {data.get('detail')}"
            else:
                details = f"Status: {response.status_code}, Expected: 401"
            
            self.log_test("Auth Me - Invalid Token", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Me - Invalid Token", False, str(e))
            return False
    
    def test_auth_me_no_token(self):
        """Test /auth/me endpoint with no authorization header"""
        try:
            response = requests.get(f"{self.api_url}/auth/me", timeout=10)
            # Should return 403 for missing authorization
            success = response.status_code == 403
            
            if success:
                details = "Correctly rejected request without authorization header"
            else:
                details = f"Status: {response.status_code}, Expected: 403"
            
            self.log_test("Auth Me - No Token", success, details)
            return success
            
        except Exception as e:
            self.log_test("Auth Me - No Token", False, str(e))
            return False
    
    def test_territory_assignment(self):
        """Test territory assignment functionality"""
        try:
            # First create a test user with specific email pattern
            timestamp = 1756780976  # Use the specific timestamp from the request
            test_email = f"territory{timestamp}@example.com"
            
            # Register the test user
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "first_name": "Territory",
                "last_name": "Test"
            }
            
            register_response = requests.post(f"{self.api_url}/auth/register", json=register_payload, timeout=10)
            if register_response.status_code != 200:
                self.log_test("Territory Assignment - User Registration", False, f"Failed to register test user: {register_response.status_code}")
                return False
            
            # Get the JWT token
            register_data = register_response.json()
            user_token = register_data["access_token"]
            user_id = register_data["user"]["id"]
            
            # Test 1: Assign ZIP code "10001" to the user
            headers = {"Authorization": f"Bearer {user_token}"}
            territory_payload = {"zip_code": "10001"}
            
            assign_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            success_assign = assign_response.status_code == 200
            if success_assign:
                assign_data = assign_response.json()
                success_assign = assign_data.get("zip_code") == "10001"
                assign_details = f"Territory assigned: {assign_data.get('message', 'No message')}" if success_assign else f"Unexpected response: {assign_data}"
            else:
                assign_details = f"Status: {assign_response.status_code}, Response: {assign_response.text[:200]}"
            
            self.log_test("Territory Assignment - Assign ZIP 10001", success_assign, assign_details)
            
            # Test 2: Verify territory appears in user's profile via /auth/me
            me_response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success_me = me_response.status_code == 200
            
            if success_me:
                me_data = me_response.json()
                owned_territories = me_data.get("owned_territories", [])
                success_me = "10001" in owned_territories
                me_details = f"User territories: {owned_territories}" if success_me else f"ZIP 10001 not found in territories: {owned_territories}"
            else:
                me_details = f"Status: {me_response.status_code}"
            
            self.log_test("Territory Assignment - Verify in User Profile", success_me, me_details)
            
            # Test 3: Create super admin to test admin endpoint
            admin_payload = {
                "email": f"admin{timestamp}@example.com",
                "password": "adminpass123",
                "first_name": "Super",
                "last_name": "Admin"
            }
            
            admin_response = requests.post(f"{self.api_url}/admin/create-super-admin", json=admin_payload, timeout=10)
            if admin_response.status_code != 200:
                self.log_test("Territory Assignment - Admin Creation", False, f"Failed to create admin: {admin_response.status_code}")
                return False
            
            admin_data = admin_response.json()
            admin_token = admin_data["access_token"]
            
            # Test 4: Use admin token to get all users and verify territory
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            users_response = requests.get(f"{self.api_url}/admin/users", headers=admin_headers, timeout=10)
            
            success_admin = users_response.status_code == 200
            if success_admin:
                users_data = users_response.json()
                # Find the test user
                test_user = None
                for user in users_data:
                    if "territory1756780976" in user.get("email", ""):
                        test_user = user
                        break
                
                if test_user:
                    territories_count = test_user.get("total_territories", 0)
                    owned_territories = test_user.get("owned_territories", [])
                    success_admin = territories_count == 1 and "10001" in owned_territories
                    admin_details = f"Found user with email containing 'territory1756780976': {test_user['email']}, territories: {owned_territories}, count: {territories_count}" if success_admin else f"User found but wrong territory data: territories={owned_territories}, count={territories_count}"
                else:
                    success_admin = False
                    admin_details = f"User with email containing 'territory1756780976' not found in admin list. Available emails: {[u.get('email') for u in users_data[:5]]}"
            else:
                admin_details = f"Status: {users_response.status_code}"
            
            self.log_test("Territory Assignment - Admin Dashboard Verification", success_admin, admin_details)
            
            # Test 5: Test duplicate territory assignment
            duplicate_response = requests.post(
                f"{self.api_url}/users/assign-territory", 
                json=territory_payload, 
                headers=headers, 
                timeout=10
            )
            
            success_duplicate = duplicate_response.status_code == 200
            if success_duplicate:
                duplicate_data = duplicate_response.json()
                success_duplicate = "already assigned" in duplicate_data.get("message", "").lower()
                duplicate_details = f"Correctly handled duplicate assignment: {duplicate_data.get('message')}" if success_duplicate else f"Unexpected response for duplicate: {duplicate_data}"
            else:
                duplicate_details = f"Status: {duplicate_response.status_code}"
            
            self.log_test("Territory Assignment - Duplicate Assignment Handling", success_duplicate, duplicate_details)
            
            return success_assign and success_me and success_admin and success_duplicate
            
        except Exception as e:
            self.log_test("Territory Assignment - General", False, str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting ZIP Intel Generator API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API availability
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        print("\n🔐 Testing Authentication System...")
        
        # Test user registration
        print("\n📝 Testing User Registration...")
        self.test_auth_register_valid()
        self.test_auth_register_duplicate_email()
        self.test_auth_register_weak_password()
        
        # Test user login
        print("\n🔑 Testing User Login...")
        self.test_auth_login_valid()
        self.test_auth_login_wrong_password()
        self.test_auth_login_nonexistent_email()
        
        # Test /auth/me endpoint
        print("\n👤 Testing User Profile Endpoint...")
        self.test_auth_me_valid_token()
        self.test_auth_me_invalid_token()
        self.test_auth_me_no_token()
        
        # Test territory assignment functionality
        print("\n🗺️ Testing Territory Assignment...")
        self.test_territory_assignment()
        
        print("\n📋 Testing ZIP Code Validation...")
        self.test_invalid_zip_validation()
        
        print("\n🏠 Testing ZIP Analysis Workflow...")
        
        # Test with one primary ZIP code for full workflow
        primary_zip = self.test_zip_codes[0]  # 90210
        
        print(f"\n🔍 Testing full workflow with ZIP: {primary_zip}")
        
        # Create analysis
        success, analysis_data = self.test_zip_analysis_creation(primary_zip)
        if not success:
            print(f"❌ Failed to create analysis for {primary_zip}. Skipping dependent tests.")
            return False
        
        # Wait a moment for data to be available
        time.sleep(2)
        
        # Test retrieval
        self.test_zip_analysis_retrieval(primary_zip)
        
        # Test PDF generation
        self.test_pdf_generation(primary_zip)
        
        # Test content assets
        self.test_content_assets(primary_zip)
        
        # Test additional ZIP codes for creation only
        print(f"\n🌍 Testing additional ZIP codes...")
        for zip_code in self.test_zip_codes[1:]:
            self.test_zip_analysis_creation(zip_code)
            time.sleep(1)  # Brief pause between requests
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! API is fully functional.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    tester = ZipIntelAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())