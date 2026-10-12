from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.scan import ScanHistoryItem


class RiskDistributionItem(BaseModel):
    level: str
    count: int
    percentage: float
    color: str


class CategoryDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float


class ActivityTimelineItem(BaseModel):
    date: str
    label: str
    total: int
    threats: int
    clean: int


class DashboardStatsResponse(BaseModel):
    total_scans: int
    critical_risk_scans: int
    high_risk_scans: int
    medium_risk_scans: int
    low_risk_scans: int
    total_threats: int
    total_clean: int
    message_scans: int
    url_scans: int
    average_risk_score: float
    categories_detected_count: int
    risk_distribution: List[RiskDistributionItem]
    category_distribution: List[CategoryDistributionItem]
    activity_over_time: List[ActivityTimelineItem]
    recent_scans: List[ScanHistoryItem]
