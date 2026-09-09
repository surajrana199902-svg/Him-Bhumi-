#!/usr/bin/env python3
"""
Regression test for refactored verification endpoint in HimBhumi app.
Tests demo OTP fallback when Twilio env vars are NOT set.
"""
import requests
import re
import json
import os

BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://himalayan-estates-1.preview.emergentagent.com') + '/api'

def check_no_objectid(data, path="root"):
    """Recursively check for MongoDB ObjectID leaks (_id field)"""
    if isinstance(data, dict):
        if '_id' in data:
            print(f"❌ CRITICAL: ObjectID leak found at {path}: {data['_id']}")
            return False
        return all(check_no_objectid(v, f"{path}.{k}") for k, v in data.items())
    elif isinstance(data, list):
        return all(check_no_objectid(item, f"{path}[{i}]") for i, item in enumerate(data))
    return True

def test_verification_regression():
    """Run all regression tests for verification endpoint"""
    print("=" * 80)
    print("HimBhumi Verification Endpoint Regression Test")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print()
    
    test_mobile = "9876500001"
    dev_otp = None
    listing_id = None
    
    # Test 1: Send OTP with valid mobile number
    print("Test 1: POST /api/listings/verify/send with valid mobile")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/listings/verify/send",
            json={"channel": "mobile", "value": test_mobile},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'devOtp' in data, "Missing devOtp in response"
        assert 'mocked' in data, "Missing mocked flag in response"
        assert data['mocked'] is True, f"Expected mocked=true, got {data['mocked']}"
        assert 'sent' in data and data['sent'] is True, "Expected sent=true"
        
        dev_otp = data['devOtp']
        assert isinstance(dev_otp, str), f"devOtp should be string, got {type(dev_otp)}"
        assert len(dev_otp) == 6, f"devOtp should be 6 digits, got {len(dev_otp)}"
        assert dev_otp.isdigit(), f"devOtp should be numeric, got {dev_otp}"
        
        assert check_no_objectid(data, "verify/send"), "ObjectID leak detected"
        
        print(f"✅ Test 1 PASSED: Got 6-digit devOtp={dev_otp}, mocked=true")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False
    
    print()
    
    # Test 2: Check OTP with correct code
    print("Test 2: POST /api/listings/verify/check with correct OTP")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/listings/verify/check",
            json={"channel": "mobile", "value": test_mobile, "otp": dev_otp},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'verified' in data, "Missing verified in response"
        assert data['verified'] is True, f"Expected verified=true, got {data['verified']}"
        
        assert check_no_objectid(data, "verify/check"), "ObjectID leak detected"
        
        print(f"✅ Test 2 PASSED: OTP verified successfully")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False
    
    print()
    
    # Test 3: Re-send OTP for wrong OTP test
    print("Test 3: Re-send OTP for wrong OTP test")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/listings/verify/send",
            json={"channel": "mobile", "value": test_mobile},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        dev_otp = data['devOtp']
        print(f"✅ Test 3 PASSED: Re-sent OTP, got devOtp={dev_otp}")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False
    
    print()
    
    # Test 4: Check OTP with wrong code
    print("Test 4: POST /api/listings/verify/check with wrong OTP")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/listings/verify/check",
            json={"channel": "mobile", "value": test_mobile, "otp": "000000"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert 'error' in data, "Expected error message in response"
        
        assert check_no_objectid(data, "verify/check-wrong"), "ObjectID leak detected"
        
        print(f"✅ Test 4 PASSED: Wrong OTP correctly rejected with 400")
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return False
    
    print()
    
    # Test 5: Send OTP with empty value
    print("Test 5: POST /api/listings/verify/send with empty value")
    print("-" * 80)
    try:
        response = requests.post(
            f"{BASE_URL}/listings/verify/send",
            json={"channel": "mobile", "value": ""},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert 'error' in data, "Expected error message in response"
        
        assert check_no_objectid(data, "verify/send-empty"), "ObjectID leak detected"
        
        print(f"✅ Test 5 PASSED: Empty value correctly rejected with 400")
    except Exception as e:
        print(f"❌ Test 5 FAILED: {e}")
        return False
    
    print()
    
    # Test 6: Full listing creation
    print("Test 6: POST /api/listings - Full listing creation")
    print("-" * 80)
    try:
        listing_payload = {
            "title": "Regression Villa",
            "category": "Villa",
            "listingType": "For sale",
            "price": "₹ 90 L",
            "area": "1800",
            "areaUnit": "sq. ft.",
            "state": "Himachal Pradesh",
            "district": "Solan",
            "city": "Solan",
            "contactName": "Reg Owner",
            "contactMobile": test_mobile,
            "mobileVerified": True,
            "authorized": True,
            "photos": ["data:image/jpeg;base64,AAA"]
        }
        
        response = requests.post(
            f"{BASE_URL}/listings",
            json=listing_payload,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        assert 'listingId' in data, "Missing listingId in response"
        assert 'id' in data, "Missing id in response"
        assert 'status' in data, "Missing status in response"
        
        listing_id = data['id']
        listing_human_id = data['listingId']
        
        # Validate listingId format: HB-[A-Z0-9]{6}
        pattern = r'^HB-[A-Z0-9]{6}$'
        assert re.match(pattern, listing_human_id), f"listingId '{listing_human_id}' doesn't match pattern {pattern}"
        
        assert data['status'] == 'pending_review', f"Expected status=pending_review, got {data['status']}"
        
        assert check_no_objectid(data, "listings/create"), "ObjectID leak detected"
        
        print(f"✅ Test 6 PASSED: Listing created with listingId={listing_human_id}, id={listing_id}, status=pending_review")
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
        return False
    
    print()
    
    # Test 7: Delete the created listing (cleanup)
    print("Test 7: DELETE /api/listings/:id - Cleanup")
    print("-" * 80)
    try:
        response = requests.delete(
            f"{BASE_URL}/listings/{listing_id}",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'success' in data and data['success'] is True, "Expected success=true"
        
        assert check_no_objectid(data, "listings/delete"), "ObjectID leak detected"
        
        print(f"✅ Test 7 PASSED: Listing deleted successfully")
    except Exception as e:
        print(f"❌ Test 7 FAILED: {e}")
        return False
    
    print()
    print("=" * 80)
    print("✅ ALL REGRESSION TESTS PASSED")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = test_verification_regression()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
