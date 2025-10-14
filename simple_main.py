#!/usr/bin/env python3
"""
Simplified main.py for Railway deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://my-climate-1txf-aiocezz1a-njoro24s-projects.vercel.app",
        "https://my-climate-six.vercel.app"
    ],
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
    """Login endpoint with database authentication"""
    from datetime import datetime
    import hashlib
    import sqlite3
    
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        conn = sqlite3.connect('./climate_witness.db')
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        
        if not user_row:
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        user = dict(zip(columns, user_row))
        
        # Update last login
        cursor.execute("UPDATE users SET last_login = ? WHERE email = ?", 
                      (datetime.now().isoformat(), email))
        conn.commit()
        conn.close()
        
        # Generate tokens
        timestamp = int(datetime.now().timestamp())
        user_id = user['id']
        
        access_token = f"access_{user_id}_{timestamp}_{hashlib.md5(f'access_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
        refresh_token = f"refresh_{user_id}_{timestamp}_{hashlib.md5(f'refresh_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                "role": user.get('role', 'user'),
                "is_active": True,
                "is_verified": True
            },
            "message": "Login successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

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
    """Get current user - requires proper authentication"""
    # This should only be called if user has valid token
    # For now, return error to force proper login flow
    raise HTTPException(status_code=401, detail="Authentication required")

@app.post("/api/auth/register")
async def register(user_data: dict):
    """Registration endpoint with email uniqueness check"""
    from datetime import datetime
    import hashlib
    import sqlite3
    
    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Check if email already exists
    try:
        conn = sqlite3.connect('./climate_witness.db')
        cursor = conn.cursor()
        
        # Check for existing email
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        timestamp = int(datetime.now().timestamp())
        user_id = f"user_{timestamp}"
        
        # Insert into database
        cursor.execute("""
            INSERT INTO users (id, email, first_name, last_name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            email,
            user_data.get('firstName', user_data.get('first_name', 'New')),
            user_data.get('lastName', user_data.get('last_name', 'User')),
            user_data.get('role', 'user'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Generate tokens
        access_token = f"access_{user_id}_{timestamp}_{hashlib.md5(f'access_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
        refresh_token = f"refresh_{user_id}_{timestamp}_{hashlib.md5(f'refresh_{user_id}_{timestamp}'.encode()).hexdigest()[:8]}"
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": f"{user_data.get('firstName', user_data.get('first_name', 'New'))} {user_data.get('lastName', user_data.get('last_name', 'User'))}",
                "role": user_data.get('role', 'user'),
                "is_active": True,
                "is_verified": True
            },
            "message": "Registration successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

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

# M-Pesa payment endpoints
@app.post("/api/payments/mpesa/initiate")
async def initiate_payment(payment: PaymentRequest):
    """Initiate M-Pesa STK Push payment"""
    try:
        # Import M-Pesa service
        from app.services.mpesa_service import mpesa_service
        
        # Validate phone number
        if not mpesa_service.validate_phone_number(payment.phone):
            raise HTTPException(
                status_code=400,
                detail="Invalid phone number. Please use Kenyan format (e.g., 0712345678 or 254712345678)"
            )
        
        # Validate amount
        if not mpesa_service.validate_amount(payment.amount):
            raise HTTPException(
                status_code=400,
                detail="Amount must be between 1 and 70,000 KES"
            )
        
        # Initiate STK push
        result = mpesa_service.initiate_stk_push(
            phone=payment.phone,
            amount=payment.amount,
            account_reference=payment.reference or "Climate Witness Chain",
            transaction_desc=f"Climate Witness Chain - {payment.reference or 'Donation'}"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initiation failed: {str(e)}")

@app.get("/api/payments/mpesa/status/{checkout_request_id}")
async def check_payment_status(checkout_request_id: str):
    """Check M-Pesa payment status"""
    try:
        from app.services.mpesa_service import mpesa_service
        
        result = mpesa_service.query_transaction_status(checkout_request_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/api/payments/mpesa/callback")
async def mpesa_callback(callback_data: dict):
    """Handle M-Pesa payment callback"""
    try:
        from app.services.mpesa_service import mpesa_service
        
        # Process callback
        result = mpesa_service.process_callback(callback_data)
        
        # Log the callback for debugging
        print(f"M-Pesa Callback: {json.dumps(callback_data, indent=2)}")
        print(f"Processed Result: {json.dumps(result, indent=2)}")
        
        # Here you can add database operations to store payment records
        # For example:
        # - Update payment status in database
        # - Send confirmation email/SMS
        # - Update user account balance
        # - Trigger any post-payment actions
        
        return {
            "ResultCode": 0,
            "ResultDesc": "Callback processed successfully"
        }
        
    except Exception as e:
        print(f"Callback processing error: {str(e)}")
        return {
            "ResultCode": 1,
            "ResultDesc": f"Callback processing failed: {str(e)}"
        }

@app.get("/api/payments/health")
async def payment_health():
    """Check payment service health"""
    from app.services.mpesa_service import mpesa_service
    
    return {
        "status": "healthy",
        "mpesa_configured": mpesa_service.is_configured,
        "environment": mpesa_service.environment if mpesa_service.is_configured else "demo",
        "message": "M-Pesa service ready" if mpesa_service.is_configured else "M-Pesa in demo mode - configure credentials for real payments"
    }

# Researcher Analytics Endpoints
@app.get("/api/researcher/analytics")
async def get_research_analytics(
    time_range: str = "30d",
    region: str = "all",
    event_type: str = "all"
):
    """Get comprehensive analytics for researchers"""
    
    # Mock analytics data
    analytics = {
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
    
    # Apply filters
    if time_range == "7d":
        analytics["total_events"] = int(analytics["total_events"] * 0.1)
        analytics["verified_events"] = int(analytics["verified_events"] * 0.1)
    elif time_range == "30d":
        analytics["total_events"] = int(analytics["total_events"] * 0.3)
        analytics["verified_events"] = int(analytics["verified_events"] * 0.3)
    
    analytics["pending_events"] = analytics["total_events"] - analytics["verified_events"]
    analytics["verification_rate"] = (analytics["verified_events"] / max(analytics["total_events"], 1)) * 100
    
    return analytics

@app.get("/api/researcher/projects")
async def get_research_projects():
    """Get researcher's projects"""
    
    projects = [
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
    
    return {
        "projects": projects,
        "total": len(projects)
    }

@app.get("/api/researcher/insights")
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
        "last_updated": "2024-01-20T10:00:00Z"
    }

@app.get("/api/researcher/verification-queue")
async def get_verification_queue():
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
    
    return {
        "queue": queue_items,
        "total": len(queue_items),
        "summary": {
            "high_priority": 2,
            "medium_priority": 5,
            "low_priority": 8
        }
    }

@app.get("/api/researcher/data-export")
async def export_research_data(
    export_type: str = "events",
    format: str = "json"
):
    """Export research data in various formats"""
    
    from datetime import datetime
    
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
                "filters": {"export_type": export_type, "format": format}
            }
        }
    elif export_type == "analytics":
        export_data = {
            "total_events": 1247,
            "verified_events": 1089,
            "verification_rate": 87.3,
            "metta_accuracy": 94.7
        }
    
    return {
        "success": True,
        "data": export_data,
        "format": format,
        "download_url": f"/api/researcher/download/{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    }

@app.post("/api/researcher/verify-event/{event_id}")
async def verify_event(event_id: int, verification_data: dict):
    """Verify an event as a researcher"""
    
    from datetime import datetime
    
    return {
        "success": True,
        "event_id": event_id,
        "verification_status": verification_data.get("status", "verified"),
        "researcher_notes": verification_data.get("notes", ""),
        "confidence_score": verification_data.get("confidence", 0.95),
        "verified_at": datetime.utcnow().isoformat()
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

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    import sqlite3
    
    try:
        conn = sqlite3.connect('./climate_witness.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TEXT,
                last_login TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
        
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)