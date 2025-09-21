"""
Researcher-specific API routes for Climate Witness Chain
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for researcher endpoints
class ResearchAnalytics(BaseModel):
    total_events: int
    verified_events: int
    pending_events: int
    active_reporters: int
    metta_accuracy: float
    verification_rate: float
    regional_distribution: Dict[str, int]
    event_type_distribution: Dict[str, int]
    temporal_trends: List[Dict[str, Any]]

class DataExportRequest(BaseModel):
    export_type: str
    filters: Dict[str, Any]
    format: str = "json"

class ResearchProject(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    status: str = "active"
    created_at: Optional[datetime] = None
    researcher_id: int
    data_sources: List[str] = []
    analysis_methods: List[str] = []

# Mock data for demonstration
MOCK_ANALYTICS = {
    "total_events": 1247,
    "verified_events": 1089,
    "pending_events": 158,
    "active_reporters": 342,
    "metta_accuracy": 94.7,
    "verification_rate": 87.3,
    "regional_distribution": {
        "Africa": 456,
        "Asia": 321,
        "Europe": 189,
        "North America": 156,
        "South America": 89,
        "Oceania": 36
    },
    "event_type_distribution": {
        "Drought": 387,
        "Flood": 298,
        "Extreme Heat": 234,
        "Locust Swarm": 189,
        "Wildfire": 139
    },
    "temporal_trends": [
        {"month": "Jan", "events": 89, "verified": 78, "accuracy": 92.1},
        {"month": "Feb", "events": 94, "verified": 85, "accuracy": 93.4},
        {"month": "Mar", "events": 112, "verified": 98, "accuracy": 94.2},
        {"month": "Apr", "events": 108, "verified": 96, "accuracy": 95.1},
        {"month": "May", "events": 125, "verified": 118, "accuracy": 94.7}
    ]
}

MOCK_RESEARCH_PROJECTS = [
    {
        "id": 1,
        "title": "East Africa Drought Patterns Analysis",
        "description": "Comprehensive study of drought patterns in East Africa using community-reported data",
        "status": "active",
        "created_at": "2024-01-15T10:00:00Z",
        "researcher_id": 1,
        "data_sources": ["community_reports", "satellite_data", "weather_stations"],
        "analysis_methods": ["metta_ai", "statistical_analysis", "geospatial_mapping"]
    },
    {
        "id": 2,
        "title": "Flood Prediction Model Development",
        "description": "Machine learning model for flood prediction using historical community reports",
        "status": "in_progress",
        "created_at": "2024-02-01T14:30:00Z",
        "researcher_id": 1,
        "data_sources": ["community_reports", "rainfall_data"],
        "analysis_methods": ["machine_learning", "metta_ai", "predictive_modeling"]
    }
]

@router.get("/analytics", response_model=ResearchAnalytics)
async def get_research_analytics(
    time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y, all"),
    region: str = Query("all", description="Region filter"),
    event_type: str = Query("all", description="Event type filter")
):
    """Get comprehensive analytics for researchers"""
    
    # Apply filters to mock data (in real implementation, query database)
    analytics = MOCK_ANALYTICS.copy()
    
    # Simulate filtering effects
    if time_range == "7d":
        analytics["total_events"] = int(analytics["total_events"] * 0.1)
        analytics["verified_events"] = int(analytics["verified_events"] * 0.1)
    elif time_range == "30d":
        analytics["total_events"] = int(analytics["total_events"] * 0.3)
        analytics["verified_events"] = int(analytics["verified_events"] * 0.3)
    
    if region != "all":
        # Filter by region
        total_regional = analytics["regional_distribution"].get(region, 0)
        analytics["total_events"] = total_regional
        analytics["verified_events"] = int(total_regional * 0.87)
    
    # Recalculate derived metrics
    analytics["pending_events"] = analytics["total_events"] - analytics["verified_events"]
    analytics["verification_rate"] = (analytics["verified_events"] / max(analytics["total_events"], 1)) * 100
    
    return ResearchAnalytics(**analytics)

@router.get("/projects")
async def get_research_projects(
    status: Optional[str] = Query(None, description="Filter by project status"),
    limit: int = Query(10, description="Number of projects to return")
):
    """Get researcher's projects"""
    
    projects = MOCK_RESEARCH_PROJECTS.copy()
    
    if status:
        projects = [p for p in projects if p["status"] == status]
    
    return {
        "projects": projects[:limit],
        "total": len(projects)
    }

@router.post("/projects")
async def create_research_project(project: ResearchProject):
    """Create a new research project"""
    
    new_project = project.dict()
    new_project["id"] = len(MOCK_RESEARCH_PROJECTS) + 1
    new_project["created_at"] = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "project": new_project,
        "message": "Research project created successfully"
    }

@router.get("/data-export")
async def export_research_data(
    export_type: str = Query(..., description="Type of data to export"),
    format: str = Query("json", description="Export format: json, csv, geojson"),
    time_range: str = Query("30d", description="Time range filter"),
    region: str = Query("all", description="Region filter")
):
    """Export research data in various formats"""
    
    export_data = {}
    
    if export_type == "events":
        export_data = {
            "events": [
                {
                    "id": 1,
                    "type": "drought",
                    "location": {"lat": -1.2921, "lng": 36.8219, "name": "Nairobi, Kenya"},
                    "severity": "moderate",
                    "verified": True,
                    "reported_at": "2024-01-15T10:00:00Z",
                    "metta_confidence": 0.94
                },
                {
                    "id": 2,
                    "type": "flood",
                    "location": {"lat": -4.0383, "lng": 39.6682, "name": "Mombasa, Kenya"},
                    "severity": "severe",
                    "verified": True,
                    "reported_at": "2024-01-20T14:30:00Z",
                    "metta_confidence": 0.89
                }
            ],
            "metadata": {
                "total_records": 2,
                "export_date": datetime.utcnow().isoformat(),
                "filters": {"time_range": time_range, "region": region}
            }
        }
    
    elif export_type == "analytics":
        export_data = MOCK_ANALYTICS
    
    elif export_type == "metta_atoms":
        export_data = {
            "knowledge_atoms": [
                {
                    "id": "atom_001",
                    "type": "climate_pattern",
                    "content": "(drought-pattern East-Africa (severity moderate) (confidence 0.94))",
                    "generated_at": "2024-01-15T10:00:00Z",
                    "source_events": [1, 3, 7, 12]
                },
                {
                    "id": "atom_002",
                    "type": "prediction",
                    "content": "(flood-risk Coastal-Kenya (probability 0.78) (timeframe 30-days))",
                    "generated_at": "2024-01-20T14:30:00Z",
                    "source_events": [2, 5, 9]
                }
            ],
            "metadata": {
                "total_atoms": 2,
                "ai_model": "MeTTa-Climate-v2.1",
                "export_date": datetime.utcnow().isoformat()
            }
        }
    
    return {
        "success": True,
        "data": export_data,
        "format": format,
        "download_url": f"/api/researcher/download/{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    }

@router.get("/insights")
async def get_research_insights():
    """Get AI-generated research insights"""
    
    insights = [
        {
            "id": 1,
            "type": "trend_analysis",
            "title": "Increasing Drought Frequency in East Africa",
            "description": "MeTTa analysis shows 23% increase in drought reports over the last 6 months",
            "confidence": 0.92,
            "impact": "high",
            "recommendations": [
                "Increase monitoring in affected regions",
                "Deploy early warning systems",
                "Coordinate with local agricultural authorities"
            ],
            "generated_at": "2024-01-20T10:00:00Z"
        },
        {
            "id": 2,
            "type": "correlation_discovery",
            "title": "Locust Swarm Patterns Correlate with Rainfall",
            "description": "Strong correlation (r=0.84) between rainfall patterns and locust swarm reports",
            "confidence": 0.89,
            "impact": "medium",
            "recommendations": [
                "Integrate rainfall data into locust prediction models",
                "Develop combined monitoring protocols"
            ],
            "generated_at": "2024-01-18T15:30:00Z"
        }
    ]
    
    return {
        "insights": insights,
        "total": len(insights),
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/collaboration")
async def get_collaboration_opportunities():
    """Get collaboration opportunities with other researchers"""
    
    opportunities = [
        {
            "id": 1,
            "type": "data_sharing",
            "title": "Drought Research Collaboration - University of Nairobi",
            "description": "Share East Africa drought data for joint research publication",
            "partner": "Dr. Sarah Kimani, University of Nairobi",
            "status": "pending",
            "potential_impact": "high",
            "data_requirements": ["drought_events", "verification_data", "metta_analysis"]
        },
        {
            "id": 2,
            "type": "joint_research",
            "title": "Climate Prediction Model Development",
            "description": "Collaborate on machine learning models for climate event prediction",
            "partner": "Climate Research Institute, ICRAF",
            "status": "active",
            "potential_impact": "very_high",
            "data_requirements": ["historical_events", "weather_data", "community_reports"]
        }
    ]
    
    return {
        "opportunities": opportunities,
        "total": len(opportunities)
    }

@router.get("/verification-queue")
async def get_verification_queue(
    priority: str = Query("all", description="Priority filter: high, medium, low, all"),
    limit: int = Query(20, description="Number of items to return")
):
    """Get events pending verification by researchers"""
    
    queue_items = [
        {
            "id": 1,
            "event_id": 156,
            "type": "drought",
            "location": "Turkana County, Kenya",
            "reported_by": "Community Reporter #342",
            "reported_at": "2024-01-20T08:30:00Z",
            "priority": "high",
            "metta_confidence": 0.87,
            "supporting_evidence": ["photo", "weather_data"],
            "similar_reports": 3
        },
        {
            "id": 2,
            "event_id": 157,
            "type": "locust_swarm",
            "location": "Samburu County, Kenya",
            "reported_by": "Agricultural Officer",
            "reported_at": "2024-01-20T11:15:00Z",
            "priority": "high",
            "metta_confidence": 0.92,
            "supporting_evidence": ["photo", "video", "gps_data"],
            "similar_reports": 1
        }
    ]
    
    if priority != "all":
        queue_items = [item for item in queue_items if item["priority"] == priority]
    
    return {
        "queue": queue_items[:limit],
        "total": len(queue_items),
        "summary": {
            "high_priority": 2,
            "medium_priority": 5,
            "low_priority": 8
        }
    }

@router.post("/verify-event/{event_id}")
async def verify_event(
    event_id: int,
    verification_data: Dict[str, Any]
):
    """Verify an event as a researcher"""
    
    return {
        "success": True,
        "event_id": event_id,
        "verification_status": verification_data.get("status", "verified"),
        "researcher_notes": verification_data.get("notes", ""),
        "confidence_score": verification_data.get("confidence", 0.95),
        "verified_at": datetime.utcnow().isoformat()
    }