import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.scan import Scan
from app.schemas.scan import (
    ScanHistoryItem,
    ScanHistoryListResponse,
    ScanDetailResponse,
    ScanDeleteResponse,
    IndicatorItem
)

router = APIRouter(prefix="/scans", tags=["Scans History"])


@router.get("", response_model=ScanHistoryListResponse)
def get_all_scans(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of scans to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    scan_type: Optional[str] = Query(None, description="Optional filter by scan type ('message' or 'url')"),
    risk_level: Optional[str] = Query(None, description="Optional filter by risk level ('Low', 'Medium', 'High', 'Critical')"),
    db: Session = Depends(get_db)
):
    """
    Retrieve persistent scan history from SQLite.
    Returns privacy-friendly records sorted newest first.
    Zero personal credentials (OTPs, PINs, Passwords, Cards) are returned.
    """
    query = db.query(Scan)

    if scan_type:
        query = query.filter((Scan.scan_type == scan_type) | (Scan.input_type == scan_type))

    if risk_level:
        query = query.filter(Scan.risk_level == risk_level)

    total = query.count()
    records = query.order_by(desc(Scan.created_at)).offset(offset).limit(limit).all()

    items = []
    for r in records:
        # Resolve scan_type
        resolved_type = r.scan_type or ("url" if r.input_type == "url" else "message")
        
        # Calculate indicator count
        ind_count = len(r.indicators) if r.indicators else 0

        # Resolve risk_level
        resolved_level = r.risk_level
        if not resolved_level:
            if r.risk_score >= 81.0:
                resolved_level = "Critical"
            elif r.risk_score >= 61.0:
                resolved_level = "High"
            elif r.risk_score >= 31.0:
                resolved_level = "Medium"
            else:
                resolved_level = "Low"

        items.append(
            ScanHistoryItem(
                id=r.scan_id,
                scan_type=resolved_type,
                input_preview=r.input_preview,
                input_hash=r.input_hash,
                risk_score=round(r.risk_score, 1),
                risk_level=resolved_level,
                prediction=r.prediction,
                category=r.category,
                confidence=round(r.confidence if r.confidence is not None else 0.85, 2),
                indicator_count=ind_count,
                timestamp=r.created_at
            )
        )

    return ScanHistoryListResponse(total=total, scans=items)


@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_by_id(scan_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific scan record with full explainability indicators and recommendations.
    """
    record = db.query(Scan).filter(Scan.scan_id == scan_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan record #{scan_id} not found.")

    resolved_type = record.scan_type or ("url" if record.input_type == "url" else "message")

    # Resolve risk_level
    resolved_level = record.risk_level
    if not resolved_level:
        if record.risk_score >= 81.0:
            resolved_level = "Critical"
        elif record.risk_score >= 61.0:
            resolved_level = "High"
        elif record.risk_score >= 31.0:
            resolved_level = "Medium"
        else:
            resolved_level = "Low"

    # Format indicators
    indicators_out = [
        IndicatorItem(
            indicator=i.indicator,
            severity=i.severity,
            description=i.description
        ) for i in record.indicators
    ]

    # Parse recommendations from stored JSON or text
    recs = []
    if record.recommendations:
        try:
            recs = json.loads(record.recommendations)
        except Exception:
            recs = [line.strip() for line in record.recommendations.split("\n") if line.strip()]

    return ScanDetailResponse(
        id=record.scan_id,
        scan_type=resolved_type,
        input_preview=record.input_preview,
        input_hash=record.input_hash,
        risk_score=round(record.risk_score, 1),
        risk_level=resolved_level,
        prediction=record.prediction,
        category=record.category,
        confidence=round(record.confidence if record.confidence is not None else 0.85, 2),
        indicators=indicators_out,
        explanation=record.explanation,
        recommendations=recs,
        timestamp=record.created_at
    )


@router.delete("/{scan_id}", response_model=ScanDeleteResponse)
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a single scan record and all associated indicators.
    Privacy Guarantee: Deletion removes all associated database records.
    """
    record = db.query(Scan).filter(Scan.scan_id == scan_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan record #{scan_id} not found.")

    db.delete(record)
    db.commit()

    return ScanDeleteResponse(
        success=True,
        message=f"Scan record #{scan_id} deleted successfully.",
        deleted_id=scan_id
    )


@router.delete("", response_model=ScanDeleteResponse)
def delete_all_scans(db: Session = Depends(get_db)):
    """
    Permanently purge ALL scan history records from the SQLite database.
    Privacy Guarantee: Deletes all scans and indicators in a single transaction.
    """
    total_count = db.query(Scan).count()
    if total_count == 0:
        return ScanDeleteResponse(
            success=True,
            message="Scan history is already empty.",
            deleted_count=0
        )

    # Delete all scans (cascading deletes indicators and feedbacks)
    db.query(Scan).delete()
    db.commit()

    return ScanDeleteResponse(
        success=True,
        message=f"Successfully purged all {total_count} scan records from SQLite.",
        deleted_count=total_count
    )
