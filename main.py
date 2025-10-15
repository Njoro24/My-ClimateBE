import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import threading
import requests
from contextlib import asynccontextmanager
from typing import List
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global thread safety
_initialized = False
_init_lock = threading.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global _initialized
    with _init_lock:
        if not _initialized:
            print(" Starting Climate Witness Chain API...")
            
            # Initialize database tables for climate models
            from app.models.database import create_tables
            create_tables()
            print("Climate database tables initialized")
            
            # Start background cleanup task
            from app.services.climate_service import ClimateService
            climate_service = ClimateService()
            await climate_service.cleanup_old_data()
            print("Climate data cleanup scheduled")
            
            _initialized = True
        else:
            print("API already initialized, skipping startup...")
    yield
    # Shutdown
    print("Shutting down Climate Witness Chain API...")

# Create FastAPI app ONCE
app = FastAPI(
    title="Climate Witness Chain API",
    description="Backend API for community-driven climate data collection using MeTTa knowledge atoms",
    version="1.0.0",
    lifespan=lifespan
)

# Backup manual CORS handler - ensures CORS works even if middleware fails
@app.middleware("http")
async def ensure_cors_headers(request: Request, call_next):
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        from fastapi import Response
        response = Response()
        origin = request.headers.get("origin")
        
        # Allow specific origins or all for debugging
        allowed_origins = [
            "https://my-climate-1txf.vercel.app",
            "https://my-climate-1txf-git-main-njoro24s-projects.vercel.app", 
            "https://my-climate-1txf-v3xwkbvop-njoro24s-projects.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173"
        ]
        
        if origin in allowed_origins or origin and origin.endswith('.vercel.app'):
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"  # Fallback
            
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        
        logger.info(f"OPTIONS request from origin: {origin}")
        return response
    
    # Process normal requests
    response = await call_next(request)
    
    # Add CORS headers to response
    origin = request.headers.get("origin")
    if origin:
        allowed_origins = [
            "https://my-climate-1txf.vercel.app",
            "https://my-climate-1txf-git-main-njoro24s-projects.vercel.app", 
            "https://my-climate-1txf-v3xwkbvop-njoro24s-projects.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173"
        ]
        
        if origin in allowed_origins or origin.endswith('.vercel.app'):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
    return response

# CORS configuration - Specific origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payment models
class MpesaPaymentRequest(BaseModel):
    phone: str
    amount: float
    reference: str

class PaymentResponse(BaseModel):
    success: bool
    message: str
    checkout_request_id: str = None

from app.api.routes import events, metta, users, auth, community_verification, economic_impact, insurance, dao_governance, alerts, ai_metta, plant_recommendations, contact, admin, payments, researcher, explainable_ai, media_integrity, civic_decision_making

try:
    from app.api.routes import blockchain
    BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Blockchain service disabled: {e}")
    BLOCKCHAIN_AVAILABLE = False

# Import the climate models and services we created
from app.models.database import get_db
from app.services.climate_service import ClimateService
from app.models.climatemodels import (
    ClimateReportCreate, 
    ClimateReportResponse,
    LocationAnalysisResponse,
    AlertResponse,
    ReportStatsResponse
)

# Initialize climate service
climate_service = ClimateService()

# handle endpoints
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(metta.router, prefix="/api/metta", tags=["metta"])
app.include_router(ai_metta.router, prefix="/api/ai-metta", tags=["ai-metta"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(community_verification.router, prefix="/api/community-verification", tags=["community-verification"])
app.include_router(economic_impact.router, prefix="/api/economic-impact", tags=["economic-impact"])
app.include_router(insurance.router, prefix="/api/insurance", tags=["insurance"])
app.include_router(dao_governance.router, prefix="/api/dao", tags=["dao-governance"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(plant_recommendations.router, prefix="/api/plants", tags=["plant-recommendations"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(researcher.router, prefix="/api/researcher", tags=["researcher"])

# Enhanced AI and Civic Decision-Making Routes
app.include_router(explainable_ai.router, prefix="/api/explainable-ai", tags=["explainable-ai"])
app.include_router(media_integrity.router, prefix="/api/media-integrity", tags=["media-integrity"])
app.include_router(civic_decision_making.router, prefix="/api/civic-decisions", tags=["civic-decision-making"])

if BLOCKCHAIN_AVAILABLE:
    app.include_router(blockchain.router, prefix="/api/blockchain", tags=["blockchain"])
    print("Blockchain service enabled")
else:
    print("Blockchain service disabled - install 'setuptools' to enable")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# M-Pesa Payment Endpoints
@app.post("/api/payments/mpesa/initiate", response_model=PaymentResponse, tags=["payments"])
async def initiate_mpesa_payment(payment_request: MpesaPaymentRequest):
    """Initiate M-Pesa STK Push payment"""
    try:
        logger.info(f"Received payment request: {payment_request.dict()}")
        
        # Validate phone number format
        phone = payment_request.phone.strip()
        if not (phone.startswith('254') and len(phone) == 12 and phone[3:].isdigit()):
            raise HTTPException(
                status_code=400, 
                detail="Phone number must be in Kenyan format: 2547XXXXXXXX (12 digits starting with 254)"
            )
        
        # Validate amount
        if payment_request.amount < 10:  # M-Pesa minimum is usually 10 KES
            raise HTTPException(
                status_code=400, 
                detail="Amount must be at least 10 KES"
            )
        
        # Try both payment service endpoints - CORRECTED URL
        endpoints = [
            {
                'url': 'http://localhost:3001/api/payments/mpesa/initiate',  # ✅ CORRECTED from /stk-push to /initiate
                'payload': {
                    'phone': phone,
                    'amount': str(payment_request.amount),
                    'accountRef': payment_request.reference
                }
            },
            {
                'url': 'http://localhost:3000/api/payments/mpesa/initiate',
                'payload': {
                    'phone': phone,
                    'amount': payment_request.amount,
                    'reference': payment_request.reference
                }
            }
        ]
        
        last_error = None
        
        for endpoint in endpoints:
            try:
                logger.info(f"Trying endpoint: {endpoint['url']}")
                
                response = requests.post(
                    endpoint['url'],
                    json=endpoint['payload'],
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
                logger.info(f"Payment service response status: {response.status_code}")
                logger.info(f"Payment service response content: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    return PaymentResponse(
                        success=data.get('success', True),
                        message=data.get('message', 'Payment initiated'),
                        checkout_request_id=data.get('checkoutRequestID') or data.get('checkout_request_id', '')
                    )
                else:
                    last_error = f"Endpoint {endpoint['url']} failed: {response.status_code} - {response.text}"
                    logger.warning(last_error)
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f"Cannot connect to payment service at {endpoint['url']}: {str(e)}"
                logger.warning(last_error)
                continue
            except requests.exceptions.Timeout:
                last_error = f"Payment service timeout at {endpoint['url']}"
                logger.warning(last_error)
                continue
            except requests.exceptions.RequestException as e:
                last_error = f"Payment service error at {endpoint['url']}: {str(e)}"
                logger.warning(last_error)
                continue
        
        # If all endpoints failed
        raise HTTPException(
            status_code=503, 
            detail=f"Payment service unavailable. {last_error}"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/payments/mpesa/initiate-forward", tags=["payments"])
async def mpesa_initiate_forward(request: Request):
    """Forward M-Pesa payment request to Node.js payments server"""
    try:
        # Get the raw request body and log it for debugging
        body = await request.body()
        body_str = body.decode('utf-8')
        logger.info(f"Forwarding payment request: {body_str}")
        
        # Parse to validate JSON
        try:
            request_data = json.loads(body_str)
            logger.info(f"Parsed request data: {request_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Forward to Node.js server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:3000/api/payments/mpesa/initiate",
                content=body,
                headers={"Content-Type": "application/json"}
            )
        
        logger.info(f"Node.js server response status: {response.status_code}")
        logger.info(f"Node.js server response: {response.text}")
        
        # Return the response from Node.js server
        return response.json()
        
    except httpx.RequestError as e:
        error_msg = f"Payment service connection error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/payments/mpesa/callback", tags=["payments"])
async def mpesa_callback(callback_data: dict):
    """Handle M-Pesa payment callback"""
    # Process payment confirmation
    print("M-Pesa callback received:", callback_data)
    
    # Extract payment details
    result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    
    if result_code == 0:
        # Payment successful
        print("Payment successful!")
        # Here you can update your database, send notifications, etc.
        return {"status": "success", "message": "Payment processed successfully"}
    else:
        # Payment failed
        print("Payment failed!")
        return {"status": "failed", "message": "Payment was not completed"}

@app.get("/api/payments/status/{checkout_request_id}", tags=["payments"])
async def check_payment_status(checkout_request_id: str):
    """Check M-Pesa payment status"""
    # You can implement payment status checking here
    return {"checkout_request_id": checkout_request_id, "status": "pending"}

# Add a health check endpoint to test payment service connectivity
@app.get("/api/payments/health", tags=["payments"])
async def payment_health_check():
    """Check if payment services are available"""
    services = {
        "port_3000": "http://localhost:3000/api/payments/health",
        "port_3001": "http://localhost:3001/api/payments/health"
    }
    
    results = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            results[name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response": response.text[:200] if response.text else "No response"
            }
        except requests.exceptions.RequestException as e:
            results[name] = {
                "status": "unreachable",
                "error": str(e)
            }
    
    return results

# Climate Report Endpoints
@app.post("/api/climate/reports", response_model=ClimateReportResponse, tags=["climate"])
async def create_climate_report(report: ClimateReportCreate):
    """Create a new climate report"""
    try:
        return await climate_service.create_climate_report(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating climate report: {str(e)}")

@app.get("/api/climate/reports/{location", response_model=List[ClimateReportResponse], tags=["climate"])
async def get_climate_reports(location: str, limit: int = 10):
    """Get recent climate reports for a location"""
    reports = await climate_service.get_recent_reports(location, limit)
    if not reports:
        raise HTTPException(status_code=404, detail="No climate reports found for this location")
    return reports

@app.get("/api/climate/analysis/{location}", response_model=dict, tags=["climate"])
async def get_climate_analysis(location: str):
    """Get climate analysis for a location"""
    analysis = await climate_service.get_location_analysis(location)
    if not analysis:
        raise HTTPException(status_code=404, detail="Climate analysis not available for this location")
    return analysis

@app.get("/api/climate/alerts/{location}", response_model=List[AlertResponse], tags=["climate"])
async def get_climate_alerts(location: str):
    """Get active climate alerts for a location"""
    alerts = await climate_service.get_climate_alerts(location)
    return alerts

@app.get("/api/climate/stats/{location}", response_model=ReportStatsResponse, tags=["climate"])
async def get_climate_stats(location: str):
    """Get statistics for climate reports in a location"""
    stats = await climate_service.get_report_stats(location)
    return stats

@app.get("/api/climate/locations", tags=["climate"])
async def get_climate_locations():
    """Get all locations with climate reports"""
    locations = await climate_service.get_all_locations()
    return {"locations": locations}

@app.get("/api/climate/global/patterns", tags=["climate"])
async def get_climate_global_patterns():
    """Get global climate patterns"""
    patterns = await climate_service.get_global_analysis()
    return patterns

@app.post("/api/climate/reports/{report_id}/verify", tags=["climate"])
async def verify_climate_report(report_id: int, verified: bool = True):
    """Verify or unverify a climate report"""
    success = await climate_service.verify_report(report_id, verified)
    if not success:
        raise HTTPException(status_code=404, detail="Climate report not found")
    return {"status": "success", "verified": verified}

@app.get("/api/climate/health", tags=["climate"])
async def climate_health_check():
    """Climate service health check"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "climate_witness_service"
    }

@app.options("/{full_path:path}")
async def options_handler(request: Request):
    """Handle preflight OPTIONS requests"""
    from fastapi import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

@app.get("/")
async def root(request: Request):
    origin = request.headers.get('origin', 'No origin')
    logger.info(f"Root endpoint accessed from origin: {origin}")
    return {
        "message": "Climate Witness Chain API is running", 
        "cors_enabled": True,
        "origin": origin,
        "timestamp": "2024-01-15"
    }

@app.get("/api/cors-test")
async def cors_test(request: Request):
    """Simple CORS test endpoint"""
    origin = request.headers.get('origin', 'No origin')
    return {
        "message": "CORS test successful",
        "origin": origin,
        "method": request.method,
        "timestamp": "2024-01-15",
        "headers": dict(request.headers)
    }

@app.get("/api/test-cors")
async def test_cors(request: Request):
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS is working!", 
        "timestamp": "2024-01-15",
        "origin": request.headers.get("origin", "No origin header"),
        "user_agent": request.headers.get("user-agent", "No user agent"),
        "method": request.method
    }

@app.post("/api/test-cors")
async def test_cors_post(request: Request):
    """Test POST endpoint to verify CORS is working"""
    return {
        "message": "CORS POST is working!", 
        "timestamp": "2024-01-15",
        "origin": request.headers.get("origin", "No origin header"),
        "content_type": request.headers.get("content-type", "No content type"),
        "method": request.method
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)