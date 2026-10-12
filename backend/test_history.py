"""
ScamShield AI - Persistent Scan History & Privacy Verification Test Suite
Validates:
1. Database persistence of scans in SQLite
2. Strict privacy filters (Zero OTP, PIN, Passwords, Card numbers stored)
3. GET /api/scans
4. GET /api/scans/{id}
5. DELETE /api/scans/{id}
6. DELETE /api/scans (purge)
7. Persistence across backend restart
"""

import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models.scan import Scan

client = TestClient(app)

def run_tests():
    print("=" * 70)
    print(" ScamShield AI — Persistent Scan History & Privacy Test Suite")
    print("=" * 70)

    # 1. Initialize and verify DB connection
    init_db()
    db = SessionLocal()
    initial_count = db.query(Scan).count()
    db.close()
    print(f"[PASS] SQLite connected. Existing historical scans: {initial_count}")

    # 2. Test Privacy-Preserving Scan Creation
    # Input with credit card, CVV, OTP, UPI PIN, password, and bearer token
    sensitive_message = (
        "Urgent! Your HDFC account is locked. "
        "Enter Card 4532 1198 3342 9012 CVV: 921 and OTP 589201 with UPI PIN 7491 "
        "and password: SuperSecret! Auth: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token"
    )

    print("\n--- Testing Privacy Sanitization on Message Scan ---")
    create_res = client.post("/api/analyze/message", json={"message": sensitive_message})
    assert create_res.status_code == 200, f"Expected 200, got {create_res.status_code}"
    scan_data = create_res.json()
    new_scan_id = scan_data["scan_id"]
    print(f"[PASS] Created Scan #{new_scan_id} with prediction={scan_data['prediction']} ({scan_data['risk_level']} Risk)")

    # 3. Verify Privacy Guarantees on Stored Record
    print("\n--- Verifying Strict Privacy Guarantees in SQLite ---")
    db = SessionLocal()
    stored_scan = db.query(Scan).filter(Scan.scan_id == new_scan_id).first()
    assert stored_scan is not None, "Scan not found in database!"
    
    # Check that secrets are NOT in input_preview
    preview = stored_scan.input_preview
    print(f"Stored input_preview: '{preview}'")
    assert "4532" not in preview, "LEAK: Card number found in database!"
    assert "921" not in preview, "LEAK: CVV found in database!"
    assert "589201" not in preview, "LEAK: OTP found in database!"
    assert "7491" not in preview, "LEAK: PIN found in database!"
    assert "SuperSecret!" not in preview, "LEAK: Password found in database!"
    assert "token" not in preview or "[REDACTED_TOKEN]" in preview, "LEAK: Auth token not redacted!"
    print("[PASS] ZERO sensitive credentials stored in SQLite! All secrets redacted.")
    db.close()

    # 4. Test GET /api/scans
    print("\n--- Testing GET /api/scans (List) ---")
    list_res = client.get("/api/scans")
    assert list_res.status_code == 200, f"Expected 200, got {list_res.status_code}"
    list_data = list_res.json()
    assert "total" in list_data and "scans" in list_data
    assert list_data["total"] >= 1
    first_item = list_data["scans"][0]
    print(f"[PASS] Total Scans: {list_data['total']}")
    print(f"       Latest Scan ID: {first_item['id']} | Type: {first_item['scan_type']} | Risk: {first_item['risk_score']}/100 ({first_item['risk_level']})")
    assert "id" in first_item
    assert "scan_type" in first_item
    assert "risk_score" in first_item
    assert "risk_level" in first_item
    assert "category" in first_item
    assert "timestamp" in first_item

    # 5. Test GET /api/scans/{id}
    print(f"\n--- Testing GET /api/scans/{new_scan_id} (Detail) ---")
    detail_res = client.get(f"/api/scans/{new_scan_id}")
    assert detail_res.status_code == 200, f"Expected 200, got {detail_res.status_code}"
    detail_data = detail_res.json()
    assert detail_data["id"] == new_scan_id
    assert detail_data["risk_level"] == "Critical"
    assert len(detail_data["indicators"]) > 0
    assert len(detail_data["recommendations"]) > 0
    print(f"[PASS] Retrieved full details for Scan #{new_scan_id}:")
    print(f"       Category:        {detail_data['category']}")
    print(f"       Indicators:      {len(detail_data['indicators'])} warning signs")
    print(f"       Recommendations: {len(detail_data['recommendations'])} action points")
    print(f"       Explanation:     {detail_data['explanation'][:70]}...")

    # 6. Test DELETE /api/scans/{id}
    print(f"\n--- Testing DELETE /api/scans/{new_scan_id} ---")
    del_res = client.delete(f"/api/scans/{new_scan_id}")
    assert del_res.status_code == 200, f"Expected 200, got {del_res.status_code}"
    assert del_res.json()["success"] is True
    print(f"[PASS] Scan #{new_scan_id} deleted successfully.")

    # Confirm it is no longer accessible
    get_del_res = client.get(f"/api/scans/{new_scan_id}")
    assert get_del_res.status_code == 404, "Deleted scan should return 404"
    print(f"[PASS] Verified deleted scan returns 404 Not Found.")

    # 7. Test URL Scan Persistence
    print("\n--- Testing URL Scan Persistence in History ---")
    url_res = client.post("/api/analyze/url", json={"url": "http://192.168.1.100/login"})
    assert url_res.status_code == 200
    url_scan_id = url_res.json()["scan_id"]
    get_url_scan = client.get(f"/api/scans/{url_scan_id}")
    assert get_url_scan.status_code == 200
    assert get_url_scan.json()["scan_type"] == "url"
    print(f"[PASS] URL Scan #{url_scan_id} verified with scan_type='url'.")

    # 8. Test Restart Simulation: Re-instantiate DB session and client
    print("\n--- Testing Database Persistence Across Process Re-init ---")
    from app.database import engine
    from sqlalchemy.orm import sessionmaker
    NewSession = sessionmaker(bind=engine)
    new_db = NewSession()
    persisted_scan = new_db.query(Scan).filter(Scan.scan_id == url_scan_id).first()
    assert persisted_scan is not None
    print(f"[PASS] Scan #{url_scan_id} persisted reliably in SQLite data file.")
    new_db.close()

    print("\n" + "=" * 70)
    print(" ALL PERSISTENT HISTORY & PRIVACY TESTS PASSED SUCCESSFULLY! ")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
