"""
Insurance API Routes
Handles micro-insurance endpoints for the Climate Witness DAO
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.database.crud import *
from app.services.insurance_service import SimpleInsuranceService

router = APIRouter()

# Global insurance service instance
insurance_service = SimpleInsuranceService()

# Request/Response Models
class CreatePolicyRequest(BaseModel):
    user_id: str

class CheckEligibilityRequest(BaseModel):
    user_id: str
    event_id: str

class ProcessPayoutRequest(BaseModel):
    user_id: str
    event_id: str

@router.post("/create-policy")
async def create_insurance_policy(
    request: CreatePolicyRequest,
    crud = None
):
    """Create a simple insurance policy for a user"""
    try:
        result = await insurance_service.create_simple_policy(request.user_id)
        
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Policy creation failed'))
        
        return {
            "message": "Insurance policy created successfully",
            "policy": result['policy'],
            "coverage_amount": result['policy']['coverage_amount'],
            "premium_paid": result['policy']['premium_paid']
        }
        
    except HTTPException:
        raise
    except Exception as e:
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