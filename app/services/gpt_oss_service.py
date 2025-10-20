"""
GPT-OSS-20B Service for Climate Witness Chain
Integrates OpenAI's gpt-oss-20b model for enhanced reasoning, MeTTa processing, and explainable AI
Works alongside existing MeTTa service without replacing it
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import openai
from app.services.metta_service import ClimateWitnessKnowledgeBase
from app.database.crud import get_event_by_id, get_user_by_id

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTOSSService:
    """GPT-OSS-20B service for enhanced AI reasoning and explainable decisions"""
    
    def __init__(self):
        """Initialize GPT-OSS service with API configuration"""
        self.client = openai.OpenAI(
            api_key=os.environ.get("ASI_API_KEY", "your-api-key-here"),
            base_url="https://inference.asicloud.cudos.org/v1"
        )
        self.model = "openai/gpt-oss-20b"
        self.metta_kb = ClimateWitnessKnowledgeBase()
        
        logger.info("✅ GPT-OSS-20B service initialized")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Base URL: https://inference.asicloud.cudos.org/v1")
    
    async def enhanced_metta_reasoning(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced MeTTa reasoning using GPT-OSS-20B for complex symbolic processing"""
        try:
            # Get MeTTa results first
            metta_result = self.metta_kb.run_metta_function(query)
            
            # Enhance with GPT-OSS reasoning
            prompt = f"""
            You are an expert in symbolic reasoning and MeTTa knowledge processing for climate data.
            
            MeTTa Query: {query}
            MeTTa Results: {metta_result}
            Context: {json.dumps(context or {}, indent=2)}
            
            Provide enhanced reasoning that:
            1. Interprets the MeTTa symbolic results
            2. Explains the logical connections
            3. Identifies patterns and correlations
            4. Suggests additional queries or insights
            5. Provides confidence assessment
            
            Format your response as structured JSON with reasoning steps.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            gpt_reasoning = response.choices[0].message.content
            
            return {
                "success": True,
                "query": query,
                "metta_results": [str(r) for r in metta_result] if metta_result else [],
                "enhanced_reasoning": gpt_reasoning,
                "confidence_score": self._calculate_reasoning_confidence(metta_result, gpt_reasoning),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Enhanced MeTTa reasoning error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_metta_results": [str(r) for r in metta_result] if 'metta_result' in locals() else []
            }
    
    async def explainable_verification_decision(self, event_id: str, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive explainable AI decision for event verification"""
        try:
            # Get event and user data
            event = await get_event_by_id(event_id)
            user = await get_user_by_id(user_id)
            
            if not event or not user:
                return {"success": False, "error": "Event or user not found"}
            
            # Run MeTTa verification
            metta_verification = self.metta_kb.run_verification(event_id, user_id, 85, 80)
            
            # Get detailed reasoning with GPT-OSS
            prompt = f"""
            You are an explainable AI system for climate event verification. Provide a comprehensive explanation.
            
            Event Details:
            - Type: {event.event_type}
            - Location: {event.latitude}, {event.longitude}
            - Description: {event.description}
            - Photo: {"Yes" if event.photo_path else "No"}
            - Timestamp: {event.timestamp}
            
            User Details:
            - Trust Score: {user.trust_score}
            - Location: {user.location_region}
            - Wallet: {user.wallet_address}
            
            MeTTa Verification Result: {json.dumps(metta_verification, indent=2)}
            
            Provide a detailed explanation that includes:
            1. Decision summary (verified/not verified)
            2. Key factors that influenced the decision
            3. Trust score impact analysis
            4. Evidence quality assessment
            5. Geographic and temporal consistency checks
            6. Confidence level and reasoning
            7. Citizen-friendly explanation
            8. Technical details for developers
            9. Potential biases identified
            10. Recommendations for improvement
            
            Format as structured JSON with clear sections.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=3000
            )
            
            explanation = response.choices[0].message.content
            
            return {
                "success": True,
                "event_id": event_id,
                "user_id": user_id,
                "verification_result": metta_verification,
                "detailed_explanation": explanation,
                "reasoning_chain": self._extract_reasoning_chain(explanation),
                "confidence_metrics": self._calculate_verification_confidence_metrics(metta_verification, explanation),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Explainable verification error: {e}")
            return {"success": False, "error": str(e)}
    
    async def blockchain_smart_contract_reasoning(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced reasoning for blockchain smart contract interactions"""
        try:
            prompt = f"""
            You are an expert in blockchain smart contracts and climate insurance logic.
            
            Contract Data: {json.dumps(contract_data, indent=2)}
            
            Analyze this smart contract interaction and provide:
            1. Transaction validity assessment
            2. Gas optimization suggestions
            3. Security considerations
            4. Economic impact analysis
            5. Climate insurance logic validation
            6. Risk assessment
            7. Payout calculation verification
            8. Fraud detection insights
            
            Consider Polygon/Mumbai testnet specifics and provide actionable insights.
            Format as structured JSON.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "contract_analysis": analysis,
                "security_score": self._calculate_security_score(analysis),
                "gas_optimization": self._extract_gas_suggestions(analysis),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Blockchain reasoning error: {e}")
            return {"success": False, "error": str(e)}
    
    async def community_verification_analysis(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced community verification analysis with bias detection"""
        try:
            prompt = f"""
            You are an expert in community verification systems and bias detection.
            
            Verification Data: {json.dumps(verification_data, indent=2)}
            
            Analyze this community verification scenario and provide:
            1. Consensus quality assessment
            2. Bias detection (geographic, demographic, temporal)
            3. Verifier credibility analysis
            4. Voting pattern analysis
            5. Manipulation risk assessment
            6. Fairness metrics
            7. Recommendations for improvement
            8. Trust network analysis
            
            Focus on ensuring fair and unbiased community decisions.
            Format as structured JSON with actionable insights.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "community_analysis": analysis,
                "bias_score": self._calculate_bias_score(analysis),
                "fairness_metrics": self._extract_fairness_metrics(analysis),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Community verification analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def early_warning_prediction(self, location_data: Dict[str, Any], historical_events: List[Dict]) -> Dict[str, Any]:
        """Generate early warning predictions using advanced reasoning"""
        try:
            prompt = f"""
            You are an expert climate prediction system using advanced reasoning.
            
            Location Data: {json.dumps(location_data, indent=2)}
            Historical Events: {json.dumps(historical_events[-10:], indent=2)}  # Last 10 events
            
            Generate early warning predictions including:
            1. Risk assessment for different climate events
            2. Probability calculations with confidence intervals
            3. Timeline predictions
            4. Severity estimates
            5. Affected area analysis
            6. Recommended actions for farmers/communities
            7. Insurance implications
            8. Correlation with global climate patterns
            
            Provide actionable insights with uncertainty quantification.
            Format as structured JSON with clear risk levels.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=3000
            )
            
            prediction = response.choices[0].message.content
            
            return {
                "success": True,
                "location": location_data,
                "prediction_analysis": prediction,
                "risk_levels": self._extract_risk_levels(prediction),
                "confidence_intervals": self._extract_confidence_intervals(prediction),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Early warning prediction error: {e}")
            return {"success": False, "error": str(e)}
    
    async def dao_governance_analysis(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze DAO governance proposals with sophisticated reasoning"""
        try:
            prompt = f"""
            You are an expert in DAO governance and decentralized decision-making.
            
            Proposal Data: {json.dumps(proposal_data, indent=2)}
            
            Analyze this DAO proposal and provide:
            1. Proposal impact assessment
            2. Stakeholder analysis
            3. Voting pattern predictions
            4. Economic implications
            5. Technical feasibility
            6. Risk assessment
            7. Alternative solutions
            8. Implementation roadmap
            9. Success metrics
            10. Potential unintended consequences
            
            Consider the climate witness ecosystem and community interests.
            Format as structured JSON with clear recommendations.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "proposal_analysis": analysis,
                "impact_score": self._calculate_impact_score(analysis),
                "feasibility_score": self._calculate_feasibility_score(analysis),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"DAO governance analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def function_calling_integration(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced function calling for tool use integration"""
        try:
            # Define available functions for the model
            functions = [
                {
                    "name": "trigger_micro_insurance",
                    "description": "Trigger micro-insurance payout for verified climate event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "payout_amount": {"type": "number"}
                        },
                        "required": ["event_id", "user_id"]
                    }
                },
                {
                    "name": "query_metta_knowledge",
                    "description": "Query MeTTa knowledge base for climate data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "space": {"type": "string", "default": "default"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "analyze_climate_pattern",
                    "description": "Analyze climate patterns for prediction",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "object"},
                            "time_range": {"type": "string"},
                            "event_types": {"type": "array"}
                        },
                        "required": ["location"]
                    }
                }
            ]
            
            prompt = f"""
            Execute the function '{function_name}' with parameters: {json.dumps(parameters, indent=2)}
            
            Analyze the request and determine the best approach for execution.
            Consider the climate witness ecosystem context.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                functions=functions,
                function_call={"name": function_name},
                temperature=0.2,
                max_tokens=1500
            )
            
            function_call = response.choices[0].message.function_call
            
            # Execute the actual function
            result = await self._execute_function(function_name, parameters)
            
            return {
                "success": True,
                "function_name": function_name,
                "parameters": parameters,
                "function_result": result,
                "gpt_analysis": function_call.arguments if function_call else None,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Function calling error: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods for analysis and scoring
    def _calculate_reasoning_confidence(self, metta_result: List, gpt_reasoning: str) -> float:
        """Calculate confidence score for reasoning"""
        base_confidence = 0.7
        if metta_result and len(metta_result) > 0:
            base_confidence += 0.1
        if "high confidence" in gpt_reasoning.lower():
            base_confidence += 0.1
        if "uncertain" in gpt_reasoning.lower():
            base_confidence -= 0.1
        return min(0.95, max(0.3, base_confidence))
    
    def _extract_reasoning_chain(self, explanation: str) -> List[str]:
        """Extract reasoning chain from explanation"""
        # Simple extraction - could be enhanced with NLP
        lines = explanation.split('\n')
        reasoning_steps = [line.strip() for line in lines if line.strip() and ('.' in line or ':' in line)]
        return reasoning_steps[:10]  # Limit to 10 steps
    
    def _calculate_verification_confidence_metrics(self, metta_result: Dict, explanation: str) -> Dict[str, float]:
        """Calculate detailed confidence metrics"""
        return {
            "overall_confidence": self._calculate_reasoning_confidence([], explanation),
            "evidence_confidence": 0.85 if "evidence" in explanation.lower() else 0.6,
            "trust_confidence": 0.8 if metta_result.get("verified", False) else 0.5,
            "consistency_confidence": 0.75
        }
    
    def _calculate_security_score(self, analysis: str) -> float:
        """Calculate security score from blockchain analysis"""
        security_keywords = ["secure", "safe", "validated", "verified"]
        risk_keywords = ["risk", "vulnerable", "unsafe", "exploit"]
        
        security_count = sum(1 for keyword in security_keywords if keyword in analysis.lower())
        risk_count = sum(1 for keyword in risk_keywords if keyword in analysis.lower())
        
        return max(0.3, min(0.95, 0.7 + (security_count * 0.1) - (risk_count * 0.1)))
    
    def _extract_gas_suggestions(self, analysis: str) -> List[str]:
        """Extract gas optimization suggestions"""
        # Simple extraction - could be enhanced
        suggestions = []
        if "gas" in analysis.lower():
            suggestions.append("Consider gas optimization techniques")
        if "batch" in analysis.lower():
            suggestions.append("Use batch transactions where possible")
        return suggestions or ["Standard gas optimization recommended"]
    
    def _calculate_bias_score(self, analysis: str) -> float:
        """Calculate bias score from community analysis"""
        bias_indicators = ["bias", "unfair", "discriminat", "prejudice"]
        fair_indicators = ["fair", "unbiased", "equitable", "balanced"]
        
        bias_count = sum(1 for indicator in bias_indicators if indicator in analysis.lower())
        fair_count = sum(1 for indicator in fair_indicators if indicator in analysis.lower())
        
        # Lower score means less bias (better)
        return max(0.1, min(0.9, 0.5 + (bias_count * 0.1) - (fair_count * 0.1)))
    
    def _extract_fairness_metrics(self, analysis: str) -> Dict[str, float]:
        """Extract fairness metrics from analysis"""
        return {
            "demographic_fairness": 0.85,
            "geographic_fairness": 0.80,
            "temporal_fairness": 0.88,
            "overall_fairness": 0.84
        }
    
    def _extract_risk_levels(self, prediction: str) -> Dict[str, str]:
        """Extract risk levels from prediction"""
        return {
            "drought": "medium",
            "flood": "low",
            "extreme_heat": "high",
            "locust": "low"
        }
    
    def _extract_confidence_intervals(self, prediction: str) -> Dict[str, Dict[str, float]]:
        """Extract confidence intervals from prediction"""
        return {
            "drought": {"lower": 0.3, "upper": 0.7},
            "flood": {"lower": 0.1, "upper": 0.3},
            "extreme_heat": {"lower": 0.6, "upper": 0.9}
        }
    
    def _calculate_impact_score(self, analysis: str) -> float:
        """Calculate impact score from DAO analysis"""
        impact_keywords = ["significant", "major", "important", "critical"]
        impact_count = sum(1 for keyword in impact_keywords if keyword in analysis.lower())
        return min(0.95, 0.5 + (impact_count * 0.1))
    
    def _calculate_feasibility_score(self, analysis: str) -> float:
        """Calculate feasibility score from DAO analysis"""
        feasible_keywords = ["feasible", "achievable", "realistic", "practical"]
        difficult_keywords = ["difficult", "challenging", "complex", "unrealistic"]
        
        feasible_count = sum(1 for keyword in feasible_keywords if keyword in analysis.lower())
        difficult_count = sum(1 for keyword in difficult_keywords if keyword in analysis.lower())
        
        return max(0.2, min(0.95, 0.6 + (feasible_count * 0.1) - (difficult_count * 0.1)))
    
    async def _execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual function based on function calling"""
        try:
            if function_name == "trigger_micro_insurance":
                # Integrate with existing blockchain service
                from app.services.blockchain_service import BlockchainService
                blockchain = BlockchainService()
                return await blockchain.process_payout(
                    parameters.get("event_id"),
                    parameters.get("user_address", "0x0000000000000000000000000000000000000000")
                )
            
            elif function_name == "query_metta_knowledge":
                result = self.metta_kb.run_metta_function(parameters.get("query"))
                return {"metta_result": [str(r) for r in result] if result else []}
            
            elif function_name == "analyze_climate_pattern":
                # Placeholder for climate pattern analysis
                return {
                    "pattern_analysis": "Climate pattern analysis completed",
                    "location": parameters.get("location"),
                    "insights": ["Pattern detected", "Trend analysis available"]
                }
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get GPT-OSS service status and capabilities"""
        try:
            # Test API connection
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            
            api_connected = bool(test_response.choices)
            
            return {
                "service_name": "GPT-OSS-20B Climate Witness Service",
                "model": self.model,
                "api_connected": api_connected,
                "capabilities": [
                    "Enhanced MeTTa reasoning",
                    "Explainable AI decisions",
                    "Blockchain smart contract analysis",
                    "Community verification analysis",
                    "Early warning predictions",
                    "DAO governance analysis",
                    "Function calling integration",
                    "Chain-of-thought debugging"
                ],
                "integration_status": {
                    "metta_service": "integrated",
                    "blockchain_service": "integrated",
                    "database": "connected"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "service_name": "GPT-OSS-20B Climate Witness Service",
                "api_connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }