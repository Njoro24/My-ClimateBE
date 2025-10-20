"""
GPT-OSS-20B API Routes for Climate Witness Chain
Enhanced AI reasoning, explainable decisions, and advanced function calling
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.gpt_oss_service import GPTOSSService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class EnhancedMeTTaRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    reasoning_level: str = "detailed"

class ExplainableVerificationRequest(BaseModel):
    event_id: str
    user_id: str
    explanation_level: str = "comprehensive"

class BlockchainAnalysisRequest(BaseModel):
    contract_data: Dict[str, Any]
    analysis_type: str = "full"

class CommunityVerificationRequest(BaseModel):
    verification_data: Dict[str, Any]
    bias_detection: bool = True

class EarlyWarningRequest(BaseModel):
    location_data: Dict[str, Any]
    historical_events: List[Dict[str, Any]] = []
    prediction_horizon: str = "7_days"

class DAOProposalRequest(BaseModel):
    proposal_data: Dict[str, Any]
    analysis_depth: str = "comprehensive"

class FunctionCallRequest(BaseModel):
    function_name: str
    parameters: Dict[str, Any]
    execution_mode: str = "safe"

@router.post("/enhanced-metta-reasoning")
async def enhanced_metta_reasoning(request: EnhancedMeTTaRequest):
    """Enhanced MeTTa reasoning using GPT-OSS-20B for complex symbolic processing"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.enhanced_metta_reasoning(
            query=request.query,
            context=request.context
        )
        
        return {
            "success": True,
            "enhanced_reasoning": result,
            "reasoning_level": request.reasoning_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Enhanced MeTTa reasoning error: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced reasoning failed: {str(e)}")

@router.post("/explainable-verification")
async def explainable_verification_decision(request: ExplainableVerificationRequest):
    """Generate comprehensive explainable AI decision for event verification"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.explainable_verification_decision(
            event_id=request.event_id,
            user_id=request.user_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Verification analysis failed"))
        
        return {
            "success": True,
            "explainable_decision": result,
            "explanation_level": request.explanation_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explainable verification error: {e}")
        raise HTTPException(status_code=500, detail=f"Explainable verification failed: {str(e)}")

@router.post("/blockchain-analysis")
async def blockchain_smart_contract_analysis(request: BlockchainAnalysisRequest):
    """Enhanced reasoning for blockchain smart contract interactions"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.blockchain_smart_contract_reasoning(
            contract_data=request.contract_data
        )
        
        return {
            "success": True,
            "blockchain_analysis": result,
            "analysis_type": request.analysis_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Blockchain analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Blockchain analysis failed: {str(e)}")

@router.post("/community-verification-analysis")
async def community_verification_analysis(request: CommunityVerificationRequest):
    """Advanced community verification analysis with bias detection"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.community_verification_analysis(
            verification_data=request.verification_data
        )
        
        return {
            "success": True,
            "community_analysis": result,
            "bias_detection_enabled": request.bias_detection,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Community verification analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Community analysis failed: {str(e)}")

@router.post("/early-warning-prediction")
async def early_warning_prediction(request: EarlyWarningRequest):
    """Generate early warning predictions using advanced reasoning"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.early_warning_prediction(
            location_data=request.location_data,
            historical_events=request.historical_events
        )
        
        return {
            "success": True,
            "early_warning": result,
            "prediction_horizon": request.prediction_horizon,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Early warning prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Early warning prediction failed: {str(e)}")

@router.post("/dao-governance-analysis")
async def dao_governance_analysis(request: DAOProposalRequest):
    """Analyze DAO governance proposals with sophisticated reasoning"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.dao_governance_analysis(
            proposal_data=request.proposal_data
        )
        
        return {
            "success": True,
            "dao_analysis": result,
            "analysis_depth": request.analysis_depth,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"DAO governance analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"DAO analysis failed: {str(e)}")

@router.post("/function-calling")
async def advanced_function_calling(request: FunctionCallRequest):
    """Advanced function calling for tool use integration"""
    try:
        gpt_service = GPTOSSService()
        result = await gpt_service.function_calling_integration(
            function_name=request.function_name,
            parameters=request.parameters
        )
        
        return {
            "success": True,
            "function_call_result": result,
            "execution_mode": request.execution_mode,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Function calling error: {e}")
        raise HTTPException(status_code=500, detail=f"Function calling failed: {str(e)}")

@router.get("/service-status")
async def get_gpt_oss_service_status():
    """Get GPT-OSS service status and capabilities"""
    try:
        gpt_service = GPTOSSService()
        status = await gpt_service.get_service_status()
        
        return {
            "success": True,
            "service_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Service status error: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback_status": {
                "service_name": "GPT-OSS-20B Climate Witness Service",
                "status": "error",
                "message": "Service temporarily unavailable"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/capabilities")
async def get_gpt_oss_capabilities():
    """Get detailed capabilities of GPT-OSS service"""
    return {
        "success": True,
        "capabilities": {
            "enhanced_metta_reasoning": {
                "description": "Advanced symbolic reasoning with MeTTa integration",
                "features": ["Pattern recognition", "Logical inference", "Confidence scoring"],
                "use_cases": ["Complex climate queries", "Knowledge base analysis", "Decision support"]
            },
            "explainable_verification": {
                "description": "Comprehensive explainable AI for event verification",
                "features": ["Chain-of-thought reasoning", "Bias detection", "Citizen-friendly explanations"],
                "use_cases": ["Event verification", "Trust score analysis", "Decision transparency"]
            },
            "blockchain_analysis": {
                "description": "Smart contract reasoning and optimization",
                "features": ["Security analysis", "Gas optimization", "Risk assessment"],
                "use_cases": ["Contract deployment", "Transaction validation", "Payout processing"]
            },
            "community_verification": {
                "description": "Advanced community consensus analysis",
                "features": ["Bias detection", "Fairness metrics", "Manipulation detection"],
                "use_cases": ["Community voting", "Consensus building", "Trust network analysis"]
            },
            "early_warning": {
                "description": "Predictive climate event analysis",
                "features": ["Risk assessment", "Timeline prediction", "Uncertainty quantification"],
                "use_cases": ["Disaster preparedness", "Insurance planning", "Agricultural guidance"]
            },
            "dao_governance": {
                "description": "DAO proposal analysis and governance support",
                "features": ["Impact assessment", "Feasibility analysis", "Stakeholder analysis"],
                "use_cases": ["Proposal evaluation", "Governance decisions", "Community planning"]
            },
            "function_calling": {
                "description": "Advanced tool use and function integration",
                "features": ["Safe execution", "Parameter validation", "Result analysis"],
                "use_cases": ["Automated workflows", "System integration", "Process automation"]
            }
        },
        "model_info": {
            "name": "gpt-oss-20b",
            "provider": "OpenAI",
            "parameters": "20.9B total, 3.6B active/token",
            "context_window": "131k tokens",
            "features": ["Chain-of-thought", "Function calling", "Structured outputs"]
        },
        "integration": {
            "metta_service": "Full integration with existing MeTTa knowledge base",
            "blockchain_service": "Enhanced smart contract analysis",
            "database": "Direct access to climate data",
            "apis": "RESTful API endpoints for all capabilities"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/test-integration")
async def test_gpt_oss_integration():
    """Test GPT-OSS integration with existing services"""
    try:
        gpt_service = GPTOSSService()
        
        # Test MeTTa integration
        metta_test = await gpt_service.enhanced_metta_reasoning(
            query="(test-query integration)",
            context={"test": True}
        )
        
        # Test service status
        status = await gpt_service.get_service_status()
        
        return {
            "success": True,
            "integration_tests": {
                "metta_integration": {
                    "status": "success" if metta_test.get("success") else "failed",
                    "details": metta_test
                },
                "service_status": {
                    "status": "success" if status.get("api_connected") else "failed",
                    "details": status
                }
            },
            "overall_status": "healthy" if metta_test.get("success") and status.get("api_connected") else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Integration test error: {e}")
        return {
            "success": False,
            "error": str(e),
            "integration_tests": {
                "status": "failed",
                "error_details": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/example-requests")
async def get_example_requests():
    """Get example requests for GPT-OSS endpoints"""
    return {
        "success": True,
        "examples": {
            "enhanced_metta_reasoning": {
                "endpoint": "/api/gpt-oss/enhanced-metta-reasoning",
                "method": "POST",
                "example_request": {
                    "query": "(verify-event drought_001 user_123)",
                    "context": {
                        "event_type": "drought",
                        "location": "Kenya",
                        "severity": "high"
                    },
                    "reasoning_level": "detailed"
                }
            },
            "explainable_verification": {
                "endpoint": "/api/gpt-oss/explainable-verification",
                "method": "POST",
                "example_request": {
                    "event_id": "evt_123456",
                    "user_id": "usr_789012",
                    "explanation_level": "comprehensive"
                }
            },
            "blockchain_analysis": {
                "endpoint": "/api/gpt-oss/blockchain-analysis",
                "method": "POST",
                "example_request": {
                    "contract_data": {
                        "function": "processPayout",
                        "parameters": {"eventId": "0x123", "amount": "0.01"},
                        "gas_estimate": 150000
                    },
                    "analysis_type": "full"
                }
            },
            "early_warning_prediction": {
                "endpoint": "/api/gpt-oss/early-warning-prediction",
                "method": "POST",
                "example_request": {
                    "location_data": {
                        "latitude": -1.2921,
                        "longitude": 36.8219,
                        "region": "Nairobi, Kenya"
                    },
                    "historical_events": [],
                    "prediction_horizon": "7_days"
                }
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }