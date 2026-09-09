#!/usr/bin/env python3
"""
Backend test for HimBhumi publish-on-approve and tracker features.
Tests ONLY the two new backend behaviors in /app/app/api/[[...path]]/route.js
"""
import os
import requests
import json
import sys

# Read base URL from .env
BASE_URL = None
with open('/app/.env', 'r') as f:
    for line in f:
        if line.startswith('NEXT_PUBLIC_BASE_URL='):
            BASE_URL = line.split('=', 1)[1].strip()
            break

if not BASE_URL:
    print("❌ NEXT_PUBLIC_BASE_URL not found in .env")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"
print(f"Testing against: {API_BASE}\n")

# Test counters
passed = 0
failed = 0

def test(name, condition, details=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"✅ {name}")
        if details:
            print(f"   {details}")
    else:
        failed += 1
        print(f"❌ {name}")
        if details:
            print(f"   {details}")

def check_no_objectid(data, context=""):
    """Recursively check for MongoDB ObjectID leaks"""
    if isinstance(data, dict):
        if '_id' in data:
            return False, f"Found _id in {context}"
        for key, value in data.items():
            ok, msg = check_no_objectid(value, f"{context}.{key}")
            if not ok:
                return False, msg
    elif isinstance(data, list):
        for i, item in enumerate(data):
            ok, msg = check_no_objectid(item, f"{context}[{i}]")
            if not ok:
                return False, msg
    return True, ""

print("=" * 80)
print("SETUP: Create a listing via POST /api/listings")
print("=" * 80)

listing_payload = {
    "title": "Test Hillside Villa",
    "category": "Villa",
    "listingType": "For sale",
    "price": "₹ 1.2 Cr",
    "area": "2400",
    "areaUnit": "sq. ft.",
    "bedrooms": "3",
    "bathrooms": "2",
    "propertyAge": "New",
    "description": "A test villa",
    "state": "Himachal Pradesh",
    "district": "Solan",
    "city": "Kasauli",
    "locality": "Garkhal",
    "landmark": "Near Kasauli Club",
    "mapsLink": "https://maps.google.com/",
    "contactName": "Test Owner",
    "contactMobile": "9876500000",
    "whatsapp": "9876500000",
    "email": "owner@example.com",
    "showPhone": True,
    "photos": ["data:image/jpeg;base64,ABC123"],
    "image": "data:image/jpeg;base64,ABC123",
    "mobileVerified": True,
    "authorized": True
}

try:
    resp = requests.post(f"{API_BASE}/listings", json=listing_payload, timeout=10)
    test("POST /listings returns 201", resp.status_code == 201, f"Status: {resp.status_code}")
    
    if resp.status_code == 201:
        data = resp.json()
        listing_id = data.get('id')
        listing_id_human = data.get('listingId')
        status = data.get('status')
        
        test("Response contains UUID id", listing_id and len(listing_id) == 36, f"id: {listing_id}")
        test("Response contains listingId (HB-XXXXXX)", listing_id_human and listing_id_human.startswith('HB-'), f"listingId: {listing_id_human}")
        test("Status is pending_review", status == 'pending_review', f"status: {status}")
        
        print(f"\n📝 Captured: id={listing_id}, listingId={listing_id_human}\n")
    else:
        print(f"❌ Failed to create listing: {resp.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Setup failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("TEST 1: Public tracker lookup")
print("=" * 80)

try:
    # Test valid listingId lookup
    resp = requests.get(f"{API_BASE}/listings?listingId={listing_id_human}", timeout=10)
    test("GET /listings?listingId=<listingId> returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        listing = data.get('listing', {})
        
        test("Response has 'listing' object", 'listing' in data)
        test("listing.listingId matches", listing.get('listingId') == listing_id_human)
        test("listing.title is correct", listing.get('title') == "Test Hillside Villa")
        test("listing.status is pending_review", listing.get('status') == 'pending_review')
        test("listing.verified is false", listing.get('verified') == False)
        test("listing.featured is false", listing.get('featured') == False)
        test("listing.category present", listing.get('category') == 'Villa')
        test("listing.listingType present", listing.get('listingType') == 'For sale')
        test("listing.price present", listing.get('price') == '₹ 1.2 Cr')
        test("listing.city present", listing.get('city') == 'Kasauli')
        test("listing.district present", listing.get('district') == 'Solan')
        test("listing.image present", 'image' in listing)
        test("listing.propertyId is null (not approved yet)", listing.get('propertyId') is None)
        test("listing.createdAt present", 'createdAt' in listing)
        
        # Critical: check NO contact info leaked
        test("NO contactMobile leaked", 'contactMobile' not in listing)
        test("NO email leaked", 'email' not in listing)
        test("NO whatsapp leaked", 'whatsapp' not in listing)
        test("NO contactName leaked", 'contactName' not in listing)
        
        # Check no ObjectID
        ok, msg = check_no_objectid(data, "tracker_response")
        test("No ObjectID (_id) in tracker response", ok, msg if not ok else "")
    
    # Test bogus listingId
    resp = requests.get(f"{API_BASE}/listings?listingId=HB-ZZZZZZ", timeout=10)
    test("GET /listings?listingId=HB-ZZZZZZ returns 404", resp.status_code == 404, f"Status: {resp.status_code}")
    
except Exception as e:
    print(f"❌ Test 1 error: {e}")

print("\n" + "=" * 80)
print("TEST 2: Publish-on-approve")
print("=" * 80)

try:
    # Approve the listing
    resp = requests.put(f"{API_BASE}/listings/{listing_id}", json={"status": "approved"}, timeout=10)
    test("PUT /listings/<id> status=approved returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        test("Response has success=true", data.get('success') == True)
        test("Response has published=true", data.get('published') == True)
    
    # Verify the property was created
    resp = requests.get(f"{API_BASE}/properties/{listing_id}", timeout=10)
    test("GET /properties/<id> returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        prop = resp.json()
        
        test("Property title matches", prop.get('title') == "Test Hillside Villa")
        test("Property type == category (Villa)", prop.get('type') == 'Villa')
        test("Property price present", prop.get('price') == '₹ 1.2 Cr')
        test("Property location is city", prop.get('location') == 'Kasauli')
        test("Property address contains Kasauli", 'Kasauli' in prop.get('address', ''))
        test("Property address contains Solan", 'Solan' in prop.get('address', ''))
        
        # Check gallery
        gallery = prop.get('gallery', [])
        test("Property gallery is array", isinstance(gallery, list))
        test("Property gallery contains photo", len(gallery) > 0 and 'data:image/jpeg;base64,ABC123' in gallery)
        
        # Check specs
        specs = prop.get('specs', [])
        test("Property specs is array", isinstance(specs, list))
        
        bedrooms_spec = next((s for s in specs if s.get('label') == 'Bedrooms'), None)
        test("Specs includes Bedrooms", bedrooms_spec is not None)
        if bedrooms_spec:
            test("Bedrooms value is '3'", bedrooms_spec.get('value') == '3')
        
        bathrooms_spec = next((s for s in specs if s.get('label') == 'Bathrooms'), None)
        test("Specs includes Bathrooms", bathrooms_spec is not None)
        if bathrooms_spec:
            test("Bathrooms value is '2'", bathrooms_spec.get('value') == '2')
        
        area_spec = next((s for s in specs if s.get('label') == 'Area'), None)
        test("Specs includes Area", area_spec is not None)
        
        # Check no ObjectID
        ok, msg = check_no_objectid(prop, "property")
        test("No ObjectID (_id) in property", ok, msg if not ok else "")
    
    # Verify property appears in list
    resp = requests.get(f"{API_BASE}/properties", timeout=10)
    test("GET /properties returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        properties = data.get('properties', [])
        found = any(p.get('id') == listing_id for p in properties)
        test("Approved property appears in /properties list", found)
    
    # Verify tracker now shows propertyId
    resp = requests.get(f"{API_BASE}/listings?listingId={listing_id_human}", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        listing = data.get('listing', {})
        test("Tracker now shows propertyId == listing id", listing.get('propertyId') == listing_id)
    
except Exception as e:
    print(f"❌ Test 2 error: {e}")

print("\n" + "=" * 80)
print("TEST 3: Un-publish on reject")
print("=" * 80)

try:
    # Reject the listing
    resp = requests.put(f"{API_BASE}/listings/{listing_id}", json={"status": "rejected"}, timeout=10)
    test("PUT /listings/<id> status=rejected returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    # Verify the mirrored property was removed
    resp = requests.get(f"{API_BASE}/properties/{listing_id}", timeout=10)
    test("GET /properties/<id> returns 404 (property removed)", resp.status_code == 404, f"Status: {resp.status_code}")
    
    # Verify tracker shows rejected status and null propertyId
    resp = requests.get(f"{API_BASE}/listings?listingId={listing_id_human}", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        listing = data.get('listing', {})
        test("Tracker shows status=rejected", listing.get('status') == 'rejected')
        test("Tracker shows propertyId=null", listing.get('propertyId') is None)
    
except Exception as e:
    print(f"❌ Test 3 error: {e}")

print("\n" + "=" * 80)
print("TEST 4: Delete cleanup")
print("=" * 80)

try:
    # Re-approve first
    resp = requests.put(f"{API_BASE}/listings/{listing_id}", json={"status": "approved"}, timeout=10)
    test("Re-approve: PUT /listings/<id> status=approved returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    # Confirm property exists
    resp = requests.get(f"{API_BASE}/properties/{listing_id}", timeout=10)
    test("Confirm GET /properties/<id> returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    # Delete the listing
    resp = requests.delete(f"{API_BASE}/listings/{listing_id}", timeout=10)
    test("DELETE /listings/<id> returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        test("Delete response has success=true", data.get('success') == True)
    
    # Verify both listing and property are gone
    resp = requests.get(f"{API_BASE}/properties/{listing_id}", timeout=10)
    test("GET /properties/<id> returns 404 (property deleted)", resp.status_code == 404, f"Status: {resp.status_code}")
    
    resp = requests.get(f"{API_BASE}/listings/{listing_id}", timeout=10)
    test("GET /listings/<id> returns 404 (listing deleted)", resp.status_code == 404, f"Status: {resp.status_code}")
    
except Exception as e:
    print(f"❌ Test 4 error: {e}")

print("\n" + "=" * 80)
print("TEST 5: Regression - Original seeded properties")
print("=" * 80)

try:
    resp = requests.get(f"{API_BASE}/properties", timeout=10)
    test("GET /properties returns 200", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        properties = data.get('properties', [])
        
        # Should have at least 6 starter properties
        test("At least 6 seeded properties exist", len(properties) >= 6, f"Found {len(properties)} properties")
        
        # Check for some known starter properties
        titles = [p.get('title') for p in properties]
        test("'The Cedar House' exists", 'The Cedar House' in titles)
        test("'Pinecrest Estate' exists", 'Pinecrest Estate' in titles)
        
        # Check no ObjectID leaks
        ok, msg = check_no_objectid(data, "properties_list")
        test("No ObjectID (_id) in properties list", ok, msg if not ok else "")
        
        # Verify all properties have UUID ids
        all_uuid = all(p.get('id') and len(p.get('id', '')) == 36 for p in properties)
        test("All properties have UUID ids", all_uuid)
    
except Exception as e:
    print(f"❌ Test 5 error: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Total: {passed + failed}")

if failed > 0:
    print("\n⚠️  Some tests failed. Review the output above for details.")
    sys.exit(1)
else:
    print("\n🎉 All tests passed!")
    sys.exit(0)
