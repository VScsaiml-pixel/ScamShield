from datetime import datetime, timezone
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scan import Scan
from app.models.indicator import Indicator
from app.schemas.scan import (
    MessageAnalyzeRequest, 
    MessageAnalyzeResponse, 
    URLAnalyzeRequest, 
    URLAnalyzeResponse, 
    URLFeaturesOut,
    IndicatorItem
)
from app.ml.pipeline import get_detector
from app.ml.url_analyzer import get_url_analyzer
from app.utils.security import hash_input, mask_sensitive_preview

router = APIRouter(prefix="/analyze", tags=["Analyze"])


@router.post("/message", response_model=MessageAnalyzeResponse)
def analyze_message(payload: MessageAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Core AI/ML message scam detection endpoint with Explainable AI and Hybrid Risk Scoring.
    Processes input message using TF-IDF + Logistic Regression and rule-based explainable indicators.
    Saves analysis history to SQLite.
    """
    message_text = payload.message.strip()
    if not message_text:
        raise HTTPException(status_code=400, detail="Message text cannot be empty.")

    # 1. Run Machine Learning & Rule-based Detector
    detector = get_detector()
    result = detector.predict(message_text)

    # 2. Mask sensitive credentials for privacy-preserving storage
    input_preview = mask_sensitive_preview(message_text, max_length=120)
    input_hash = hash_input(message_text)
    now = datetime.now(timezone.utc)

    # 3. Store Scan Record in SQLite
    saved_scan_id = None
    try:
        scan_record = Scan(
            user_id=None,  # Guest / unauthenticated scan
            scan_type="message",
            input_type="text",
            input_hash=input_hash,
            input_preview=input_preview,
            prediction=result["prediction"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            category=result["category"],
            confidence=result["confidence"],
            explanation=result["explanation"],
            recommendations=json.dumps(result["recommendations"]),
            created_at=now
        )
        db.add(scan_record)
        db.flush()  # obtain scan_id
        saved_scan_id = scan_record.scan_id

        # Store triggered indicators
        for ind in result["indicators"]:
            indicator_record = Indicator(
                scan_id=saved_scan_id,
                indicator=ind["indicator"],
                severity=ind["severity"],
                description=ind["description"]
            )
            db.add(indicator_record)

        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[Warning] Failed to persist message scan to database: {exc}")

    # 4. Format and Return Response with Explainable Evidence and Risk Breakdown
    indicators_out = [
        IndicatorItem(
            indicator=ind["indicator"],
            severity=ind["severity"],
            description=ind["description"],
            evidence=ind.get("evidence")
        ) for ind in result["indicators"]
    ]

    return MessageAnalyzeResponse(
        prediction=result["prediction"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        category=result["category"],
        confidence=result["confidence"],
        indicators=indicators_out,
        risk_breakdown=result.get("risk_breakdown"),
        explanation=result["explanation"],
        recommendations=result["recommendations"],
        input_preview=input_preview,
        scan_id=saved_scan_id,
        analyzed_at=now
    )


@router.post("/url", response_model=URLAnalyzeResponse)
def analyze_url(payload: URLAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Static Lexical URL Security Scanner (PRD Section 14).
    Inspects URL strings safely without navigating or downloading remote content.
    Checks HTTPS, domain structure, subdomains, phishing keywords, TLD risk, and shorteners.
    Saves analysis history to SQLite.
    """
    url_text = payload.url.strip()
    if not url_text:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    # 1. Run Static URL Analyzer
    analyzer = get_url_analyzer()
    try:
        result = analyzer.analyze_url(url_text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to analyze URL: {str(exc)}")

    # 2. Privacy hash & preview
    input_preview = mask_sensitive_preview(url_text, max_length=120)
    input_hash = hash_input(url_text)
    now = datetime.now(timezone.utc)

    # 3. Store Scan Record in SQLite
    saved_scan_id = None
    try:
        scan_record = Scan(
            user_id=None,
            scan_type="url",
            input_type="url",
            input_hash=input_hash,
            input_preview=input_preview,
            prediction=result["prediction"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            category=result["category"],
            confidence=result["confidence"],
            explanation=result["explanation"],
            recommendations=json.dumps(result["recommendations"]),
            created_at=now
        )
        db.add(scan_record)
        db.flush()
        saved_scan_id = scan_record.scan_id

        # Store indicators
        for ind in result["indicators"]:
            indicator_record = Indicator(
                scan_id=saved_scan_id,
                indicator=ind["indicator"],
                severity=ind["severity"],
                description=ind["description"]
            )
            db.add(indicator_record)

        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[Warning] Failed to persist URL scan to database: {exc}")

    # 4. Format Output
    indicators_out = [
        IndicatorItem(
            indicator=ind["indicator"],
            severity=ind["severity"],
            description=ind["description"],
            evidence=ind.get("evidence")
        ) for ind in result["indicators"]
    ]

    features_out = URLFeaturesOut(**result["features"])

    return URLAnalyzeResponse(
        url=result["url"],
        prediction=result["prediction"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        category=result["category"],
        confidence=result["confidence"],
        indicators=indicators_out,
        features=features_out,
        threat_intel_status=result["threat_intel_status"],
        explanation=result["explanation"],
        recommendations=result["recommendations"],
        scan_id=saved_scan_id,
        analyzed_at=now
    )
