from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    drought = "drought"
    flood = "flood"
    locust_swarm = "locust_swarm"
    heatwave = "heatwave"
    heavy_rainfall = "heavy_rainfall"
    crop_failure = "crop_failure"

class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    severe = "severe"

class ClimateReportCreate(BaseModel):
    user: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=100)
    event_type: EventType
    severity: SeverityLevel = SeverityLevel.medium
    description: Optional[str] = Field(None, max_length=500)
    evidence_link: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class ClimateReportResponse(BaseModel):
    id: int
    user: str
    location: str
    event_type: EventType
    severity: SeverityLevel
    description: Optional[str]
    evidence_link: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: datetime
    verified: bool = False

class PredictionResponse(BaseModel):
    event_type: str
    probability: float = Field(..., ge=0, le=1)
    timeframe: str
    reasoning: str
    confidence_factors: List[str]
    recommended_actions: List[str]

class RiskScoreResponse(BaseModel):
    score: float = Field(..., ge=0, le=1)
    level: str
    severe_events: int
    total_events: int

class LocationAnalysisResponse(BaseModel):
    location: str
    recent_events: List[str]
    detected_patterns: List[Dict]
    risk_score: RiskScoreResponse
    predictions: List[PredictionResponse]
    timestamp: datetime

class AlertResponse(BaseModel):
    id: int
    location: str
    alert_type: str
    message: str
    severity: SeverityLevel
    created_at: datetime
    active: bool = True

class ReportStatsResponse(BaseModel):
    total_reports: int
    verified_reports: int
    verification_rate: float
    severity_distribution: Dict[str, int]