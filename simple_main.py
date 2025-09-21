#!/usr/bin/env python3
"""
Simplified main.py for Railway deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Climate Witness Chain API",
    description="Backend API for community-driven climate data collection",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', 'https://my-climate-six.vercel.app,http://localhost:3000,http://localhost:5173,*').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Climate Witness Chain API is running",
        "status": "healthy",
        "environment": os.getenv('ENVIRONMENT', 'production'),
        "railway_domain": os.getenv('RAILWAY_PUBLIC_DOMAIN', 'Not set')
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "climate_witness_api",
        "environment": os.getenv('ENVIRONMENT', 'production')
    }

# Basic auth endpoint for testing
@app.post("/api/auth/login")
async def login(credentials: dict):
    """Demo login endpoint that matches frontend expectations"""
    from datetime import datetime
    import hashlib
    
    # Generate demo tokens in the expected format
    timestamp = int(datetime.now().timestamp())
    user_id = "demo_user"
    
    # Create tokens in the format the frontend expects
    access_token = f"access_{user_id}_{timestamp}_{hashlib.md5(f'access_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
    refresh_token = f"refresh_{user_id}_{timestamp}_{hashlib.md5(f'refresh_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": 1,
            "email": credentials.get("email", "demo@climatewitness.com"),
            "full_name": "Demo User",
            "role": "user",
            "is_active": True,
            "is_verified": True
        },
        "message": "Login successful"
    }

# Request models
class LoginRequest(BaseModel):
    email: str
    password: str

class PaymentRequest(BaseModel):
    phone: str
    amount: float
    reference: str = "demo"

# Auth endpoints
@app.post("/api/auth/refresh")
async def refresh_token(request: dict):
    """Demo refresh token endpoint"""
    from datetime import datetime
    import hashlib
    
    timestamp = int(datetime.now().timestamp())
    user_id = "demo_user"
    
    access_token = f"access_{user_id}_{timestamp}_{hashlib.md5(f'access_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
    refresh_token = f"refresh_{user_id}_{timestamp}_{hashlib.md5(f'refresh_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Demo current user endpoint"""
    return {
        "user": {
            "id": 1,
            "email": "demo@climatewitness.com",
            "full_name": "Demo User",
            "role": "user",
            "is_active": True,
            "is_verified": True
        }
    }

@app.post("/api/auth/register")
async def register(user_data: dict):
    """Demo registration endpoint"""
    from datetime import datetime
    import hashlib
    
    # Generate demo tokens for new user
    timestamp = int(datetime.now().timestamp())
    user_id = f"user_{timestamp}"
    
    access_token = f"access_{user_id}_{timestamp}_{hashlib.md5(f'access_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
    refresh_token = f"refresh_{user_id}_{timestamp}_{hashlib.md5(f'refresh_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": timestamp,
            "email": user_data.get("email", "newuser@climatewitness.com"),
            "full_name": f"{user_data.get('first_name', 'New')} {user_data.get('last_name', 'User')}",
            "role": user_data.get("role", "user"),
            "is_active": True,
            "is_verified": True
        },
        "message": "Registration successful"
    }

@app.post("/api/auth/logout")
async def logout():
    """Demo logout endpoint"""
    return {"message": "Logged out successfully"}

# Events endpoints
@app.get("/api/events/stats")
async def get_events_stats():
    """Demo events stats endpoint"""
    return {
        "total_events": 150,
        "active_events": 25,
        "completed_events": 125,
        "total_participants": 1250,
        "recent_events": []
    }

@app.get("/api/events")
async def get_events():
    """Demo events list endpoint"""
    return {
        "events": [],
        "total": 0,
        "page": 1,
        "limit": 10
    }

# Basic payment endpoint for testing
@app.post("/api/payments/mpesa/initiate")
async def initiate_payment(payment: PaymentRequest):
    return {
        "success": True,
        "message": "Demo payment initiated",
        "checkout_request_id": "demo_checkout_123"
    }

# Researcher endpoints for analytics
@app.get("/api/researcher/analytics")
async def get_research_analytics():
    """Demo analytics endpoint for researchers"""
    return {
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
        }
    }

@app.get("/api/researcher/projects")
async def get_research_projects():
    """Demo projects endpoint"""
    return {
        "projects": [
            {
                "id": 1,
                "title": "East Africa Drought Patterns Analysis",
                "description": "Comprehensive study of drought patterns in East Africa using community-reported data",
                "status": "active",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "title": "Flood Prediction Model Development", 
                "description": "Machine learning model for flood prediction using historical community reports",
                "status": "in_progress",
                "created_at": "2024-02-01T14:30:00Z"
            }
        ],
        "total": 2
    }

@app.get("/api/researcher/insights")
async def get_research_insights():
    """Demo insights endpoint"""
    return {
        "insights": [
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
                ]
            }
        ]
    }

@app.get("/api/researcher/verification-queue")
async def get_verification_queue():
    """Demo verification queue endpoint"""
    return {
        "queue": [
            {
                "id": 1,
                "event_id": 156,
                "type": "drought",
                "location": "Turkana County, Kenya",
                "reported_by": "Community Reporter #342",
                "priority": "high",
                "metta_confidence": 0.87,
                "similar_reports": 3
            }
        ]
    }

@app.get("/api/researcher/data-export")
async def export_research_data():
    """Demo data export endpoint"""
    return {
        "success": True,
        "data": {
            "events": [
                {
                    "id": 1,
                    "type": "drought",
                    "location": {"lat": -1.2921, "lng": 36.8219, "name": "Nairobi, Kenya"},
                    "severity": "moderate",
                    "verified": True
                }
            ]
        },
        "format": "json"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)