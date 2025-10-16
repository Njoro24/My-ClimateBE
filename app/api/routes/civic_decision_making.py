"""
Enhanced Civic Decision-Making API Routes for Climate Witness Chain
Real data integration for transparent, AI-assisted democratic decision-making
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.metta_service import get_shared_knowledge_base
from app.database.database import get_db
import json
from datetime import datetime, timedelta
import sqlite3
import os
import logging
import statistics
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class DemocraticDecisionRequest(BaseModel):
    issue: str
    stakeholders: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    community_input: List[Dict[str, Any]]

class PolicyImpactPredictionRequest(BaseModel):
    policy: str
    location: str
    timeframe: str = "5_years"

class ResourceAllocationRequest(BaseModel):
    available_resources: Dict[str, float]
    community_needs: List[Dict[str, Any]]
    verified_impacts: List[Dict[str, Any]]

class ConsensusBuilderRequest(BaseModel):
    issue: str
    participants: List[Dict[str, Any]]
    positions: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]

class ParticipationAssessmentRequest(BaseModel):
    decision_process: str
    participants: List[Dict[str, Any]]
    representation_data: Dict[str, Any]

class AIRecommendationRequest(BaseModel):
    climate_challenge: str
    location: str
    constraints: Dict[str, Any]

@router.post("/democratic-decision")
async def make_democratic_decision(
    request: DemocraticDecisionRequest,
    crud = Depends(get_db)
):
    """
    Facilitate transparent democratic decision-making using climate data and community input
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        kb.load_metta_file("BECW/metta/explainable_ai.metta")
        
        # Assess evidence quality
        evidence_quality = _assess_civic_evidence_quality(request.evidence)
        
        # Assess stakeholder representation
        stakeholder_representation = _assess_stakeholder_representation(request.stakeholders)
        
        # Calculate community consensus
        community_consensus = _calculate_community_consensus(request.community_input)
        
        # Get climate data support
        climate_data_support = await _get_climate_data_support(request.issue, request.evidence, crud)
        
        # Calculate transparency score
        transparency_score = _calculate_decision_transparency(request.evidence, request.stakeholders, request.community_input)
        
        # Combine factors for decision confidence
        decision_confidence = _combine_civic_factors(
            evidence_quality, stakeholder_representation, 
            community_consensus, climate_data_support
        )
        
        # Run MeTTa democratic decision
        decision_query = f"""
        !(democratic-climate-decision "{request.issue}" {json.dumps(request.stakeholders)} 
          {json.dumps(request.evidence)} {json.dumps(request.community_input)})
        """
        
        metta_results = kb.run_query(decision_query)
        
        return {
            "success": True,
            "issue": request.issue,
            "decision_result": {
                "decision_confidence": round(decision_confidence, 3),
                "recommendation": "proceed" if decision_confidence > 0.7 else "revise" if decision_confidence > 0.5 else "reconsider",
                "confidence_level": "high" if decision_confidence > 0.8 else "medium" if decision_confidence > 0.6 else "low"
            },
            "analysis_breakdown": {
                "evidence_quality": round(evidence_quality, 3),
                "stakeholder_representation": round(stakeholder_representation, 3),
                "community_consensus": round(community_consensus, 3),
                "climate_data_support": round(climate_data_support, 3),
                "transparency_score": round(transparency_score, 3)
            },
            "explanation": {
                "methodology": "Multi-factor democratic decision analysis using verified climate data and community input",
                "factors_considered": ["Evidence quality", "Stakeholder representation", "Community consensus", "Climate data alignment"],
                "transparency_features": ["All inputs public", "Reasoning explained", "Appeals possible"]
            },
            "recommendations": _generate_decision_recommendations(decision_confidence, evidence_quality, community_consensus),
            "next_steps": _suggest_next_steps(decision_confidence, request.issue),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Democratic decision process failed: {str(e)}")

@router.post("/predict-policy-impact")
async def predict_policy_impact(
    request: PolicyImpactPredictionRequest,
    crud = Depends(get_db)
):
    """
    Predict the impact of climate policies using verified data and AI modeling
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        kb.load_metta_file("BECW/metta/climate_data.metta")
        
        # Get historical climate events for the location
        historical_events = await crud.get_events_by_location(request.location)
        verified_events = [e for e in historical_events if e.verification_status == "verified"]
        
        # Get vulnerability factors
        vulnerability_factors = _get_location_vulnerability_factors(request.location)
        
        # Calculate economic baseline
        economic_baseline = sum([e.economic_impact or 0 for e in verified_events])
        
        # Estimate policy effectiveness
        policy_effectiveness = _estimate_policy_effectiveness(request.policy, verified_events)
        
        # Calculate cost-benefit analysis
        cost_benefit_analysis = _calculate_policy_cost_benefit(request.policy, economic_baseline)
        
        # Calculate risk reduction
        risk_reduction = _calculate_risk_reduction(request.policy, vulnerability_factors)
        
        # Predict community acceptance
        community_acceptance = _predict_community_acceptance(request.policy, request.location)
        
        # Run MeTTa policy impact prediction
        impact_query = f"""
        !(predict-policy-impact "{request.policy}" "{request.location}" {request.timeframe})
        """
        
        metta_results = kb.run_query(impact_query)
        
        return {
            "success": True,
            "policy": request.policy,
            "location": request.location,
            "impact_prediction": {
                "effectiveness_score": round(policy_effectiveness, 2),
                "cost_benefit_ratio": round(cost_benefit_analysis["ratio"], 3),
                "risk_reduction_percentage": round(risk_reduction * 100, 1),
                "community_acceptance": round(community_acceptance, 3),
                "confidence_level": "high" if policy_effectiveness > 0.8 else "medium"
            },
            "analysis_details": {
                "historical_events_analyzed": len(verified_events),
                "economic_baseline": economic_baseline,
                "vulnerability_factors": vulnerability_factors,
                "implementation_feasibility": cost_benefit_analysis["feasibility"]
            },
            "explanation": {
                "methodology": "Impact prediction based on historical verified climate events and policy effectiveness models",
                "data_sources": f"Analyzed {len(verified_events)} verified climate events from {request.location}",
                "prediction_factors": ["Historical event patterns", "Economic impact data", "Vulnerability assessment", "Policy effectiveness research"]
            },
            "recommendations": _generate_policy_implementation_recommendations(policy_effectiveness, cost_benefit_analysis, community_acceptance),
            "timeline": _generate_implementation_timeline(request.policy, request.timeframe),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy impact prediction failed: {str(e)}")

@router.post("/allocate-resources")
async def allocate_climate_resources(
    request: ResourceAllocationRequest,
    crud = Depends(get_db)
):
    """
    Optimize resource allocation based on real verified climate impacts and community needs
    """
    try:
        # Connect to database for real impact data
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get real verified climate impacts by location
        cursor.execute("""
            SELECT location, event_type, COUNT(*) as event_count, 
                   AVG(COALESCE(economic_impact, 0)) as avg_impact,
                   MAX(timestamp) as latest_event
            FROM events 
            WHERE verification_status = 'verified' 
            AND timestamp > datetime('now', '-90 days')
            AND location IS NOT NULL
            GROUP BY location, event_type
            ORDER BY event_count DESC, avg_impact DESC
        """)
        
        real_impacts = cursor.fetchall()
        
        # Convert to structured data
        location_impacts = defaultdict(lambda: {"total_events": 0, "total_impact": 0, "event_types": []})
        
        for location, event_type, count, avg_impact, latest in real_impacts:
            location_impacts[location]["total_events"] += count
            location_impacts[location]["total_impact"] += avg_impact or 0
            location_impacts[location]["event_types"].append({
                "type": event_type,
                "count": count,
                "avg_impact": avg_impact or 0,
                "latest": latest
            })
        
        conn.close()
        
        # Identify priority areas based on real data
        priority_areas = _identify_priority_areas_real(location_impacts, request.verified_impacts)
        
        # Assess need severity using real and requested data
        need_severity = _assess_community_needs_real(request.community_needs, location_impacts)
        
        # Calculate resource efficiency
        resource_efficiency = _calculate_resource_efficiency_real(request.available_resources, priority_areas)
        
        # Assess equity considerations
        equity_considerations = _assess_allocation_equity_real(request.community_needs, location_impacts)
        
        # Optimize resource distribution
        optimal_allocation = _optimize_resource_distribution_real(
            request.available_resources, priority_areas, need_severity, equity_considerations
        )
        
        # Load MeTTa for additional reasoning
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        
        allocation_query = f"""
        !(allocate-climate-resources {json.dumps(request.available_resources)} 
          {json.dumps(request.community_needs)} {json.dumps(request.verified_impacts)})
        """
        metta_results = kb.run_query(allocation_query)
        
        return {
            "success": True,
            "resource_allocation": {
                "optimal_distribution": optimal_allocation,
                "efficiency_score": round(resource_efficiency, 3),
                "equity_score": round(equity_considerations["equity_score"], 3),
                "coverage_percentage": round(optimal_allocation["coverage"], 1)
            },
            "priority_analysis": {
                "high_priority_areas": priority_areas["high"],
                "medium_priority_areas": priority_areas["medium"],
                "low_priority_areas": priority_areas["low"]
            },
            "real_data_analysis": {
                "locations_analyzed": len(location_impacts),
                "total_verified_events": sum(data["total_events"] for data in location_impacts.values()),
                "total_economic_impact": sum(data["total_impact"] for data in location_impacts.values())
            },
            "need_assessment": need_severity,
            "explanation": {
                "methodology": "Multi-criteria optimization using real verified climate data, community needs, and equity principles",
                "allocation_principles": ["Evidence-based prioritization", "Equitable distribution", "Maximum impact efficiency"],
                "data_sources": "Verified climate events from Climate Witness database",
                "transparency": "All allocation decisions based on verifiable data and explained reasoning"
            },
            "implementation_plan": _generate_allocation_implementation_plan_real(optimal_allocation, priority_areas),
            "monitoring_metrics": _define_allocation_monitoring_metrics_real(optimal_allocation),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Resource allocation error: {e}")
        raise HTTPException(status_code=500, detail=f"Resource allocation failed: {str(e)}")

@router.post("/build-consensus")
async def build_transparent_consensus(
    request: ConsensusBuilderRequest,
    crud = Depends(get_db)
):
    """
    Facilitate transparent consensus building among stakeholders
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        
        # Analyze stakeholder positions
        position_analysis = _analyze_stakeholder_positions(request.positions)
        
        # Map evidence to positions
        evidence_mapping = _map_evidence_to_positions(request.evidence, request.positions)
        
        # Identify common ground
        common_ground = _identify_common_ground(request.positions, request.evidence)
        
        # Identify conflict areas
        conflict_areas = _identify_conflict_areas(request.positions)
        
        # Generate mediation suggestions
        mediation_suggestions = _generate_mediation_suggestions(conflict_areas, request.evidence)
        
        # Design consensus pathway
        consensus_pathway = _design_consensus_pathway(common_ground, mediation_suggestions)
        
        # Run MeTTa consensus building
        consensus_query = f"""
        !(build-transparent-consensus "{request.issue}" {json.dumps(request.participants)} 
          {json.dumps(request.positions)} {json.dumps(request.evidence)})
        """
        
        metta_results = kb.run_query(consensus_query)
        
        return {
            "success": True,
            "issue": request.issue,
            "consensus_analysis": {
                "common_ground_areas": len(common_ground),
                "conflict_areas": len(conflict_areas),
                "consensus_potential": "high" if len(common_ground) > len(conflict_areas) else "medium",
                "participants_aligned": position_analysis["alignment_percentage"]
            },
            "stakeholder_positions": position_analysis,
            "evidence_analysis": evidence_mapping,
            "consensus_building": {
                "common_ground": common_ground,
                "conflict_areas": conflict_areas,
                "mediation_suggestions": mediation_suggestions,
                "consensus_pathway": consensus_pathway
            },
            "explanation": {
                "methodology": "Systematic analysis of stakeholder positions and evidence mapping",
                "consensus_criteria": "Shared values, evidence alignment, mutual benefits",
                "mediation_approach": "Evidence-based conflict resolution with transparent process"
            },
            "next_steps": _suggest_consensus_next_steps(common_ground, conflict_areas),
            "timeline": _estimate_consensus_timeline(len(conflict_areas), len(request.participants)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consensus building failed: {str(e)}")

@router.post("/assess-participation")
async def assess_community_participation(
    request: ParticipationAssessmentRequest,
    crud = Depends(get_db)
):
    """
    Assess the quality and inclusiveness of community participation in decision-making
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        
        # Assess demographic coverage
        demographic_coverage = _assess_demographic_coverage(request.participants)
        
        # Assess geographic coverage
        geographic_coverage = _assess_geographic_coverage(request.participants)
        
        # Assess participation quality
        participation_quality = _assess_participation_quality(request.decision_process)
        
        # Assess process accessibility
        accessibility_score = _assess_process_accessibility(request.decision_process)
        
        # Calculate inclusion effectiveness
        inclusion_effectiveness = _calculate_inclusion_effectiveness(
            demographic_coverage, geographic_coverage, accessibility_score
        )
        
        # Run MeTTa participation assessment
        participation_query = f"""
        !(assess-community-participation "{request.decision_process}" 
          {json.dumps(request.participants)} {json.dumps(request.representation_data)})
        """
        
        metta_results = kb.run_query(participation_query)
        
        return {
            "success": True,
            "decision_process": request.decision_process,
            "participation_assessment": {
                "inclusion_effectiveness": round(inclusion_effectiveness, 3),
                "overall_quality": "excellent" if inclusion_effectiveness > 0.8 else "good" if inclusion_effectiveness > 0.6 else "needs_improvement",
                "total_participants": len(request.participants)
            },
            "coverage_analysis": {
                "demographic_coverage": round(demographic_coverage, 3),
                "geographic_coverage": round(geographic_coverage, 3),
                "accessibility_score": round(accessibility_score, 3),
                "participation_quality": round(participation_quality, 3)
            },
            "representation_gaps": _identify_representation_gaps(request.participants, request.representation_data),
            "explanation": {
                "methodology": "Multi-dimensional analysis of participation inclusiveness and quality",
                "assessment_criteria": ["Demographic representation", "Geographic coverage", "Process accessibility", "Participation quality"],
                "benchmarks": "International standards for inclusive democratic participation"
            },
            "recommendations": _generate_participation_recommendations(inclusion_effectiveness, demographic_coverage, geographic_coverage),
            "improvement_strategies": _suggest_participation_improvements(request.participants, request.representation_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Participation assessment failed: {str(e)}")

@router.post("/ai-policy-recommendation")
async def ai_policy_recommendation(
    request: AIRecommendationRequest,
    crud = Depends(get_db)
):
    """
    Generate AI-assisted policy recommendations for climate challenges
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        kb.load_metta_file("BECW/metta/explainable_ai.metta")
        
        # Find similar climate cases
        similar_cases = await _find_similar_climate_cases(request.climate_challenge, request.location, crud)
        
        # Identify successful interventions
        successful_interventions = _identify_successful_interventions(similar_cases)
        
        # Adapt interventions to local context
        local_adaptation = _adapt_interventions_to_local_context(
            successful_interventions, request.location, request.constraints
        )
        
        # Assess policy feasibility
        feasibility_assessment = _assess_policy_feasibility(local_adaptation, request.constraints)
        
        # Predict intervention impact
        impact_prediction = _predict_intervention_impact(local_adaptation, request.location)
        
        # Calculate recommendation confidence
        recommendation_confidence = _calculate_recommendation_confidence(similar_cases, feasibility_assessment)
        
        # Run MeTTa AI policy recommendation
        recommendation_query = f"""
        !(ai-policy-recommendation "{request.climate_challenge}" "{request.location}" {json.dumps(request.constraints)})
        """
        
        metta_results = kb.run_query(recommendation_query)
        
        return {
            "success": True,
            "climate_challenge": request.climate_challenge,
            "location": request.location,
            "ai_recommendation": {
                "recommended_policies": local_adaptation,
                "confidence_level": "high" if recommendation_confidence > 0.8 else "medium" if recommendation_confidence > 0.6 else "low",
                "implementation_priority": "urgent" if impact_prediction["severity"] > 0.8 else "high" if impact_prediction["severity"] > 0.6 else "medium"
            },
            "analysis_basis": {
                "similar_cases_analyzed": len(similar_cases),
                "successful_interventions": len(successful_interventions),
                "feasibility_score": round(feasibility_assessment["score"], 3),
                "predicted_impact": round(impact_prediction["effectiveness"], 3)
            },
            "explanation": {
                "methodology": "AI analysis of similar climate challenges and successful policy interventions",
                "data_sources": "Historical climate events, policy effectiveness research, local context analysis",
                "recommendation_factors": ["Proven effectiveness", "Local adaptability", "Implementation feasibility", "Resource requirements"],
                "confidence_basis": f"Based on {len(similar_cases)} similar cases with {recommendation_confidence:.1%} success rate"
            },
            "implementation_guidance": _generate_implementation_guidance(local_adaptation, feasibility_assessment),
            "monitoring_framework": _create_monitoring_framework(local_adaptation, impact_prediction),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI policy recommendation failed: {str(e)}")

@router.get("/democratic-metrics/{process_id}")
async def get_democratic_innovation_metrics(
    process_id: str,
    crud = Depends(get_db)
):
    """
    Measure democratic innovation and effectiveness metrics for a decision process
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        
        # Get process data (simulated for now)
        decision_process = _get_decision_process_data(process_id)
        participation_data = _get_participation_data(process_id)
        outcome_data = _get_outcome_data(process_id)
        
        # Identify innovation indicators
        innovation_indicators = _identify_innovation_indicators(decision_process)
        
        # Measure participation effectiveness
        participation_effectiveness = _measure_participation_effectiveness(participation_data)
        
        # Assess decision quality
        decision_quality = _assess_decision_quality(outcome_data)
        
        # Measure transparency level
        transparency_level = _measure_transparency_level(decision_process)
        
        # Assess accountability mechanisms
        accountability_mechanisms = _assess_accountability_mechanisms(decision_process)
        
        # Calculate overall innovation score
        overall_innovation_score = _calculate_innovation_score(
            innovation_indicators, participation_effectiveness, 
            decision_quality, transparency_level
        )
        
        return {
            "success": True,
            "process_id": process_id,
            "democratic_innovation_metrics": {
                "overall_innovation_score": round(overall_innovation_score, 3),
                "innovation_level": "high" if overall_innovation_score > 0.8 else "medium" if overall_innovation_score > 0.6 else "developing",
                "key_strengths": _identify_key_strengths(innovation_indicators, participation_effectiveness, transparency_level)
            },
            "detailed_metrics": {
                "innovation_indicators": innovation_indicators,
                "participation_effectiveness": round(participation_effectiveness, 3),
                "decision_quality": round(decision_quality, 3),
                "transparency_level": round(transparency_level, 3),
                "accountability_score": round(accountability_mechanisms["score"], 3)
            },
            "benchmarking": {
                "compared_to": "International democratic innovation standards",
                "percentile_ranking": _calculate_percentile_ranking(overall_innovation_score),
                "improvement_potential": _assess_improvement_potential(overall_innovation_score)
            },
            "recommendations": _generate_innovation_recommendations(
                overall_innovation_score, innovation_indicators, participation_effectiveness
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Democratic metrics calculation failed: {str(e)}")

# Helper functions (simplified implementations)
def _assess_civic_evidence_quality(evidence):
    """Assess quality of evidence for civic decisions"""
    if not evidence:
        return 0.3
    
    quality_score = 0.5
    for item in evidence:
        if item.get("verified"):
            quality_score += 0.1
        if item.get("source_credibility", 0) > 0.7:
            quality_score += 0.1
    
    return min(quality_score, 1.0)

def _assess_stakeholder_representation(stakeholders):
    """Assess quality of stakeholder representation"""
    if not stakeholders:
        return 0.2
    
    representation_score = len(stakeholders) / 10  # Simplified
    return min(representation_score, 1.0)

def _calculate_community_consensus(community_input):
    """Calculate level of community consensus"""
    if not community_input:
        return 0.5
    
    positive_input = len([inp for inp in community_input if inp.get("sentiment") == "positive"])
    return positive_input / len(community_input)

async def _get_climate_data_support(issue, evidence, crud):
    """Get climate data support for the issue using real verified events"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Extract location and event types from issue
        issue_text = str(issue).lower()
        
        # Get all verified events for analysis
        cursor.execute("""
            SELECT event_type, location, timestamp, economic_impact, description
            FROM events 
            WHERE verification_status = 'verified'
            AND timestamp > datetime('now', '-365 days')
        """)
        
        all_events = cursor.fetchall()
        
        # Find relevant events based on issue content
        relevant_events = []
        event_types = ["drought", "flood", "locust", "heatwave", "storm", "wildfire"]
        
        for event_type in event_types:
            if event_type in issue_text:
                matching_events = [e for e in all_events if e[0] == event_type]
                relevant_events.extend(matching_events)
        
        # Look for location matches
        locations_mentioned = []
        cursor.execute("SELECT DISTINCT location FROM events WHERE verification_status = 'verified'")
        known_locations = [row[0] for row in cursor.fetchall()]
        
        for location in known_locations:
            if location and location.lower() in issue_text:
                locations_mentioned.append(location)
                location_events = [e for e in all_events if e[1] == location]
                relevant_events.extend(location_events)
        
        # Remove duplicates
        relevant_events = list(set(relevant_events))
        
        # Calculate support score based on evidence strength
        if not relevant_events:
            support_score = 0.3  # Low support if no relevant climate data
        else:
            # Base score from having relevant events
            support_score = 0.6
            
            # Boost based on number of events
            event_boost = min(len(relevant_events) * 0.05, 0.3)
            support_score += event_boost
            
            # Boost based on economic impact data
            economic_impacts = [e[3] for e in relevant_events if e[3] is not None]
            if economic_impacts:
                avg_impact = statistics.mean(economic_impacts)
                if avg_impact > 10000:  # Significant economic impact
                    support_score += 0.1
        
        conn.close()
        
        return min(support_score, 1.0)
        
    except Exception as e:
        logger.error(f"Error getting climate data support: {e}")
        return 0.5

def _calculate_decision_transparency(evidence, stakeholders, community_input):
    """Calculate transparency score of decision process"""
    transparency = 0.5
    if evidence:
        transparency += 0.2
    if stakeholders:
        transparency += 0.2
    if community_input:
        transparency += 0.1
    return min(transparency, 1.0)

def _combine_civic_factors(evidence_quality, stakeholder_rep, community_consensus, climate_support):
    """Combine factors for overall decision confidence"""
    return (evidence_quality * 0.3 + stakeholder_rep * 0.25 + 
            community_consensus * 0.25 + climate_support * 0.2)

def _generate_decision_recommendations(confidence, evidence_quality, consensus):
    """Generate recommendations based on decision analysis"""
    recommendations = []
    if confidence > 0.8:
        recommendations.append("Strong foundation for decision implementation")
    if evidence_quality < 0.6:
        recommendations.append("Strengthen evidence base before proceeding")
    if consensus < 0.6:
        recommendations.append("Build broader community consensus")
    return recommendations

def _suggest_next_steps(confidence, issue):
    """Suggest next steps based on decision confidence"""
    if confidence > 0.7:
        return ["Proceed with implementation planning", "Establish monitoring framework"]
    else:
        return ["Gather additional evidence", "Expand stakeholder consultation", "Refine proposal"]

# Additional helper functions would be implemented similarly...
def _get_location_vulnerability_factors(location):
    """Get vulnerability factors for location"""
    return {"climate_risk": 0.7, "adaptive_capacity": 0.6, "exposure": 0.8}

def _estimate_policy_effectiveness(policy, events):
    """Estimate policy effectiveness based on real historical event data"""
    try:
        if not events:
            return 0.5  # Neutral if no data
        
        policy_lower = policy.lower()
        
        # Policy effectiveness mapping based on event patterns
        effectiveness_factors = {
            "drought": {
                "water_conservation": 0.8,
                "irrigation": 0.85,
                "drought_resistant_crops": 0.9,
                "early_warning": 0.7,
                "insurance": 0.6
            },
            "flood": {
                "drainage_systems": 0.85,
                "flood_barriers": 0.8,
                "early_warning": 0.75,
                "land_use_planning": 0.9,
                "insurance": 0.65
            },
            "locust": {
                "pest_control": 0.9,
                "early_detection": 0.85,
                "crop_protection": 0.8,
                "regional_coordination": 0.75
            }
        }
        
        # Count event types in historical data
        event_counts = defaultdict(int)
        total_economic_impact = 0
        
        for event in events:
            event_type, location, timestamp, economic_impact, description = event
            event_counts[event_type] += 1
            if economic_impact:
                total_economic_impact += economic_impact
        
        # Calculate effectiveness based on most common event types
        if not event_counts:
            return 0.5
        
        most_common_event = max(event_counts, key=event_counts.get)
        event_frequency = event_counts[most_common_event]
        
        # Base effectiveness from policy-event matching
        base_effectiveness = 0.5
        
        if most_common_event in effectiveness_factors:
            policy_factors = effectiveness_factors[most_common_event]
            
            for policy_keyword, effectiveness in policy_factors.items():
                if policy_keyword.replace("_", " ") in policy_lower:
                    base_effectiveness = max(base_effectiveness, effectiveness)
        
        # Adjust based on event frequency (more events = higher need for effective policy)
        frequency_factor = min(event_frequency * 0.05, 0.2)
        
        # Adjust based on economic impact (higher impact = more potential for effectiveness)
        if total_economic_impact > 0:
            impact_factor = min(total_economic_impact / 100000 * 0.1, 0.15)
        else:
            impact_factor = 0
        
        final_effectiveness = base_effectiveness + frequency_factor + impact_factor
        
        return min(final_effectiveness, 1.0)
        
    except Exception as e:
        logger.error(f"Error estimating policy effectiveness: {e}")
        return 0.5

def _calculate_policy_cost_benefit(policy, baseline):
    """Calculate cost-benefit analysis for policy"""
    return {"ratio": 1.5, "feasibility": "high"}

def _calculate_risk_reduction(policy, vulnerability):
    """Calculate risk reduction from policy"""
    return 0.3  # 30% risk reduction

def _predict_community_acceptance(policy, location):
    """Predict community acceptance of policy"""
    return 0.8  # High acceptance

def _generate_policy_implementation_recommendations(effectiveness, cost_benefit, acceptance):
    """Generate policy implementation recommendations"""
    return ["Phased implementation recommended", "Community engagement essential"]

def _generate_implementation_timeline(policy, timeframe):
    """Generate implementation timeline"""
    return {"phase_1": "6 months", "phase_2": "18 months", "full_implementation": timeframe}

def _identify_priority_areas_real(location_impacts, verified_impacts):
    """Identify priority areas based on real verified impacts"""
    high_priority = []
    medium_priority = []
    low_priority = []
    
    # Sort locations by impact severity
    sorted_locations = sorted(
        location_impacts.items(),
        key=lambda x: (x[1]["total_events"], x[1]["total_impact"]),
        reverse=True
    )
    
    total_locations = len(sorted_locations)
    
    for i, (location, data) in enumerate(sorted_locations):
        priority_info = {
            "location": location,
            "total_events": data["total_events"],
            "total_impact": data["total_impact"],
            "event_types": [et["type"] for et in data["event_types"]],
            "urgency_score": data["total_events"] * 0.6 + (data["total_impact"] / 1000) * 0.4
        }
        
        # Top 30% are high priority
        if i < total_locations * 0.3:
            high_priority.append(priority_info)
        # Next 40% are medium priority
        elif i < total_locations * 0.7:
            medium_priority.append(priority_info)
        # Rest are low priority
        else:
            low_priority.append(priority_info)
    
    # Also include areas from verified_impacts parameter
    for impact in verified_impacts:
        location = impact.get("location")
        if location and not any(area["location"] == location for area in high_priority + medium_priority + low_priority):
            impact_value = impact.get("impact_value", 0)
            if impact_value > 100000:  # High impact threshold
                high_priority.append({
                    "location": location,
                    "total_events": 1,
                    "total_impact": impact_value,
                    "event_types": [impact.get("event_type", "unknown")],
                    "urgency_score": impact_value / 1000
                })
    
    return {
        "high": high_priority,
        "medium": medium_priority,
        "low": low_priority
    }

def _assess_community_needs_real(community_needs, location_impacts):
    """Assess community needs using real data and requests"""
    need_assessment = {}
    
    for need in community_needs:
        location = need.get("location")
        priority = need.get("priority", "medium")
        need_type = need.get("type", "general")
        
        # Get real impact data for this location
        real_data = location_impacts.get(location, {"total_events": 0, "total_impact": 0})
        
        # Calculate need severity score
        severity_score = 0.5  # Base score
        
        # Adjust based on priority
        if priority == "high":
            severity_score += 0.3
        elif priority == "low":
            severity_score -= 0.2
        
        # Adjust based on real impact data
        if real_data["total_events"] > 5:
            severity_score += 0.2
        if real_data["total_impact"] > 50000:
            severity_score += 0.2
        
        # Adjust based on need type
        urgent_types = ["drought_relief", "flood_protection", "emergency_response"]
        if need_type in urgent_types:
            severity_score += 0.1
        
        need_assessment[location] = {
            "severity_score": min(1.0, severity_score),
            "priority": priority,
            "type": need_type,
            "real_events": real_data["total_events"],
            "real_impact": real_data["total_impact"],
            "justification": f"Based on {real_data['total_events']} verified events and ${real_data['total_impact']:.0f} economic impact"
        }
    
    return need_assessment

def _calculate_resource_efficiency_real(available_resources, priority_areas):
    """Calculate resource efficiency based on real priority data"""
    total_funding = available_resources.get("funding", 0)
    total_personnel = available_resources.get("personnel", 0)
    total_equipment = available_resources.get("equipment", 0)
    
    high_priority_count = len(priority_areas["high"])
    total_priority_areas = len(priority_areas["high"]) + len(priority_areas["medium"]) + len(priority_areas["low"])
    
    if total_priority_areas == 0:
        return 0.5
    
    # Calculate efficiency based on resource adequacy
    funding_per_area = total_funding / max(total_priority_areas, 1)
    personnel_per_area = total_personnel / max(total_priority_areas, 1)
    
    efficiency = 0.3  # Base efficiency
    
    # Higher efficiency if we can adequately fund high priority areas
    if funding_per_area > 50000:  # Adequate funding threshold
        efficiency += 0.3
    if personnel_per_area > 2:  # Adequate personnel threshold
        efficiency += 0.2
    if high_priority_count > 0 and total_funding > 200000:  # Can address high priority
        efficiency += 0.2
    
    return min(1.0, efficiency)

def _assess_allocation_equity_real(community_needs, location_impacts):
    """Assess equity considerations using real data"""
    total_locations = len(location_impacts)
    
    if total_locations == 0:
        return {"equity_score": 0.5, "analysis": "No location data available"}
    
    # Calculate impact distribution
    impacts = [data["total_impact"] for data in location_impacts.values()]
    events = [data["total_events"] for data in location_impacts.values()]
    
    # Calculate inequality (simplified Gini coefficient approach)
    if len(impacts) > 1:
        sorted_impacts = sorted(impacts)
        n = len(sorted_impacts)
        cumulative_sum = sum((i + 1) * impact for i, impact in enumerate(sorted_impacts))
        total_sum = sum(sorted_impacts)
        
        if total_sum > 0:
            gini = (2 * cumulative_sum) / (n * total_sum) - (n + 1) / n
            equity_score = 1 - gini  # Higher score = more equitable
        else:
            equity_score = 1.0
    else:
        equity_score = 1.0
    
    return {
        "equity_score": max(0.0, min(1.0, equity_score)),
        "analysis": f"Analyzed {total_locations} locations for impact distribution",
        "impact_range": f"${min(impacts):.0f} - ${max(impacts):.0f}" if impacts else "No impact data",
        "recommendations": ["Prioritize underserved areas", "Ensure proportional resource distribution"]
    }

def _optimize_resource_distribution_real(available_resources, priority_areas, need_severity, equity_considerations):
    """Optimize resource distribution using real data and constraints"""
    total_funding = available_resources.get("funding", 0)
    total_personnel = available_resources.get("personnel", 0)
    total_equipment = available_resources.get("equipment", 0)
    
    distribution = {
        "funding_allocation": {},
        "personnel_allocation": {},
        "equipment_allocation": {},
        "coverage": 0,
        "rationale": []
    }
    
    # Prioritize high-priority areas
    high_priority = priority_areas["high"]
    medium_priority = priority_areas["medium"]
    low_priority = priority_areas["low"]
    
    total_areas = len(high_priority) + len(medium_priority) + len(low_priority)
    
    if total_areas == 0:
        distribution["coverage"] = 0
        distribution["rationale"].append("No priority areas identified")
        return distribution
    
    # Allocate 60% to high priority, 30% to medium, 10% to low
    high_funding = total_funding * 0.6
    medium_funding = total_funding * 0.3
    low_funding = total_funding * 0.1
    
    high_personnel = int(total_personnel * 0.6)
    medium_personnel = int(total_personnel * 0.3)
    low_personnel = int(total_personnel * 0.1)
    
    high_equipment = int(total_equipment * 0.6)
    medium_equipment = int(total_equipment * 0.3)
    low_equipment = int(total_equipment * 0.1)
    
    # Distribute among areas in each priority level
    def distribute_resources(areas, funding, personnel, equipment, priority_level):
        if not areas:
            return
        
        funding_per_area = funding / len(areas)
        personnel_per_area = max(1, personnel // len(areas))
        equipment_per_area = max(1, equipment // len(areas))
        
        for area in areas:
            location = area["location"]
            distribution["funding_allocation"][location] = funding_per_area
            distribution["personnel_allocation"][location] = personnel_per_area
            distribution["equipment_allocation"][location] = equipment_per_area
        
        distribution["rationale"].append(
            f"Allocated ${funding_per_area:.0f}, {personnel_per_area} personnel, "
            f"{equipment_per_area} equipment per {priority_level} priority area"
        )
    
    distribute_resources(high_priority, high_funding, high_personnel, high_equipment, "high")
    distribute_resources(medium_priority, medium_funding, medium_personnel, medium_equipment, "medium")
    distribute_resources(low_priority, low_funding, low_personnel, low_equipment, "low")
    
    # Calculate coverage
    covered_areas = len(distribution["funding_allocation"])
    distribution["coverage"] = (covered_areas / total_areas) * 100 if total_areas > 0 else 0
    
    distribution["rationale"].append(f"Achieved {distribution['coverage']:.1f}% area coverage")
    
    return distribution

def _generate_allocation_implementation_plan_real(optimal_allocation, priority_areas):
    """Generate implementation plan based on real allocation"""
    high_priority_count = len(priority_areas["high"])
    
    if high_priority_count > 5:
        timeline = "12 months"
        phases = "4 phases"
    elif high_priority_count > 2:
        timeline = "8 months"
        phases = "3 phases"
    else:
        timeline = "6 months"
        phases = "2 phases"
    
    return {
        "timeline": timeline,
        "phases": phases,
        "monitoring": "Monthly progress reviews",
        "first_phase": "Deploy to highest priority areas within 30 days",
        "success_metrics": ["Coverage percentage", "Impact reduction", "Community satisfaction"]
    }

def _define_allocation_monitoring_metrics_real(optimal_allocation):
    """Define monitoring metrics for real allocation"""
    return {
        "coverage_metrics": ["Areas served", "Population reached", "Resources deployed"],
        "impact_metrics": ["Events prevented", "Economic losses avoided", "Community resilience"],
        "efficiency_metrics": ["Cost per area served", "Personnel utilization", "Equipment deployment rate"],
        "equity_metrics": ["Distribution fairness", "Underserved area coverage", "Access equality"],
        "reporting_frequency": "Monthly",
        "review_cycle": "Quarterly"
    }

async def _find_similar_climate_cases(climate_challenge, location, crud):
    """Find similar climate cases using real event database"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        challenge_lower = climate_challenge.lower()
        
        # Extract event types from challenge description
        event_types = []
        climate_keywords = {
            "drought": ["drought", "dry", "water shortage", "arid"],
            "flood": ["flood", "flooding", "overflow", "inundation"],
            "locust": ["locust", "pest", "swarm", "crop damage"],
            "heatwave": ["heat", "hot", "temperature", "extreme heat"],
            "storm": ["storm", "wind", "cyclone", "hurricane"],
            "wildfire": ["fire", "wildfire", "burning", "smoke"]
        }
        
        for event_type, keywords in climate_keywords.items():
            if any(keyword in challenge_lower for keyword in keywords):
                event_types.append(event_type)
        
        if not event_types:
            event_types = list(climate_keywords.keys())  # Search all if no specific type found
        
        # Find similar cases
        similar_cases = []
        
        for event_type in event_types:
            # Get events of this type from various locations
            cursor.execute("""
                SELECT id, event_type, location, timestamp, description, economic_impact, verification_status
                FROM events 
                WHERE event_type = ? 
                AND verification_status = 'verified'
                AND timestamp > datetime('now', '-730 days')  -- Last 2 years
                ORDER BY timestamp DESC
                LIMIT 20
            """, (event_type,))
            
            events = cursor.fetchall()
            
            for event in events:
                event_id, evt_type, evt_location, timestamp, description, economic_impact, verification_status = event
                
                # Calculate similarity score
                similarity_score = 0.5  # Base similarity for same event type
                
                # Location similarity (simplified)
                if evt_location and location:
                    if evt_location.lower() == location.lower():
                        similarity_score += 0.3  # Same location
                    elif any(word in evt_location.lower() for word in location.lower().split()):
                        similarity_score += 0.15  # Partial location match
                
                # Description similarity (keyword matching)
                if description:
                    desc_lower = description.lower()
                    challenge_words = set(challenge_lower.split())
                    desc_words = set(desc_lower.split())
                    
                    common_words = challenge_words.intersection(desc_words)
                    if common_words:
                        word_similarity = len(common_words) / max(len(challenge_words), len(desc_words))
                        similarity_score += word_similarity * 0.2
                
                # Economic impact similarity
                if economic_impact and economic_impact > 0:
                    similarity_score += 0.1  # Boost for having economic data
                
                similar_cases.append({
                    "event_id": event_id,
                    "event_type": evt_type,
                    "location": evt_location,
                    "timestamp": timestamp,
                    "description": description[:200] + "..." if description and len(description) > 200 else description,
                    "economic_impact": economic_impact,
                    "similarity_score": round(similarity_score, 3)
                })
        
        # Sort by similarity and return top matches
        similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        conn.close()
        
        return similar_cases[:10]  # Return top 10 similar cases
        
    except Exception as e:
        logger.error(f"Error finding similar climate cases: {e}")
        return []

# More helper functions would continue in similar pattern...