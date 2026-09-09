#!/usr/bin/env python3
"""
Backend test for Email OTP verification and listing creation with emailVerified.
Tests against NEXT_PUBLIC_BASE_URL/api endpoints.
SMTP env vars are intentionally NOT set, so demo OTP fallback must be active.
"""

import requests
import sys
import re

# Read NEXT_PUBLIC_BASE_URL from .env
BASE_URL = None
try:
    with open('/app/.env', 'r') as f:
        for line in f:
            if line.startswith('NEXT_PUBLIC_BASE_URL='):
                BASE_URL = line.split('=', 1)[1].strip()
                break
except Exception as e:
    print(f"❌ Failed to read .env: {e}")
    sys.exit(1)

if not BASE_URL:
    print("❌ NEXT_PUBLIC_BASE_URL not found in .env")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"
print(f"🧪 Testing Email OTP backend against: {API_BASE}\n")

passed = 0
failed = 0

def assert_test(condition, message):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {message}")
    else:
        failed += 1
        print(f"  ❌ {message}")

def check_no_objectid(data, context=""):
    """Ensure no Mongo ObjectID (_id) leaks in response"""
    if isinstance(data, dict):
        if '_id' in data:
            assert_test(False, f"{context} contains _id (ObjectID leak)")
            return False
        for v in data.values():
            if not check_no_objectid(v, context):
                return False
    elif isinstance(data, list):
        for item in data:
            if not check_no_objectid(item, context):
                return False
    return True

# Test owner email
owner_email = "owner@example.com"
invalid_email = "notanemail"
dev_otp = None
listing_id = None
listing_uuid = None

print("=" * 70)
print("Test 1: Email OTP send with valid email")
print("=" * 70)
try:
    resp = requests.post(f"{API_BASE}/listings/verify/send", json={"channel": "email", "value": owner_email}, timeout=10)
    print(f"POST /listings/verify/send → {resp.status_code}")
    assert_test(resp.status_code == 200, "Status 200 for valid email send")
    
    data = resp.json()
    print(f"Response: {data}")
    
    assert_test('sent' in data and data['sent'] is True, "Response contains sent:true")
    assert_test('mocked' in data and data['mocked'] is True, "Response contains mocked:true (demo fallback)")
    assert_test('devOtp' in data, "Response contains devOtp (demo OTP)")
    
    if 'devOtp' in data:
        dev_otp = data['devOtp']
        assert_test(isinstance(dev_otp, str) and len(dev_otp) == 6 and dev_otp.isdigit(), 
                   f"devOtp is 6-digit string: {dev_otp}")
    
    check_no_objectid(data, "OTP send response")
    
except Exception as e:
    print(f"❌ Test 1 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 2: Email OTP send with invalid email")
print("=" * 70)
try:
    resp = requests.post(f"{API_BASE}/listings/verify/send", json={"channel": "email", "value": invalid_email}, timeout=10)
    print(f"POST /listings/verify/send (invalid email) → {resp.status_code}")
    assert_test(resp.status_code == 400, "Status 400 for invalid email format")
    
    data = resp.json()
    print(f"Response: {data}")
    assert_test('error' in data, "Response contains error message")
    
except Exception as e:
    print(f"❌ Test 2 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 3: Email OTP check with correct OTP")
print("=" * 70)
if dev_otp:
    try:
        resp = requests.post(f"{API_BASE}/listings/verify/check", json={"value": owner_email, "otp": dev_otp}, timeout=10)
        print(f"POST /listings/verify/check (correct OTP) → {resp.status_code}")
        assert_test(resp.status_code == 200, "Status 200 for correct OTP")
        
        data = resp.json()
        print(f"Response: {data}")
        
        assert_test('verified' in data and data['verified'] is True, "Response contains verified:true")
        assert_test('channel' in data and data['channel'] == 'email', "Response contains channel:'email'")
        
        check_no_objectid(data, "OTP check response")
        
    except Exception as e:
        print(f"❌ Test 3 failed with exception: {e}")
        failed += 1
else:
    print("⚠️  Skipping Test 3: No devOtp from Test 1")
    failed += 1

print("\n" + "=" * 70)
print("Test 4: Email OTP check with wrong OTP")
print("=" * 70)
try:
    resp = requests.post(f"{API_BASE}/listings/verify/check", json={"value": owner_email, "otp": "000000"}, timeout=10)
    print(f"POST /listings/verify/check (wrong OTP) → {resp.status_code}")
    assert_test(resp.status_code == 400, "Status 400 for wrong OTP")
    
    data = resp.json()
    print(f"Response: {data}")
    assert_test('error' in data, "Response contains error message")
    
except Exception as e:
    print(f"❌ Test 4 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 5: Email OTP check for email that never got a code")
print("=" * 70)
try:
    new_email = "newemail@example.com"
    resp = requests.post(f"{API_BASE}/listings/verify/check", json={"value": new_email, "otp": "123456"}, timeout=10)
    print(f"POST /listings/verify/check (no prior send) → {resp.status_code}")
    assert_test(resp.status_code == 400, "Status 400 for email without prior send")
    
    data = resp.json()
    print(f"Response: {data}")
    assert_test('error' in data, "Response contains error message")
    
except Exception as e:
    print(f"❌ Test 5 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 6: Listing creation with valid payload")
print("=" * 70)
try:
    valid_payload = {
        "title": "Test Hillside Villa",
        "category": "Villa",
        "listingType": "For sale",
        "price": "₹ 85 L",
        "contactName": "Test Owner",
        "email": owner_email,
        "emailVerified": True,
        "authorized": True,
        "photos": ["data:image/jpeg;base64,AAA"],
        "area": "1800",
        "areaUnit": "sq. ft.",
        "district": "Solan",
        "city": "Kasauli",
        "state": "Himachal Pradesh",
        "bedrooms": "3",
        "bathrooms": "2",
        "description": "A beautiful hillside villa for testing"
    }
    
    resp = requests.post(f"{API_BASE}/listings", json=valid_payload, timeout=10)
    print(f"POST /listings (valid payload) → {resp.status_code}")
    assert_test(resp.status_code == 201, "Status 201 for valid listing creation")
    
    data = resp.json()
    print(f"Response: {data}")
    
    assert_test('listingId' in data, "Response contains listingId")
    if 'listingId' in data:
        listing_id = data['listingId']
        pattern = r'^HB-[A-Z0-9]{6}$'
        assert_test(re.match(pattern, listing_id) is not None, 
                   f"listingId matches pattern /^HB-[A-Z0-9]{{6}}$/: {listing_id}")
    
    assert_test('id' in data, "Response contains UUID id")
    if 'id' in data:
        listing_uuid = data['id']
        # Check if it's a valid UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert_test(re.match(uuid_pattern, listing_uuid) is not None, 
                   f"id is valid UUID: {listing_uuid}")
    
    assert_test('status' in data and data['status'] == 'pending_review', 
               "Response contains status:'pending_review'")
    
    check_no_objectid(data, "Listing creation response")
    
except Exception as e:
    print(f"❌ Test 6 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 7: Listing creation validation - missing email")
print("=" * 70)
try:
    invalid_payload = {
        "title": "Test Villa",
        "category": "Villa",
        "listingType": "For sale",
        "price": "₹ 85 L",
        "contactName": "Test Owner",
        # email missing
        "emailVerified": True,
        "authorized": True
    }
    
    resp = requests.post(f"{API_BASE}/listings", json=invalid_payload, timeout=10)
    print(f"POST /listings (missing email) → {resp.status_code}")
    assert_test(resp.status_code == 400, "Status 400 for missing email")
    
    data = resp.json()
    print(f"Response: {data}")
    assert_test('error' in data, "Response contains error message")
    
except Exception as e:
    print(f"❌ Test 7 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 8: Listing creation validation - email present but emailVerified:false")
print("=" * 70)
try:
    invalid_payload = {
        "title": "Test Villa",
        "category": "Villa",
        "listingType": "For sale",
        "price": "₹ 85 L",
        "contactName": "Test Owner",
        "email": owner_email,
        "emailVerified": False,  # Not verified
        "authorized": True
    }
    
    resp = requests.post(f"{API_BASE}/listings", json=invalid_payload, timeout=10)
    print(f"POST /listings (emailVerified:false) → {resp.status_code}")
    assert_test(resp.status_code == 400, "Status 400 for emailVerified:false")
    
    data = resp.json()
    print(f"Response: {data}")
    assert_test('error' in data, "Response contains error message")
    
except Exception as e:
    print(f"❌ Test 8 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 9: Listing creation validation - emailVerified:true but authorized:false")
print("=" * 70)
try:
    invalid_payload = {
        "title": "Test Villa",
        "category": "Villa",
        "listingType": "For sale",
        "price": "₹ 85 L",
        "contactName": "Test Owner",
        "email": owner_email,
        "emailVerified": True,
        "authorized": False  # Not authorized
    }
    
    resp = requests.post(f"{API_BASE}/listings", json=invalid_payload, timeout=10)
    print(f"POST /listings (authorized:false) → {resp.status_code}")
    assert_test(resp.status_code == 400, "Status 400 for authorized:false")
    
    data = resp.json()
    print(f"Response: {data}")
    assert_test('error' in data, "Response contains error message")
    
except Exception as e:
    print(f"❌ Test 9 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print("Test 10: DELETE listing cleanup")
print("=" * 70)
if listing_uuid:
    try:
        resp = requests.delete(f"{API_BASE}/listings/{listing_uuid}", timeout=10)
        print(f"DELETE /listings/{listing_uuid} → {resp.status_code}")
        assert_test(resp.status_code == 200, "Status 200 for DELETE")
        
        data = resp.json()
        print(f"Response: {data}")
        assert_test('success' in data and data['success'] is True, "Response contains success:true")
        
        check_no_objectid(data, "DELETE response")
        
    except Exception as e:
        print(f"❌ Test 10 failed with exception: {e}")
        failed += 1
else:
    print("⚠️  Skipping Test 10: No listing UUID from Test 6")
    failed += 1

print("\n" + "=" * 70)
print("Test 11: Regression - GET /properties still returns seeded data")
print("=" * 70)
try:
    resp = requests.get(f"{API_BASE}/properties", timeout=10)
    print(f"GET /properties → {resp.status_code}")
    assert_test(resp.status_code == 200, "Status 200 for GET /properties")
    
    data = resp.json()
    assert_test('properties' in data, "Response contains properties array")
    
    if 'properties' in data:
        properties = data['properties']
        assert_test(len(properties) > 0, f"Properties array not empty: {len(properties)} properties")
        
        # Check for seeded properties
        titles = [p.get('title', '') for p in properties]
        assert_test('The Cedar House' in titles or 'Pinecrest Estate' in titles, 
                   "Seeded properties present")
        
        # Check no ObjectID leaks
        check_no_objectid(properties, "Properties array")
        
        # Check all have UUID ids
        for prop in properties:
            if 'id' in prop:
                uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                if not re.match(uuid_pattern, prop['id']):
                    assert_test(False, f"Property has non-UUID id: {prop['id']}")
    
except Exception as e:
    print(f"❌ Test 11 failed with exception: {e}")
    failed += 1

print("\n" + "=" * 70)
print(f"📊 Test Summary: {passed} passed, {failed} failed")
print("=" * 70)

if failed > 0:
    print("❌ Some tests failed")
    sys.exit(1)
else:
    print("✅ All tests passed")
    sys.exit(0)
