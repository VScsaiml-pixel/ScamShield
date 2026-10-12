from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IndicatorItem(BaseModel):
    indicator: str
    severity: str  # low, medium, high, critical
    description: str
    evidence: Optional[str] = None


class MessageAnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="The message or text content to scan")


# Alias for backward compatibility
ScanTextMessageRequest = MessageAnalyzeRequest


class MessageAnalyzeResponse(BaseModel):
    prediction: str  # 'Legitimate', 'Suspicious', 'Scam'
    risk_score: float  # 0.0 - 100.0
    risk_level: str  # 'Low', 'Medium', 'High', 'Critical'
    category: str  # e.g., 'UPI / Payment Scam', 'Banking / KYC Phishing', etc.
    confidence: float  # 0.0 - 1.0
    indicators: List[IndicatorItem]
    explanation: str
    recommendations: List[str]
    input_preview: str
    risk_breakdown: Optional[Dict[str, Any]] = None
    scan_id: Optional[int] = None
    analyzed_at: datetime


# Alias for backward compatibility
ScanResultResponse = MessageAnalyzeResponse


class URLAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=3, max_length=2048, description="The URL string to evaluate safely")


# Alias for backward compatibility
ScanURLRequest = URLAnalyzeRequest


class URLFeaturesOut(BaseModel):
    scheme: str
    host: str
    is_https: bool
    is_ip_address: bool
    has_unusual_port: bool
    subdomain_count: int
    url_length: int
    tld: str
    is_shortener: bool


class URLAnalyzeResponse(BaseModel):
    url: str
    prediction: str  # 'Legitimate', 'Suspicious', 'Scam'
    risk_score: float  # 0.0 - 100.0
    risk_level: str  # 'Low', 'Medium', 'High', 'Critical'
    category: str
    confidence: float  # 0.0 - 1.0
    indicators: List[IndicatorItem]
    features: URLFeaturesOut
    threat_intel_status: str
    explanation: str
    recommendations: List[str]
    scan_id: Optional[int] = None
    analyzed_at: datetime


class ScanHistoryItem(BaseModel):
    id: int
    scan_type: str  # 'message' or 'url'
    input_preview: Optional[str] = None
    input_hash: Optional[str] = None
    risk_score: float
    risk_level: str
    prediction: str
    category: str
    confidence: float
    indicator_count: int = 0
    timestamp: datetime


class ScanHistoryListResponse(BaseModel):
    total: int
    scans: List[ScanHistoryItem]


class ScanDetailResponse(BaseModel):
    id: int
    scan_type: str
    input_preview: Optional[str] = None
    input_hash: Optional[str] = None
    risk_score: float
    risk_level: str
    prediction: str
    category: str
    confidence: float
    indicators: List[IndicatorItem] = []
    explanation: Optional[str] = None
    recommendations: List[str] = []
    timestamp: datetime


class ScanDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_id: Optional[int] = None
    deleted_count: Optional[int] = None

