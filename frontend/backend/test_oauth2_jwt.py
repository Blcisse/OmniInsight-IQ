#!/usr/bin/env python3
"""
Test script for OAuth2 login, JWT token issuance, and token validation.
"""
import asyncio
import sys

import httpx


BASE_URL = "http://localhost:8000"
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


async def setup_test_user():
    """Create a test user via the registration endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            # Try to register the user
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": TEST_USERNAME,
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "role": "admin",
                },
            )
            
            if response.status_code == 201:
                print(f"✓ Created test user '{TEST_USERNAME}'")
                return True
            elif response.status_code == 400:
                # User might already exist
                error_data = response.json()
                if "already registered" in str(error_data.get("detail", "")).lower():
                    print(f"✓ Test user '{TEST_USERNAME}' already exists")
                    return True
                else:
                    print(f"⚠ Registration failed: {error_data}")
                    return False
            else:
                print(f"⚠ Registration returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"⚠ Could not register user (may already exist): {e}")
            return False


async def test_oauth2_login():
    """Test OAuth2 login endpoint."""
    print("\n" + "="*60)
    print("TEST 1: OAuth2 Login")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        # Test login with correct credentials
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                data={
                    "username": TEST_USERNAME,
                    "password": TEST_PASSWORD,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and data["token_type"] == "bearer":
                    print(f"✓ Login successful")
                    print(f"  Token type: {data['token_type']}")
                    print(f"  Access token received: {data['access_token'][:50]}...")
                    return data["access_token"]
                else:
                    print(f"✗ Login failed: Invalid response format")
                    print(f"  Response: {data}")
                    return None
            else:
                print(f"✗ Login failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Login request failed: {e}")
            return None


async def test_invalid_login():
    """Test login with invalid credentials."""
    print("\n" + "="*60)
    print("TEST 2: Invalid Login (Should Fail)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                data={
                    "username": TEST_USERNAME,
                    "password": "wrongpassword",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if response.status_code == 401:
                print(f"✓ Correctly rejected invalid credentials (401)")
                return True
            else:
                print(f"✗ Should have returned 401, got {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_jwt_token_validation(token: str):
    """Test JWT token validation endpoint."""
    print("\n" + "="*60)
    print("TEST 3: JWT Token Validation")
    print("="*60)
    
    if not token:
        print("✗ No token provided, skipping validation test")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") and "username" in data:
                    print(f"✓ Token validation successful")
                    print(f"  Username: {data['username']}")
                    print(f"  Role: {data.get('role', 'N/A')}")
                    print(f"  Expires at: {data.get('exp', 'N/A')}")
                    return True
                else:
                    print(f"✗ Token validation failed: Invalid response")
                    print(f"  Response: {data}")
                    return False
            else:
                print(f"✗ Token validation failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Validation request failed: {e}")
            return False


async def test_protected_endpoint(token: str):
    """Test accessing a protected endpoint with JWT token."""
    print("\n" + "="*60)
    print("TEST 4: Protected Endpoint Access")
    print("="*60)
    
    if not token:
        print("✗ No token provided, skipping protected endpoint test")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Successfully accessed protected endpoint")
                print(f"  User ID: {data.get('id')}")
                print(f"  Username: {data.get('username')}")
                print(f"  Email: {data.get('email')}")
                print(f"  Role: {data.get('role')}")
                return True
            else:
                print(f"✗ Failed to access protected endpoint: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Protected endpoint request failed: {e}")
            return False


async def test_invalid_token():
    """Test with an invalid token."""
    print("\n" + "="*60)
    print("TEST 5: Invalid Token (Should Fail)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/auth/validate",
                headers={"Authorization": "Bearer invalid_token_12345"},
            )
            
            if response.status_code == 401:
                print(f"✓ Correctly rejected invalid token (401)")
                return True
            else:
                print(f"✗ Should have returned 401, got {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_missing_token():
    """Test without providing a token."""
    print("\n" + "="*60)
    print("TEST 6: Missing Token (Should Fail)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/auth/me",
            )
            
            if response.status_code == 401 or response.status_code == 403:
                print(f"✓ Correctly rejected request without token ({response.status_code})")
                return True
            else:
                print(f"✗ Should have returned 401/403, got {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("OAUTH2 & JWT AUTHENTICATION TEST SUITE")
    print("="*60)
    
    # Check if server is running
    print("\nChecking server availability...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ Server is running")
            else:
                print(f"✗ Server returned status {response.status_code}")
                return 1
    except Exception as e:
        print(f"✗ Cannot connect to server at {BASE_URL}")
        print(f"  Error: {e}")
        print(f"  Make sure the backend server is running on port 8000")
        return 1
    
    # Setup test user
    print("\nSetting up test user...")
    await setup_test_user()
    
    # Wait a moment for server to be ready
    await asyncio.sleep(1)
    
    # Run tests
    results = []
    
    # Test 1: OAuth2 Login
    token = await test_oauth2_login()
    results.append(("OAuth2 Login", token is not None))
    
    # Test 2: Invalid Login
    invalid_login_result = await test_invalid_login()
    results.append(("Invalid Login Rejection", invalid_login_result))
    
    # Test 3: JWT Token Validation
    if token:
        validation_result = await test_jwt_token_validation(token)
        results.append(("JWT Token Validation", validation_result))
    else:
        results.append(("JWT Token Validation", False))
    
    # Test 4: Protected Endpoint
    if token:
        protected_result = await test_protected_endpoint(token)
        results.append(("Protected Endpoint Access", protected_result))
    else:
        results.append(("Protected Endpoint Access", False))
    
    # Test 5: Invalid Token
    invalid_token_result = await test_invalid_token()
    results.append(("Invalid Token Rejection", invalid_token_result))
    
    # Test 6: Missing Token
    missing_token_result = await test_missing_token()
    results.append(("Missing Token Rejection", missing_token_result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - OAuth2 & JWT Authentication is working correctly!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

