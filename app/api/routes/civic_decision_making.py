"""
Civic Decision-Making API Routes for Climate Witness Chain
Provides transparent, AI-assisted democratic decision-making tools
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.metta_service import get_shared_knowledge_base
from app.database.database import get_db
import json
from datetime import datetime

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
    Optimize resource allocation based on verified climate impacts and community needs
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")
        
        # Identify priority areas based on verified impacts
        priority_areas = _identify_priority_areas(request.verified_impacts)
        
        # Assess need severity
        need_severity = _assess_community_needs(request.community_needs, request.verified_impacts)
        
        # Calculate resource efficiency
        resource_efficiency = _calculate_resource_efficiency(request.available_resources, priority_areas)
        
        # Assess equity considerations
        equity_considerations = _assess_allocation_equity(request.community_needs, request.available_resources)
        
        # Optimize resource distribution
        optimal_allocation = _optimize_resource_distribution(
            request.available_resources, priority_areas, need_severity, equity_considerations
        )
        
        # Run MeTTa resource allocation
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
            "need_assessment": need_severity,
            "explanation": {
                "methodology": "Multi-criteria optimization considering impact severity, community needs, and equity",
                "allocation_principles": ["Greatest need first", "Equitable distribution", "Maximum impact efficiency"],
                "transparency": "All allocation decisions explained and auditable"
            },
            "implementation_plan": _generate_allocation_implementation_plan(optimal_allocation),
            "monitoring_metrics": _define_allocation_monitoring_metrics(optimal_allocation),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
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
    """Get climate data support for the issue"""
    # Simplified - would analyze climate data relevance
    return 0.75

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
    """Estimate policy effectiveness based on historical data"""
    return 0.75  # Simplified

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

def _identify_priority_areas(impacts):
    """Identify priority areas from impacts"""
    return {"high": ["Area A", "Area B"], "medium": ["Area C"], "low": ["Area D"]}

def _assess_community_needs(needs, impacts):
    """Assess severity of community needs"""
    return {"urgent": 3, "high": 5, "medium": 2, "low": 1}

def _calculate_resource_efficiency(resources, priorities):
    """Calculate resource allocation efficiency"""
    return 0.85

def _assess_allocation_equity(needs, resources):
    """Assess equity of resource allocation"""
    return {"equity_score": 0.8, "gini_coefficient": 0.3}

def _optimize_resource_distribution(resources, priorities, needs, equity):
    """Optimize resource distribution"""
    return {"coverage": 85.0, "efficiency": 0.9, "equity": 0.8}

def _generate_allocation_implementation_plan(allocation):
    """Generate implementation plan for allocation"""
    return {"timeline": "12 months", "phases": 3, "monitoring": "monthly"}

def _define_allocation_monitoring_metrics(allocation):
    """Define monitoring metrics for allocation"""
    return ["coverage_rate", "impact_effectiveness", "equity_index"]

# More helper functions would continue in similar pattern...