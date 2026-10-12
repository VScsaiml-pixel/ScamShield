import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Ensure data directory exists if using relative sqlite path
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = Path(db_path).parent
    if db_dir and not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

# For SQLite, check_same_thread=False is needed for multi-threaded FastAPI workers
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Create tables and ensure required columns exist in SQLite database."""
    Base.metadata.create_all(bind=engine)

    # Check and add new columns if upgrading existing SQLite database
    with engine.connect() as conn:
        try:
            cursor = conn.connection.cursor()
            cursor.execute("PRAGMA table_info(scans)")
            cols = [col[1] for col in cursor.fetchall()]
            if cols:
                if "scan_type" not in cols:
                    conn.execute(text("ALTER TABLE scans ADD COLUMN scan_type VARCHAR(20) DEFAULT 'message'"))
                if "risk_level" not in cols:
                    conn.execute(text("ALTER TABLE scans ADD COLUMN risk_level VARCHAR(20) DEFAULT 'Low'"))
                if "confidence" not in cols:
                    conn.execute(text("ALTER TABLE scans ADD COLUMN confidence FLOAT DEFAULT 0.85"))

                # Backfill risk_level and scan_type where NULL
                conn.execute(text("UPDATE scans SET scan_type = CASE WHEN input_type = 'url' THEN 'url' ELSE 'message' END WHERE scan_type IS NULL OR scan_type = ''"))
                conn.execute(text("""
                    UPDATE scans SET risk_level = CASE 
                        WHEN risk_score >= 81 THEN 'Critical'
                        WHEN risk_score >= 61 THEN 'High'
                        WHEN risk_score >= 31 THEN 'Medium'
                        ELSE 'Low'
                    END WHERE risk_level IS NULL OR risk_level = ''
                """))
                conn.execute(text("UPDATE scans SET confidence = 0.85 WHERE confidence IS NULL"))
                conn.commit()
        except Exception as exc:
            print(f"[Notice] DB schema check: {exc}")


def get_db():
    """FastAPI dependency that provides a database session and ensures clean closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
