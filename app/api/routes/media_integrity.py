"""
Enhanced Media Integrity & Decentralized News Verification API Routes
Real data integration for climate misinformation detection and media verification
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.metta_service import get_shared_knowledge_base
from app.database.database import get_db
import json
import hashlib
from datetime import datetime, timedelta
import os
import requests
from PIL import Image
from PIL.ExifTags import TAGS
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class MediaVerificationRequest(BaseModel):
    media_type: str  # photo, video, audio, document, news-article, social-media-post
    source: str
    metadata: Dict[str, Any]
    claims: Optional[List[str]] = []

class NewsVerificationRequest(BaseModel):
    article_id: str
    claims: List[str]
    sources: List[str]
    content: str

class MisinformationDetectionRequest(BaseModel):
    claim: str
    location: Optional[str] = None
    timeframe: Optional[str] = "30_days"

class FactCheckRequest(BaseModel):
    claim: str
    community_responses: List[Dict[str, Any]]

class CrossPlatformVerificationRequest(BaseModel):
    content_hash: str
    platforms: List[str]

@router.post("/verify-media")
async def verify_media_authenticity(
    request: MediaVerificationRequest,
    crud = Depends(get_db)
):
    """
    Verify the authenticity of media content using multiple verification methods
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/media_integrity.metta")
        
        # Generate media ID for tracking
        media_id = hashlib.sha256(f"{request.source}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
        
        # Analyze metadata integrity
        metadata_score = _analyze_metadata_integrity(request.metadata)
        
        # Assess source credibility
        source_credibility = _assess_source_credibility(request.source)
        
        # Perform technical authenticity checks
        technical_score = _technical_authenticity_check(request.media_type, request.metadata)
        
        # Calculate overall authenticity score
        overall_score = (metadata_score * 0.35 + source_credibility * 0.4 + technical_score * 0.25)
        is_authentic = overall_score > 0.7
        
        # Run MeTTa verification
        verification_query = f"""
        !(verify-media-authenticity "{media_id}" {request.media_type} "{request.source}" {json.dumps(request.metadata)})
        """
        
        metta_results = kb.run_query(verification_query)
        
        return {
            "success": True,
            "media_id": media_id,
            "authenticity_result": {
                "is_authentic": is_authentic,
                "overall_score": round(overall_score, 3),
                "confidence_level": "high" if overall_score > 0.8 else "medium" if overall_score > 0.6 else "low"
            },
            "verification_breakdown": {
                "metadata_integrity": round(metadata_score, 3),
                "source_credibility": round(source_credibility, 3),
                "technical_authenticity": round(technical_score, 3)
            },
            "explanation": {
                "methodology": "Multi-factor authenticity verification using metadata analysis, source validation, and technical checks",
                "factors_considered": ["File metadata consistency", "Source reputation", "Technical manipulation indicators"],
                "confidence_factors": _generate_authenticity_confidence_factors(metadata_score, source_credibility, technical_score)
            },
            "recommendations": _generate_authenticity_recommendations(is_authentic, overall_score),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media verification failed: {str(e)}")

@router.post("/verify-news")
async def verify_news_article(
    request: NewsVerificationRequest,
    crud = Depends(get_db)
):
    """
    Verify news articles using decentralized fact-checking and source validation
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/media_integrity.metta")
        
        # Verify individual claims
        claim_verifications = []
        for claim in request.claims:
            claim_verification = await _verify_individual_claim(claim, kb, crud)
            claim_verifications.append(claim_verification)
        
        # Validate news sources
        source_validations = []
        for source in request.sources:
            source_validation = _validate_news_source(source)
            source_validations.append(source_validation)
        
        # Calculate consensus score
        consensus_score = sum([cv["credibility"] for cv in claim_verifications]) / len(claim_verifications) if claim_verifications else 0
        
        # Calculate source reliability
        source_reliability = sum([sv["reliability"] for sv in source_validations]) / len(source_validations) if source_validations else 0
        
        # Get network trust score (simplified)
        network_trust = 0.75  # Would be calculated from decentralized network
        
        # Combine scores
        final_credibility = (consensus_score * 0.5 + source_reliability * 0.3 + network_trust * 0.2)
        
        # Run MeTTa news verification
        news_query = f"""
        !(decentralized-news-verification "{request.article_id}" {json.dumps(request.claims)} {json.dumps(request.sources)})
        """
        
        metta_results = kb.run_query(news_query)
        
        return {
            "success": True,
            "article_id": request.article_id,
            "verification_result": {
                "credibility_score": round(final_credibility, 3),
                "credibility_level": "high" if final_credibility > 0.8 else "medium" if final_credibility > 0.6 else "low",
                "verified_claims": len([cv for cv in claim_verifications if cv["credibility"] > 0.7]),
                "total_claims": len(claim_verifications)
            },
            "claim_analysis": claim_verifications,
            "source_analysis": source_validations,
            "decentralized_consensus": {
                "consensus_score": round(consensus_score, 3),
                "source_reliability": round(source_reliability, 3),
                "network_trust": round(network_trust, 3)
            },
            "explanation": {
                "methodology": "Decentralized verification combining claim fact-checking, source validation, and network consensus",
                "verification_process": "Each claim independently verified against known facts and expert consensus"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News verification failed: {str(e)}")

@router.post("/detect-misinformation")
async def detect_misinformation(
    request: MisinformationDetectionRequest,
    crud = Depends(get_db)
):
    """
    Detect potential misinformation using climate knowledge and expert consensus
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/media_integrity.metta")
        kb.load_metta_file("BECW/metta/climate_data.metta")
        
        # Get verified climate events for comparison
        verified_events = []
        if request.location:
            events = await crud.get_events_by_location(request.location)
            verified_events = [e for e in events if e.verification_status == "verified"]
        
        # Check claim against verified climate data
        contradictory_evidence = _find_contradictory_evidence(request.claim, verified_events)
        
        # Get scientific consensus (simplified)
        scientific_consensus = _get_climate_consensus(request.claim)
        
        # Detect misinformation patterns
        misinformation_indicators = _count_misinformation_patterns(request.claim)
        
        # Determine if claim is misinformation
        is_misinformation = misinformation_indicators > 2 or len(contradictory_evidence) > 0
        
        # Run MeTTa misinformation detection
        misinformation_query = f"""
        !(detect-climate-misinformation "{request.claim}" "{request.location or 'global'}" {request.timeframe})
        """
        
        metta_results = kb.run_query(misinformation_query)
        
        return {
            "success": True,
            "claim": request.claim,
            "misinformation_detected": is_misinformation,
            "confidence_level": "high" if misinformation_indicators > 3 else "medium" if misinformation_indicators > 1 else "low",
            "analysis": {
                "contradictory_evidence": contradictory_evidence,
                "scientific_consensus": scientific_consensus,
                "misinformation_indicators": misinformation_indicators,
                "verified_events_checked": len(verified_events)
            },
            "explanation": {
                "methodology": "Cross-reference claim against verified climate data and scientific consensus",
                "evidence_sources": "Verified community reports, scientific literature, expert opinions",
                "detection_criteria": "Factual contradictions, pattern matching, consensus deviation"
            },
            "recommendations": _generate_misinformation_recommendations(is_misinformation, misinformation_indicators),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Misinformation detection failed: {str(e)}")

@router.post("/community-fact-check")
async def community_fact_check(
    request: FactCheckRequest,
    crud = Depends(get_db)
):
    """
    Perform community-based fact-checking with expert and citizen input
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/media_integrity.metta")
        
        # Separate expert and citizen responses
        expert_responses = [r for r in request.community_responses if r.get("user_type") == "expert"]
        citizen_responses = [r for r in request.community_responses if r.get("user_type") == "citizen"]
        
        # Calculate expert consensus
        expert_consensus = _calculate_expert_consensus(expert_responses)
        
        # Calculate citizen consensus
        citizen_consensus = _calculate_citizen_consensus(citizen_responses)
        
        # Weighted consensus (experts have higher weight)
        weighted_consensus = (expert_consensus * 0.7 + citizen_consensus * 0.3)
        
        # Assess confidence level
        confidence_level = _assess_consensus_confidence(expert_responses, citizen_responses)
        
        # Run MeTTa community fact-check
        fact_check_query = f"""
        !(community-fact-check "{request.claim}" {json.dumps(request.community_responses)})
        """
        
        metta_results = kb.run_query(fact_check_query)
        
        return {
            "success": True,
            "claim": request.claim,
            "fact_check_result": {
                "consensus_score": round(weighted_consensus, 3),
                "confidence_level": confidence_level,
                "claim_status": "verified" if weighted_consensus > 0.7 else "disputed" if weighted_consensus > 0.3 else "false"
            },
            "community_analysis": {
                "expert_consensus": round(expert_consensus, 3),
                "citizen_consensus": round(citizen_consensus, 3),
                "expert_responses": len(expert_responses),
                "citizen_responses": len(citizen_responses),
                "total_responses": len(request.community_responses)
            },
            "explanation": {
                "methodology": "Weighted consensus combining expert opinions (70%) and citizen input (30%)",
                "quality_factors": "Response quality, user credibility, evidence provided",
                "consensus_threshold": "Claims require >70% consensus for verification"
            },
            "transparency": {
                "all_responses_public": True,
                "weighting_explained": True,
                "appeals_possible": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Community fact-check failed: {str(e)}")

@router.post("/cross-platform-verify")
async def cross_platform_verification(
    request: CrossPlatformVerificationRequest,
    crud = Depends(get_db)
):
    """
    Verify content consistency across multiple platforms
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/media_integrity.metta")
        
        # Simulate platform verifications
        platform_verifications = []
        for platform in request.platforms:
            verification = _verify_on_platform(request.content_hash, platform)
            platform_verifications.append(verification)
        
        # Calculate consistency score
        consistency_score = _calculate_cross_platform_consistency(platform_verifications)
        
        # Analyze timestamps
        timestamp_analysis = _analyze_cross_platform_timestamps(platform_verifications)
        
        # Detect manipulation indicators
        manipulation_indicators = _detect_cross_platform_manipulation(platform_verifications)
        
        # Calculate final credibility
        credibility_score = max(0, consistency_score - (manipulation_indicators * 0.1))
        
        # Run MeTTa cross-platform verification
        cross_platform_query = f"""
        !(cross-platform-verification "{request.content_hash}" {json.dumps(request.platforms)})
        """
        
        metta_results = kb.run_query(cross_platform_query)
        
        return {
            "success": True,
            "content_hash": request.content_hash,
            "verification_result": {
                "credibility_score": round(credibility_score, 3),
                "consistency_score": round(consistency_score, 3),
                "manipulation_indicators": manipulation_indicators,
                "platforms_verified": len(request.platforms)
            },
            "platform_analysis": platform_verifications,
            "timestamp_analysis": timestamp_analysis,
            "explanation": {
                "methodology": "Cross-platform consistency analysis and manipulation detection",
                "verification_criteria": "Content matching, timestamp consistency, modification detection",
                "platforms_checked": request.platforms
            },
            "recommendations": _generate_cross_platform_recommendations(credibility_score, manipulation_indicators),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-platform verification failed: {str(e)}")

def _extract_real_metadata(file_path: str) -> Dict[str, Any]:
    """Extract real EXIF metadata from image files"""
    metadata = {}
    
    try:
        if file_path.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif')):
            with Image.open(file_path) as image:
                # Get basic image info
                metadata.update({
                    "ImageWidth": image.width,
                    "ImageHeight": image.height,
                    "Format": image.format,
                    "Mode": image.mode
                })
                
                # Extract EXIF data
                exif_data = image.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata[tag] = value
                
                # Extract GPS data if available
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    if exif and 34853 in exif:  # GPS tag
                        gps_data = exif[34853]
                        if 2 in gps_data and 4 in gps_data:  # Latitude and Longitude
                            lat = _convert_gps_to_decimal(gps_data[2], gps_data[1])
                            lon = _convert_gps_to_decimal(gps_data[4], gps_data[3])
                            metadata["GPS"] = [lat, lon]
                
    except Exception as e:
        logger.warning(f"Could not extract EXIF data: {e}")
        metadata["exif_error"] = str(e)
    
    return metadata

def _convert_gps_to_decimal(coord, ref):
    """Convert GPS coordinates from EXIF format to decimal degrees"""
    try:
        degrees = float(coord[0])
        minutes = float(coord[1])
        seconds = float(coord[2])
        
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
            
        return decimal
    except:
        return 0.0

@router.post("/upload-media")
async def upload_media_for_verification(
    file: UploadFile = File(...),
    media_type: str = "photo",
    source: str = "user_upload",
    crud = Depends(get_db)
):
    """
    Upload media file for integrity verification with real metadata extraction
    """
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads/media_verification", exist_ok=True)
        
        # Generate unique filename
        file_hash = hashlib.sha256(f"{file.filename}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
        file_path = f"uploads/media_verification/{file_hash}_{file.filename}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract real metadata
        real_metadata = _extract_real_metadata(file_path)
        
        # Combine with basic file info
        metadata = {
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_hash": hashlib.sha256(content).hexdigest(),
            **real_metadata
        }
        
        # Cross-check GPS coordinates with known climate events if available
        if "GPS" in metadata:
            lat, lon = metadata["GPS"]
            nearby_events = await _find_nearby_climate_events(lat, lon, radius_km=50)
            metadata["nearby_climate_events"] = nearby_events
        
        # Perform verification
        verification_request = MediaVerificationRequest(
            media_type=media_type,
            source=source,
            metadata=metadata
        )
        
        # Use the existing verification endpoint
        verification_result = await verify_media_authenticity(verification_request, crud)
        
        return {
            "success": True,
            "file_info": {
                "filename": file.filename,
                "file_path": file_path,
                "file_hash": metadata["file_hash"],
                "size": metadata["size"],
                "real_metadata_extracted": len(real_metadata) > 0
            },
            "extracted_metadata": {
                "has_gps": "GPS" in metadata,
                "has_timestamp": "DateTime" in metadata,
                "camera_info": f"{metadata.get('Make', 'Unknown')} {metadata.get('Model', '')}".strip(),
                "image_dimensions": f"{metadata.get('ImageWidth', 0)}x{metadata.get('ImageHeight', 0)}",
                "nearby_events": len(metadata.get("nearby_climate_events", []))
            },
            "verification_result": verification_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media upload and verification failed: {str(e)}")

async def _find_nearby_climate_events(lat: float, lon: float, radius_km: int = 50) -> List[Dict]:
    """Find verified climate events near the given coordinates"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Simple distance calculation (approximate)
        # In a real implementation, you'd use proper geospatial queries
        cursor.execute("""
            SELECT id, event_type, location, latitude, longitude, timestamp, description
            FROM events 
            WHERE verification_status = 'verified' 
            AND latitude IS NOT NULL 
            AND longitude IS NOT NULL
            AND timestamp > datetime('now', '-90 days')
        """)
        
        events = cursor.fetchall()
        nearby_events = []
        
        for event in events:
            event_id, event_type, location, event_lat, event_lon, timestamp, description = event
            
            # Calculate approximate distance (simplified)
            if event_lat and event_lon:
                lat_diff = abs(lat - float(event_lat))
                lon_diff = abs(lon - float(event_lon))
                
                # Rough distance calculation (1 degree ≈ 111 km)
                distance_km = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                
                if distance_km <= radius_km:
                    nearby_events.append({
                        "event_id": event_id,
                        "event_type": event_type,
                        "location": location,
                        "distance_km": round(distance_km, 2),
                        "timestamp": timestamp,
                        "description": description[:100] + "..." if len(description) > 100 else description
                    })
        
        conn.close()
        return sorted(nearby_events, key=lambda x: x["distance_km"])[:5]  # Return 5 closest
        
    except Exception as e:
        logger.error(f"Error finding nearby events: {e}")
        return []

# Helper functions
def _analyze_metadata_integrity(metadata):
    """Analyze metadata for integrity indicators using real EXIF data"""
    score = 0.3  # Base score for having metadata
    
    # Check for essential EXIF data
    if metadata.get("DateTime"):
        score += 0.2
        # Verify timestamp is reasonable (not future, not too old)
        try:
            timestamp = datetime.fromisoformat(metadata["DateTime"].replace(":", "-", 2))
            now = datetime.now()
            if timestamp <= now and timestamp >= (now - timedelta(days=365)):
                score += 0.1
        except:
            score -= 0.1
    
    if metadata.get("GPS"):
        score += 0.2
        # Verify GPS coordinates are valid
        try:
            lat, lon = metadata["GPS"]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                score += 0.1
        except:
            score -= 0.1
    
    if metadata.get("Make") and metadata.get("Model"):
        score += 0.15
        # Check if camera/phone model is known
        known_devices = ["iPhone", "Samsung", "Canon", "Nikon", "Sony", "Huawei", "Xiaomi"]
        if any(device in str(metadata.get("Make", "")) + str(metadata.get("Model", "")) for device in known_devices):
            score += 0.05
    
    # Check for manipulation indicators
    if metadata.get("Software"):
        editing_software = ["Photoshop", "GIMP", "Lightroom", "Snapseed", "FaceApp"]
        if any(software.lower() in str(metadata.get("Software", "")).lower() for software in editing_software):
            score -= 0.2  # Penalty for editing software
    
    # Check image dimensions and quality
    if metadata.get("ImageWidth") and metadata.get("ImageHeight"):
        width, height = metadata.get("ImageWidth", 0), metadata.get("ImageHeight", 0)
        if width * height > 1000000:  # > 1MP suggests real camera
            score += 0.1
    
    return min(max(score, 0.0), 1.0)

def _assess_source_credibility(source):
    """Assess credibility of the source using real user data"""
    try:
        # Connect to database to get real user trust scores
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Try to find user by email or username
        cursor.execute("SELECT trust_score, verification_count FROM users WHERE email = ? OR username = ?", (source, source))
        user_data = cursor.fetchone()
        
        if user_data:
            trust_score, verification_count = user_data
            # Convert trust score (0-100) to credibility (0-1)
            base_credibility = trust_score / 100.0
            
            # Boost credibility based on verification history
            if verification_count > 10:
                base_credibility += 0.1
            elif verification_count > 5:
                base_credibility += 0.05
            
            conn.close()
            return min(base_credibility, 1.0)
        
        conn.close()
        
        # Fallback to source type assessment
        credibility_map = {
            "verified_journalist": 0.9,
            "citizen_reporter": 0.7,
            "official_source": 0.95,
            "anonymous_source": 0.3,
            "user_upload": 0.6,
            "government_agency": 0.85,
            "ngo_source": 0.75,
            "academic_institution": 0.9
        }
        return credibility_map.get(source, 0.5)
        
    except Exception as e:
        logger.error(f"Error assessing source credibility: {e}")
        return 0.5

def _technical_authenticity_check(media_type, metadata):
    """Perform technical authenticity checks"""
    # Simplified technical check
    score = 0.7  # Base technical score
    
    if media_type == "photo":
        if metadata.get("exif_data"):
            score += 0.2
    elif media_type == "video":
        if metadata.get("codec_info"):
            score += 0.15
    
    return min(score, 1.0)

def _generate_authenticity_confidence_factors(metadata_score, source_credibility, technical_score):
    """Generate confidence factors for authenticity assessment"""
    factors = []
    
    if metadata_score > 0.8:
        factors.append("Strong metadata integrity")
    if source_credibility > 0.8:
        factors.append("Highly credible source")
    if technical_score > 0.8:
        factors.append("No technical manipulation detected")
    
    return factors

def _generate_authenticity_recommendations(is_authentic, overall_score):
    """Generate recommendations based on authenticity assessment"""
    if is_authentic:
        return ["Media appears authentic", "Safe to use with proper attribution"]
    else:
        return ["Media authenticity questionable", "Recommend additional verification", "Use with caution"]

async def _verify_individual_claim(claim, kb, crud):
    """Verify an individual claim against real climate data"""
    try:
        # Connect to database to check against verified climate events
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Extract key terms from claim
        claim_lower = claim.lower()
        event_types = ["drought", "flood", "locust", "heatwave", "storm", "wildfire"]
        locations = []
        detected_events = []
        
        # Simple keyword extraction
        for event_type in event_types:
            if event_type in claim_lower:
                detected_events.append(event_type)
        
        # Look for location mentions (simplified)
        cursor.execute("SELECT DISTINCT location FROM events WHERE verification_status = 'verified'")
        known_locations = [row[0] for row in cursor.fetchall()]
        
        for location in known_locations:
            if location and location.lower() in claim_lower:
                locations.append(location)
        
        evidence_found = False
        supporting_events = []
        contradicting_events = []
        
        # Check for supporting or contradicting evidence
        if detected_events and locations:
            for event_type in detected_events:
                for location in locations:
                    # Look for verified events of this type in this location
                    cursor.execute("""
                        SELECT id, event_type, location, timestamp, description 
                        FROM events 
                        WHERE event_type = ? AND location LIKE ? AND verification_status = 'verified'
                        ORDER BY timestamp DESC LIMIT 5
                    """, (event_type, f"%{location}%"))
                    
                    events = cursor.fetchall()
                    if events:
                        evidence_found = True
                        supporting_events.extend(events)
        
        # Calculate credibility based on evidence
        if supporting_events:
            credibility = 0.8 + (len(supporting_events) * 0.02)  # Higher with more supporting events
        elif evidence_found:
            credibility = 0.6
        else:
            # Check for contradictory patterns
            credibility = 0.4  # Neutral when no evidence found
        
        # Check for misinformation patterns
        misinformation_keywords = ["hoax", "fake", "conspiracy", "lie", "scam", "never happened"]
        if any(keyword in claim_lower for keyword in misinformation_keywords):
            credibility = max(credibility - 0.3, 0.1)
        
        conn.close()
        
        return {
            "claim": claim,
            "credibility": min(credibility, 1.0),
            "evidence_found": evidence_found,
            "supporting_events": len(supporting_events),
            "detected_event_types": detected_events,
            "detected_locations": locations,
            "sources": ["verified_climate_events", "community_reports"] if evidence_found else ["no_evidence"]
        }
        
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        return {
            "claim": claim,
            "credibility": 0.5,
            "evidence_found": False,
            "error": str(e),
            "sources": ["error"]
        }

def _validate_news_source(source):
    """Validate a news source"""
    # Simplified source validation
    return {
        "source": source,
        "reliability": 0.8,  # Would be calculated from source history
        "verification_status": "verified",
        "bias_rating": "minimal"
    }

def _find_contradictory_evidence(claim, verified_events):
    """Find evidence that contradicts the claim using real event data"""
    contradictions = []
    claim_lower = claim.lower()
    
    try:
        # Connect to database for real verified events
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get recent verified events
        cursor.execute("""
            SELECT event_type, location, timestamp, description 
            FROM events 
            WHERE verification_status = 'verified' 
            AND timestamp > datetime('now', '-30 days')
            ORDER BY timestamp DESC
        """)
        
        recent_events = cursor.fetchall()
        
        # Check for direct contradictions
        denial_patterns = [
            ("no climate change", ["drought", "flood", "heatwave", "storm"]),
            ("climate change is fake", ["drought", "flood", "heatwave", "storm"]),
            ("no drought", ["drought"]),
            ("no flooding", ["flood"]),
            ("weather is normal", ["drought", "flood", "heatwave", "storm"]),
            ("no extreme weather", ["drought", "flood", "heatwave", "storm", "wildfire"])
        ]
        
        for denial_phrase, contradicted_events in denial_patterns:
            if denial_phrase in claim_lower:
                for event_type, location, timestamp, description in recent_events:
                    if event_type in contradicted_events:
                        contradictions.append({
                            "type": "direct_contradiction",
                            "claim_phrase": denial_phrase,
                            "contradicting_event": {
                                "event_type": event_type,
                                "location": location,
                                "timestamp": timestamp,
                                "description": description[:100] + "..." if len(description) > 100 else description
                            },
                            "explanation": f"Claim denies {denial_phrase} but verified {event_type} occurred in {location} on {timestamp}"
                        })
        
        # Check for temporal contradictions
        if "never happened" in claim_lower or "didn't happen" in claim_lower:
            # Extract potential event references
            event_types = ["drought", "flood", "locust", "heatwave", "storm", "wildfire"]
            for event_type in event_types:
                if event_type in claim_lower:
                    matching_events = [e for e in recent_events if e[0] == event_type]
                    if matching_events:
                        contradictions.append({
                            "type": "temporal_contradiction",
                            "claim_phrase": f"claims {event_type} never happened",
                            "contradicting_events": len(matching_events),
                            "explanation": f"Found {len(matching_events)} verified {event_type} events in recent records"
                        })
        
        # Check for scale contradictions
        minimization_patterns = [
            ("minor", "severe"),
            ("small", "major"),
            ("not serious", "critical"),
            ("exaggerated", "verified")
        ]
        
        for minimize_word, actual_severity in minimization_patterns:
            if minimize_word in claim_lower:
                # Look for events with high severity
                cursor.execute("""
                    SELECT event_type, location, description 
                    FROM events 
                    WHERE verification_status = 'verified' 
                    AND (description LIKE '%severe%' OR description LIKE '%major%' OR description LIKE '%critical%')
                    AND timestamp > datetime('now', '-30 days')
                """)
                
                severe_events = cursor.fetchall()
                if severe_events:
                    contradictions.append({
                        "type": "scale_contradiction",
                        "claim_phrase": f"minimizes impact as '{minimize_word}'",
                        "contradicting_evidence": f"{len(severe_events)} verified severe events",
                        "explanation": f"Claim minimizes impact but {len(severe_events)} severe events documented"
                    })
        
        conn.close()
        return contradictions
        
    except Exception as e:
        logger.error(f"Error finding contradictory evidence: {e}")
        return []

def _get_climate_consensus(claim):
    """Get scientific consensus on climate claim"""
    # Simplified consensus assessment
    return {
        "consensus_level": "strong",
        "agreement_percentage": 97,
        "source": "scientific_literature"
    }

def _count_misinformation_patterns(claim):
    """Count misinformation indicators in claim"""
    indicators = 0
    
    # Check for common misinformation patterns
    misinformation_keywords = ["hoax", "conspiracy", "fake", "lie", "scam"]
    for keyword in misinformation_keywords:
        if keyword in claim.lower():
            indicators += 1
    
    return indicators

def _generate_misinformation_recommendations(is_misinformation, indicators):
    """Generate recommendations for misinformation handling"""
    if is_misinformation:
        return [
            "Flag as potential misinformation",
            "Provide fact-check information",
            "Limit distribution",
            "Offer educational resources"
        ]
    else:
        return ["Information appears credible", "Continue monitoring"]

def _calculate_expert_consensus(expert_responses):
    """Calculate consensus among expert responses"""
    if not expert_responses:
        return 0.5
    
    positive_responses = len([r for r in expert_responses if r.get("verdict") == "true"])
    return positive_responses / len(expert_responses)

def _calculate_citizen_consensus(citizen_responses):
    """Calculate consensus among citizen responses"""
    if not citizen_responses:
        return 0.5
    
    positive_responses = len([r for r in citizen_responses if r.get("verdict") == "true"])
    return positive_responses / len(citizen_responses)

def _assess_consensus_confidence(expert_responses, citizen_responses):
    """Assess confidence in consensus"""
    total_responses = len(expert_responses) + len(citizen_responses)
    
    if total_responses > 20:
        return "high"
    elif total_responses > 10:
        return "medium"
    else:
        return "low"

def _verify_on_platform(content_hash, platform):
    """Verify content on a specific platform"""
    # Simplified platform verification
    return {
        "platform": platform,
        "found": True,
        "timestamp": datetime.utcnow().isoformat(),
        "modifications": 0,
        "credibility": 0.8
    }

def _calculate_cross_platform_consistency(platform_verifications):
    """Calculate consistency across platforms"""
    if not platform_verifications:
        return 0.0
    
    found_count = len([pv for pv in platform_verifications if pv["found"]])
    return found_count / len(platform_verifications)

def _analyze_cross_platform_timestamps(platform_verifications):
    """Analyze timestamp consistency across platforms"""
    return {
        "consistent_timestamps": True,
        "time_variance": "< 1 hour",
        "suspicious_patterns": False
    }

def _detect_cross_platform_manipulation(platform_verifications):
    """Detect manipulation indicators across platforms"""
    manipulation_count = 0
    
    for pv in platform_verifications:
        if pv.get("modifications", 0) > 0:
            manipulation_count += 1
    
    return manipulation_count

def _generate_cross_platform_recommendations(credibility_score, manipulation_indicators):
    """Generate recommendations for cross-platform verification"""
    if credibility_score > 0.8 and manipulation_indicators == 0:
        return ["Content appears consistent across platforms", "High credibility"]
    elif manipulation_indicators > 0:
        return ["Manipulation detected", "Verify original source", "Use with caution"]
    else:
        return ["Limited platform presence", "Seek additional verification"]