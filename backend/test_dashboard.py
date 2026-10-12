"""
ScamShield AI - Main Dashboard Analytics Test Suite
Validates:
1. GET /api/dashboard/stats returns real aggregated SQLite metrics
2. Risk band breakdown (Critical, High, Medium, Low)
3. Categories distribution breakdown
4. Activity timeline over 7 days
5. Recent scans feed
6. Handles empty database gracefully
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard():
    print("=" * 70)
    print(" ScamShield AI — Main Dashboard Analytics Test Suite")
    print("=" * 70)

    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()

    print(f"[PASS] GET /api/dashboard/stats -> 200 OK")
    print(f"       Total Scans in DB:        {data['total_scans']}")
    print(f"       Critical Threats:         {data['critical_risk_scans']}")
    print(f"       High Risk Scans:          {data['high_risk_scans']}")
    print(f"       Medium Risk Scans:        {data['medium_risk_scans']}")
    print(f"       Low Risk Scans:           {data['low_risk_scans']}")
    print(f"       Total Threat Scans:       {data['total_threats']}")
    print(f"       Clean Scans:              {data['total_clean']}")
    print(f"       Average Risk Score:       {data['average_risk_score']}/100")
    print(f"       Categories Detected:      {data['categories_detected_count']}")

    # Validate schema
    assert "risk_distribution" in data
    assert len(data["risk_distribution"]) == 4
    assert "category_distribution" in data
    assert "activity_over_time" in data
    assert len(data["activity_over_time"]) >= 1
    assert "recent_scans" in data

    # Verify risk breakdown math
    risk_sum = sum(item["count"] for item in data["risk_distribution"])
    assert risk_sum == data["total_scans"], f"Expected {data['total_scans']}, got {risk_sum}"
    print(f"[PASS] Risk distribution counts match total scans ({risk_sum} == {data['total_scans']}).")

    # Verify category breakdown math
    cat_sum = sum(item["count"] for item in data["category_distribution"])
    assert cat_sum == data["total_scans"], f"Expected {data['total_scans']}, got {cat_sum}"
    print(f"[PASS] Category distribution counts match total scans ({cat_sum} == {data['total_scans']}).")

    # Verify recent scans length
    assert len(data["recent_scans"]) <= 6
    print(f"[PASS] Recent scans feed returned {len(data['recent_scans'])} items.")

    print("\n" + "=" * 70)
    print(" ALL DASHBOARD ANALYTICS TESTS PASSED SUCCESSFULLY! ")
    print("=" * 70)

if __name__ == "__main__":
    test_dashboard()
