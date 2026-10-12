from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    scan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    scan_type = Column(String(20), nullable=False, default="message")  # 'message' or 'url'
    input_type = Column(String(20), nullable=False, default="text")    # 'text' or 'url'
    input_hash = Column(String(64), index=True, nullable=True)         # Privacy SHA-256 fingerprint
    input_preview = Column(String(255), nullable=True)                 # Redacted preview (zero credentials)
    prediction = Column(String(50), nullable=False)                    # 'Legitimate', 'Suspicious', 'Scam'
    risk_score = Column(Float, nullable=False)                        # 0.0 - 100.0
    risk_level = Column(String(20), nullable=False, default="Low")     # 'Low', 'Medium', 'High', 'Critical'
    category = Column(String(100), nullable=False)                    # Threat category
    confidence = Column(Float, nullable=False, default=0.85)           # Model confidence 0.0 - 1.0
    explanation = Column(Text, nullable=True)                         # Summary explanation
    recommendations = Column(Text, nullable=True)                     # Serialized JSON recommendations
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="scans")
    indicators = relationship("Indicator", back_populates="scan", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="scan", cascade="all, delete-orphan")
