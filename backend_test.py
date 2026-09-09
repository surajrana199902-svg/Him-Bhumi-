import os
import uuid
import requests

BASE = os.environ.get("NEXT_PUBLIC_BASE_URL", "https://himalayan-estates-1.preview.emergentagent.com").rstrip("/") + "/api"


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def main():
    created_id = None
    try:
        r = requests.get(f"{BASE}/properties", timeout=30)
        check(r.status_code == 200, "GET properties returns 200")
        payload = r.json()
        props = payload.get("properties")
        check(isinstance(props, list) and len(props) >= 6, "properties auto-seed starter listings")
        check(isinstance(payload.get("locations"), list) and len(payload["locations"]) > 0, "properties response includes location metadata")
        check(all("_id" not in p and isinstance(p.get("id"), str) and len(p["id"]) == 36 for p in props), "properties expose UUID ids without Mongo ObjectIDs")
        locations = {p.get("location") for p in props}
        check("Baddi" in locations, "seed data includes Baddi")
        r = requests.get(f"{BASE}/properties", params={"location": "Baddi"}, timeout=30)
        check(r.status_code == 200 and len(r.json().get("properties", [])) > 0, "Baddi filter returns results")
        check(all(p.get("location") == "Baddi" for p in r.json()["properties"]), "Baddi filter narrows every result")
        other = next(loc for loc in locations if loc != "Baddi")
        r = requests.get(f"{BASE}/properties", params={"location": other}, timeout=30)
        check(r.status_code == 200 and all(p.get("location") == other for p in r.json().get("properties", [])), "second location filter narrows results")
        first_id = props[0]["id"]
        r = requests.get(f"{BASE}/properties/{first_id}", timeout=30)
        check(r.status_code == 200 and r.json().get("id") == first_id and "_id" not in r.json(), "GET property by UUID returns property without ObjectID")
        r = requests.get(f"{BASE}/properties/{uuid.uuid4()}", timeout=30)
        check(r.status_code == 404, "unknown property UUID returns 404")

        for body in ({}, {"fullName": "Aarav Mehta"}, {"fullName": "Aarav Mehta", "mobile": "+919876543210"}):
            r = requests.post(f"{BASE}/inquiries", json=body, timeout=30)
            check(r.status_code == 400, "inquiry rejects missing required fields")
        inquiry_body = {"fullName": "Aarav Mehta", "mobile": "+919876543210", "propertyId": first_id, "message": "Please share the site visit details."}
        r = requests.post(f"{BASE}/inquiries", json=inquiry_body, timeout=30)
        check(r.status_code == 201, "valid inquiry is accepted")
        inquiry = r.json().get("inquiry", {})
        check(isinstance(inquiry.get("id"), str) and len(inquiry["id"]) == 36 and "_id" not in inquiry, "inquiry receives UUID without ObjectID")
        r = requests.get(f"{BASE}/inquiries", timeout=30)
        check(r.status_code == 200 and any(i.get("id") == inquiry.get("id") for i in r.json().get("inquiries", [])), "inquiry persists and is returned by GET")

        for body in ({}, {"title": "Test Residence"}, {"title": "Test Residence", "location": "Mandi"}):
            r = requests.post(f"{BASE}/properties", json=body, timeout=30)
            check(r.status_code == 400, "property creation rejects missing required fields")
        new_body = {"title": "Ridgeview Test Residence", "location": "Mandi", "price": "₹ 1.35 Cr", "type": "Villa", "area": "2,100 sq. ft.", "image": "https://example.com/ridgeview.jpg"}
        r = requests.post(f"{BASE}/properties", json=new_body, timeout=30)
        check(r.status_code == 201, "valid property is created")
        created = r.json().get("property", {})
        created_id = created.get("id")
        check(isinstance(created_id, str) and len(created_id) == 36 and "_id" not in created, "created property uses UUID without ObjectID")
        r = requests.put(f"{BASE}/properties/{created_id}", json={"title": "Ridgeview Updated Residence", "location": "Mandi", "price": "₹ 1.40 Cr"}, timeout=30)
        check(r.status_code == 200, "property PUT updates UUID property")
        r = requests.get(f"{BASE}/properties/{created_id}", timeout=30)
        check(r.status_code == 200 and r.json().get("title") == "Ridgeview Updated Residence", "property update persists")
        r = requests.delete(f"{BASE}/properties/{created_id}", timeout=30)
        check(r.status_code == 200 and r.json().get("success") is True, "property DELETE removes UUID property")
        r = requests.get(f"{BASE}/properties/{created_id}", timeout=30)
        check(r.status_code == 404, "deleted property is no longer retrievable")
        print("BACKEND TEST RESULT: PASS")
    except Exception as exc:
        print(f"BACKEND TEST RESULT: FAIL: {exc}")
        raise


if __name__ == "__main__":
    main()
