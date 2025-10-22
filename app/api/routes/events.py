from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from typing import List, Optional, Dict, Any, Union
import uuid
import os
from datetime import datetime
import json
import logging

try:
    from hyperon import Atom
    HYPERON_AVAILABLE = True
except ImportError:
    print("Warning: Hyperon not available, MeTTa functionality will be limited")
    HYPERON_AVAILABLE = False
    class Atom:
        def __init__(self, *args, **kwargs):
            pass
        def is_symbol(self):
            return False
        def is_expression(self):
            return False
        def is_grounded(self):
            return False
        def get_children(self):
            return []
        def get_grounded_value(self):
            return None
        def __str__(self):
            return "dummy_atom"

from app.database.crud import create_event as db_create_event, get_event_by_id, get_events_by_user, get_events_by_region, update_event_verification
from app.database.models import User, Event
from app.services.ai_verification_service import (
    verify_climate_image,
    verify_event_description,
    map_problem_to_event_type,
)
from app.services.ipfs_service import upload_to_ipfs, upload_metadata_to_ipfs
from app.services.metta_service import MeTTaService

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/user/{user_id}")
async def get_user_events(user_id: str):
    return {
        "events": []
    }

def serialize_catom(catom: Atom) -> Any:
    """Convert Atom to a JSON-serializable object"""
    if not HYPERON_AVAILABLE:
        return str(catom)
    
    try:
        # Check if atom is a symbol
        if catom.is_symbol():
            return str(catom)
        
        if catom.is_expression():
            children = catom.get_children()
            return [serialize_catom(child) for child in children]
        
        # Check if atom is grounded with a value
        if catom.is_grounded():
            value = catom.get_grounded_value()
            return str(value) if value is not None else str(catom)
        
        # Fallback: use string representation
        return str(catom)
        
    except Exception as e:
        logger.error(f"Failed to serialize Atom: {str(e)}, type: {type(catom).__name__}")
        return {"error": f"Failed to serialize Atom: {str(e)}", "type": type(catom).__name__}

def serialize_metta_result(result: Any) -> Any:
    """Recursively serialize MeTTa results to JSON-serializable format"""
    if isinstance(result, Atom):
        return serialize_catom(result)
    elif isinstance(result, list):
        return [serialize_metta_result(item) for item in result]
    elif isinstance(result, tuple):
        return tuple(serialize_metta_result(item) for item in result)
    elif isinstance(result, dict):
        return {key: serialize_metta_result(value) for key, value in result.items()}
    elif hasattr(result, '__dict__'):
        # Handle objects with __dict__ attribute
        return {key: serialize_metta_result(value) for key, value in result.__dict__.items()}
    else:
        # Return primitive types as-is
        return result

@router.post("/")
async def create_event(
    event_type: str = Form(...),
    description: str = Form(""),
    latitude: float = Form(...),
    longitude: float = Form(...),
    user: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    request: Request = None
):
    """Create a new climate event with AI + MeTTa verification"""
    try:
        # Validate required fields
        if not event_type or not event_type.strip():
            raise HTTPException(status_code=422, detail="Event type is required")
        
        if latitude is None or longitude is None:
            raise HTTPException(status_code=422, detail="Latitude and longitude are required")
        
        if not user or not user.strip():
            raise HTTPException(status_code=422, detail="User information is required")
        
        event_id = str(uuid.uuid4())
        ipfs_hash, photo_path = None, None
        verification_status = "pending"
        
        logger.info(f"Creating event: type={event_type}, lat={latitude}, lng={longitude}, user_len={len(user)}")

        # Parse user (accepts JSON string or plain user ID)
        user_str = user if isinstance(user, str) else str(user)
        try:
            # Try to parse as JSON (full user object)
            user_data = json.loads(user_str)
            logger.info(f"Parsed user data: {user_data}")
            
            # Create user object with required fields and defaults for optional ones
            user_obj = User(
                id=user_data.get('id', ''),
                email=user_data.get('email', ''),
                password_hash=user_data.get('password_hash', ''),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                role=user_data.get('role', 'user'),
                wallet_address=user_data.get('wallet_address'),
                trust_score=user_data.get('trust_score', 50),
                location_region=user_data.get('location_region'),
                profile_image=user_data.get('profile_image'),
                is_active=user_data.get('is_active', True),
                is_verified=user_data.get('is_verified', False),
                created_at=user_data.get('created_at'),
                updated_at=user_data.get('updated_at'),
                last_login_at=user_data.get('last_login_at')
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse user JSON: {e}, user_str: {user_str}")
            # Fallback: treat as user_id string
            user_obj = User(id=user_str, email="", password_hash="", first_name="", last_name="")
        except Exception as e:
            logger.error(f"Failed to create user object: {e}, user_data: {user_data if 'user_data' in locals() else 'N/A'}")
            raise HTTPException(status_code=422, detail=f"Invalid user data: {str(e)}")

        # Handle photo upload
        photo_content = None
        photo_filename = None
        if photo is not None:
            photo_content = await photo.read()
            photo_filename = getattr(photo, 'filename', 'uploaded_photo')
        elif request is not None:
            # Try to read raw body as binary
            try:
                photo_content = await request.body()
                photo_filename = f"{event_id}_raw_upload"
            except Exception as e:
                logger.error(f"Failed to read raw photo body: {e}")

        if photo_content:
            try:
                ipfs_hash = await upload_to_ipfs(photo_content, photo_filename or 'uploaded_photo')
                photo_path = f"ipfs://{ipfs_hash}" if ipfs_hash else None
            except Exception as e:
                logger.error(f"IPFS upload failed: {e}")
                # Fallback to local storage
                if not photo_path:
                    os.makedirs("uploads", exist_ok=True)
                    filename = f"{event_id}_{photo_filename or 'uploaded_photo'}"
                    photo_path = f"uploads/{filename}"
                    with open(photo_path, "wb") as buffer:
                        buffer.write(photo_content)

        # Run AI verification
        image_confidence, desc_confidence = 0, 0
        image_verification, desc_verification = None, None

        # Image verification (if photo provided)
        if photo_content:
            try:
                image_verification = await verify_climate_image(
                    photo_content,
                    event_type,
                    description,
                    {"latitude": latitude, "longitude": longitude},
                )
                image_confidence = image_verification.get("verification", {}).get("confidence", 0)
            except Exception as e:
                logger.error(f"AI image verification failed: {e}")
                image_verification = {"error": str(e)}

        # Description verification
        try:
            desc_verification = await verify_event_description(
                description,
                event_type,
                {"latitude": latitude, "longitude": longitude},
            )
            desc_confidence = desc_verification.get("analysis", {}).get("confidence", 0)
        except Exception as e:
            logger.error(f"AI description verification failed: {e}")
            desc_verification = {"error": str(e)}

        # Create Event object
        event = Event(
            id=event_id,
            user_id=user_obj.id,
            event_type=event_type,
            description=description,
            latitude=latitude,
            longitude=longitude,
            photo_path=photo_path,
            timestamp=datetime.now(),
            created_at=datetime.now(),
            verification_status="pending",
        )

        # MeTTa verification
        metta_verification_result, dao_result, early_warning_result = {}, {}, {}

        if HYPERON_AVAILABLE:
            try:
                metta_service = MeTTaService()
                logger.info('MeTTa: creating atoms')
                await metta_service.create_atoms(event, user_obj)
                logger.info('MeTTa: running verification')
                raw_metta_verification = await metta_service.run_verification(
                    event, user_obj, image_confidence, desc_confidence
                )
                str_value = str(raw_metta_verification).strip().lower()
                raw_verification = str_value == "true"
                metta_verification_result = {"verified": raw_verification}
                if raw_verification:
                    verification_status = "verified"
            except Exception as e:
                logger.error(f"MeTTa verification failed: {e}")
                metta_verification_result = {"verified": False, "error": str(e)}



            try:
                logger.info('MeTTa: evaluating DAO proposal')
                dao_raw = await metta_service.evaluate_dao_proposal(event.id)
                dao_result = serialize_metta_result(dao_raw)
            except Exception as e:
                dao_result = {"error": str(e)}

            try:
                logger.info('MeTTa: generating early warning')
                early_warning_raw = await metta_service.generate_early_warning(
                    {"latitude": latitude, "longitude": longitude}, [event_type]
                )
                early_warning_result = serialize_metta_result(early_warning_raw)
            except Exception as e:
                early_warning_result = {"error": str(e)}
        else:
            # Fallback when MeTTa is not available
            logger.info('MeTTa not available, using fallback verification')
            # Simple fallback verification based on AI confidence
            if image_confidence > 0.7 or desc_confidence > 0.7:
                verification_status = "verified"
                metta_verification_result = {"verified": True, "fallback": True}
            else:
                metta_verification_result = {"verified": False, "fallback": True}
            

            dao_result = {"message": "MeTTa not available"}
            early_warning_result = {"message": "MeTTa not available"}

        # Save event
        event.verification_status = verification_status
        success = await db_create_event(event)

        return {
            "message": "Event created successfully",
            "event_id": event_id,
            "status": verification_status,
            "ipfs_hash": ipfs_hash,
            "ai_verification": {
                "image": image_verification,
                "description": desc_verification,
            },
            "metta_verification": serialize_metta_result(metta_verification_result),
            "dao_relief": dao_result,
            "early_warning": early_warning_result,
        }

    except Exception as e:
        logger.error(f"Failed to create event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

# Additional endpoints
@router.post("/map-problem")
async def map_user_problem(problem_description: str = Form(...)):
    """Map user's problem description to event types using AI"""
    try:
        mapping_result = await map_problem_to_event_type(problem_description)
        return {
            "success": mapping_result["success"],
            "original_problem": problem_description,
            "suggested_event_type": mapping_result["mapping"]["event_type"],
            "confidence": mapping_result["mapping"]["confidence"],
            "reasoning": mapping_result["mapping"]["reasoning"],
            "alternative_types": mapping_result["mapping"]["alternative_types"],
            "available_types": ["drought", "flood", "wildfire", "locust", "extreme_heat", "storm"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to map problem: {str(e)}")

@router.post("/{event_id}/verify")
async def verify_event(event_id: str):
    """Re-verify an event using AI"""
    try:
        event = await get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        verification_results = {}
        if event.description:
            verification_results["description"] = await verify_event_description(
                event.description,
                event.event_type,
                {"latitude": event.latitude, "longitude": event.longitude},
            )

        if event.photo_path and not event.photo_path.startswith("ipfs://"):
            try:
                with open(event.photo_path, "rb") as f:
                    photo_content = f.read()
                verification_results["image"] = await verify_climate_image(
                    photo_content,
                    event.event_type,
                    event.description,
                    {"latitude": event.latitude, "longitude": event.longitude},
                )
            except Exception as e:
                logger.error(f"Image re-verification failed: {e}")

        new_status = "verified" if (
            verification_results.get("description", {}).get("analysis", {}).get("consistent", False)
            and verification_results.get("image", {}).get("verification", {}).get("verified", True)
        ) else "pending"

        await update_event_verification(event_id, new_status)
        return {
            "message": "Event re-verification completed",
            "event_id": event_id,
            "new_status": new_status,
            "verification_results": verification_results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.get("/region/{bounds}")
async def get_events_by_region(bounds: str):
    """Get events within geographic bounds"""
    try:
        lat1, lng1, lat2, lng2 = map(float, bounds.split(","))
        min_lat, max_lat = min(lat1, lat2), max(lat1, lat2)
        min_lng, max_lng = min(lng1, lng2), max(lng1, lng2)
        events = await get_events_by_region(min_lat, max_lat, min_lng, max_lng)
        return [event.to_dict() for event in events]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bounds format")

@router.get("/user/{user_id}")
async def get_user_events(user_id: str):
    """Get all events by a specific user"""
    events = await get_events_by_user(user_id)
    return [event.to_dict() for event in events]

@router.put("/{event_id}/verify")
async def update_event_verification_endpoint(
    event_id: str,
    status: str = Form(...),
    tx_hash: Optional[str] = Form(None),
    payout_amount: Optional[float] = Form(None),
):
    """Update event verification status"""
    success = await update_event_verification(event_id, status, tx_hash, payout_amount)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event verification updated successfully"}
@router.get("/stats")
async def get_events_stats():
    """Get events statistics"""
    try:
        # Add your stats logic here
        return {
            "total_events": 0,
            "verified_events": 0,
            "pending_events": 0,
            "by_type": {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
