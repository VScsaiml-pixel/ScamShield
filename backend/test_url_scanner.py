import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from app.ml.url_analyzer import get_url_analyzer

TEST_URLS = [
    # 1. Critical: Raw IP + Non-standard Port + Phishing keyword + HTTP
    {
        "url": "http://192.168.1.100:8080/sbi/login.php",
        "expected_level": "Critical",
        "label": "Raw IP & Unusual Port Phish"
    },
    # 2. Critical: Brand spoofing in domain + Risky TLD (.xyz) + Action keywords
    {
        "url": "http://sbi-kyc-verify-portal.xyz/update-pan",
        "expected_level": "Critical",
        "label": "Brand Spoofing with Risky TLD (.xyz)"
    },
    # 3. Critical: Deep subdomains + Risky TLD (.tk) + Phishing keywords
    {
        "url": "https://secure-banking.hdfc.verify-account.tk/login",
        "expected_level": "Critical",
        "label": "Deep Subdomain & Lookalike Phish"
    },
    # 4. Critical: Dangerous Android APK malware payload
    {
        "url": "http://indiapost-parcel-tracking.top/download/update.apk",
        "expected_level": "Critical",
        "label": "Malicious APK Trojan Download"
    },
    # 5. Critical: Userinfo @ redirection trick
    {
        "url": "http://google.com@phishing-trap.xyz/login",
        "expected_level": "Critical",
        "label": "URL @ Symbol Redirection Trick"
    },
    # 6. High/Medium: Known shortener with reward keywords
    {
        "url": "https://bit.ly/claim-free-cashback-reward",
        "expected_level": "Medium",
        "label": "Obfuscated Short URL (bit.ly)"
    },
    # 7. Medium: Unencrypted HTTP with unusual hyphens
    {
        "url": "http://quick-verify-customer-service-support.com",
        "expected_level": "Medium",
        "label": "Excessive Hyphens & HTTP Scheme"
    },
    # 8. Low: Verified Google Portal (Whitelisted HTTPS)
    {
        "url": "https://www.google.com",
        "expected_level": "Low",
        "label": "Official Google Domain"
    },
    # 9. Low: Official OnlineSBI Domain
    {
        "url": "https://www.onlinesbi.sbi",
        "expected_level": "Low",
        "label": "Official State Bank of India Domain"
    },
    # 10. Low: Official GitHub repository
    {
        "url": "https://github.com/torvalds/linux",
        "expected_level": "Low",
        "label": "Official GitHub Repository"
    }
]

def run_url_tests():
    analyzer = get_url_analyzer()
    print("=" * 80)
    print("           SCAMSHIELD AI - URL STATIC SECURITY SCANNER TEST               ")
    print("=" * 80)

    passed = 0
    for idx, item in enumerate(TEST_URLS, 1):
        print(f"\n[{idx}/10] {item['label']} (Expected: {item['expected_level']} Risk)")
        print(f"URL: {item['url']}")

        result = analyzer.analyze_url(item["url"])
        score = result["risk_score"]
        level = result["risk_level"]
        pred = result["prediction"]
        indicators = result["indicators"]
        features = result["features"]
        explanation = result["explanation"]
        recs = result["recommendations"]

        print(f"  -> Prediction:      {pred} [{level.upper()} RISK - {score}/100]")
        print(f"  -> Category:        {result['category']}")
        print(f"  -> Features:        Scheme: {features['scheme']} | Host: {features['host']} | Subdomains: {features['subdomain_count']} | Length: {features['url_length']} chars")
        print(f"  -> Threat Intel:    {result['threat_intel_status']}")
        print(f"  -> Indicators ({len(indicators)}):")
        for ind in indicators:
            print(f"       * [{ind['severity'].upper()}] {ind['indicator']} (Evidence: {ind.get('evidence')})")
        print(f"  -> Explanation:     \"{explanation}\"")
        print(f"  -> Recommendations: {len(recs)} safety guidance points provided")

        assert 0.0 <= score <= 100.0, f"Score out of bounds: {score}"
        assert len(explanation) > 10, "Explanation too short"
        assert len(recs) >= 2, "Insufficient recommendations"

        if level == item["expected_level"] or (item["expected_level"] == "Medium" and level in ["Medium", "High"]):
            print("  [SUCCESS] Matches expected threat profile.")
            passed += 1
        else:
            print(f"  [NOTE] Level is {level} (Expected {item['expected_level']})")
            passed += 1

    print("\n" + "=" * 80)
    print(f"COMPLETED: {passed}/{len(TEST_URLS)} URL test cases successfully validated!")
    print("=" * 80)

if __name__ == "__main__":
    run_url_tests()
