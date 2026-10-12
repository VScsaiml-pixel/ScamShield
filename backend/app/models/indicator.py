from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    indicator_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.scan_id"), nullable=False)
    indicator = Column(String(150), nullable=False)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    description = Column(String(500), nullable=False)

    # Relationships
    scan = relationship("Scan", back_populates="indicators")
