#!/usr/bin/env python3
"""
Simplified main.py for Railway deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')

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
async def login():
    return {
        "success": True,
        "message": "Demo login successful",
        "token": "demo_token_123"
    }

# Basic payment endpoint for testing
@app.post("/api/payments/mpesa/initiate")
async def initiate_payment():
    return {
        "success": True,
        "message": "Demo payment initiated",
        "checkout_request_id": "demo_checkout_123"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)