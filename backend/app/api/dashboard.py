from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.scan import Scan
from app.schemas.dashboard import (
    DashboardStatsResponse,
    RiskDistributionItem,
    CategoryDistributionItem,
    ActivityTimelineItem
)
from app.schemas.scan import ScanHistoryItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Computes real-time scanning analytics directly from SQLite database.
    Provides risk level breakdown, scam category distribution, scan volume over time,
    and recent activity records.
    """
    scans = db.query(Scan).order_by(desc(Scan.created_at)).all()
    total = len(scans)

    if total == 0:
        # Graceful empty state
        return DashboardStatsResponse(
            total_scans=0,
            critical_risk_scans=0,
            high_risk_scans=0,
            medium_risk_scans=0,
            low_risk_scans=0,
            total_threats=0,
            total_clean=0,
            message_scans=0,
            url_scans=0,
            average_risk_score=0.0,
            categories_detected_count=0,
            risk_distribution=[
                RiskDistributionItem(level="Critical", count=0, percentage=0.0, color="#f43f5e"),
                RiskDistributionItem(level="High", count=0, percentage=0.0, color="#f97316"),
                RiskDistributionItem(level="Medium", count=0, percentage=0.0, color="#f59e0b"),
                RiskDistributionItem(level="Low", count=0, percentage=0.0, color="#10b981"),
            ],
            category_distribution=[],
            activity_over_time=[],
            recent_scans=[]
        )

    # 1. Risk Level Counts
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    threats_count = 0
    clean_count = 0
    message_count = 0
    url_count = 0
    total_score = 0.0

    category_counts = defaultdict(int)
    date_counts = defaultdict(lambda: {"total": 0, "threats": 0, "clean": 0})

    for s in scans:
        total_score += s.risk_score

        # Risk resolution
        score = s.risk_score
        if score >= 81.0 or s.risk_level == "Critical":
            critical_count += 1
        elif score >= 61.0 or s.risk_level == "High":
            high_count += 1
        elif score >= 31.0 or s.risk_level == "Medium":
            medium_count += 1
        else:
            low_count += 1

        # Prediction counts
        if s.prediction in ("Scam", "Suspicious"):
            threats_count += 1
        else:
            clean_count += 1

        # Type counts
        stype = s.scan_type or ("url" if s.input_type == "url" else "message")
        if stype == "url":
            url_count += 1
        else:
            message_count += 1

        # Category
        if s.category:
            category_counts[s.category] += 1

        # Date for activity timeline
        scan_date = s.created_at.strftime("%Y-%m-%d") if s.created_at else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        date_counts[scan_date]["total"] += 1
        if s.prediction in ("Scam", "Suspicious"):
            date_counts[scan_date]["threats"] += 1
        else:
            date_counts[scan_date]["clean"] += 1

    avg_score = round(total_score / total, 1)

    # 2. Risk Distribution
    risk_distribution = [
        RiskDistributionItem(
            level="Critical",
            count=critical_count,
            percentage=round((critical_count / total) * 100, 1),
            color="#f43f5e"
        ),
        RiskDistributionItem(
            level="High",
            count=high_count,
            percentage=round((high_count / total) * 100, 1),
            color="#f97316"
        ),
        RiskDistributionItem(
            level="Medium",
            count=medium_count,
            percentage=round((medium_count / total) * 100, 1),
            color="#f59e0b"
        ),
        RiskDistributionItem(
            level="Low",
            count=low_count,
            percentage=round((low_count / total) * 100, 1),
            color="#10b981"
        ),
    ]

    # 3. Category Distribution (Sorted by Count Descending)
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    category_distribution = [
        CategoryDistributionItem(
            category=cat,
            count=cnt,
            percentage=round((cnt / total) * 100, 1)
        )
        for cat, cnt in sorted_categories
    ]

    # 4. Activity Over Time (Last 7 Days Continuous)
    today = datetime.now(timezone.utc).date()
    timeline_days = []
    # Build continuous window of the past 7 days
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        label = day.strftime("%b %d")
        data = date_counts.get(day_str, {"total": 0, "threats": 0, "clean": 0})
        timeline_days.append(
            ActivityTimelineItem(
                date=day_str,
                label=label,
                total=data["total"],
                threats=data["threats"],
                clean=data["clean"]
            )
        )

    # If all 7 days have 0 (e.g. data is from a different test date), ensure active dates from DB are included
    if sum(d.total for d in timeline_days) == 0 and date_counts:
        timeline_days = []
        for d_str in sorted(date_counts.keys()):
            data = date_counts[d_str]
            try:
                parsed_d = datetime.strptime(d_str, "%Y-%m-%d")
                lbl = parsed_d.strftime("%b %d")
            except Exception:
                lbl = d_str
            timeline_days.append(
                ActivityTimelineItem(
                    date=d_str,
                    label=lbl,
                    total=data["total"],
                    threats=data["threats"],
                    clean=data["clean"]
                )
            )

    # 5. Recent Scans (Top 6)
    recent_items = []
    for s in scans[:6]:
        resolved_type = s.scan_type or ("url" if s.input_type == "url" else "message")
        ind_count = len(s.indicators) if s.indicators else 0
        resolved_level = s.risk_level
        if not resolved_level:
            if s.risk_score >= 81.0:
                resolved_level = "Critical"
            elif s.risk_score >= 61.0:
                resolved_level = "High"
            elif s.risk_score >= 31.0:
                resolved_level = "Medium"
            else:
                resolved_level = "Low"

        recent_items.append(
            ScanHistoryItem(
                id=s.scan_id,
                scan_type=resolved_type,
                input_preview=s.input_preview,
                input_hash=s.input_hash,
                risk_score=round(s.risk_score, 1),
                risk_level=resolved_level,
                prediction=s.prediction,
                category=s.category,
                confidence=round(s.confidence if s.confidence is not None else 0.85, 2),
                indicator_count=ind_count,
                timestamp=s.created_at
            )
        )

    return DashboardStatsResponse(
        total_scans=total,
        critical_risk_scans=critical_count,
        high_risk_scans=high_count,
        medium_risk_scans=medium_count,
        low_risk_scans=low_count,
        total_threats=threats_count,
        total_clean=clean_count,
        message_scans=message_count,
        url_scans=url_count,
        average_risk_score=avg_score,
        categories_detected_count=len(category_counts),
        risk_distribution=risk_distribution,
        category_distribution=category_distribution,
        activity_over_time=timeline_days,
        recent_scans=recent_items
    )
