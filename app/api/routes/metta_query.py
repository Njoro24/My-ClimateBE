"""
MeTTa Natural Language Query API Routes for Climate Witness Chain
Handles natural language queries and converts them to MeTTa functions
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.metta_service import ClimateWitnessKnowledgeBase
from app.database.database import get_db
import json
from datetime import datetime
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class NaturalLanguageQueryRequest(BaseModel):
    query: str
    user_location: Optional[str] = None
    user_trust_score: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class MettaFunctionRequest(BaseModel):
    metta_function: str
    parameters: Optional[Dict[str, Any]] = None

@router.post("/natural-language-query")
async def process_natural_language_query(request: NaturalLanguageQueryRequest):
    """
    Process natural language queries and convert them to MeTTa functions
    """
    try:
        start_time = datetime.now()
        
        # Get MeTTa knowledge base
        kb = ClimateWitnessKnowledgeBase()
        
        # Parse the natural language query
        parsed_query = _parse_natural_language_query(request.query)
        
        # Generate MeTTa function based on query type
        metta_function = _generate_metta_function(parsed_query, request)
        
        # Execute the MeTTa function
        execution_result = _execute_metta_function(kb, metta_function, request)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Get knowledge base stats
        kb_state = kb.get_knowledge_base_state()
        
        return {
            "success": True,
            "query": request.query,
            "parsed_query": parsed_query,
            "metta_function": metta_function,
            "execution_result": execution_result,
            "execution_time": round(execution_time, 2),
            "atoms_queried": kb_state.get("atom_counts", {}).get("events", 0),
            "user_context": {
                "location": request.user_location,
                "trust_score": request.user_trust_score
            },
            "explanation": _generate_query_explanation(parsed_query, execution_result),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Natural language query error: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": request.query,
            "fallback_response": _generate_fallback_response(request.query, request),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/execute-metta-function")
async def execute_metta_function(request: MettaFunctionRequest):
    """
    Execute a specific MeTTa function directly
    """
    try:
        kb = ClimateWitnessKnowledgeBase()
        
        # Execute the MeTTa function
        result = kb.run_metta_function(request.metta_function)
        
        return {
            "success": True,
            "metta_function": request.metta_function,
            "result": result,
            "result_count": len(result) if isinstance(result, list) else 1,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"MeTTa function execution error: {e}")
        raise HTTPException(status_code=500, detail=f"MeTTa function execution failed: {str(e)}")

@router.get("/knowledge-base-stats")
async def get_knowledge_base_stats():
    """
    Get current knowledge base statistics
    """
    try:
        kb = ClimateWitnessKnowledgeBase()
        kb_state = kb.get_knowledge_base_state()
        
        return {
            "success": True,
            "knowledge_base_stats": kb_state,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge base stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base stats: {str(e)}")

@router.get("/example-queries")
async def get_example_queries():
    """
    Get example natural language queries for MeTTa system
    """
    examples = [
        {
            "query": "Show me drought events in Turkana County",
            "description": "Find climate events by location and type",
            "metta_function": "(match &event-space (event-type $event drought) (location $event \"Turkana\"))"
        },
        {
            "query": "What are the trust scores of community reporters?",
            "description": "Query trust scores for active reporters",
            "metta_function": "(match &trust-space (and (trust-score $user $score) (> $score 60)) (list $user $score))"
        },
        {
            "query": "Find recent flood events with high severity",
            "description": "Query events by type and severity level",
            "metta_function": "(match &self (and (event-type $event flood) (severity $event $level) (> $level 0.7)) $event)"
        },
        {
            "query": "Show climate events near Nairobi coordinates",
            "description": "Find events within geographic radius",
            "metta_function": "(match &self (and (location $event $lat $lon) (< (distance -1.2921 36.8219 $lat $lon) 50)) $event)"
        },
        {
            "query": "Verify locust swarm event with satellite data",
            "description": "Run verification logic on locust events",
            "metta_function": "(auto-verify locust_swarm satellite_evidence 88 92)"
        },

        {
            "query": "Calculate economic impact of drought events",
            "description": "Assess economic damage from climate events",
            "metta_function": "(match &self (and (event-type $event drought) (economic-impact $event $damage)) (list $event $damage))"
        },
        {
            "query": "Find events verified by multiple reporters",
            "description": "Query events with community consensus",
            "metta_function": "(match &self (and (verified $event) (reporter-count $event $count) (> $count 2)) $event)"
        },
        {
            "query": "Assess weather risk for maize farming in Kisumu",
            "description": "Real-time weather risk assessment for crops",
            "metta_function": "(assess-weather-risk \"maize\" -0.0917 34.7680 \"Kisumu\")"
        }
    ]
    
    return {
        "success": True,
        "example_queries": examples,
        "total_examples": len(examples),
        "timestamp": datetime.utcnow().isoformat()
    }

# Helper Functions

def _parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Parse natural language query to identify intent and entities
    """
    query_lower = query.lower()
    
    # Query type detection
    query_type = "general"
    entities = {}
    
    # Event-related queries
    if any(word in query_lower for word in ["event", "drought", "flood", "locust", "climate"]):
        query_type = "event_query"
        
        # Extract event types
        event_types = []
        for event_type in ["drought", "flood", "locust", "wildfire", "storm"]:
            if event_type in query_lower:
                event_types.append(event_type)
        entities["event_types"] = event_types
    
    # User/Trust queries
    elif any(word in query_lower for word in ["trust", "user", "score"]):
        query_type = "trust_query"
        
        # Extract user ID if present
        user_match = re.search(r"user\s+(\w+)", query_lower)
        if user_match:
            entities["user_id"] = user_match.group(1)
    
    # Payout/Economic queries
    elif any(word in query_lower for word in ["payout", "payment", "reward", "economic"]):
        query_type = "economic_query"
    
    # Verification queries
    elif any(word in query_lower for word in ["verify", "verification", "validate"]):
        query_type = "verification_query"
    
    # Location extraction
    locations = ["turkana", "marsabit", "kajiado", "nairobi", "mombasa", "nakuru"]
    for location in locations:
        if location in query_lower:
            entities["location"] = location.title()
            break
    
    # Number extraction
    numbers = re.findall(r'\b\d+\b', query)
    if numbers:
        entities["numbers"] = [int(n) for n in numbers]
    
    return {
        "query_type": query_type,
        "entities": entities,
        "original_query": query
    }

def _generate_metta_function(parsed_query: Dict[str, Any], request: NaturalLanguageQueryRequest) -> str:
    """
    Generate appropriate MeTTa function based on parsed query
    """
    query_type = parsed_query["query_type"]
    entities = parsed_query["entities"]
    
    if query_type == "event_query":
        if "location" in entities and "event_types" in entities:
            location = entities["location"]
            event_type = entities["event_types"][0] if entities["event_types"] else "drought"
            return f'(match &self (and (event-type $event {event_type}) (location $event "{location} County")) $event)'
        elif "location" in entities:
            location = entities["location"]
            return f'(match &self (location $event "{location} County") $event)'
        elif "event_types" in entities:
            event_type = entities["event_types"][0]
            return f'(match &self (event-type $event {event_type}) $event)'
        else:
            return '(match &self (event $x) $x)'
    
    elif query_type == "trust_query":
        if "user_id" in entities:
            user_id = entities["user_id"]
            return f'(match &self (trust-score {user_id} $score) $score)'
        elif request.user_trust_score is not None:
            return f'(match &self (trust-score $user {request.user_trust_score}) $user)'
        else:
            return '(match &self (trust-score $user $score) (list $user $score))'
    
    elif query_type == "economic_query":
        if "event_types" in entities:
            event_type = entities["event_types"][0]
            return f'(payout-eligible {event_type}_001 $amount)'
        else:
            return '(match &self (payout-eligible $event $amount) (list $event $amount))'
    
    elif query_type == "verification_query":
        if "numbers" in entities and len(entities["numbers"]) >= 2:
            confidence1, confidence2 = entities["numbers"][:2]
            return f'(auto-verify event_001 user_001 {confidence1} {confidence2})'
        else:
            return '(match &self (verified $event) $event)'
    
    else:
        # General query - try to find relevant atoms
        if request.user_location:
            return f'(match &self (location $event "{request.user_location}") $event)'
        else:
            return '(match &self $x $x)'

def _execute_metta_function(kb, metta_function: str, request: NaturalLanguageQueryRequest) -> Dict[str, Any]:
    """
    Execute the MeTTa function and format results
    """
    try:
        # Execute the function
        result = kb.run_metta_function(metta_function)
        
        # Format results based on type
        if isinstance(result, list):
            formatted_results = []
            for item in result:
                if hasattr(item, '__str__'):
                    formatted_results.append(str(item))
                else:
                    formatted_results.append(repr(item))
            
            return {
                "status": "success",
                "results": formatted_results,
                "result_count": len(formatted_results),
                "execution_status": "completed"
            }
        else:
            return {
                "status": "success",
                "results": [str(result)] if result else [],
                "result_count": 1 if result else 0,
                "execution_status": "completed"
            }
            
    except Exception as e:
        logger.error(f"MeTTa execution error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "results": [],
            "result_count": 0,
            "execution_status": "failed"
        }

def _generate_query_explanation(parsed_query: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate explanation for the query and results
    """
    query_type = parsed_query["query_type"]
    entities = parsed_query["entities"]
    
    explanation = {
        "query_interpretation": f"Interpreted as {query_type.replace('_', ' ')}",
        "entities_found": entities,
        "metta_reasoning": "Used MeTTa knowledge base to find matching atoms",
        "result_interpretation": ""
    }
    
    if execution_result["status"] == "success":
        result_count = execution_result["result_count"]
        if result_count > 0:
            explanation["result_interpretation"] = f"Found {result_count} matching results in the knowledge base"
        else:
            explanation["result_interpretation"] = "No matching results found in the knowledge base"
    else:
        explanation["result_interpretation"] = f"Query execution failed: {execution_result.get('error', 'Unknown error')}"
    
    return explanation

def _generate_fallback_response(query: str, request: NaturalLanguageQueryRequest) -> Dict[str, Any]:
    """
    Generate fallback response when MeTTa query fails
    """
    query_lower = query.lower()
    
    # Provide contextual fallback based on query content
    if "drought" in query_lower:
        return {
            "response": "I understand you're asking about drought events. The system is currently processing your query.",
            "suggestion": "Try asking: 'Show me recent drought events' or 'What drought events happened in Turkana?'",
            "context": f"Your location: {request.user_location or 'Not set'}"
        }
    elif "trust" in query_lower:
        return {
            "response": f"Your current trust score is {request.user_trust_score or 'not set'}. Trust scores help verify climate events.",
            "suggestion": "Try asking: 'How can I improve my trust score?' or 'What affects trust calculation?'",
            "context": "Trust scores range from 0-100 based on reporting accuracy"
        }
    elif "payout" in query_lower:
        return {
            "response": "Payouts are calculated based on event verification and severity. The system is processing payout information.",
            "suggestion": "Try asking: 'How are payouts calculated?' or 'What events get rewards?'",
            "context": "Verified events receive cryptocurrency rewards"
        }
    else:
        return {
            "response": "I'm processing your query about climate data and verification. Please try a more specific question.",
            "suggestion": "Try asking about: drought events, trust scores, payouts, or verification process",
            "context": f"Location: {request.user_location or 'Not set'}, Trust: {request.user_trust_score or 'Not set'}"
        }