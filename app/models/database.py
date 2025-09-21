from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import enum
from datetime import datetime
from typing import Generator

Base = declarative_base()

class EventTypeEnum(enum.Enum):
    drought = "drought"
    flood = "flood"
    locust_swarm = "locust_swarm"
    heatwave = "heatwave"
    heavy_rainfall = "heavy_rainfall"
    crop_failure = "crop_failure"

class SeverityEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    severe = "severe"

class AuthUser(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    wallet_address = Column(String, nullable=True)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClimateReport(Base):
    __tablename__ = "climate_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False, index=True)
    event_type = Column(Enum(EventTypeEnum), nullable=False)
    severity = Column(Enum(SeverityEnum), default=SeverityEnum.medium)
    description = Column(Text)
    evidence_link = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    verified = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'location': self.location,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'description': self.description,
            'evidence_link': self.evidence_link,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp,
            'verified': self.verified
        }

class ClimateAlert(Base):
    __tablename__ = "climate_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(SeverityEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    active = Column(Boolean, default=True)

class PatternCache(Base):
    __tablename__ = "pattern_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    analysis_data = Column(Text, nullable=False)  # JSON data
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

# Database setup
def get_database_url():
    return "sqlite:///./climate_witness.db"

def create_database_engine():
    return create_engine(get_database_url(), connect_args={"check_same_thread": False})

def create_tables():
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)

def get_session():
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db() -> Generator:
    """Get database session with context manager"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()
