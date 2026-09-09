import os
import uuid
import requests
import re

BASE = os.environ.get("NEXT_PUBLIC_BASE_URL", "https://himalayan-estates-1.preview.emergentagent.com").rstrip("/") + "/api"


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"✅ PASS: {message}")


def main():
    created_listing_id = None
    dev_otp = None
    test_mobile = "9876543210"
    
    try:
        print("\n=== TESTING LISTING ENDPOINTS ===\n")
        
        # ===== 1. OTP VERIFICATION (MOCKED) =====
        print("--- 1. OTP Verification Flow ---")
        
        # Test: send OTP with valid mobile
        r = requests.post(f"{BASE}/listings/verify/send", json={"channel": "mobile", "value": test_mobile}, timeout=30)
        check(r.status_code == 200, "POST /listings/verify/send with valid mobile returns 200")
        otp_response = r.json()
        check(otp_response.get("sent") is True, "OTP send response has sent: true")
        check(otp_response.get("mocked") is True, "OTP send response has mocked: true")
        check("devOtp" in otp_response, "OTP send response contains devOtp")
        dev_otp = otp_response.get("devOtp")
        check(isinstance(dev_otp, str) and len(dev_otp) == 6 and dev_otp.isdigit(), "devOtp is a 6-digit string")
        print(f"   📱 Received devOtp: {dev_otp}")
        
        # Test: send OTP with empty value
        r = requests.post(f"{BASE}/listings/verify/send", json={"channel": "mobile", "value": ""}, timeout=30)
        check(r.status_code == 400, "POST /listings/verify/send with empty value returns 400")
        
        # Test: check OTP with correct code
        r = requests.post(f"{BASE}/listings/verify/check", json={"channel": "mobile", "value": test_mobile, "otp": dev_otp}, timeout=30)
        check(r.status_code == 200, "POST /listings/verify/check with correct OTP returns 200")
        verify_response = r.json()
        check(verify_response.get("verified") is True, "OTP check response has verified: true")
        check(verify_response.get("channel") == "mobile", "OTP check response has correct channel")
        
        # Test: check OTP with wrong code
        r = requests.post(f"{BASE}/listings/verify/check", json={"channel": "mobile", "value": test_mobile, "otp": "000000"}, timeout=30)
        check(r.status_code == 400, "POST /listings/verify/check with wrong OTP returns 400")
        
        # Test: check OTP without first sending (different mobile)
        r = requests.post(f"{BASE}/listings/verify/check", json={"channel": "mobile", "value": "9999999999", "otp": "123456"}, timeout=30)
        check(r.status_code == 400, "POST /listings/verify/check without first sending returns 400")
        
        print("\n--- 2. Listing Creation Validation ---")
        
        # Test: missing required field (no title)
        r = requests.post(f"{BASE}/listings", json={
            "category": "Residential",
            "listingType": "Sell",
            "price": "5000000",
            "contactName": "Rajesh Kumar",
            "contactMobile": test_mobile
        }, timeout=30)
        check(r.status_code == 400, "POST /listings without title returns 400")
        
        # Test: missing mobileVerified
        r = requests.post(f"{BASE}/listings", json={
            "title": "Beautiful Villa in Shimla",
            "category": "Residential",
            "listingType": "Sell",
            "price": "5000000",
            "contactName": "Rajesh Kumar",
            "contactMobile": test_mobile,
            "authorized": True
        }, timeout=30)
        check(r.status_code == 400, "POST /listings without mobileVerified returns 400")
        
        # Test: missing authorized
        r = requests.post(f"{BASE}/listings", json={
            "title": "Beautiful Villa in Shimla",
            "category": "Residential",
            "listingType": "Sell",
            "price": "5000000",
            "contactName": "Rajesh Kumar",
            "contactMobile": test_mobile,
            "mobileVerified": True
        }, timeout=30)
        check(r.status_code == 400, "POST /listings without authorized returns 400")
        
        # Test: valid listing creation
        valid_listing = {
            "title": "Luxury Mountain Villa in Shimla",
            "category": "Residential",
            "listingType": "Sell",
            "price": "8500000",
            "area": "3500",
            "areaUnit": "sq. ft.",
            "state": "Himachal Pradesh",
            "district": "Shimla",
            "city": "Shimla",
            "contactName": "Rajesh Kumar",
            "contactMobile": test_mobile,
            "mobileVerified": True,
            "authorized": True,
            "photos": ["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/wA=="],
            "showPhone": True,
            "description": "A stunning villa with panoramic mountain views"
        }
        r = requests.post(f"{BASE}/listings", json=valid_listing, timeout=30)
        check(r.status_code == 201, "POST /listings with valid data returns 201")
        listing_response = r.json()
        check("listingId" in listing_response, "Listing response contains listingId")
        check("id" in listing_response, "Listing response contains id (UUID)")
        check("status" in listing_response, "Listing response contains status")
        
        listing_id_pattern = re.compile(r'^HB-[A-Z0-9]{6}$')
        check(listing_id_pattern.match(listing_response.get("listingId", "")), "listingId matches pattern HB-[A-Z0-9]{6}")
        check(listing_response.get("status") == "pending_review", "Listing status is pending_review")
        
        created_listing_id = listing_response.get("id")
        check(isinstance(created_listing_id, str) and len(created_listing_id) == 36, "Listing id is a valid UUID")
        print(f"   🏠 Created listing: {listing_response.get('listingId')} (UUID: {created_listing_id})")
        
        print("\n--- 3. GET Listings ---")
        
        # Test: GET all listings
        r = requests.get(f"{BASE}/listings", timeout=30)
        check(r.status_code == 200, "GET /listings returns 200")
        listings_response = r.json()
        check("listings" in listings_response, "GET /listings response contains listings array")
        listings = listings_response.get("listings", [])
        check(isinstance(listings, list), "listings is an array")
        check(any(l.get("id") == created_listing_id for l in listings), "Created listing is present in GET /listings")
        check(all("_id" not in l for l in listings), "No Mongo ObjectID (_id) in listings")
        check(all(isinstance(l.get("id"), str) for l in listings), "All listings have UUID id")
        
        # Test: GET listings with status filter
        r = requests.get(f"{BASE}/listings", params={"status": "pending_review"}, timeout=30)
        check(r.status_code == 200, "GET /listings?status=pending_review returns 200")
        filtered_listings = r.json().get("listings", [])
        check(any(l.get("id") == created_listing_id for l in filtered_listings), "Created listing present in pending_review filter")
        check(all(l.get("status") == "pending_review" for l in filtered_listings), "All filtered listings have status pending_review")
        
        # Test: GET single listing by id
        r = requests.get(f"{BASE}/listings/{created_listing_id}", timeout=30)
        check(r.status_code == 200, "GET /listings/:id returns 200")
        single_listing = r.json()
        check(single_listing.get("id") == created_listing_id, "Single listing has correct id")
        check("_id" not in single_listing, "Single listing has no Mongo ObjectID")
        check(single_listing.get("title") == valid_listing["title"], "Single listing has correct title")
        
        # Test: GET non-existent listing
        r = requests.get(f"{BASE}/listings/{uuid.uuid4()}", timeout=30)
        check(r.status_code == 404, "GET /listings/nonexistent-id returns 404")
        
        print("\n--- 4. PUT Listings (Update) ---")
        
        # Test: Update status to approved
        r = requests.put(f"{BASE}/listings/{created_listing_id}", json={"status": "approved"}, timeout=30)
        check(r.status_code == 200, "PUT /listings/:id to update status returns 200")
        check(r.json().get("success") is True, "PUT response has success: true")
        
        # Verify status update
        r = requests.get(f"{BASE}/listings/{created_listing_id}", timeout=30)
        check(r.status_code == 200 and r.json().get("status") == "approved", "Status update persisted (approved)")
        
        # Test: Update verified and featured flags
        r = requests.put(f"{BASE}/listings/{created_listing_id}", json={"verified": True, "featured": True}, timeout=30)
        check(r.status_code == 200, "PUT /listings/:id to update verified and featured returns 200")
        
        # Verify flags update
        r = requests.get(f"{BASE}/listings/{created_listing_id}", timeout=30)
        updated_listing = r.json()
        check(updated_listing.get("verified") is True, "verified flag update persisted")
        check(updated_listing.get("featured") is True, "featured flag update persisted")
        
        # Test: Update title
        r = requests.put(f"{BASE}/listings/{created_listing_id}", json={"title": "Updated Luxury Villa Title"}, timeout=30)
        check(r.status_code == 200, "PUT /listings/:id to update title returns 200")
        
        # Verify title update
        r = requests.get(f"{BASE}/listings/{created_listing_id}", timeout=30)
        check(r.json().get("title") == "Updated Luxury Villa Title", "Title update persisted")
        
        print("\n--- 5. DELETE Listing ---")
        
        # Test: Delete listing
        r = requests.delete(f"{BASE}/listings/{created_listing_id}", timeout=30)
        check(r.status_code == 200, "DELETE /listings/:id returns 200")
        check(r.json().get("success") is True, "DELETE response has success: true")
        
        # Verify deletion
        r = requests.get(f"{BASE}/listings/{created_listing_id}", timeout=30)
        check(r.status_code == 404, "Deleted listing returns 404 on GET")
        
        print("\n--- 6. Regression Check ---")
        
        # Test: Existing properties endpoint still works
        r = requests.get(f"{BASE}/properties", timeout=30)
        check(r.status_code == 200, "GET /properties still returns 200 (regression check)")
        props = r.json().get("properties", [])
        check(len(props) >= 6, "Properties endpoint still returns seeded data")
        check(all("_id" not in p for p in props), "Properties still have no ObjectID leak")
        
        print("\n" + "="*50)
        print("🎉 ALL LISTING BACKEND TESTS PASSED!")
        print("="*50 + "\n")
        
    except Exception as exc:
        print(f"\n❌ BACKEND LISTING TEST FAILED: {exc}\n")
        raise


if __name__ == "__main__":
    main()
