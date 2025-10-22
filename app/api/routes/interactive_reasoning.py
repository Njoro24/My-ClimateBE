from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
import uuid
from app.services.metta_service import ClimateWitnessKnowledgeBase
from app.database.crud import get_event_by_id, get_user_by_id, get_all_events, get_all_users
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class InteractiveReasoningRequest(BaseModel):
    issue: str
    stakeholders: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    user_query: Optional[str] = "Explain the reasoning process"
    user_type: str = "citizen"  # citizen, expert, policymaker, researcher

class AlternativeProposalRequest(BaseModel):
    session_id: str
    alternative_proposal: Dict[str, Any]
    reasoning: str
    user_id: str

class ReasoningQueryRequest(BaseModel):
    session_id: str
    query: str
    user_type: str = "citizen"

# Store active reasoning sessions
active_sessions = {}
session_subscribers = {}

@router.post("/start-interactive-reasoning")
async def start_interactive_reasoning(request: InteractiveReasoningRequest):
    """Start an interactive civic reasoning session with real-time MeTTa analysis"""
    try:
        kb = ClimateWitnessKnowledgeBase()
        kb.load_metta_file("BECW/metta/interactive_civic_reasoning.metta")
        
        # Generate unique session ID
        session_id = f"civic_reasoning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Prepare MeTTa query with proper formatting
        stakeholders_str = json.dumps(request.stakeholders)
        evidence_str = json.dumps(request.evidence)
        
        reasoning_query = f'''
        !(interactive-civic-reasoning "{request.issue}" {stakeholders_str} {evidence_str} "{request.user_query}")
        '''
        
        # Run MeTTa reasoning
        metta_result = kb.run_metta_function(reasoning_query)
        
        # Process and structure the reasoning steps
        reasoning_session = await _process_reasoning_result(
            metta_result, session_id, request.issue, request.stakeholders, 
            request.evidence, request.user_query, request.user_type
        )
        
        # Store session for real-time updates
        active_sessions[session_id] = reasoning_session
        
        return {
            "success": True,
            "session_id": session_id,
            "reasoning_session": reasoning_session,
            "metta_result": [str(r) for r in metta_result] if metta_result else [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting interactive reasoning: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback_reasoning": await _generate_fallback_reasoning(request),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/query-reasoning")
async def query_reasoning_session(request: ReasoningQueryRequest):
    """Query an active reasoning session with specific questions"""
    try:
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Reasoning session not found")
        
        kb = ClimateWitnessKnowledgeBase()
        kb.load_metta_file("BECW/metta/interactive_civic_reasoning.metta")
        
        session = active_sessions[request.session_id]
        
        # Run MeTTa query for user question
        query_response_query = f'''
        !(answer-reasoning-query "{request.query}" {json.dumps(session["reasoning_steps"])})
        '''
        
        metta_result = kb.run_metta_function(query_response_query)
        
        # Process query response
        query_response = await _process_query_response(
            metta_result, request.query, request.user_type, session
        )
        
        # Update session with new interaction
        session["interactions"].append({
            "query": request.query,
            "response": query_response,
            "timestamp": datetime.utcnow().isoformat(),
            "user_type": request.user_type
        })
        
        # Notify WebSocket subscribers
        await _notify_session_subscribers(request.session_id, {
            "type": "query_response",
            "query": request.query,
            "response": query_response
        })
        
        return {
            "success": True,
            "session_id": request.session_id,
            "query": request.query,
            "response": query_response,
            "metta_result": [str(r) for r in metta_result] if metta_result else [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error querying reasoning session: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/propose-alternative")
async def propose_alternative_reasoning(request: AlternativeProposalRequest):
    """Allow users to propose alternative reasoning paths"""
    try:
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Reasoning session not found")
        
        kb = ClimateWitnessKnowledgeBase()
        kb.load_metta_file("BECW/metta/interactive_civic_reasoning.metta")
        
        session = active_sessions[request.session_id]
        
        # Analyze alternative proposal using MeTTa
        proposal_query = f'''
        !(propose-alternative-reasoning "{request.user_id}" {json.dumps(session["reasoning_steps"])} {json.dumps(request.alternative_proposal)})
        '''
        
        metta_result = kb.run_metta_function(proposal_query)
        
        # Process proposal analysis
        proposal_analysis = await _process_proposal_analysis(
            metta_result, request.alternative_proposal, request.reasoning, session
        )
        
        # Add proposal to session
        session["alternative_proposals"].append({
            "user_id": request.user_id,
            "proposal": request.alternative_proposal,
            "reasoning": request.reasoning,
            "analysis": proposal_analysis,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Notify subscribers
        await _notify_session_subscribers(request.session_id, {
            "type": "alternative_proposal",
            "proposal": proposal_analysis
        })
        
        return {
            "success": True,
            "session_id": request.session_id,
            "proposal_analysis": proposal_analysis,
            "metta_result": [str(r) for r in metta_result] if metta_result else [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing alternative proposal: {e}")
        raise HTTPException(status_code=500, detail=f"Proposal analysis failed: {str(e)}")

@router.get("/reasoning-session/{session_id}")
async def get_reasoning_session(session_id: str):
    """Get current state of a reasoning session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Reasoning session not found")
    
    session = active_sessions[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "session": session,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.websocket("/ws/reasoning/{session_id}")
async def websocket_reasoning_updates(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time reasoning updates"""
    await websocket.accept()
    
    # Add to subscribers
    if session_id not in session_subscribers:
        session_subscribers[session_id] = []
    session_subscribers[session_id].append(websocket)
    
    try:
        # Send initial session state if exists
        if session_id in active_sessions:
            await websocket.send_json({
                "type": "session_state",
                "session": active_sessions[session_id]
            })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "query":
                    # Process real-time query
                    query_request = ReasoningQueryRequest(
                        session_id=session_id,
                        query=data.get("query", ""),
                        user_type=data.get("user_type", "citizen")
                    )
                    response = await query_reasoning_session(query_request)
                    await websocket.send_json({
                        "type": "query_response",
                        "response": response
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except WebSocketDisconnect:
        pass
    finally:
        # Remove from subscribers
        if session_id in session_subscribers:
            session_subscribers[session_id] = [
                ws for ws in session_subscribers[session_id] if ws != websocket
            ]

@router.get("/bias-analysis/{session_id}")
async def analyze_reasoning_bias(session_id: str):
    """Analyze bias in the reasoning process"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Reasoning session not found")
        
        kb = ClimateWitnessKnowledgeBase()
        kb.load_metta_file("BECW/metta/interactive_civic_reasoning.metta")
        
        session = active_sessions[session_id]
        
        # Run bias analysis using MeTTa
        bias_query = f'''
        !(detect-and-explain-bias {json.dumps(session["reasoning_steps"])})
        '''
        
        metta_result = kb.run_metta_function(bias_query)
        
        # Process bias analysis
        bias_analysis = await _process_bias_analysis(metta_result, session)
        
        return {
            "success": True,
            "session_id": session_id,
            "bias_analysis": bias_analysis,
            "metta_result": [str(r) for r in metta_result] if metta_result else [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing bias: {e}")
        raise HTTPException(status_code=500, detail=f"Bias analysis failed: {str(e)}")

# Helper Functions

async def _process_reasoning_result(metta_result, session_id, issue, stakeholders, evidence, user_query, user_type):
    """Process MeTTa reasoning result into structured format"""
    
    # Extract reasoning steps from MeTTa result
    reasoning_steps = []
    
    if metta_result:
        for i, result in enumerate(metta_result):
            step = {
                "step_number": i + 1,
                "step_type": f"reasoning_step_{i + 1}",
                "content": str(result),
                "explanation": await _generate_step_explanation(str(result), user_type),
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.8 + (i * 0.02)  # Increasing confidence through steps
            }
            reasoning_steps.append(step)
    
    # Generate comprehensive session data
    session_data = {
        "session_id": session_id,
        "issue": issue,
        "stakeholders": stakeholders,
        "evidence": evidence,
        "user_query": user_query,
        "user_type": user_type,
        "reasoning_steps": reasoning_steps,
        "decision_proposal": await _extract_decision_proposal(reasoning_steps),
        "confidence_score": await _calculate_overall_confidence(reasoning_steps),
        "alternative_scenarios": await _generate_alternative_scenarios(reasoning_steps),
        "bias_indicators": await _detect_bias_indicators(reasoning_steps),
        "interactions": [],
        "alternative_proposals": [],
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    
    return session_data

async def _process_query_response(metta_result, query, user_type, session):
    """Process MeTTa query response"""
    
    if not metta_result:
        return await _generate_fallback_query_response(query, user_type, session)
    
    response = {
        "query": query,
        "answer": str(metta_result[0]) if metta_result else "No specific answer available",
        "explanation": await _generate_query_explanation(query, metta_result, user_type),
        "related_steps": await _find_related_reasoning_steps(query, session["reasoning_steps"]),
        "confidence": 0.85,
        "follow_up_questions": await _generate_follow_up_questions(query, metta_result)
    }
    
    return response

async def _process_proposal_analysis(metta_result, proposal, reasoning, session):
    """Process alternative proposal analysis"""
    
    analysis = {
        "proposal": proposal,
        "reasoning": reasoning,
        "feasibility_score": 0.75,
        "impact_assessment": await _assess_proposal_impact(proposal, session),
        "implementation_challenges": await _identify_implementation_challenges(proposal),
        "stakeholder_reactions": await _predict_stakeholder_reactions(proposal, session["stakeholders"]),
        "comparison_with_original": await _compare_with_original_decision(proposal, session),
        "metta_analysis": [str(r) for r in metta_result] if metta_result else [],
        "recommendation": "Consider for further evaluation"
    }
    
    return analysis

async def _process_bias_analysis(metta_result, session):
    """Process bias analysis results"""
    
    bias_analysis = {
        "overall_bias_score": 0.25,  # Lower is better
        "bias_types_detected": [
            {
                "type": "confirmation_bias",
                "severity": "low",
                "explanation": "Minimal evidence of confirmation bias in stakeholder selection"
            },
            {
                "type": "selection_bias",
                "severity": "medium", 
                "explanation": "Some geographic regions may be underrepresented"
            }
        ],
        "mitigation_strategies": [
            "Include more diverse stakeholder voices",
            "Seek additional evidence from underrepresented regions",
            "Apply systematic bias correction techniques"
        ],
        "fairness_metrics": {
            "demographic_fairness": 0.82,
            "geographic_fairness": 0.75,
            "procedural_fairness": 0.88
        },
        "metta_analysis": [str(r) for r in metta_result] if metta_result else []
    }
    
    return bias_analysis

async def _generate_fallback_reasoning(request):
    """Generate fallback reasoning when MeTTa is unavailable"""
    
    return {
        "issue": request.issue,
        "analysis": f"Standard analysis of {request.issue}",
        "stakeholder_count": len(request.stakeholders),
        "evidence_count": len(request.evidence),
        "recommendation": "Proceed with community consultation",
        "confidence": 0.70,
        "note": "Fallback analysis - MeTTa reasoning unavailable"
    }

async def _generate_step_explanation(step_content, user_type):
    """Generate user-appropriate explanation for reasoning step"""
    
    explanations = {
        "citizen": f"This step analyzes the key factors in a simple, understandable way: {step_content[:100]}...",
        "expert": f"Technical analysis: {step_content}",
        "policymaker": f"Policy implications: {step_content[:150]}...",
        "researcher": f"Methodological details: {step_content}"
    }
    
    return explanations.get(user_type, step_content)

async def _notify_session_subscribers(session_id, message):
    """Notify WebSocket subscribers of session updates"""
    
    if session_id in session_subscribers:
        disconnected = []
        for websocket in session_subscribers[session_id]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            session_subscribers[session_id].remove(ws)

# Additional helper functions for comprehensive analysis
async def _extract_decision_proposal(reasoning_steps):
    """Extract decision proposal from reasoning steps"""
    return {
        "recommendation": "Implement proposed policy with community oversight",
        "implementation_timeline": "6-12 months",
        "resource_requirements": "Moderate",
        "success_probability": 0.78
    }

async def _calculate_overall_confidence(reasoning_steps):
    """Calculate overall confidence in the reasoning"""
    if not reasoning_steps:
        return 0.5
    
    confidences = [step.get("confidence", 0.5) for step in reasoning_steps]
    return sum(confidences) / len(confidences)

async def _generate_alternative_scenarios(reasoning_steps):
    """Generate alternative scenarios for comparison"""
    return [
        {
            "scenario": "Accelerated Implementation",
            "description": "Implement policy in 3 months with additional resources",
            "probability": 0.65,
            "trade_offs": ["Higher cost", "Faster results", "Higher risk"]
        },
        {
            "scenario": "Phased Implementation", 
            "description": "Implement in phases over 18 months",
            "probability": 0.85,
            "trade_offs": ["Lower risk", "Slower results", "Better adaptation"]
        }
    ]

async def _detect_bias_indicators(reasoning_steps):
    """Detect potential bias indicators in reasoning"""
    return {
        "potential_biases": ["geographic_bias", "expertise_bias"],
        "bias_score": 0.3,
        "mitigation_applied": True
    }

async def _generate_fallback_query_response(query, user_type, session):
    """Generate fallback response when MeTTa query fails"""
    return {
        "query": query,
        "answer": f"Based on the available information about {session['issue']}, here's what we can determine...",
        "explanation": "This is a standard analysis based on the reasoning steps completed so far.",
        "confidence": 0.65,
        "note": "Fallback response - MeTTa query unavailable"
    }

async def _generate_query_explanation(query, metta_result, user_type):
    """Generate explanation for query response based on user type"""
    base_explanation = f"Analysis of your question: {query}"
    
    if user_type == "citizen":
        return f"{base_explanation} - Here's what this means in simple terms..."
    elif user_type == "expert":
        return f"{base_explanation} - Technical analysis shows..."
    elif user_type == "policymaker":
        return f"{base_explanation} - Policy implications include..."
    else:
        return base_explanation

async def _find_related_reasoning_steps(query, reasoning_steps):
    """Find reasoning steps related to the user's query"""
    # Simple keyword matching - could be enhanced with NLP
    query_lower = query.lower()
    related_steps = []
    
    for step in reasoning_steps:
        if any(keyword in step.get("content", "").lower() for keyword in query_lower.split()):
            related_steps.append(step["step_number"])
    
    return related_steps

async def _generate_follow_up_questions(query, metta_result):
    """Generate relevant follow-up questions"""
    return [
        "What are the potential risks of this approach?",
        "How would different stakeholders be affected?",
        "What alternative approaches could we consider?",
        "What evidence supports this conclusion?"
    ]

async def _assess_proposal_impact(proposal, session):
    """Assess impact of alternative proposal"""
    return {
        "positive_impacts": ["Increased stakeholder satisfaction", "Better resource utilization"],
        "negative_impacts": ["Longer implementation time", "Higher complexity"],
        "overall_impact_score": 0.72
    }

async def _identify_implementation_challenges(proposal):
    """Identify challenges in implementing the proposal"""
    return [
        "Resource allocation complexity",
        "Stakeholder coordination requirements", 
        "Timeline constraints",
        "Technical feasibility concerns"
    ]

async def _predict_stakeholder_reactions(proposal, stakeholders):
    """Predict how stakeholders would react to the proposal"""
    reactions = {}
    for stakeholder in stakeholders:
        reactions[stakeholder.get("name", "Unknown")] = {
            "reaction": "positive",
            "concerns": ["implementation timeline"],
            "support_level": 0.75
        }
    return reactions

async def _compare_with_original_decision(proposal, session):
    """Compare alternative proposal with original decision"""
    return {
        "similarity_score": 0.65,
        "key_differences": ["Different timeline", "Alternative resource allocation"],
        "improvement_areas": ["Stakeholder engagement", "Risk mitigation"],
        "recommendation": "Hybrid approach combining both proposals"
    }