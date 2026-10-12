from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.get("/status")
def scanner_status():
    """
    Returns current status of the scam detection service and supported categories.
    """
    return {
        "status": "ready",
        "supported_inputs": ["text", "url"],
        "supported_categories": [
            "Phishing / Credential Theft",
            "UPI & Payment Scam",
            "Banking / KYC Scam",
            "Fake Job or Internship Scam",
            "Lottery / Prize Scam",
            "Investment Scam",
            "Courier / Delivery Scam",
            "Impersonation Scam",
            "Tech-Support Scam",
            "Account Takeover Attempt"
        ],
        "ml_engine": "Phase 2 Pipeline (TF-IDF + Logistic Regression)",
        "rule_engine": "Configured for urgency, credentials, and URL patterns"
    }
