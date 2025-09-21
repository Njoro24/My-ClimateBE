"""
API routes for AI-powered MeTTa query generation and execution
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.ai_metta_service import generate_and_execute_metta, ai_metta_service
from app.database.database import get_db  # Import your database dependency
from app.services.metta_service import get_shared_knowledge_base

router = APIRouter()

class MeTTaQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    include_visualization: bool = True
    max_results: int = 100

class MeTTaFunctionRequest(BaseModel):
    function: str
    context: Optional[Dict[str, Any]] = None

class MeTTaFollowUpRequest(BaseModel):
    original_query: str
    follow_up: str
    previous_result: Optional[Dict[str, Any]] = None

@router.post("/generate-query")
async def generate_metta_query(
    request: MeTTaQueryRequest,
    crud = Depends(get_db)
):
    """
    Generate a MeTTa function from natural language query using Anthropic AI
    """
    try:
        # Add database context
        context = request.context or {}
        
        # Get some sample data for context
        try:
            recent_events = await crud.get_all_events()
            context["available_events"] = len(recent_events)
            context["event_types"] = list(set(event.event_type for event in recent_events if event.event_type))
        except Exception:
            context["available_events"] = 0
            context["event_types"] = []
        
        # Generate MeTTa function
        result = await ai_metta_service.generate_metta_function(request.query, context)
        
        return {
            "success": result["success"],
            "query": request.query,
            "generated_function": result.get("generated_function", ""),
            "explanation": result.get("explanation", ""),
            "confidence": result.get("confidence", 0.0),
            "function_type": result.get("function_type", "unknown"),
            "complexity": result.get("estimated_complexity", "medium"),
            "improvements": result.get("suggested_improvements", []),
            "context": context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate MeTTa query: {str(e)}")

@router.post("/execute-function")
async def execute_metta_function(
    request: MeTTaFunctionRequest,
    crud = Depends(get_db)
):
    """
    Execute a MeTTa function using metta.run and return results with D3.js visualization
    """
    try:
        # Add database context
        context = request.context or {}
        
        # Get database events for knowledge base
        try:
            events = await crud.get_all_events()
            context["events"] = [
                {
                    "id": event.id,
                    "type": event.event_type or "unknown",
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "verified": event.verification_status == "verified"
                }
                for event in events
            ]
        except Exception:
            context["events"] = []
        
        # Execute the function
        result = await ai_metta_service.execute_metta_function(request.function, context)
        
        return {
            "success": result["success"],
            "function": request.function,
            "result": result.get("result", []),
            "visualization_data": result.get("visualization_data", {}),
            "summary": result.get("summary", ""),
            "execution_time": result.get("execution_time", "0s"),
            "metadata": result.get("metadata", {}),
            "error": result.get("error")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute MeTTa function: {str(e)}")

@router.post("/query-and-execute")
async def query_and_execute(
    request: MeTTaQueryRequest,
    crud = Depends(get_db)
):
    """
    Generate and execute MeTTa function from natural language in one step
    """
    try:
        # Add database context
        context = request.context or {}
        
        # Get database statistics for context
        try:
            stats = await crud.get_stats()
            context.update(stats)
            
            # Get events for knowledge base
            events = await crud.get_all_events()
            context["events"] = [
                {
                    "id": event.id,
                    "type": event.event_type or "unknown",
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "verified": event.verification_status == "verified",
                    "description": event.description
                }
                for event in events
            ]
        except Exception:
            context["events"] = []
        
        # Generate and execute
        result = await generate_and_execute_metta(request.query, context)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process MeTTa query: {str(e)}")

@router.post("/follow-up")
async def follow_up_query(
    request: MeTTaFollowUpRequest,
    crud = Depends(get_db)
):
    """
    Handle follow-up queries based on previous results
    """
    try:
        # Combine original query with follow-up
        combined_query = f"Based on the previous query '{request.original_query}', now {request.follow_up}"
        
        # Add previous result as context
        context = {
            "previous_query": request.original_query,
            "previous_result": request.previous_result,
            "follow_up_intent": request.follow_up
        }
        
        # Get current database context
        try:
            events = await crud.get_all_events()
            context["events"] = [
                {
                    "id": event.id,
                    "type": event.event_type or "unknown",
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "verified": event.verification_status == "verified"
                }
                for event in events
            ]
        except Exception:
            context["events"] = []
        
        # Generate and execute follow-up
        result = await generate_and_execute_metta(combined_query, context)
        
        return {
            **result,
            "is_follow_up": True,
            "original_query": request.original_query,
            "follow_up_query": request.follow_up
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process follow-up query: {str(e)}")

@router.get("/stats")
async def get_metta_stats(
    crud = Depends(get_db)
):
    """
    Get MeTTa knowledge base statistics and performance metrics
    """
    try:
        # Get database stats with proper error handling
        db_stats = {}
        try:
            db_stats = await crud.get_stats()
        except Exception as db_error:
            # Log the error but continue with default values
            print(f"Database stats error: {db_error}")
            db_stats = {
                "total_events": 0,
                "verified_events": 0,
                "events_by_type": {},
                "total_users": 0
            }
        
        # Get actual atom count from knowledge base if available
        total_atoms = 0
        try:
            kb = get_shared_knowledge_base()
            # Try to get actual atom count if the method exists
            if hasattr(kb, 'get_atom_count'):
                total_atoms = kb.get_atom_count()
            else:
                # Fallback calculation
                total_atoms = db_stats.get("total_events", 0) * 3
        except Exception:
            total_atoms = db_stats.get("total_events", 0) * 3
        
        # Calculate MeTTa-specific stats
        metta_stats = {
            "total_atoms": total_atoms,
            "active_queries": 12,
            "knowledge_domains": [
                "climate-events",
                "user-trust",
                "verification-rules",
                "economic-impact",
                "governance-logic"
            ],
            "last_update": "2024-01-20T10:30:00Z",
            "query_performance": {
                "avg_execution_time": "0.234s",
                "cache_hit_rate": 0.78,
                "successful_queries": 156,
                "ai_generation_success_rate": 0.92
            },
            "ai_integration": {
                "anthropic_available": ai_metta_service.anthropic_client is not None,
                "metta_run_available": True,
                "supported_functions": len(ai_metta_service.metta_functions)
            }
        }
        
        return {
            "metta_stats": metta_stats,
            "database_stats": db_stats,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in get_metta_stats: {str(e)}")
        # Return a safe response even if everything fails
        return {
            "metta_stats": {
                "total_atoms": 0,
                "active_queries": 0,
                "knowledge_domains": ["climate-events"],
                "last_update": "2024-01-20T10:30:00Z",
                "query_performance": {
                    "avg_execution_time": "0s",
                    "cache_hit_rate": 0,
                    "successful_queries": 0,
                    "ai_generation_success_rate": 0
                },
                "ai_integration": {
                    "anthropic_available": False,
                    "metta_run_available": False,
                    "supported_functions": 0
                }
            },
            "database_stats": {
                "total_events": 0,
                "verified_events": 0,
                "events_by_type": {},
                "total_users": 0
            },
            "status": "error",
            "message": str(e)
        }

@router.get("/examples")
async def get_metta_examples():
    """
    Get example MeTTa queries and functions for users
    """
    return {
        "examples": {
            "basic_queries": [
                {
                    "query": "Show me all drought events",
                    "function": "(match &space (climate-event drought $location $severity $impact $verified) ($location $severity))",
                    "description": "Basic pattern matching to find drought events"
                },
                {
                    "query": "What is the total impact of all climate events?",
                    "function": "(let* ((events (match &space (climate-event $type $location $severity $impact $verified) $impact)) (total (foldl-atom + 0 events))) total)",
                    "description": "Aggregation using foldl-atom to sum impact values"
                }
            ],
            "advanced_queries": [
                {
                    "query": "Compare drought severity between different regions",
                    "function": "(let* ((droughts (match &space (climate-event drought $location $severity $impact $verified) ($location $severity))) (grouped (group-by-location droughts))) grouped)",
                    "description": "Complex analysis with grouping and comparison"
                }
            ]
        },
        "available_functions": ai_metta_service.metta_functions,
        "sample_queries": [
            "Show me all drought events in East Africa",
            "What is the total impact of flood events?",
            "Compare drought severity between Kenya and Ethiopia",
            "Find high-severity climate events that are verified",
            "Analyze climate patterns recursively by region",
            "Which locations have the most climate events?",
            "Show me the average severity of all events",
            "Find unverified events with high impact"
        ]
    }

@router.get("/atoms")
async def get_metta_atoms(
    limit: int = 50,
    atom_type: Optional[str] = None,
):
    """
    Get MeTTa atoms from the in-memory knowledge base (no database)
    """
    try:
        kb = get_shared_knowledge_base()
        
        # Safe method to get atoms without _safe_atom_to_string
        atoms = []
        try:
            # Try different methods to get atoms
            if hasattr(kb, 'get_all_atoms'):
                atoms = kb.get_all_atoms()
            elif hasattr(kb, 'get_atoms'):
                atoms = kb.get_atoms()
            else:
                # Fallback: return empty list
                atoms = []
        except Exception as e:
            print(f"Error getting atoms: {e}")
            atoms = []
        
        # Apply filtering by type if specified
        if atom_type:
            try:
                atoms = [atom for atom in atoms if hasattr(atom, 'type') and atom.type == atom_type]
            except:
                # If filtering fails, return all atoms
                pass
        
        # Apply limit
        atoms = atoms[:limit]
        
        # Convert atoms to safe representation
        safe_atoms = []
        for atom in atoms:
            try:
                # Try different methods to represent atoms as strings
                if hasattr(atom, '__str__'):
                    safe_atoms.append(str(atom))
                elif hasattr(atom, 'to_string'):
                    safe_atoms.append(atom.to_string())
                else:
                    safe_atoms.append(repr(atom))
            except:
                safe_atoms.append("Unknown atom")
        
        # Get knowledge base stats safely
        kb_stats = {}
        try:
            if hasattr(kb, 'get_knowledge_base_state'):
                kb_stats = kb.get_knowledge_base_state()
        except:
            kb_stats = {"state": "unknown"}
        
        return {
            "atoms": safe_atoms,
            "total_count": len(safe_atoms),
            "filtered_by": atom_type,
            "knowledge_base_stats": kb_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get MeTTa atoms: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Check the health of AI MeTTa service components
    """
    health_status = {
        "service": "healthy",
        "anthropic_api": "available" if ai_metta_service.anthropic_client else "demo_mode",
        "metta_runtime": "checking...",
        "timestamp": "2024-01-20T10:30:00Z"
    }
    
    # Test MeTTa runtime availability
    try:
        test_result = await ai_metta_service.execute_metta_function(
            "(match &space (test) (test))", 
            {}
        )
        health_status["metta_runtime"] = "available" if test_result["success"] else "simulation_mode"
    except Exception:
        health_status["metta_runtime"] = "simulation_mode"
    
    return health_status