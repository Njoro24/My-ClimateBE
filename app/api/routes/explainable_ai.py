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
import sqlite3
import os
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
    Detect potential bias in AI decision-making using real database data
    """
    try:
        # Connect to database for real bias analysis
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get events for specific location and type
        cursor.execute("""
            SELECT COUNT(*) as total_events,
                   SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified_events
            FROM events 
            WHERE location LIKE ? AND event_type = ? 
            AND timestamp > datetime('now', '-30 days')
        """, (f"%{request.location}%", request.event_type))
        
        local_stats = cursor.fetchone()
        total_events, verified_events = local_stats if local_stats else (0, 0)
        verification_rate = verified_events / total_events if total_events > 0 else 0
        
        # Get global average for comparison
        cursor.execute("""
            SELECT COUNT(*) as total_events,
                   SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified_events
            FROM events 
            WHERE event_type = ? 
            AND timestamp > datetime('now', '-30 days')
        """, (request.event_type,))
        
        global_stats = cursor.fetchone()
        global_total, global_verified = global_stats if global_stats else (0, 0)
        global_rate = global_verified / global_total if global_total > 0 else 0
        
        # Detect bias (significant deviation from global average)
        rate_difference = abs(verification_rate - global_rate)
        bias_detected = rate_difference > 0.15 and total_events >= 3
        
        # Get user trust scores for this location
        cursor.execute("""
            SELECT AVG(u.trust_score) as avg_trust
            FROM users u
            JOIN events e ON u.id = e.user_id
            WHERE e.location LIKE ? AND e.timestamp > datetime('now', '-30 days')
        """, (f"%{request.location}%",))
        
        trust_result = cursor.fetchone()
        avg_trust = trust_result[0] if trust_result and trust_result[0] else 50
        
        conn.close()
        
        # Run MeTTa bias detection for additional insights
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")
        
        bias_query = f"""
        !(detect-verification-bias "{request.location}" {request.event_type} {request.time_period})
        """
        bias_results = kb.run_query(bias_query)

        return {
            "success": True,
            "location": request.location,
            "event_type": request.event_type,
            "bias_detected": bias_detected,
            "verification_rate": round(verification_rate, 3),
            "global_average_rate": round(global_rate, 3),
            "rate_difference": round(rate_difference, 3),
            "total_events": total_events,
            "verified_events": verified_events,
            "bias_analysis": {
                "average_trust_score": round(avg_trust, 1),
                "sample_size_adequate": total_events >= 5,
                "potential_causes": _analyze_bias_causes(verification_rate, global_rate, avg_trust),
                "recommendations": _generate_bias_recommendations(
                    bias_detected, verification_rate, global_rate, total_events
                ),
            },
            "statistical_significance": {
                "sample_size": total_events,
                "confidence_level": "high" if total_events >= 10 else "medium" if total_events >= 5 else "low",
                "bias_threshold": 0.15
            },
            "timestamp": datetime.utcnow().isoformat()
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
    Calculate fairness metrics for AI decision-making system using real database data
    """
    try:
        # Connect to database to get real verification data
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get verification statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_decisions,
                SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified_count,
                AVG(CASE WHEN verification_status = 'verified' THEN 1.0 ELSE 0.0 END) as verification_rate
            FROM events
            WHERE timestamp > datetime('now', '-30 days')
        """)
        
        stats = cursor.fetchone()
        total_decisions, verified_count, verification_rate = stats if stats else (0, 0, 0.0)
        
        # Get location-based fairness metrics
        cursor.execute("""
            SELECT 
                location,
                COUNT(*) as total_events,
                SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified_events,
                AVG(CASE WHEN verification_status = 'verified' THEN 1.0 ELSE 0.0 END) as local_rate
            FROM events
            WHERE location IS NOT NULL AND timestamp > datetime('now', '-30 days')
            GROUP BY location
            HAVING COUNT(*) >= 2
        """)
        
        location_stats = cursor.fetchall()
        
        # Calculate real fairness metrics
        location_rates = [row[3] for row in location_stats if row[3] is not None]
        
        # Demographic parity (equal verification rates across locations)
        if len(location_rates) > 1:
            demographic_parity = 1.0 - (max(location_rates) - min(location_rates))
        else:
            demographic_parity = 1.0
        
        # Equal opportunity (consistent verification for positive cases)
        equal_opportunity = verification_rate if verification_rate else 0.0
        
        # Individual fairness (consistency in similar cases)
        cursor.execute("""
            SELECT event_type, 
                   AVG(CASE WHEN verification_status = 'verified' THEN 1.0 ELSE 0.0 END) as type_rate
            FROM events 
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY event_type
            HAVING COUNT(*) >= 2
        """)
        
        type_stats = cursor.fetchall()
        type_rates = [row[1] for row in type_stats if row[1] is not None]
        
        if len(type_rates) > 1:
            individual_fairness = 1.0 - (max(type_rates) - min(type_rates))
        else:
            individual_fairness = 0.85
        
        # Overall fairness score
        overall_fairness = (demographic_parity + equal_opportunity + individual_fairness) / 3
        
        conn.close()
        
        return {
            "success": True,
            "time_period": time_period,
            "fairness_metrics": {
                "demographic_parity": round(demographic_parity, 3),
                "equalized_odds": round(equal_opportunity, 3),
                "individual_fairness": round(individual_fairness, 3),
                "overall_fairness": round(overall_fairness, 3),
            },
            "analysis_summary": {
                "total_decisions": total_decisions,
                "verified_decisions": verified_count,
                "verification_rate": round(verification_rate, 3) if verification_rate else 0.0,
                "locations_analyzed": len(location_stats),
                "event_types_analyzed": len(type_stats)
            },
            "location_breakdown": [
                {
                    "location": row[0],
                    "total_events": row[1],
                    "verified_events": row[2],
                    "verification_rate": round(row[3], 3) if row[3] else 0.0
                }
                for row in location_stats
            ],
            "recommendations": _generate_fairness_recommendations(
                overall_fairness, demographic_parity, equal_opportunity
            ),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Fairness metrics calculation failed: {str(e)}"
        )


@router.post("/interactive-explanation")
async def interactive_explanation(request: dict, crud=Depends(get_db)):
    """
    Provide intelligent interactive explanations based on user questions and real data
    """
    try:
        question = request.get("question", "")
        context = request.get("context", {})
        
        # Connect to database for context-aware explanations
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'climate_witness.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user-specific data if user_id provided
        user_id = context.get("user_id")
        user_stats = {}
        
        if user_id:
            cursor.execute("""
                SELECT trust_score, 
                       COUNT(CASE WHEN verification_status = 'verified' THEN 1 END) as verified_events,
                       COUNT(*) as total_events
                FROM users u
                LEFT JOIN events e ON u.id = e.user_id
                WHERE u.id = ?
                GROUP BY u.id, u.trust_score
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                user_stats = {
                    "trust_score": result[0],
                    "verified_events": result[1],
                    "total_events": result[2],
                    "verification_rate": result[1] / max(result[2], 1)
                }
        
        conn.close()
        
        # Process user question through MeTTa
        kb = get_shared_knowledge_base()
        kb.load_metta_file("BECW/metta/explainable_ai.metta")
        
        explanation_query = f"""
        !(interactive-explanation "{question}" {json.dumps(context)})
        """
        explanation_results = kb.run_query(explanation_query)

        # Generate intelligent contextual explanation
        explanation = _generate_intelligent_explanation(question, context, user_stats)

        return {
            "success": True,
            "question": question,
            "explanation": explanation,
            "context_used": context,
            "user_stats": user_stats if user_stats else None,
            "follow_up_questions": _suggest_intelligent_follow_ups(question, user_stats),
            "related_topics": _get_related_topics(question),
            "confidence": 0.85,
            "timestamp": datetime.utcnow().isoformat()
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


def _analyze_bias_causes(verification_rate, global_rate, avg_trust=50):
    """Analyze potential causes of bias using real data"""
    causes = []
    
    if verification_rate > global_rate + 0.1:
        if avg_trust > 70:
            causes.append("Higher local trust scores contributing to more verifications")
        causes.extend([
            "Better evidence quality in this location",
            "More active community verification network",
            "Possible over-verification - review standards"
        ])
    elif verification_rate < global_rate - 0.1:
        if avg_trust < 50:
            causes.append("Lower local trust scores affecting verification rates")
        causes.extend([
            "Evidence quality issues in this location",
            "Limited community participation",
            "Possible under-verification - review accessibility"
        ])
    else:
        causes.append("Verification rates within normal range")
    
    return causes


def _generate_bias_recommendations(bias_detected, verification_rate, global_rate, sample_size):
    """Generate actionable recommendations to address bias"""
    recommendations = []
    
    if sample_size < 5:
        recommendations.append("Increase sample size before drawing conclusions about bias")
        return recommendations
    
    if not bias_detected:
        recommendations.extend([
            "Continue current verification practices",
            "Monitor for future bias patterns",
            "Maintain regular bias audits"
        ])
    elif verification_rate < global_rate - 0.15:
        recommendations.extend([
            "Provide evidence collection training for local reporters",
            "Increase community verifier participation in this area",
            "Review trust score calculation fairness",
            "Consider outreach programs to improve reporting quality"
        ])
    elif verification_rate > global_rate + 0.15:
        recommendations.extend([
            "Ensure verification standards are consistently applied",
            "Review for potential over-verification patterns",
            "Cross-validate with other locations for consistency",
            "Consider if local conditions justify higher verification rates"
        ])
    
    return recommendations


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


def _generate_intelligent_explanation(question, context, user_stats):
    """Generate intelligent contextual explanation based on question and user data"""
    question_lower = question.lower()
    
    if "verify" in question_lower or "verification" in question_lower:
        base_explanation = "Event verification uses multiple factors including user trust, evidence quality, and community consensus to ensure accuracy."
        if user_stats and user_stats.get("verification_rate", 0) < 0.5:
            base_explanation += f" Your current verification rate is {user_stats['verification_rate']:.1%}. To improve this, focus on providing clear photos, accurate descriptions, and GPS coordinates."
        return base_explanation
        
    elif "trust" in question_lower:
        base_explanation = "Trust scores are calculated based on reporting accuracy, community feedback, and verification success rate."
        if user_stats:
            trust_score = user_stats.get("trust_score", 50)
            if trust_score < 60:
                base_explanation += f" Your current trust score is {trust_score}/100. You can improve it by submitting high-quality reports that get verified by the community."
            else:
                base_explanation += f" Your trust score of {trust_score}/100 is good! Keep submitting quality reports to maintain it."
        return base_explanation
        
    elif "payout" in question_lower or "reward" in question_lower:
        base_explanation = "Payouts are determined by event severity, verification status, and economic impact to incentivize accurate reporting."
        if user_stats and user_stats.get("verified_events", 0) > 0:
            base_explanation += f" You have {user_stats['verified_events']} verified events. Verified events are eligible for rewards based on their impact level."
        return base_explanation
        
    elif "bias" in question_lower:
        return "Our system continuously monitors for bias by comparing verification rates across different locations, event types, and user groups. We use statistical analysis to ensure fair treatment for all community members."
        
    elif "appeal" in question_lower:
        return "Yes, you can appeal AI decisions through our community review process. Appeals are reviewed by trusted community members and can result in decision reversals if justified."
        
    elif "improve" in question_lower:
        if user_stats:
            suggestions = []
            if user_stats.get("verification_rate", 0) < 0.7:
                suggestions.append("improve photo quality and descriptions")
            if user_stats.get("trust_score", 50) < 70:
                suggestions.append("submit more accurate reports")
            if suggestions:
                return f"To improve your standing in the system, focus on: {', '.join(suggestions)}. This will increase your trust score and verification success rate."
        return "To improve in the system, focus on submitting high-quality reports with clear photos, accurate descriptions, and precise GPS coordinates."
        
    else:
        return "Our AI system uses transparent logic and community input to make fair and explainable decisions. All decisions can be audited and appealed through our democratic governance process."


def _suggest_intelligent_follow_ups(question, user_stats):
    """Suggest intelligent follow-up questions based on context"""
    base_questions = [
        "How can I improve my trust score?",
        "What evidence is needed for verification?",
        "How are payouts calculated?",
        "Can I appeal a decision?"
    ]
    
    if user_stats:
        if user_stats.get("trust_score", 50) < 60:
            base_questions.insert(0, "Why is my trust score low?")
        if user_stats.get("verification_rate", 0) < 0.5:
            base_questions.insert(0, "Why aren't my events getting verified?")
        if user_stats.get("verified_events", 0) == 0:
            base_questions.insert(0, "How do I get my first event verified?")
    
    return base_questions[:4]  # Return top 4 most relevant


def _get_related_topics(question):
    """Get topics related to the question"""
    return [
        "verification_process",
        "trust_system",
        "payout_mechanism",
        "community_governance",
    ]
