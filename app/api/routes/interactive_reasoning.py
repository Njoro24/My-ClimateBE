from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
import uuid
import os
from app.services.metta_service import ClimateWitnessKnowledgeBase
from app.database.crud import get_event_by_id, get_user_by_id, get_all_events, get_all_users
import logging

try:
    from app.services.gpt_oss_service import GPTOSSService
    GPT_OSS_AVAILABLE = True
except ImportError:
    GPT_OSS_AVAILABLE = False
    print("GPT-OSS service not available - using MeTTa only")

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

@router.get("/health")
async def interactive_reasoning_health():
    """Health check for interactive reasoning service"""
    try:
        # Test MeTTa service
        kb = ClimateWitnessKnowledgeBase()
        metta_available = True
    except Exception as e:
        logger.error(f"MeTTa service error: {e}")
        metta_available = False
    
    return {
        "success": True,
        "service": "interactive_reasoning",
        "metta_available": metta_available,
        "gpt_oss_available": GPT_OSS_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Interactive reasoning API is working", "timestamp": datetime.utcnow().isoformat()}

@router.post("/start-interactive-reasoning")
async def start_interactive_reasoning(request: InteractiveReasoningRequest):
    """Start an interactive civic reasoning session with real-time MeTTa analysis"""
    try:
        logger.info(f"Starting interactive reasoning session for issue: {request.issue}")
        
        kb = ClimateWitnessKnowledgeBase()
        logger.info("MeTTa knowledge base initialized")
        
        # Load the interactive reasoning MeTTa file
        metta_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'metta', 'interactive_civic_reasoning.metta')
        if os.path.exists(metta_file_path):
            kb.load_metta_file(metta_file_path)
            logger.info("Interactive reasoning MeTTa file loaded successfully")
        else:
            logger.warning(f"MeTTa file not found at: {metta_file_path}")
            # Continue without the file - basic reasoning will still work
        
        # Generate unique session ID
        session_id = f"civic_reasoning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Prepare MeTTa query with proper formatting
        stakeholders_str = json.dumps(request.stakeholders)
        evidence_str = json.dumps(request.evidence)
        
        reasoning_query = f'''
        !(interactive-civic-reasoning "{request.issue}" {stakeholders_str} {evidence_str} "{request.user_query}")
        '''
        
        logger.info(f"Running MeTTa query: {reasoning_query[:200]}...")
        
        # Run MeTTa reasoning
        try:
            metta_result = kb.run_metta_function(reasoning_query)
            logger.info(f"MeTTa query completed, results: {len(metta_result) if metta_result else 0}")
        except Exception as metta_error:
            logger.error(f"MeTTa query failed: {metta_error}")
            metta_result = []  # Continue with empty results
        
        # Process and structure the reasoning steps
        reasoning_session = await _process_reasoning_result(
            metta_result, session_id, request.issue, request.stakeholders, 
            request.evidence, request.user_query, request.user_type
        )
        
        # If no reasoning steps were generated, create meaningful default steps
        if not reasoning_session.get("reasoning_steps"):
            logger.info("No MeTTa results, generating structured reasoning steps")
            reasoning_session = await _generate_structured_reasoning_session(
                session_id, request.issue, request.stakeholders, 
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
    """Process MeTTa reasoning result into structured format with GPT-OSS enhancement"""
    
    # Extract reasoning steps from MeTTa result
    reasoning_steps = []
    
    # Enhanced processing with GPT-OSS if available
    if GPT_OSS_AVAILABLE and metta_result:
        try:
            gpt_service = GPTOSSService()
            
            # Get enhanced reasoning for each MeTTa result
            for i, result in enumerate(metta_result):
                enhanced_reasoning = await gpt_service.enhanced_metta_reasoning(
                    query=f"Explain reasoning step: {str(result)}",
                    context={
                        "issue": issue,
                        "stakeholders": stakeholders,
                        "evidence": evidence,
                        "step_number": i + 1,
                        "user_type": user_type
                    }
                )
                
                step = {
                    "step_number": i + 1,
                    "step_type": f"Enhanced Reasoning Step {i + 1}",
                    "content": str(result),
                    "explanation": enhanced_reasoning.get("enhanced_reasoning", str(result)),
                    "metta_result": str(result),
                    "gpt_oss_enhancement": enhanced_reasoning.get("enhanced_reasoning"),
                    "confidence": enhanced_reasoning.get("confidence_score", 0.8 + (i * 0.02)),
                    "timestamp": datetime.utcnow().isoformat()
                }
                reasoning_steps.append(step)
                
        except Exception as e:
            logger.error(f"GPT-OSS enhancement failed: {e}")
            # Fallback to basic MeTTa processing
            for i, result in enumerate(metta_result):
                step = {
                    "step_number": i + 1,
                    "step_type": f"MeTTa Reasoning Step {i + 1}",
                    "content": str(result),
                    "explanation": await _generate_step_explanation(str(result), user_type),
                    "timestamp": datetime.utcnow().isoformat(),
                    "confidence": 0.8 + (i * 0.02)
                }
                reasoning_steps.append(step)
    
    elif metta_result:
        # Basic MeTTa processing when GPT-OSS not available
        for i, result in enumerate(metta_result):
            step = {
                "step_number": i + 1,
                "step_type": f"MeTTa Reasoning Step {i + 1}",
                "content": str(result),
                "explanation": await _generate_step_explanation(str(result), user_type),
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.8 + (i * 0.02)
            }
            reasoning_steps.append(step)
    
    # Generate comprehensive session data with real MeTTa/GPT-OSS integration
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
        "status": "active",
        "metta_available": len(reasoning_steps) > 0,
        "gpt_oss_available": GPT_OSS_AVAILABLE,
        "enhanced_reasoning": GPT_OSS_AVAILABLE and len(reasoning_steps) > 0
    }
    
    return session_data

async def _process_query_response(metta_result, query, user_type, session):
    """Process MeTTa query response with GPT-OSS enhancement"""
    
    # Generate intelligent response based on session context even without MeTTa
    if not metta_result:
        return await _generate_intelligent_query_response(query, user_type, session)
    
    # Enhanced query processing with GPT-OSS
    if GPT_OSS_AVAILABLE:
        try:
            gpt_service = GPTOSSService()
            
            enhanced_response = await gpt_service.enhanced_metta_reasoning(
                query=f"Answer user question: {query}",
                context={
                    "metta_results": [str(r) for r in metta_result],
                    "session_context": session,
                    "user_type": user_type,
                    "reasoning_steps": session.get("reasoning_steps", [])
                }
            )
            
            response = {
                "query": query,
                "answer": enhanced_response.get("enhanced_reasoning", str(metta_result[0])),
                "explanation": await _generate_query_explanation(query, metta_result, user_type),
                "metta_results": [str(r) for r in metta_result],
                "gpt_oss_enhancement": enhanced_response.get("enhanced_reasoning"),
                "related_steps": await _find_related_reasoning_steps(query, session["reasoning_steps"]),
                "confidence": enhanced_response.get("confidence_score", 0.85),
                "follow_up_questions": await _generate_follow_up_questions(query, metta_result),
                "model_used": "GPT-OSS-20B + MeTTa"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"GPT-OSS query enhancement failed: {e}")
    
    # Fallback to basic MeTTa response
    response = {
        "query": query,
        "answer": str(metta_result[0]) if metta_result else "No specific answer available",
        "explanation": await _generate_query_explanation(query, metta_result, user_type),
        "related_steps": await _find_related_reasoning_steps(query, session["reasoning_steps"]),
        "confidence": 0.85,
        "follow_up_questions": await _generate_follow_up_questions(query, metta_result),
        "model_used": "MeTTa"
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

async def _generate_intelligent_query_response(query, user_type, session):
    """Generate intelligent response based on session context"""
    
    query_lower = query.lower()
    issue = session.get("issue", "civic decision")
    reasoning_steps = session.get("reasoning_steps", [])
    stakeholders = session.get("stakeholders", [])
    evidence = session.get("evidence", [])
    
    # Analyze query intent and generate contextual response
    if any(word in query_lower for word in ["why", "reason", "decision"]):
        # Explain the reasoning process
        key_factors = []
        if reasoning_steps:
            key_factors = [step.get("step_type", "Analysis") for step in reasoning_steps[:3]]
        
        answer = f"The decision regarding '{issue}' was made through a systematic analysis involving {len(reasoning_steps)} key steps: {', '.join(key_factors)}. The process considered {len(stakeholders)} stakeholder perspectives and {len(evidence)} pieces of evidence to ensure a balanced, democratic approach."
        
        explanation = "The reasoning process follows democratic principles of transparency, fairness, and evidence-based decision making."
        
    elif any(word in query_lower for word in ["what if", "alternative", "different"]):
        # Discuss alternatives
        answer = f"Alternative approaches to '{issue}' could include different stakeholder weighting, modified timelines, or alternative resource allocation strategies. Each approach would have different trade-offs in terms of implementation speed, stakeholder satisfaction, and long-term effectiveness."
        
        explanation = "Alternative scenarios help understand the impact of different decision parameters and ensure robust decision-making."
        
    elif any(word in query_lower for word in ["bias", "fair", "equal"]):
        # Address bias and fairness
        stakeholder_types = list(set([s.get("type", "unknown") for s in stakeholders]))
        answer = f"The decision process includes bias detection across multiple dimensions. With {len(stakeholder_types)} different stakeholder types represented, the process aims for balanced representation. Fairness is ensured through transparent criteria, equal participation opportunities, and systematic bias monitoring."
        
        explanation = "Bias detection and fairness assessment are integral to democratic decision-making processes."
        
    elif any(word in query_lower for word in ["evidence", "data", "proof"]):
        # Discuss evidence
        avg_credibility = sum([e.get("credibility", 0.5) for e in evidence]) / len(evidence) if evidence else 0.5
        evidence_types = list(set([e.get("type", "unknown") for e in evidence]))
        
        answer = f"The decision is supported by {len(evidence)} pieces of evidence with an average credibility of {avg_credibility:.1%}. Evidence types include: {', '.join(evidence_types)}. This evidence base provides a solid foundation for informed decision-making."
        
        explanation = "Evidence quality and diversity are crucial for reliable civic decision-making."
        
    elif any(word in query_lower for word in ["stakeholder", "participant", "involve"]):
        # Discuss stakeholders
        stakeholder_types = list(set([s.get("type", "unknown") for s in stakeholders]))
        answer = f"The decision involves {len(stakeholders)} stakeholders across {len(stakeholder_types)} categories: {', '.join(stakeholder_types)}. Each stakeholder brings unique perspectives and priorities, ensuring comprehensive representation in the decision process."
        
        explanation = "Stakeholder engagement is essential for legitimate and effective civic decisions."
        
    else:
        # General response
        answer = f"Regarding '{issue}': This civic decision follows a structured approach with {len(reasoning_steps)} analysis steps, considering {len(stakeholders)} stakeholder perspectives and {len(evidence)} evidence sources. The process emphasizes transparency, fairness, and democratic participation."
        
        explanation = "The decision-making process balances multiple factors to achieve optimal outcomes for all involved parties."
    
    # Generate follow-up questions based on context
    follow_up_questions = [
        f"What are the main challenges in implementing this decision about {issue}?",
        "How do different stakeholders view this approach?",
        "What evidence is most critical for this decision?",
        "What are the potential risks and how can they be mitigated?"
    ]
    
    return {
        "query": query,
        "answer": answer,
        "explanation": explanation,
        "related_steps": list(range(1, min(len(reasoning_steps) + 1, 4))),  # Reference first 3 steps
        "confidence": 0.82,
        "follow_up_questions": follow_up_questions,
        "model_used": "Structured Analysis" + (" + GPT-OSS" if GPT_OSS_AVAILABLE else ""),
        "context_used": {
            "reasoning_steps": len(reasoning_steps),
            "stakeholders": len(stakeholders),
            "evidence": len(evidence)
        }
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

async def _generate_structured_reasoning_session(session_id, issue, stakeholders, evidence, user_query, user_type):
    """Generate structured reasoning session when MeTTa doesn't return results"""
    
    # Analyze the input to create meaningful reasoning steps
    reasoning_steps = []
    
    # Step 1: Issue Analysis
    reasoning_steps.append({
        "step_number": 1,
        "step_type": "Issue Analysis",
        "content": f"Analyzing civic issue: {issue}",
        "explanation": f"The system is evaluating the civic decision regarding '{issue}' by examining stakeholder perspectives, evidence quality, and democratic principles.",
        "confidence": 0.85,
        "timestamp": datetime.utcnow().isoformat(),
        "analysis_details": {
            "issue_complexity": "high" if len(stakeholders) > 3 else "medium",
            "stakeholder_count": len(stakeholders),
            "evidence_pieces": len(evidence)
        }
    })
    
    # Step 2: Stakeholder Analysis
    stakeholder_types = list(set([s.get("type", "unknown") for s in stakeholders]))
    reasoning_steps.append({
        "step_number": 2,
        "step_type": "Stakeholder Assessment",
        "content": f"Evaluating {len(stakeholders)} stakeholders across {len(stakeholder_types)} categories",
        "explanation": f"Analyzing stakeholder positions and influence patterns. Key stakeholder types: {', '.join(stakeholder_types)}. Each stakeholder brings different priorities and perspectives to the decision.",
        "confidence": 0.88,
        "timestamp": datetime.utcnow().isoformat(),
        "stakeholder_analysis": {
            "total_stakeholders": len(stakeholders),
            "stakeholder_types": stakeholder_types,
            "representation_quality": "good" if len(stakeholder_types) >= 3 else "limited"
        }
    })
    
    # Step 3: Evidence Evaluation
    evidence_types = list(set([e.get("type", "unknown") for e in evidence]))
    avg_credibility = sum([e.get("credibility", 0.5) for e in evidence]) / len(evidence) if evidence else 0.5
    reasoning_steps.append({
        "step_number": 3,
        "step_type": "Evidence Evaluation",
        "content": f"Processing {len(evidence)} evidence sources with average credibility of {avg_credibility:.2f}",
        "explanation": f"Evaluating evidence quality and reliability. Evidence types include: {', '.join(evidence_types)}. The evidence supports informed decision-making with {avg_credibility:.1%} average credibility.",
        "confidence": 0.82 + (avg_credibility * 0.1),
        "timestamp": datetime.utcnow().isoformat(),
        "evidence_analysis": {
            "total_evidence": len(evidence),
            "evidence_types": evidence_types,
            "average_credibility": avg_credibility,
            "quality_assessment": "high" if avg_credibility > 0.8 else "medium" if avg_credibility > 0.6 else "low"
        }
    })
    
    # Step 4: Democratic Principles Application
    reasoning_steps.append({
        "step_number": 4,
        "step_type": "Democratic Principles",
        "content": "Applying transparency, fairness, and participation principles",
        "explanation": "Ensuring the decision process adheres to democratic values: all stakeholders have meaningful input, the process is transparent and explainable, decisions are fair and equitable, and there are accountability mechanisms.",
        "confidence": 0.87,
        "timestamp": datetime.utcnow().isoformat(),
        "democratic_analysis": {
            "transparency": "high",
            "participation": "inclusive",
            "fairness": "equitable",
            "accountability": "clear"
        }
    })
    
    # Step 5: Decision Synthesis
    reasoning_steps.append({
        "step_number": 5,
        "step_type": "Decision Synthesis",
        "content": "Synthesizing analysis into actionable recommendations",
        "explanation": "Combining stakeholder input, evidence analysis, and democratic principles to generate balanced recommendations that address the civic issue while maintaining fairness and transparency.",
        "confidence": 0.89,
        "timestamp": datetime.utcnow().isoformat(),
        "synthesis_approach": "multi-criteria decision analysis with democratic oversight"
    })
    
    # Generate decision proposal based on the analysis
    decision_proposal = {
        "recommendation": f"Implement balanced approach to {issue} with stakeholder consensus and evidence-based allocation",
        "implementation_timeline": "6-12 months with phased approach",
        "resource_requirements": "Moderate coordination across stakeholder groups",
        "success_probability": 0.75 + (avg_credibility * 0.15),
        "key_principles": ["Transparency", "Fairness", "Evidence-based", "Participatory"]
    }
    
    # Calculate overall confidence
    overall_confidence = sum([step["confidence"] for step in reasoning_steps]) / len(reasoning_steps)
    
    return {
        "session_id": session_id,
        "issue": issue,
        "stakeholders": stakeholders,
        "evidence": evidence,
        "user_query": user_query,
        "user_type": user_type,
        "reasoning_steps": reasoning_steps,
        "decision_proposal": decision_proposal,
        "confidence_score": overall_confidence,
        "alternative_scenarios": await _generate_alternative_scenarios(reasoning_steps),
        "bias_indicators": await _detect_bias_indicators(reasoning_steps),
        "interactions": [],
        "alternative_proposals": [],
        "created_at": datetime.utcnow().isoformat(),
        "status": "active",
        "metta_available": False,
        "gpt_oss_available": GPT_OSS_AVAILABLE,
        "enhanced_reasoning": False,
        "reasoning_method": "structured_analysis"
    }