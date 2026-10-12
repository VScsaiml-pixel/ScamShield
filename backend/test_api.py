import sys
from starlette.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Scan, Indicator, Feedback

def run_tests():
    print("========================================")
    print("ScamShield AI - API & ML Integration Verification")
    print("========================================")
    
    # 1. Test database tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        initial_scans = db.query(Scan).count()
        print(f"[PASS] SQLite Database connected. Existing Scans in DB: {initial_scans}")
    finally:
        db.close()

    # 2. Test Client for API endpoints
    client = TestClient(app)

    # Test root endpoint
    res_root = client.get("/")
    assert res_root.status_code == 200
    print(f"[PASS] GET / -> 200")

    # Test health endpoint
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "healthy"
    print(f"[PASS] GET /api/health -> 200: status='{health_data['status']}'")

    # Test POST /api/analyze/message with a Scam message
    scam_payload = {
        "message": "Dear SBI customer, your YONO account has been suspended due to pending KYC. Click http://sbi-kyc-verify.xyz immediately to update PAN and unblock within 24 hours."
    }
    res_scam = client.post("/api/analyze/message", json=scam_payload)
    assert res_scam.status_code == 200, f"Scam analyze returned {res_scam.status_code}: {res_scam.text}"
    scam_result = res_scam.json()
    assert scam_result["prediction"] in ["Scam", "Suspicious"]
    assert scam_result["risk_score"] >= 60.0
    assert len(scam_result["indicators"]) > 0
    print(f"[PASS] POST /api/analyze/message (Scam):")
    print(f"       -> Prediction: {scam_result['prediction']}")
    print(f"       -> Risk Score: {scam_result['risk_score']}/100 ({scam_result['risk_level']})")
    print(f"       -> Category:   {scam_result['category']}")
    print(f"       -> Indicators: {len(scam_result['indicators'])} found")

    # Test POST /api/analyze/message with a Legitimate message
    legit_payload = {
        "message": "Rs 1,500.00 debited from A/C XX4921 on 07-Oct-26 at Swiggy UPI. Available balance: Rs 24,310.50. - HDFC Bank"
    }
    res_legit = client.post("/api/analyze/message", json=legit_payload)
    assert res_legit.status_code == 200, f"Legit analyze returned {res_legit.status_code}: {res_legit.text}"
    legit_result = res_legit.json()
    assert legit_result["prediction"] == "Legitimate"
    assert legit_result["risk_score"] < 35.0
    print(f"[PASS] POST /api/analyze/message (Legitimate):")
    print(f"       -> Prediction: {legit_result['prediction']}")
    print(f"       -> Risk Score: {legit_result['risk_score']}/100 ({legit_result['risk_level']})")
    print(f"       -> Category:   {legit_result['category']}")

    # 3. Verify that scans were persisted into SQLite
    db = SessionLocal()
    try:
        updated_scans = db.query(Scan).count()
        assert updated_scans >= initial_scans + 2, "Expected 2 new scans in SQLite database"
        latest_scan = db.query(Scan).order_by(Scan.scan_id.desc()).first()
        print(f"[PASS] SQLite Persistence Verified: Latest Scan #{latest_scan.scan_id} saved with prediction='{latest_scan.prediction}'")
    finally:
        db.close()

    print("\n>>> All API & Machine Learning pipeline tests PASSED successfully! <<<")

if __name__ == "__main__":
    run_tests()
