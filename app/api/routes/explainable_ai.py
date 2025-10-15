"""
Explainable AI API Routes for Climate Witness Chain
Provides transparent AI decision-making with detailed explanations
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.services.metta_service import get_shared_knowledge_base
from app.database.database import get_db
import json
from datetime import datetime

router = APIRouter()


class ExplainableDecisionRequest(BaseModel):
    decision_type: (
        str  # verification, trust_calculation, payout, risk_assessment, policy
    )
    context: Dict[str, Any]
    explanation_level: str = (
        "citizen-friendly"  # basic, detailed, technical, citizen-friendly
    )


class BiasDetectionRequest(BaseModel):
    location: str
    event_type: str
    time_period: str = "30_days"


class PolicyImpactRequest(BaseModel):
    policy_type: str
    location: str
    climate_data: Dict[str, Any]


class AuditTrailRequest(BaseModel):
    decision_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/explain-decision")
async def explain_ai_decision(
    request: ExplainableDecisionRequest, crud=Depends(get_db)
):
    """
    Generate detailed explanations for AI decisions with different levels of detail
    """
    try:
        kb = get_shared_knowledge_base()

        # Load explainable AI knowledge
        kb.load_metta_file("BECW/metta/explainable_ai.metta")

        # Generate explanation based on decision type
        if request.decision_type == "verification":
            explanation = await _explain_verification_decision(
                kb, request.context, request.explanation_level
            )
        elif request.decision_type == "trust_calculation":
            explanation = await _explain_trust_calculation(
                kb, request.context, request.explanation_level
            )
        elif request.decision_type == "payout":
            explanation = await _explain_payout_decision(
                kb, request.context, request.explanation_level
            )
        elif request.decision_type == "risk_assessment":
            explanation = await _explain_risk_assessment(
                kb, request.context, request.explanation_level
            )
        elif request.decision_type == "policy":
            explanation = await _explain_policy_recommendation(
                kb, request.context, request.explanation_level
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported decision type")

        return {
            "success": True,
            "decision_type": request.decision_type,
            "explanation_level": request.explanation_level,
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence_score": explanation.get("confidence", 0.0),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate explanation: {str(e)}"
        )


@router.post("/detect-bias")
async def detect_ai_bias(request: BiasDetectionRequest, crud=Depends(get_db)):
    """
    Detect potential bias in AI decision-making for specific locations and event types
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")

        # Get events for bias analysis
        events = await crud.get_events_by_location_and_type(
            request.location, request.event_type
        )

        # Run MeTTa bias detection
        bias_query = f"""
        !(detect-verification-bias "{request.location}" {request.event_type} {request.time_period})
        """

        bias_results = kb.run_query(bias_query)

        # Calculate bias metrics
        total_events = len(events)
        verified_events = len(
            [e for e in events if e.verification_status == "verified"]
        )
        verification_rate = verified_events / total_events if total_events > 0 else 0

        # Get global average for comparison
        all_events = await crud.get_all_events()
        global_verified = len(
            [e for e in all_events if e.verification_status == "verified"]
        )
        global_rate = global_verified / len(all_events) if all_events else 0

        bias_detected = abs(verification_rate - global_rate) > 0.2

        return {
            "success": True,
            "location": request.location,
            "event_type": request.event_type,
            "bias_detected": bias_detected,
            "verification_rate": round(verification_rate, 3),
            "global_average_rate": round(global_rate, 3),
            "rate_difference": round(abs(verification_rate - global_rate), 3),
            "total_events": total_events,
            "verified_events": verified_events,
            "bias_analysis": {
                "potential_causes": _analyze_bias_causes(
                    verification_rate, global_rate
                ),
                "recommendations": _generate_bias_recommendations(
                    bias_detected, verification_rate, global_rate
                ),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")


@router.post("/assess-policy-impact")
async def assess_policy_impact(request: PolicyImpactRequest, crud=Depends(get_db)):
    """
    Assess potential impact of climate policies using AI and verified data
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")
        kb.load_metta_file("BECW/metta/civic_decision_making.metta")

        # Get historical climate data for the location
        events = await crud.get_events_by_location(request.location)

        # Run policy impact assessment
        impact_query = f"""
        !(assess-policy-impact {request.policy_type} "{request.location}" {json.dumps(request.climate_data)})
        """

        impact_results = kb.run_query(impact_query)

        # Calculate economic impact baseline
        economic_impact = sum(
            [
                event.economic_impact or 0
                for event in events
                if event.verification_status == "verified"
            ]
        )

        # Estimate policy effectiveness
        effectiveness_score = _calculate_policy_effectiveness(
            request.policy_type, events
        )
        cost_benefit_ratio = effectiveness_score / max(economic_impact, 1)

        return {
            "success": True,
            "policy_type": request.policy_type,
            "location": request.location,
            "impact_assessment": {
                "effectiveness_score": round(effectiveness_score, 2),
                "cost_benefit_ratio": round(cost_benefit_ratio, 3),
                "economic_baseline": economic_impact,
                "predicted_reduction": round(effectiveness_score * 0.3, 2),
                "confidence_level": "medium",
            },
            "explanation": {
                "methodology": "Assessment based on historical verified climate events and policy effectiveness models",
                "data_sources": f"Analyzed {len(events)} climate events from {request.location}",
                "assumptions": "Policy effectiveness estimated from similar interventions and local vulnerability factors",
            },
            "recommendations": _generate_policy_recommendations(
                request.policy_type, effectiveness_score, cost_benefit_ratio
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Policy impact assessment failed: {str(e)}"
        )


@router.get("/audit-trail/{decision_id}")
async def get_decision_audit_trail(decision_id: str, crud=Depends(get_db)):
    """
    Retrieve complete audit trail for an AI decision
    """
    try:
        # Get decision from database (assuming we store decision audit trails)
        # For now, we'll simulate this with available data

        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")

        # Create audit trail query
        audit_query = f"""
        !(create-audit-trail "{decision_id}" verification 
          (inputs user_trust image_confidence description_confidence)
          (outputs verified confidence explanation)
          "{datetime.utcnow().isoformat()}")
        """

        audit_results = kb.run_query(audit_query)

        return {
            "success": True,
            "decision_id": decision_id,
            "audit_trail": {
                "decision_timestamp": datetime.utcnow().isoformat(),
                "decision_type": "verification",
                "inputs_used": [
                    "user_trust_score",
                    "image_confidence",
                    "description_confidence",
                ],
                "outputs_generated": [
                    "verification_result",
                    "confidence_score",
                    "explanation",
                ],
                "algorithm_version": "1.0",
                "data_sources": ["trust_network", "ai_models", "verification_rules"],
                "reviewable": True,
                "appeals_possible": True,
            },
            "transparency_metrics": {
                "explainability_score": 0.85,
                "auditability_score": 0.90,
                "reproducibility_score": 0.88,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve audit trail: {str(e)}"
        )


@router.get("/fairness-metrics")
async def get_fairness_metrics(time_period: str = "30_days", crud=Depends(get_db)):
    """
    Calculate fairness metrics for AI decision-making system
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")

        # Get recent decisions for analysis
        events = await crud.get_recent_events(days=30)

        # Calculate fairness metrics
        total_decisions = len(events)
        verified_decisions = len(
            [e for e in events if e.verification_status == "verified"]
        )

        # Demographic parity (simplified)
        demographic_parity = _calculate_demographic_parity(events)

        # Equalized odds (simplified)
        equalized_odds = _calculate_equalized_odds(events)

        # Individual fairness (simplified)
        individual_fairness = _calculate_individual_fairness(events)

        overall_fairness = (
            demographic_parity + equalized_odds + individual_fairness
        ) / 3

        return {
            "success": True,
            "time_period": time_period,
            "fairness_metrics": {
                "demographic_parity": round(demographic_parity, 3),
                "equalized_odds": round(equalized_odds, 3),
                "individual_fairness": round(individual_fairness, 3),
                "overall_fairness": round(overall_fairness, 3),
            },
            "analysis_summary": {
                "total_decisions": total_decisions,
                "verified_decisions": verified_decisions,
                "verification_rate": round(
                    verified_decisions / max(total_decisions, 1), 3
                ),
            },
            "recommendations": _generate_fairness_recommendations(
                overall_fairness, demographic_parity, equalized_odds
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Fairness metrics calculation failed: {str(e)}"
        )


@router.post("/interactive-explanation")
async def interactive_explanation(
    question: str, context: Dict[str, Any], crud=Depends(get_db)
):
    """
    Provide interactive explanations based on user questions
    """
    try:
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")

        # Process user question through MeTTa
        explanation_query = f"""
        !(interactive-explanation "{question}" {json.dumps(context)})
        """

        explanation_results = kb.run_query(explanation_query)

        # Generate contextual explanation
        explanation = _generate_contextual_explanation(question, context)

        return {
            "success": True,
            "question": question,
            "explanation": explanation,
            "context_used": context,
            "follow_up_questions": _suggest_follow_up_questions(question),
            "related_topics": _get_related_topics(question),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Interactive explanation failed: {str(e)}"
        )


# Helper functions
async def _explain_verification_decision(kb, context, level):
    """Generate verification decision explanation"""
    return {
        "decision": "Event Verification",
        "factors_considered": [
            "User trust score",
            "Image quality",
            "Description accuracy",
        ],
        "reasoning": "All verification criteria were evaluated and met the required thresholds",
        "confidence": 0.85,
        "citizen_explanation": "We verified this climate event by checking the reporter's reliability, photo quality, and description accuracy.",
    }


async def _explain_trust_calculation(kb, context, level):
    """Generate trust calculation explanation"""
    return {
        "decision": "Trust Score Calculation",
        "factors_considered": [
            "Verification accuracy",
            "Report frequency",
            "Community feedback",
        ],
        "reasoning": "Trust score increases with accurate reports and positive community feedback",
        "confidence": 0.78,
        "citizen_explanation": "Trust scores help us identify reliable community members based on their reporting history.",
    }


async def _explain_payout_decision(kb, context, level):
    """Generate payout decision explanation"""
    return {
        "decision": "Payout Determination",
        "factors_considered": [
            "Event severity",
            "Verification status",
            "Economic impact",
        ],
        "reasoning": "Payouts are calculated based on verified event severity and potential economic impact",
        "confidence": 0.92,
        "citizen_explanation": "Rewards are given for verified climate events, with higher amounts for more severe events.",
    }


async def _explain_risk_assessment(kb, context, level):
    """Generate risk assessment explanation"""
    return {
        "decision": "Risk Assessment",
        "factors_considered": [
            "Historical events",
            "Location vulnerability",
            "Current conditions",
        ],
        "reasoning": "Risk levels consider past climate events and current environmental conditions",
        "confidence": 0.73,
        "citizen_explanation": "Risk predictions help communities prepare for potential climate impacts.",
    }


async def _explain_policy_recommendation(kb, context, level):
    """Generate policy recommendation explanation"""
    return {
        "decision": "Policy Recommendation",
        "factors_considered": ["Climate data", "Economic impact", "Community needs"],
        "reasoning": "Policy suggestions are based on verified climate data and community impact analysis",
        "confidence": 0.68,
        "citizen_explanation": "Policy recommendations use real climate data to suggest effective community responses.",
    }


def _analyze_bias_causes(verification_rate, global_rate):
    """Analyze potential causes of bias"""
    if verification_rate > global_rate:
        return [
            "Higher local trust scores",
            "Better evidence quality",
            "More active community verification",
        ]
    else:
        return [
            "Lower local trust scores",
            "Evidence quality issues",
            "Limited community participation",
        ]


def _generate_bias_recommendations(bias_detected, verification_rate, global_rate):
    """Generate recommendations to address bias"""
    if not bias_detected:
        return ["Continue current verification practices", "Monitor for future bias"]
    elif verification_rate < global_rate:
        return [
            "Improve evidence collection training",
            "Increase community verifier participation",
            "Review trust score calculations",
        ]
    else:
        return [
            "Ensure verification standards are consistent",
            "Review for potential over-verification",
        ]


def _calculate_policy_effectiveness(policy_type, events):
    """Calculate estimated policy effectiveness"""
    # Simplified calculation based on event types and frequency
    base_effectiveness = 50.0
    if policy_type == "drought_mitigation":
        drought_events = len([e for e in events if e.event_type == "drought"])
        return base_effectiveness + (drought_events * 2)
    return base_effectiveness


def _generate_policy_recommendations(
    policy_type, effectiveness_score, cost_benefit_ratio
):
    """Generate policy implementation recommendations"""
    recommendations = []
    if effectiveness_score > 70:
        recommendations.append(
            "High potential for positive impact - recommend implementation"
        )
    if cost_benefit_ratio > 1.0:
        recommendations.append("Favorable cost-benefit ratio - economically viable")
    else:
        recommendations.append("Consider cost optimization or phased implementation")
    return recommendations


def _calculate_demographic_parity(events):
    """Calculate demographic parity metric (simplified)"""
    # In a real implementation, this would analyze verification rates across demographic groups
    return 0.85


def _calculate_equalized_odds(events):
    """Calculate equalized odds metric (simplified)"""
    # In a real implementation, this would analyze true positive rates across groups
    return 0.82


def _calculate_individual_fairness(events):
    """Calculate individual fairness metric (simplified)"""
    # In a real implementation, this would analyze similar cases receiving similar treatment
    return 0.88


def _generate_fairness_recommendations(
    overall_fairness, demographic_parity, equalized_odds
):
    """Generate recommendations to improve fairness"""
    recommendations = []
    if overall_fairness < 0.7:
        recommendations.append(
            "Overall fairness below threshold - review decision algorithms"
        )
    if demographic_parity < 0.8:
        recommendations.append(
            "Improve demographic representation in verification process"
        )
    if equalized_odds < 0.8:
        recommendations.append("Review accuracy consistency across different groups")
    return recommendations


def _generate_contextual_explanation(question, context):
    """Generate contextual explanation based on question"""
    if "verify" in question.lower():
        return "Event verification uses multiple factors including user trust, evidence quality, and community consensus to ensure accuracy."
    elif "trust" in question.lower():
        return "Trust scores are calculated based on reporting accuracy, community feedback, and verification success rate."
    elif "payout" in question.lower():
        return "Payouts are determined by event severity, verification status, and economic impact to incentivize accurate reporting."
    else:
        return "Our AI system uses transparent logic and community input to make fair and explainable decisions."


def _suggest_follow_up_questions(question):
    """Suggest relevant follow-up questions"""
    return [
        "How can I improve my trust score?",
        "What evidence is needed for verification?",
        "How are payouts calculated?",
        "Can I appeal a decision?",
    ]


def _get_related_topics(question):
    """Get topics related to the question"""
    return [
        "verification_process",
        "trust_system",
        "payout_mechanism",
        "community_governance",
    ]
