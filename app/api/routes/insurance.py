"""
Enhanced Insurance API Routes with Real Weather Data Integration
Handles comprehensive climate insurance with MeTTa reasoning and real weather APIs
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import os
import logging

from app.database.crud import *
from app.services.insurance_service import SimpleInsuranceService
from app.services.metta_service import get_shared_knowledge_base

logger = logging.getLogger(__name__)
router = APIRouter()

# Global insurance service instance
insurance_service = SimpleInsuranceService()

# Enhanced Request/Response Models
class CreatePolicyRequest(BaseModel):
    user_id: str
    crop_type: Optional[str] = "maize"
    farm_size: Optional[float] = 1.0  # in acres
    coverage_amount: Optional[float] = 1000.0
    location: Optional[Dict[str, float]] = None  # {"latitude": -1.0, "longitude": 36.0}
    coverage_period_months: Optional[int] = 12

class CheckEligibilityRequest(BaseModel):
    user_id: str
    event_id: str

class ProcessPayoutRequest(BaseModel):
    user_id: str
    event_id: str

class ClaimRequest(BaseModel):
    user_id: str
    policy_id: str
    event_id: str
    claim_reason: str
    estimated_damage: Optional[float] = None

class WeatherRiskAssessment(BaseModel):
    location: Dict[str, float]
    crop_type: str
    assessment_period_days: Optional[int] = 30

@router.post("/create-policy")
async def create_insurance_policy(
    request: CreatePolicyRequest,
    crud = None
):
    """Create an enhanced insurance policy with real weather risk assessment"""
    try:
        # Get weather risk assessment if location provided
        risk_assessment = None
        premium_adjustment = 1.0
        
        if request.location:
            risk_assessment = await get_weather_risk_assessment(
                request.location, 
                request.crop_type
            )
            premium_adjustment = risk_assessment.get('risk_multiplier', 1.0)
        
        # Use MeTTa for policy evaluation
        kb = get_shared_knowledge_base()
        policy_query = f'!(evaluate-insurance-policy "{request.user_id}" "{request.crop_type}" {request.coverage_amount})'
        metta_evaluation = kb.run_metta_function(policy_query)
        
        # Create enhanced policy
        result = await insurance_service.create_enhanced_policy(
            user_id=request.user_id,
            crop_type=request.crop_type,
            farm_size=request.farm_size,
            coverage_amount=request.coverage_amount,
            location=request.location,
            coverage_period_months=request.coverage_period_months,
            premium_adjustment=premium_adjustment,
            risk_assessment=risk_assessment
        )
        
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Policy creation failed'))
        
        return {
            "message": "Enhanced insurance policy created successfully",
            "policy": result['policy'],
            "coverage_amount": result['policy']['coverage_amount'],
            "premium_paid": result['policy']['premium_paid'],
            "risk_assessment": risk_assessment,
            "metta_evaluation": [str(r) for r in metta_evaluation] if metta_evaluation else [],
            "weather_data_used": bool(request.location)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create insurance policy: {str(e)}")

@router.post("/check-eligibility")
async def check_payout_eligibility(
    request: CheckEligibilityRequest,
    crud = None
):
    """Check if user is eligible for insurance payout"""
    try:
        result = await insurance_service.check_payout_eligibility(request.user_id, request.event_id)
        
        if not result.get('success', False):
            return {
                "eligible": False,
                "reason": result.get('reason', result.get('error', 'Eligibility check failed'))
            }
        
        return {
            "eligible": result['eligible'],
            "policy_id": result.get('policy_id'),
            "payout_amount": result.get('payout_amount'),
            "coverage_amount": result.get('coverage_amount'),
            "event_type": result.get('event_type'),
            "verification_status": result.get('verification_status')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check eligibility: {str(e)}")

@router.post("/process-payout")
async def process_automatic_payout(
    request: ProcessPayoutRequest,
    crud = None
):
    """Process automatic insurance payout for verified event"""
    try:
        result = await insurance_service.process_automatic_payout(request.user_id, request.event_id)
        
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Payout processing failed'))
        
        return {
            "message": result.get('message', 'Payout processed successfully'),
            "payout": result['payout'],
            "transaction_id": result.get('transaction_id'),
            "amount": result['payout']['amount']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payout: {str(e)}")

@router.get("/user/{user_id}/policies")
async def get_user_policies(
    user_id: str,
    crud = None
):
    """Get all insurance policies for a user"""
    try:
        policies = await insurance_service.get_user_policies(user_id)
        
        return {
            "user_id": user_id,
            "total_policies": len(policies),
            "policies": [policy.to_dict() for policy in policies]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user policies: {str(e)}")

@router.get("/user/{user_id}/payouts")
async def get_user_payouts(
    user_id: str,
    crud = None
):
    """Get all insurance payouts for a user"""
    try:
        payouts = await insurance_service.get_user_payouts(user_id)
        
        total_received = sum(payout.amount for payout in payouts if payout.status == 'completed')
        
        return {
            "user_id": user_id,
            "total_payouts": len(payouts),
            "total_amount_received": total_received,
            "payouts": [payout.to_dict() for payout in payouts]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user payouts: {str(e)}")

@router.get("/stats")
async def get_insurance_stats(crud = None):
    """Get overall insurance system statistics"""
    try:
        stats = await insurance_service.get_insurance_stats()
        
        return {
            "message": "Insurance system statistics",
            "statistics": stats,
            "fund_health": "healthy" if stats['fund_balance'] > 0 else "needs_funding",
            "coverage_info": {
                "base_premium": insurance_service.base_premium,
                "base_coverage": insurance_service.base_coverage,
                "payout_percentage": insurance_service.payout_percentage * 100
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insurance stats: {str(e)}")

@router.get("/coverage-info")
async def get_coverage_info():
    """Get information about insurance coverage options"""
    return {
        "coverage_options": {
            "simple_climate_insurance": {
                "name": "Simple Climate Insurance",
                "description": "Basic coverage for verified climate events",
                "premium": insurance_service.base_premium,
                "coverage_amount": insurance_service.base_coverage,
                "payout_percentage": insurance_service.payout_percentage * 100,
                "requirements": [
                    "Minimum trust score of 60",
                    "No existing active policy",
                    "Valid wallet address"
                ],
                "covered_events": [
                    "Drought",
                    "Flood", 
                    "Locust swarms",
                    "Extreme heat"
                ],
                "payout_conditions": [
                    "Event must be community verified",
                    "User must be the event reporter",
                    "Event must cause economic impact"
                ]
            }
        }
    }

@router.post("/demo/auto-payout-check")
async def demo_auto_payout_check(crud = None):
    """Demo endpoint: Check all verified events for automatic payout eligibility"""
    try:
        # Get all verified events
        all_events = await crud.get_all_events()
        verified_events = [e for e in all_events if e.verification_status == 'verified']
        
        payout_results = []
        
        for event in verified_events:
            try:
                # Check if user has insurance
                eligibility = await insurance_service.check_payout_eligibility(event.user_id, event.id)
                
                if eligibility.get('eligible', False):
                    # Process automatic payout
                    payout_result = await insurance_service.process_automatic_payout(event.user_id, event.id)
                    
                    payout_results.append({
                        'event_id': event.id,
                        'user_id': event.user_id,
                        'event_type': event.event_type,
                        'payout_processed': payout_result.get('success', False),
                        'payout_amount': payout_result.get('payout', {}).get('amount', 0),
                        'message': payout_result.get('message', 'Processing failed')
                    })
                else:
                    payout_results.append({
                        'event_id': event.id,
                        'user_id': event.user_id,
                        'event_type': event.event_type,
                        'payout_processed': False,
                        'payout_amount': 0,
                        'message': eligibility.get('reason', 'Not eligible')
                    })
                    
            except Exception as e:
                payout_results.append({
                    'event_id': event.id,
                    'user_id': event.user_id,
                    'event_type': event.event_type,
                    'payout_processed': False,
                    'payout_amount': 0,
                    'message': f'Error: {str(e)}'
                })
        
        successful_payouts = len([r for r in payout_results if r['payout_processed']])
        total_payout_amount = sum(r['payout_amount'] for r in payout_results if r['payout_processed'])
        
        return {
            "message": f"Auto-payout check completed: {successful_payouts} payouts processed",
            "total_events_checked": len(verified_events),
            "successful_payouts": successful_payouts,
            "total_payout_amount": total_payout_amount,
            "results": payout_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo auto-payout check failed: {str(e)}")

@router.post("/submit-claim")
async def submit_insurance_claim(
    request: ClaimRequest,
    crud = None
):
    """Submit an insurance claim for a climate event"""
    try:
        # Use MeTTa to evaluate claim validity
        kb = get_shared_knowledge_base()
        claim_query = f'!(evaluate-insurance-claim "{request.user_id}" "{request.policy_id}" "{request.event_id}")'
        metta_evaluation = kb.run_metta_function(claim_query)
        
        # Process the claim
        result = await insurance_service.submit_claim(
            user_id=request.user_id,
            policy_id=request.policy_id,
            event_id=request.event_id,
            claim_reason=request.claim_reason,
            estimated_damage=request.estimated_damage
        )
        
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Claim submission failed'))
        
        return {
            "message": "Insurance claim submitted successfully",
            "claim": result['claim'],
            "claim_id": result['claim']['id'],
            "status": result['claim']['status'],
            "metta_evaluation": [str(r) for r in metta_evaluation] if metta_evaluation else [],
            "estimated_processing_time": "2-5 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Claim submission error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit claim: {str(e)}")

@router.get("/user/{user_id}/claims")
async def get_user_claims(
    user_id: str,
    crud = None
):
    """Get all insurance claims for a user"""
    try:
        claims = await insurance_service.get_user_claims(user_id)
        
        return {
            "user_id": user_id,
            "total_claims": len(claims),
            "claims": [claim.to_dict() for claim in claims],
            "claim_summary": {
                "pending": len([c for c in claims if c.status == 'pending']),
                "approved": len([c for c in claims if c.status == 'approved']),
                "rejected": len([c for c in claims if c.status == 'rejected'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user claims: {str(e)}")

@router.post("/weather-risk-assessment")
async def assess_weather_risk(
    request: WeatherRiskAssessment
):
    """Assess weather-based risk for insurance pricing"""
    try:
        risk_assessment = await get_weather_risk_assessment(
            request.location,
            request.crop_type,
            request.assessment_period_days
        )
        
        return {
            "location": request.location,
            "crop_type": request.crop_type,
            "assessment_period_days": request.assessment_period_days,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Weather risk assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assess weather risk: {str(e)}")

@router.get("/weather-data/{latitude}/{longitude}")
async def get_current_weather_data(
    latitude: float,
    longitude: float
):
    """Get current weather data for a location"""
    try:
        weather_data = await fetch_weather_data(latitude, longitude)
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "weather_data": weather_data,
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "OpenWeatherMap API"
        }
        
    except Exception as e:
        logger.error(f"Weather data fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")

@router.get("/policy-recommendations/{user_id}")
async def get_policy_recommendations(
    user_id: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    crop_type: Optional[str] = "maize",
    crud = None
):
    """Get personalized insurance policy recommendations"""
    try:
        # Get user data
        user = await crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get weather risk if location provided
        risk_assessment = None
        if latitude and longitude:
            risk_assessment = await get_weather_risk_assessment(
                {"latitude": latitude, "longitude": longitude},
                crop_type
            )
        
        # Use MeTTa for recommendations
        kb = get_shared_knowledge_base()
        recommendation_query = f'!(recommend-insurance-policy "{user_id}" "{crop_type}")'
        metta_recommendations = kb.run_metta_function(recommendation_query)
        
        # Generate recommendations
        recommendations = await insurance_service.generate_policy_recommendations(
            user=user,
            location={"latitude": latitude, "longitude": longitude} if latitude and longitude else None,
            crop_type=crop_type,
            risk_assessment=risk_assessment
        )
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "risk_assessment": risk_assessment,
            "metta_analysis": [str(r) for r in metta_recommendations] if metta_recommendations else [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.post("/demo/create-policies-for-all")
async def demo_create_policies_for_all(crud = None):
    """Demo endpoint: Create insurance policies for all eligible users"""
    try:
        # Get all users
        all_users = await crud.get_all_users()
        
        policy_results = []
        
        for user in all_users:
            try:
                # Check if user is eligible (trust score >= 60)
                if user.trust_score >= 60:
                    result = await insurance_service.create_simple_policy(user.id)
                    
                    policy_results.append({
                        'user_id': user.id,
                        'trust_score': user.trust_score,
                        'policy_created': result.get('success', False),
                        'message': result.get('message', result.get('error', 'Unknown error'))
                    })
                else:
                    policy_results.append({
                        'user_id': user.id,
                        'trust_score': user.trust_score,
                        'policy_created': False,
                        'message': 'Trust score too low (minimum 60 required)'
                    })
                    
            except Exception as e:
                policy_results.append({
                    'user_id': user.id,
                    'trust_score': user.trust_score,
                    'policy_created': False,
                    'message': f'Error: {str(e)}'
                })
        
        successful_policies = len([r for r in policy_results if r['policy_created']])
        
        return {
            "message": f"Demo policy creation completed: {successful_policies} policies created",
            "total_users_checked": len(all_users),
            "successful_policies": successful_policies,
            "results": policy_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo policy creation failed: {str(e)}")

# Helper functions for weather data integration
async def fetch_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch current weather data from OpenWeatherMap API"""
    try:
        api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        
        if api_key == 'demo_key':
            # Return mock data for demo
            return {
                "temperature": 25.5,
                "humidity": 65,
                "pressure": 1013.25,
                "wind_speed": 3.2,
                "weather_condition": "partly_cloudy",
                "precipitation": 0.0,
                "uv_index": 6,
                "visibility": 10.0,
                "data_source": "demo_data"
            }
        
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "pressure": data['main']['pressure'],
            "wind_speed": data['wind']['speed'],
            "weather_condition": data['weather'][0]['main'].lower(),
            "precipitation": data.get('rain', {}).get('1h', 0.0),
            "uv_index": data.get('uvi', 0),
            "visibility": data.get('visibility', 10000) / 1000,
            "data_source": "openweathermap"
        }
        
    except requests.RequestException as e:
        logger.warning(f"Weather API error: {e}, using fallback data")
        return {
            "temperature": 24.0,
            "humidity": 70,
            "pressure": 1012.0,
            "wind_speed": 2.5,
            "weather_condition": "clear",
            "precipitation": 0.0,
            "uv_index": 5,
            "visibility": 10.0,
            "data_source": "fallback_data"
        }

async def get_weather_risk_assessment(
    location: Dict[str, float], 
    crop_type: str, 
    assessment_period_days: int = 30
) -> Dict[str, Any]:
    """Assess weather-based risk for insurance pricing"""
    try:
        latitude = location['latitude']
        longitude = location['longitude']
        
        # Get current weather
        current_weather = await fetch_weather_data(latitude, longitude)
        
        # Calculate risk factors based on crop type and weather
        risk_factors = {
            "drought_risk": _calculate_drought_risk(current_weather, crop_type),
            "flood_risk": _calculate_flood_risk(current_weather, crop_type),
            "temperature_risk": _calculate_temperature_risk(current_weather, crop_type),
            "wind_risk": _calculate_wind_risk(current_weather, crop_type)
        }
        
        # Calculate overall risk score (0-1)
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        # Calculate premium multiplier (0.8 - 2.0)
        risk_multiplier = max(0.8, min(2.0, 1.0 + overall_risk))
        
        return {
            "location": location,
            "crop_type": crop_type,
            "current_weather": current_weather,
            "risk_factors": risk_factors,
            "overall_risk_score": round(overall_risk, 3),
            "risk_multiplier": round(risk_multiplier, 2),
            "risk_level": _get_risk_level(overall_risk),
            "recommendations": _get_risk_recommendations(risk_factors, crop_type),
            "assessment_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Risk assessment error: {e}")
        # Return default risk assessment
        return {
            "location": location,
            "crop_type": crop_type,
            "overall_risk_score": 0.5,
            "risk_multiplier": 1.0,
            "risk_level": "medium",
            "error": str(e),
            "assessment_date": datetime.utcnow().isoformat()
        }

def _calculate_drought_risk(weather: Dict[str, Any], crop_type: str) -> float:
    """Calculate drought risk based on weather conditions"""
    humidity = weather.get('humidity', 50)
    precipitation = weather.get('precipitation', 0)
    temperature = weather.get('temperature', 25)
    
    # Higher risk for low humidity, no precipitation, high temperature
    risk = 0.0
    if humidity < 30:
        risk += 0.4
    elif humidity < 50:
        risk += 0.2
    
    if precipitation == 0:
        risk += 0.3
    
    if temperature > 35:
        risk += 0.3
    elif temperature > 30:
        risk += 0.1
    
    return min(1.0, risk)

def _calculate_flood_risk(weather: Dict[str, Any], crop_type: str) -> float:
    """Calculate flood risk based on weather conditions"""
    precipitation = weather.get('precipitation', 0)
    humidity = weather.get('humidity', 50)
    
    risk = 0.0
    if precipitation > 10:
        risk += 0.5
    elif precipitation > 5:
        risk += 0.3
    elif precipitation > 2:
        risk += 0.1
    
    if humidity > 90:
        risk += 0.2
    
    return min(1.0, risk)

def _calculate_temperature_risk(weather: Dict[str, Any], crop_type: str) -> float:
    """Calculate temperature-related risk"""
    temperature = weather.get('temperature', 25)
    
    # Crop-specific temperature thresholds
    temp_thresholds = {
        "maize": {"min": 15, "max": 35},
        "wheat": {"min": 10, "max": 30},
        "coffee": {"min": 18, "max": 28},
        "rice": {"min": 20, "max": 35}
    }
    
    thresholds = temp_thresholds.get(crop_type, {"min": 15, "max": 35})
    
    if temperature < thresholds["min"] or temperature > thresholds["max"]:
        return 0.6
    elif temperature < thresholds["min"] + 5 or temperature > thresholds["max"] - 5:
        return 0.3
    
    return 0.0

def _calculate_wind_risk(weather: Dict[str, Any], crop_type: str) -> float:
    """Calculate wind-related risk"""
    wind_speed = weather.get('wind_speed', 0)
    
    if wind_speed > 15:  # Strong winds
        return 0.4
    elif wind_speed > 10:  # Moderate winds
        return 0.2
    
    return 0.0

def _get_risk_level(risk_score: float) -> str:
    """Convert risk score to risk level"""
    if risk_score < 0.3:
        return "low"
    elif risk_score < 0.6:
        return "medium"
    else:
        return "high"

def _get_risk_recommendations(risk_factors: Dict[str, float], crop_type: str) -> List[str]:
    """Generate risk-based recommendations"""
    recommendations = []
    
    if risk_factors["drought_risk"] > 0.5:
        recommendations.append("Consider drought-resistant crop varieties")
        recommendations.append("Implement water conservation measures")
    
    if risk_factors["flood_risk"] > 0.5:
        recommendations.append("Ensure proper drainage systems")
        recommendations.append("Consider flood-resistant crop varieties")
    
    if risk_factors["temperature_risk"] > 0.5:
        recommendations.append("Monitor temperature-sensitive growth stages")
        recommendations.append("Consider shade protection or cooling measures")
    
    if risk_factors["wind_risk"] > 0.5:
        recommendations.append("Install windbreaks or protective barriers")
        recommendations.append("Secure crop support structures")
    
    if not recommendations:
        recommendations.append("Current weather conditions are favorable for farming")
    
    return recommendations