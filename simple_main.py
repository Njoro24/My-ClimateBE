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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)