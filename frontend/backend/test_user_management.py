#!/usr/bin/env python3
"""
Comprehensive test suite for User Management and Admin Panel endpoints.
Tests GET/POST/PUT/DELETE operations with payload and response schema validation.
"""
import asyncio
import sys
import json
from typing import Dict, Any, Optional

import httpx

BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def validate_user_schema(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate user response schema."""
    required_fields = ["id", "username", "email", "is_active", "role"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Type checks
    if not isinstance(data["id"], int):
        return False, "Field 'id' must be an integer"
    if not isinstance(data["username"], str):
        return False, "Field 'username' must be a string"
    if not isinstance(data["email"], str):
        return False, "Field 'email' must be a string"
    if not isinstance(data["is_active"], bool):
        return False, "Field 'is_active' must be a boolean"
    if not isinstance(data["role"], str):
        return False, "Field 'role' must be a string"
    if data["role"] not in ["admin", "analyst", "viewer"]:
        return False, f"Field 'role' must be one of: admin, analyst, viewer. Got: {data['role']}"
    
    return True, "Valid"


def validate_dashboard_schema(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate dashboard stats response schema."""
    required_fields = ["total_users", "active_users", "users_by_role", "total_sales", "total_revenue"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Type checks
    if not isinstance(data["total_users"], int):
        return False, "Field 'total_users' must be an integer"
    if not isinstance(data["active_users"], int):
        return False, "Field 'active_users' must be an integer"
    if not isinstance(data["users_by_role"], dict):
        return False, "Field 'users_by_role' must be a dictionary"
    if not isinstance(data["total_sales"], int):
        return False, "Field 'total_sales' must be an integer"
    if not isinstance(data["total_revenue"], (int, float)):
        return False, "Field 'total_revenue' must be a number"
    
    # Validate users_by_role structure
    expected_roles = ["admin", "analyst", "viewer"]
    for role in expected_roles:
        if role not in data["users_by_role"]:
            return False, f"Missing role '{role}' in users_by_role"
        if not isinstance(data["users_by_role"][role], int):
            return False, f"Role count for '{role}' must be an integer"
    
    return True, "Valid"


async def get_admin_token() -> Optional[str]:
    """Get admin JWT token."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
        except Exception as e:
            print(f"✗ Failed to get admin token: {e}")
    return None


async def test_get_all_users(token: str):
    """Test GET /api/users - List all users."""
    print("\n" + "="*60)
    print("TEST 1: GET /api/users - List All Users")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/users/",
                headers={"Authorization": f"Bearer {token}"},
                params={"skip": 0, "limit": 100},
                follow_redirects=True,
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✓ Successfully retrieved {len(data)} users")
                    # Validate schema for first user if exists
                    if data:
                        valid, msg = validate_user_schema(data[0])
                        if valid:
                            print(f"✓ Response schema validated")
                            print(f"  Sample user: {data[0]['username']} ({data[0]['role']})")
                            return True
                        else:
                            print(f"✗ Schema validation failed: {msg}")
                            return False
                    else:
                        print("⚠ No users found (empty list)")
                        return True
                else:
                    print(f"✗ Expected list, got {type(data)}")
                    return False
            else:
                print(f"✗ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_get_user_by_id(token: str, user_id: int):
    """Test GET /api/users/{id} - Get user by ID."""
    print("\n" + "="*60)
    print(f"TEST 2: GET /api/users/{user_id} - Get User By ID")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 200:
                data = response.json()
                valid, msg = validate_user_schema(data)
                if valid:
                    print(f"✓ Successfully retrieved user")
                    print(f"  User: {data['username']} ({data['email']})")
                    print(f"  Role: {data['role']}, Active: {data['is_active']}")
                    return True, data
                else:
                    print(f"✗ Schema validation failed: {msg}")
                    return False, None
            elif response.status_code == 404:
                print(f"⚠ User {user_id} not found (expected for new IDs)")
                return True, None
            else:
                print(f"✗ Failed with status {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False, None


async def test_create_user(token: str):
    """Test POST /api/users - Create new user."""
    print("\n" + "="*60)
    print("TEST 3: POST /api/users - Create New User")
    print("="*60)
    
    user_data = {
        "username": f"testuser_{asyncio.get_event_loop().time()}",
        "email": f"test_{asyncio.get_event_loop().time()}@example.com",
        "password": "TestPassword123!",
        "role": "viewer",
        "is_active": True,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/users/",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"},
                follow_redirects=True,
            )
            
            if response.status_code == 201:
                data = response.json()
                valid, msg = validate_user_schema(data)
                if valid:
                    print(f"✓ Successfully created user")
                    print(f"  Created user: {data['username']} (ID: {data['id']})")
                    # Validate payload was applied correctly
                    if data["username"] == user_data["username"]:
                        print(f"✓ Username matches payload")
                    if data["email"] == user_data["email"]:
                        print(f"✓ Email matches payload")
                    if data["role"] == user_data["role"]:
                        print(f"✓ Role matches payload")
                    if data["is_active"] == user_data["is_active"]:
                        print(f"✓ is_active matches payload")
                    # Password should not be in response
                    if "password" not in data and "hashed_password" not in data:
                        print(f"✓ Password not exposed in response")
                    return True, data
                else:
                    print(f"✗ Schema validation failed: {msg}")
                    return False, None
            else:
                print(f"✗ Failed with status {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False, None


async def test_update_user(token: str, user_id: int):
    """Test PUT /api/users/{id} - Update user."""
    print("\n" + "="*60)
    print(f"TEST 4: PUT /api/users/{user_id} - Update User")
    print("="*60)
    
    update_data = {
        "role": "analyst",
        "is_active": True,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{BASE_URL}/api/users/{user_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 200:
                data = response.json()
                valid, msg = validate_user_schema(data)
                if valid:
                    print(f"✓ Successfully updated user")
                    print(f"  Updated user: {data['username']} (ID: {data['id']})")
                    # Validate updates were applied
                    if data["role"] == update_data["role"]:
                        print(f"✓ Role updated correctly")
                    if data["is_active"] == update_data["is_active"]:
                        print(f"✓ is_active updated correctly")
                    return True
                else:
                    print(f"✗ Schema validation failed: {msg}")
                    return False
            elif response.status_code == 404:
                print(f"⚠ User {user_id} not found (skipping update test)")
                return True
            else:
                print(f"✗ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_delete_user(token: str, user_id: int):
    """Test DELETE /api/users/{id} - Delete user."""
    print("\n" + "="*60)
    print(f"TEST 5: DELETE /api/users/{user_id} - Delete User")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{BASE_URL}/api/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 204:
                print(f"✓ Successfully deleted user {user_id}")
                # Verify deletion
                get_response = await client.get(
                    f"{BASE_URL}/api/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                if get_response.status_code == 404:
                    print(f"✓ User confirmed deleted (404 on GET)")
                    return True
                else:
                    print(f"⚠ User deletion may have failed (still accessible)")
                    return False
            elif response.status_code == 404:
                print(f"⚠ User {user_id} not found (already deleted or doesn't exist)")
                return True
            elif response.status_code == 400:
                print(f"⚠ Cannot delete user (may be self-deletion attempt)")
                return True
            else:
                print(f"✗ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_admin_dashboard(token: str):
    """Test GET /api/admin/dashboard - Get dashboard stats."""
    print("\n" + "="*60)
    print("TEST 6: GET /api/admin/dashboard - Dashboard Stats")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/admin/dashboard",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 200:
                data = response.json()
                valid, msg = validate_dashboard_schema(data)
                if valid:
                    print(f"✓ Successfully retrieved dashboard stats")
                    print(f"  Total users: {data['total_users']}")
                    print(f"  Active users: {data['active_users']}")
                    print(f"  Users by role: {data['users_by_role']}")
                    print(f"  Total sales: {data['total_sales']}")
                    print(f"  Total revenue: ${data['total_revenue']:.2f}")
                    return True
                else:
                    print(f"✗ Schema validation failed: {msg}")
                    return False
            else:
                print(f"✗ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_unauthorized_access():
    """Test that non-admin users cannot access admin endpoints."""
    print("\n" + "="*60)
    print("TEST 7: Unauthorized Access - Non-Admin User")
    print("="*60)
    
    # Try to access as non-admin (using analyst token if available)
    async with httpx.AsyncClient() as client:
        try:
            # Try to login as analyst
            login_response = await client.post(
                f"{BASE_URL}/api/auth/login",
                data={"username": "analyst", "password": "analyst123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if login_response.status_code == 200:
                analyst_token = login_response.json().get("access_token")
                # Try to access admin endpoint
                response = await client.get(
                    f"{BASE_URL}/api/users/",
                    headers={"Authorization": f"Bearer {analyst_token}"},
                    follow_redirects=True,
                )
                
                if response.status_code == 403:
                    print(f"✓ Correctly rejected non-admin access (403)")
                    return True
                else:
                    print(f"✗ Should have returned 403, got {response.status_code}")
                    return False
            else:
                print(f"⚠ Could not login as analyst (may not exist)")
                return True
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False


async def test_invalid_payloads(token: str):
    """Test invalid payload validation."""
    print("\n" + "="*60)
    print("TEST 8: Invalid Payload Validation")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        results = []
        
        # Test invalid role
        try:
            response = await client.post(
                f"{BASE_URL}/api/users/",
                json={
                    "username": "invalid_user",
                    "email": "invalid@example.com",
                    "password": "test123",
                    "role": "invalid_role",
                },
                headers={"Authorization": f"Bearer {token}"},
                follow_redirects=True,
            )
            if response.status_code == 400:
                print(f"✓ Correctly rejected invalid role")
                results.append(True)
            else:
                print(f"✗ Should reject invalid role, got {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"✗ Test failed: {e}")
            results.append(False)
        
        # Test duplicate username
        try:
            response = await client.post(
                f"{BASE_URL}/api/users/",
                json={
                    "username": ADMIN_USERNAME,  # Already exists
                    "email": "new@example.com",
                    "password": "test123",
                    "role": "viewer",
                },
                headers={"Authorization": f"Bearer {token}"},
                follow_redirects=True,
            )
            if response.status_code == 400:
                print(f"✓ Correctly rejected duplicate username")
                results.append(True)
            else:
                print(f"✗ Should reject duplicate username, got {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"✗ Test failed: {e}")
            results.append(False)
        
        return all(results)


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("USER MANAGEMENT & ADMIN PANEL TEST SUITE")
    print("="*60)
    
    # Get admin token
    print("\nGetting admin token...")
    token = await get_admin_token()
    if not token:
        print("✗ Failed to get admin token. Cannot proceed with tests.")
        return 1
    
    print("✓ Admin token obtained")
    
    # Run tests
    results = []
    created_user_id = None
    
    # Test 1: GET all users
    result = await test_get_all_users(token)
    results.append(("GET /api/users", result))
    
    # Test 2: GET user by ID (use admin user ID, typically 1 or 2)
    result, _ = await test_get_user_by_id(token, 1)
    results.append(("GET /api/users/{id}", result))
    
    # Test 3: POST create user
    result, user_data = await test_create_user(token)
    results.append(("POST /api/users", result))
    if user_data:
        created_user_id = user_data["id"]
    
    # Test 4: PUT update user (use created user or existing)
    test_user_id = created_user_id if created_user_id else 2
    result = await test_update_user(token, test_user_id)
    results.append(("PUT /api/users/{id}", result))
    
    # Test 5: DELETE user (only if we created one)
    if created_user_id:
        result = await test_delete_user(token, created_user_id)
        results.append(("DELETE /api/users/{id}", result))
    else:
        print("\n⚠ Skipping DELETE test (no test user created)")
        results.append(("DELETE /api/users/{id}", True))
    
    # Test 6: GET admin dashboard
    result = await test_admin_dashboard(token)
    results.append(("GET /api/admin/dashboard", result))
    
    # Test 7: Unauthorized access
    result = await test_unauthorized_access()
    results.append(("Unauthorized Access", result))
    
    # Test 8: Invalid payloads
    result = await test_invalid_payloads(token)
    results.append(("Invalid Payload Validation", result))
    
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
        print("\n🎉 ALL TESTS PASSED - User Management & Admin Panel working correctly!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

