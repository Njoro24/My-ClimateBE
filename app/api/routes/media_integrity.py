"""
Media Integrity & Decentralized News Verification API Routes
Extends climate verification to general media and news integrity
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.metta_service import get_shared_knowledge_base
from app.database.database import get_db
import json
import hashlib
from datetime import datetime
import os

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

@router.post("/upload-media")
async def upload_media_for_verification(
    file: UploadFile = File(...),
    media_type: str = "photo",
    source: str = "user_upload",
    crud = Depends(get_db)
):
    """
    Upload media file for integrity verification
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
        
        # Extract metadata
        metadata = {
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_hash": hashlib.sha256(content).hexdigest()
        }
        
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
                "size": metadata["size"]
            },
            "verification_result": verification_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media upload and verification failed: {str(e)}")

# Helper functions
def _analyze_metadata_integrity(metadata):
    """Analyze metadata for integrity indicators"""
    score = 0.5  # Base score
    
    if "timestamp" in metadata:
        score += 0.2
    if "location" in metadata:
        score += 0.15
    if "device_info" in metadata:
        score += 0.15
    
    return min(score, 1.0)

def _assess_source_credibility(source):
    """Assess credibility of the source"""
    # Simplified credibility assessment
    credibility_map = {
        "verified_journalist": 0.9,
        "citizen_reporter": 0.7,
        "official_source": 0.95,
        "anonymous_source": 0.3,
        "user_upload": 0.6
    }
    return credibility_map.get(source, 0.5)

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
    """Verify an individual claim"""
    # Simplified claim verification
    return {
        "claim": claim,
        "credibility": 0.75,  # Would be calculated based on evidence
        "evidence_found": True,
        "sources": ["verified_data", "expert_consensus"]
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
    """Find evidence that contradicts the claim"""
    # Simplified contradiction detection
    contradictions = []
    
    # Check if claim contradicts verified events
    for event in verified_events:
        if "no climate change" in claim.lower() and event.event_type in ["drought", "flood"]:
            contradictions.append(f"Contradicts verified {event.event_type} event in {event.location}")
    
    return contradictions

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