import re
from typing import List, Dict, Any, Tuple

# Comprehensive rule definitions matching PRD Section 13, 14, 15 and user requirements
INDICATOR_RULES = [
    {
        "id": "urgent_language",
        "name": "Urgent language detected",
        "severity": "high",
        "weight": 12.0,
        "regex": r'\b(immediately|urgently|urgent|within\s+\d+\s*(?:hours|hrs|minutes|mins)|in\s+\d+\s*(?:hours|hrs|minutes|mins)|today\s+only|last\s+chance|act\s+now|without\s+delay|right\s+now|before\s+(?:midnight|\d+\s*(?:pm|am))|expires?\s+soon|before\s+it\s+is\s+too\s+late)\b',
        "description": "Uses high-pressure or panic-inducing time limits to force hurried action."
    },
    {
        "id": "account_suspension",
        "name": "Threats of account suspension",
        "severity": "high",
        "weight": 14.0,
        "regex": r'\b(account\s+will\s+be\s+blocked|account\s+(?:has\s+been\s+)?blocked|suspended|deactivated|frozen|access\s+restricted|card\s+(?:is\s+)?blocked|power\s+will\s+be\s+disconnected|service\s+termination|permanently\s+deleted|will\s+be\s+deleted|arrest\s+warrant|digital\s+arrest)\b',
        "description": "Threatens immediate suspension, deletion, blockage of accounts, cards, utilities, or legal action."
    },
    {
        "id": "otp_request",
        "name": "Requests for OTP",
        "severity": "critical",
        "weight": 22.0,
        "regex": r'\b(enter\s+otp|share\s+otp|provide\s+otp|forward\s+otp|send\s+(?:the\s+)?(?:6-digit|4-digit)?\s*sms\s+code|one[- ]time[- ]password|verification\s+code)\b',
        "description": "Explicitly requests private one-time passwords (OTPs) that legitimate organizations never ask you to share."
    },
    {
        "id": "pin_request",
        "name": "Requests for PIN",
        "severity": "critical",
        "weight": 22.0,
        "regex": r'\b(upi\s+pin|atm\s+pin|mpin|secret\s+pin|enter\s+(?:your\s+)?(?:secret\s+)?pin|4-digit\s+pin|6-digit\s+pin)\b',
        "description": "Solicits confidential personal identification numbers (PINs) used to authorize financial debits."
    },
    {
        "id": "password_request",
        "name": "Requests for passwords",
        "severity": "critical",
        "weight": 20.0,
        "regex": r'\b(netbanking\s+password|login\s+password|account\s+password|transaction\s+password|passcode|enter\s+password|verify\s+password|login\s+credentials)\b',
        "description": "Attempts to harvest account or netbanking login credentials."
    },
    {
        "id": "card_bank_details",
        "name": "Requests for card/bank details",
        "severity": "critical",
        "weight": 18.0,
        "regex": r'\b(cvv|card\s+number|16-digit|card\s+expiry|expiration\s+date|debit\s+card\s+details|credit\s+card\s+details|banking\s+details|account\s+number\s+and\s+ifsc)\b',
        "description": "Solicits sensitive payment card or banking numbers that facilitate unauthorized charges."
    },
    {
        "id": "suspicious_payment_request",
        "name": "Suspicious payment request",
        "severity": "critical",
        "weight": 20.0,
        "regex": r'\b(scan\s+(?:this\s+)?qr(?:\s+code)?|enter\s+pin\s+to\s+receive|pay\s+rs\.?\s*\d+\s+to\s+receive|collect\s+request|pay\s+processing\s+fee|pay\s+registration\s+fee|pay\s+delivery\s+tax|security\s+deposit|token\s+fee|redelivery\s+charge|redelivery\s+fee|customs\s+duty|customs\s+clearance)\b',
        "description": "Deceptive payment mechanism claiming entering a PIN, scanning a QR code, or paying a fee will credit money."
    },
    {
        "id": "unrealistic_rewards",
        "name": "Unrealistic rewards",
        "severity": "high",
        "weight": 12.0,
        "regex": r'\b(cashback\s+(?:refund\s+)?of\s+rs|cash\s+voucher|guaranteed\s+(?:200%|10%|profit|returns)|double\s+your\s+money|passive\s+income|free\s+gift|free\s+iphone|unlimited\s+bonus)\b',
        "description": "Promises exaggerated financial returns, free high-value gifts, or unprompted cashbacks."
    },
    {
        "id": "lottery_prize_claims",
        "name": "Lottery/prize claims",
        "severity": "high",
        "weight": 14.0,
        "regex": r'\b(kbc\s+lucky\s+draw|lucky\s+draw|won\s+rs|won\s+\$|lottery\s+winner|grand\s+prize|selected\s+winner|claim\s+prize|claim\s+your\s+reward)\b',
        "description": "Claims the recipient won an unentered raffle, corporate lottery, or lucky draw."
    },
    {
        "id": "fake_job_offers",
        "name": "Fake job offers",
        "severity": "high",
        "weight": 14.0,
        "regex": r'\b(part[- ]time\s+(?:work|job)|like\s+youtube\s+videos|earn\s+[\d,]+\s+daily|no\s+experience\s+(?:needed|required)|join\s+telegram\s+group|typing\s+tasks|data\s+entry\s+job|without\s+(?:coding\s+)?interview)\b',
        "description": "Work-from-home or superficial task offer with inflated daily payouts, frequently used in task scams."
    },
    {
        "id": "suspicious_links",
        "name": "Suspicious links",
        "severity": "medium",
        "weight": 8.0,
        "regex": r'(bit\.ly|tinyurl\.com|t\.co|goo\.gl|is\.gd|cutt\.ly|rb\.gy|\.xyz|\.top|\.tk|\.live|\.work|\.club|\.info|\.cc|\.online|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)',
        "description": "Employs URL shorteners, IP addresses, or low-reputation top-level domains to hide true destinations."
    },
    {
        "id": "kyc_verification_requests",
        "name": "KYC/account verification requests",
        "severity": "high",
        "weight": 14.0,
        "regex": r'\b(kyc\s+update|pending\s+kyc|re-kyc|update\s+pan|pan\s+card\s+link|aadhaar\s+link|verify\s+identity|yono\s+account|verify\s+pan)\b',
        "description": "Demands immediate submission of government identity or KYC documents through unverified links."
    },
    {
        "id": "impersonation_authority",
        "name": "Impersonation of banks/government/companies",
        "severity": "high",
        "weight": 12.0,
        "regex": r'\b(sbi\s+customer|hdfc\s+bank|icici\s+bank|axis\s+bank|punjab\s+national\s+bank|income\s+tax\s+department|cbi|police\s+department|cyber\s+crime|trai|electricity\s+board|microsoft\s+certified|fedex\s+express|dhl\s+express|india\s+post|netflix\s+subscriber|apple\s+support|instagram\s+security|facebook\s+security|whatsapp\s+security|telegram\s+security)\b',
        "description": "Impersonates trusted institutions like banks, law enforcement, or global brands to establish false trust."
    }
]

def extract_rule_indicators(text: str) -> List[Dict[str, Any]]:
    """
    Scans input message across all indicator rules.
    Extracts triggered indicator metadata, exact matching evidence, and assigned severity.
    """
    detected = []
    for rule in INDICATOR_RULES:
        match = re.search(rule["regex"], text, re.IGNORECASE)
        if match:
            evidence_snippet = match.group(0).strip()
            detected.append({
                "id": rule["id"],
                "indicator": rule["name"],
                "severity": rule["severity"],
                "weight": rule["weight"],
                "evidence": f"'{evidence_snippet}'",
                "description": rule["description"]
            })
    return detected

def calculate_hybrid_risk_score(
    scam_prob: float,
    indicators: List[Dict[str, Any]],
    text: str,
    category: str
) -> Tuple[float, str, Dict[str, Any]]:
    """
    Computes a calibrated risk score (0-100) combining:
    - ML statistical classification probability
    - Weighted rule-based indicators
    - Scam category severity
    - Special context rules (e.g. isolated benign urgency in clean messages)

    Risk Levels:
    0 - 30   = Low Risk
    31 - 60  = Medium Risk
    61 - 80  = High Risk
    81 - 100 = Critical Risk
    """
    # 1. Base ML Contribution (up to 50 points)
    ml_pts = scam_prob * 50.0

    # 2. Rule Indicator Contribution (up to 50 points)
    raw_rule_pts = sum(ind["weight"] for ind in indicators)
    rule_pts = min(50.0, raw_rule_pts)

    # 3. Category & Critical Traps Factor
    has_critical_credential = any(ind["id"] in ["otp_request", "pin_request", "password_request", "card_bank_details"] for ind in indicators)
    has_payment_trap = any(ind["id"] == "suspicious_payment_request" for ind in indicators)
    has_suspension_threat = any(ind["id"] == "account_suspension" for ind in indicators)
    has_kyc_trap = any(ind["id"] == "kyc_verification_requests" for ind in indicators)

    # Synergy adjustment:
    # If ML probability is very low (< 0.20) and NO credentials/payment/threat indicators exist,
    # then isolated words (like "urgent meeting") should not inflate score into medium/high.
    is_benign_urgency_only = (
        scam_prob < 0.20 and 
        len(indicators) == 1 and 
        indicators[0]["id"] == "urgent_language" and
        not any(w in text.lower() for w in ["bank", "pay", "fee", "click", "http", "blocked"])
    )

    if is_benign_urgency_only:
        rule_pts = 5.0  # dampen isolated urgent words in benign personal/work context

    # Critical synergy boost:
    # If multiple critical indicators co-occur with high ML confidence
    synergy_boost = 0.0
    if has_critical_credential and (has_payment_trap or has_suspension_threat or has_kyc_trap):
        synergy_boost += 8.0
    if scam_prob > 0.70 and len(indicators) >= 2:
        synergy_boost += 5.0

    total_score = ml_pts + rule_pts + synergy_boost
    final_score = round(min(100.0, max(0.0, total_score)), 1)

    # Determine Risk Level matching PRD & prompt specification:
    # 0–30 = Low Risk
    # 31–60 = Medium Risk
    # 61–80 = High Risk
    # 81–100 = Critical Risk
    if final_score >= 81.0:
        risk_level = "Critical"
    elif final_score >= 61.0:
        risk_level = "High"
    elif final_score >= 31.0:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    breakdown = {
        "ml_contribution": round(ml_pts, 1),
        "rule_contribution": round(rule_pts, 1),
        "synergy_boost": round(synergy_boost, 1),
        "total_indicators_detected": len(indicators)
    }

    return final_score, risk_level, breakdown

def synthesize_explanation(
    prediction: str,
    risk_level: str,
    indicators: List[Dict[str, Any]],
    category: str
) -> str:
    """
    Generates a concise, evidence-grounded human-readable explanation of WHY
    the message was classified as it was, adhering to balanced advisory phrasing.
    """
    if risk_level == "Low":
        if len(indicators) == 0:
            return "This message appears legitimate. No common fraudulent indicators or sensitive credential requests were detected."
        else:
            names = [ind["indicator"].lower() for ind in indicators]
            return f"This message appears predominantly legitimate. Mild warning signal ({names[0]}) was observed but without suspicious financial or credential requests."

    indicator_reasons = []
    for ind in indicators[:3]:
        evidence = ind.get("evidence", "")
        if evidence:
            indicator_reasons.append(f"{ind['indicator'].lower()} (e.g. {evidence})")
        else:
            indicator_reasons.append(ind['indicator'].lower())

    reasons_str = ", ".join(indicator_reasons)

    if risk_level == "Critical":
        return f"This message appears to be a high-risk scam attempt because it combines {reasons_str} matching established {category} attack patterns."
    elif risk_level == "High":
        return f"This message appears potentially suspicious because it features {reasons_str} aimed at prompting urgent or sensitive user actions."
    else: # Medium
        return f"This message contains potentially suspicious elements ({reasons_str}). Exercise caution and verify the source before engaging."

def generate_safety_recommendations(prediction: str, risk_level: str, indicators: List[Dict[str, Any]], category: str) -> List[str]:
    """
    Returns actionable safety recommendations tailored to the specific indicators and risk level.
    """
    if risk_level == "Low":
        return [
            "This communication does not show common scam indicators, but remain cautious.",
            "Never share passwords, banking PINs, or OTPs even with trusted entities.",
            "Verify senders via official organizational contact details if ever in doubt."
        ]

    recs = []

    # Priority 1: Link & Attachment safety
    if any(ind["id"] == "suspicious_links" for ind in indicators) or "http" in category.lower():
        recs.append("Do NOT click any links, open attachments, or visit unverified websites mentioned in the message.")
    else:
        recs.append("Do not click links or call numbers provided directly in unsolicited messages.")

    # Priority 2: Credential & PIN safety
    if any(ind["id"] in ["pin_request", "suspicious_payment_request"] for ind in indicators) or "upi" in category.lower():
        recs.append("Remember: You NEVER need to enter your UPI PIN or scan a QR code to receive money. Entering a PIN always debits your account.")
    if any(ind["id"] in ["otp_request", "password_request", "card_bank_details"] for ind in indicators):
        recs.append("Never share your OTP, netbanking password, ATM PIN, or card CVV. Legitimate organizations never request these.")

    # Priority 3: Category-specific official verification
    cat_lower = category.lower()
    if "kyc" in cat_lower or "bank" in cat_lower:
        recs.append("Banks never threaten account suspension via SMS or third-party links. Verify directly through your official mobile banking app or branch.")
    elif "job" in cat_lower or "internship" in cat_lower:
        recs.append("Legitimate companies do not conduct hiring exclusively over Telegram or charge upfront registration/laptop security deposits.")
    elif "courier" in cat_lower or "delivery" in cat_lower:
        recs.append("Do not pay redelivery or customs clearance charges via SMS links. Track your consignment directly on the official postal or courier portal.")
    elif "government" in cat_lower or "impersonation" in cat_lower:
        recs.append("Law enforcement and government agencies (CBI, Police, Income Tax) never conduct 'digital arrests' or request payments over Skype/WhatsApp.")
    elif "lottery" in cat_lower or "prize" in cat_lower:
        recs.append("Disregard prize notifications for contests or lotteries you did not explicitly enter.")

    recs.append("Verify the sender independently using contact details from the organization's official website.")
    recs.append("Report suspected cyber frauds immediately to the National Cyber Crime Portal (cybercrime.gov.in or helpline 1930 in India).")

    return recs

# Backward compatibility alias
extract_indicators = extract_rule_indicators
