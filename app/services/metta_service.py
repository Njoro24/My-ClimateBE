"""
MeTTa Service for Climate Witness Chain
Handles MeTTa knowledge atoms, verification logic, and reasoning using proper Hyperon API
Fixed version with improved error handling and serialization
"""

import json
import uuid
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

try:
    from hyperon import MeTTa, Atom, ExpressionAtom
    HYPERON_AVAILABLE = True
except ImportError:
    print("Warning: Hyperon not available, MeTTa service will use fallback mode")
    HYPERON_AVAILABLE = False
    # Create dummy classes for compatibility
    class MeTTa:
        def __init__(self, *args, **kwargs):
            pass
        def run(self, *args, **kwargs):
            return []
        def add_atom(self, *args, **kwargs):
            pass
    
    class Atom:
        def __init__(self, *args, **kwargs):
            pass
        def __str__(self):
            return "dummy_atom"
    
    class ExpressionAtom:
        def __init__(self, *args, **kwargs):
            pass
        def __str__(self):
            return "dummy_expression"

from app.database.crud import *
from app.database.models import MeTTaAtom, Event, User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateWitnessKnowledgeBase:
    """MeTTa Knowledge Base for Climate Witness Chain using proper Hyperon API with advanced features"""
    
    def __init__(self):
        """Initialize MeTTa runner with climate knowledge and multiple atom spaces"""
        self.metta = MeTTa()
        self.space = self.metta.space()  # Get the space to query atoms
        self.atom_spaces = {}
        self.verification_history = []
        self.loaded_files = []
        
        self._initialize_atom_spaces()
        self.load_base_knowledge()
    
    def _initialize_atom_spaces(self):
        """Initialize multiple atom spaces for different domains"""
        try:
            # Create specialized atom spaces
            self.metta.run('!(bind! &event-space (new-space))')
            self.metta.run('!(bind! &trust-space (new-space))')
            self.metta.run('!(bind! &economic-space (new-space))')
            self.metta.run('!(bind! &governance-space (new-space))')
            self.metta.run('!(bind! &prediction-space (new-space))')
            
            self.atom_spaces = {
                'event': '&event-space',
                'trust': '&trust-space',
                'economic': '&economic-space',
                'governance': '&governance-space',
                'prediction': '&prediction-space'
            }
            logger.info("✅ Initialized multiple atom spaces")
        except Exception as e:
            logger.error(f"Error initializing atom spaces: {str(e)}")
            raise

    def load_base_knowledge(self):
        """Load base climate knowledge and verification rules from .metta files"""
        logger.info("Loading MeTTa knowledge from .metta files...")
        
        metta_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'metta')
        
        # List of MeTTa files to load in order
        metta_files = [
            'base_knowledge.metta',
            'helper_functions.metta', 
            'users.metta',
            'climate_data.metta',
            'verification_rules.metta',
            'advanced_verification.metta',
            'economic_analysis.metta',
            'governance_logic.metta',
            'prediction_models.metta',
            'trust_network.metta'
        ]
        
        loaded_files = []
        
        for filename in metta_files:
            filepath = os.path.join(metta_dir, filename)
            try:
                if os.path.exists(filepath):
                    logger.info(f"    Loading {filename}...")
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.metta.run(content)
                    loaded_files.append(filename)
                else:
                    logger.warning(f"   Warning: {filename} not found at {filepath}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
        
        self.loaded_files = loaded_files
        logger.info(f"✅ MeTTa knowledge loaded from {len(loaded_files)} files: {', '.join(loaded_files)}")
    
    def load_metta_file(self, filepath: str):
        """Load a specific MeTTa file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.metta.run(content)
                logger.info(f"Loaded MeTTa file: {filepath}")
            else:
                logger.warning(f"MeTTa file not found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading MeTTa file {filepath}: {str(e)}")
    
    def run_query(self, query: str) -> List[Any]:
        """Run a MeTTa query and return results"""
        try:
            result = self.metta.run(query)
            return result if result else []
        except Exception as e:
            logger.error(f"Error running MeTTa query: {str(e)}")
            return []
    
    def add_atom(self, atom_str: str, space: str = "default") -> bool:
        """Add a single atom to the specified MeTTa space"""
        try:
            if space != "default" and space in self.atom_spaces:
                space_ref = self.atom_spaces[space]
                query = f'!(add-atom {space_ref} {atom_str})'
            else:
                query = atom_str
                
            result = self.metta.run(query)
            logger.info(f"Added atom to {space}: {atom_str}")
            return True
        except Exception as e:
            logger.error(f"Error adding atom {atom_str}: {str(e)}")
            return False
    
    def query_atoms(self, query_str: str, space: str = "default", response: str = "$result") -> List[Any]:
        """Query atoms from the specified MeTTa space using match"""
        try:
            if space != "default" and space in self.atom_spaces:
                space_ref = self.atom_spaces[space]
                query = f"!(match {space_ref} {query_str} {response})"
            else:
                query = f"!(match &self {query_str} {response})"
            print(f'Query: {query}')   
            result = self.metta.run(query)
            return self._parse_query_result(result)
        except Exception as e:
            logger.error(f"Error querying {query_str}: {str(e)}")
            return []
    
    def run_metta_function(self, query_str: str) -> List[Any]:
        """Query atoms from the specified MeTTa space using match"""
        try:
            # Prepend '!' only if query_str does not already start with '!'
            query = query_str if query_str.strip().startswith('!') else f'!{query_str.strip()}'

            print(f'Query: {query}') 
            result = self.metta.run(query, flat=True)
            return result
        except Exception as e:
            logger.error(f"   ❌ Error querying {query_str}: {str(e)}")
            return []
    
    def _safe_atom_to_string(self, atom: Any) -> str:
        """Safely convert an atom to string representation with error handling"""
        try:
            if hasattr(atom, '__str__'):
                return str(atom)
            elif isinstance(atom, (str, int, float, bool)):
                return str(atom)
            elif isinstance(atom, list):
                return ' '.join([self._safe_atom_to_string(item) for item in atom])
            else:
                return f"<{type(atom).__name__}>"
        except Exception as e:
            logger.warning(f"⚠️ Error converting atom to string: {e}")
            return f"<unconvertable:{type(atom).__name__}>"
    
    def _parse_query_result(self, result: List[Any]) -> List[Dict[str, Any]]:
        """Parse MeTTa query results into a more usable format with improved error handling"""
        parsed_results = []
        
        for item in result:
            try:
                parsed_item = {
                    'raw': self._safe_atom_to_string(item),
                    'type': type(item).__name__
                }
                
                if isinstance(item, ExpressionAtom):
                    try:
                        children = item.get_children()
                        if children:
                            parsed_item.update({
                                'type': 'expression',
                                'children': [self._safe_atom_to_string(child) for child in children],
                                'arity': len(children)
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing ExpressionAtom children: {e}")
                        parsed_item['parse_error'] = str(e)
                
                parsed_results.append(parsed_item)
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing result item: {e}")
                parsed_results.append({
                    'error': f"Failed to parse: {str(e)}",
                    'type': 'parse_error',
                    'raw': f"<unparseable:{type(item).__name__}>"
                })
                
        return parsed_results
            
    def create_user_atoms(self, user: User) -> List[str]:
        """Create MeTTa atoms for a user and add them to the space"""
        atoms = []
        
        # User identity atom
        user_atom = f"(user {user.id})"
        atoms.append(user_atom)
        self.add_atom(user_atom, "trust")
        
        # Location atom
        if user.location_region:
            location_atom = f"(location {user.id} \"{user.location_region}\")"
            atoms.append(location_atom)
            self.add_atom(location_atom, "event")
        
        # Trust score atom
        trust_atom = f"(trust-score {user.id} {user.trust_score})"
        atoms.append(trust_atom)
        self.add_atom(trust_atom, "trust")
        
        # Wallet atom
        if user.wallet_address:
            wallet_atom = f"(wallet-address {user.id} \"{user.wallet_address}\")"
            atoms.append(wallet_atom)
            self.add_atom(wallet_atom, "economic")
        
        return atoms
    
    def create_event_atoms(self, event: Event, user: User) -> Tuple[List[str], str]:
        """Create MeTTa atoms for a climate event and add them to the space"""
        atoms = []
        
        # Create a unique event ID for MeTTa
        event_id = f"{event.event_type}_{event.id[:8]}"
        
        # Event identity atom
        event_atom = f"(event {event_id})"
        atoms.append(event_atom)
        self.add_atom(event_atom, "event")
        
        # Reporter relationship
        reports_atom = f"(reports {user.id} {event_id})"
        atoms.append(reports_atom)
        self.add_atom(reports_atom, "event")
        
        # Event type
        type_atom = f"(event-type {event_id} {event.event_type})"
        atoms.append(type_atom)
        self.add_atom(type_atom, "event")
        
        # Timestamp
        if event.timestamp:
            timestamp_atom = f"(timestamp {event_id} \"{event.timestamp.isoformat()}\")"
            atoms.append(timestamp_atom)
            self.add_atom(timestamp_atom, "event")
        
        # GPS coordinates
        if event.latitude and event.longitude:
            coords_atom = f"(gps-coords {event_id} ({event.latitude} {event.longitude}))"
            atoms.append(coords_atom)
            self.add_atom(coords_atom, "event")
        
        # Evidence link (photo)
        if event.photo_path:
            evidence_atom = f"(evidence-link {event_id} \"{event.photo_path}\")"
            atoms.append(evidence_atom)
            self.add_atom(evidence_atom, "event")
            
            # Photo timestamp (same as event for now)
            photo_timestamp_atom = f"(photo-timestamp {event_id} \"{event.timestamp.isoformat()}\")"
            atoms.append(photo_timestamp_atom)
            self.add_atom(photo_timestamp_atom, "event")
        
        # Description
        if event.description:
            # Escape quotes in description
            safe_description = event.description.replace('"', '\\"')
            desc_atom = f"(description {event_id} \"{safe_description}\")"
            atoms.append(desc_atom)
            self.add_atom(desc_atom, "event")
        
        # Determine impact and severity based on event type
        impact, severity = self._determine_impact_severity(event)
        if impact:
            impact_atom = f"(impact {event_id} {impact})"
            atoms.append(impact_atom)
            self.add_atom(impact_atom, "economic")
        
        if severity:
            severity_atom = f"(severity {event_id} {severity})"
            atoms.append(severity_atom)
            self.add_atom(severity_atom, "event")
        
        return atoms, event_id
    
    def _determine_impact_severity(self, event: Event) -> Tuple[Optional[str], Optional[str]]:
        """Determine impact and severity based on event type and description"""
        impact_mapping = {
            'drought': ('Livestock_Risk', 'High'),
            'flood': ('Infrastructure_Damage', 'Medium'),
            'locust': ('Crop_Failure', 'High'),
            'extreme_heat': ('Water_Scarcity', 'Medium'),
            'wildfire': ('Ecosystem_Damage', 'High'),
            'storm': ('Property_Damage', 'Medium')
        }
        
        return impact_mapping.get(event.event_type, (None, None))
    
    def run_verification(self, event_id: str, user_id: str, image_confidence: int, desc_confidence: int) -> Dict[str, Any]:
        """Run MeTTa verification logic using proper queries with improved error handling"""
        logger.info(f"🔍 Running MeTTa verification for event {event_id}")
        
        try:
            # Query for auto-verification
            auto_verify_query = f"(auto-verify {event_id} {user_id} {image_confidence} {desc_confidence})"
            auto_verify_result = self.run_metta_function(auto_verify_query)
            print(f'autoverify res: {auto_verify_result}')
            
            # Check if verification passed by looking for verified atom
            is_verified = bool(auto_verify_result) and len(auto_verify_result) > 0
            verification_method = "auto-verify"
            
            if is_verified:
                atom = f"(verified {event_id})"
                self.add_atom(atom, "event")
                verified_atoms = self.query_atoms(f"(verified {event_id})", "event")
            else:
                verified_atoms = []

            # If auto-verify didn't work, try high-trust verification
            if not is_verified:
                high_trust_query = f"(high-trust-verify {event_id} {user_id})"
                high_trust_result = self.run_metta_function(high_trust_query)
                # give the person the benefit of doubt if they are having high trust score
                is_verified = bool(high_trust_result) and len(high_trust_result) > 0
                verification_method = "high-trust-verify"
            
            # Get reasoning
            reasoning = self._get_verification_reasoning(event_id, user_id)
            
            verification_result = {
                'verified': is_verified,
                'event_id': event_id,
                'user_id': user_id,
                'reasoning': reasoning,
                'verification_time': datetime.now().isoformat(),
                'method': verification_method,
                'auto_verify_result': len(auto_verify_result),
                'verified_atoms_found': len(verified_atoms)
            }
            
            # Store verification history
            self.verification_history.append(verification_result)
            
            status = "VERIFIED" if is_verified else "FAILED"
            logger.info(f"Verification complete: {status} using {verification_method}")
            return verification_result
            
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return {
                'verified': False,
                'event_id': event_id,
                'user_id': user_id,
                'error': str(e),
                'reasoning': ['Verification failed due to technical error'],
                'verification_time': datetime.now().isoformat(),
                'method': 'error'
            }
    
    def _get_verification_reasoning(self, event_id: str, user_id: str) -> List[str]:
        """Get reasoning for verification decision using proper queries"""
        reasoning = []
        
        # Check trust score
        trust_query = f"(trust-score {user_id} $score)"
        trust_result = self.query_atoms(trust_query, "trust", "$score")
        if trust_result:
            try:
                score = trust_result[0].get('children', [])[2] if 'children' in trust_result[0] else "unknown"
                reasoning.append(f"User trust score: {score}")
                if isinstance(score, (int, float)) or (isinstance(score, str) and score.isdigit()):
                    score_val = int(score) if isinstance(score, str) else score
                    if score_val >= 60:
                        reasoning.append("✅ Trust score meets minimum threshold (60)")
                    else:
                        reasoning.append("❌ Trust score below minimum threshold (60)")
            except (IndexError, ValueError):
                reasoning.append("⚠️ Trust score format unexpected")
        
        # Check evidence
        evidence_query = f"(evidence-link {event_id} $link)"
        evidence_result = self.query_atoms(evidence_query, "event", "$link")
        if evidence_result:
            reasoning.append("✅ Photo evidence provided")
        else:
            reasoning.append("❌ No photo evidence found")
        
        # Check GPS coordinates
        gps_query = f"(gps-coords {event_id} $coords)"
        gps_result = self.query_atoms(gps_query, "event", "$coords")
        if gps_result:
            reasoning.append("✅ GPS coordinates available")
        else:
            reasoning.append("❌ No GPS coordinates found")
        
        # Check timestamp
        timestamp_query = f"(timestamp {event_id} $time)"
        timestamp_result = self.query_atoms(timestamp_query, "event", "$time")
        if timestamp_result:
            reasoning.append("✅ Event timestamp recorded")
        else:
            reasoning.append("❌ No timestamp found")
        
        print(f"MeTTa Reasoning: {reasoning}")
        return reasoning
    
    def calculate_payout(self, event_id: str) -> Optional[float]:
        """Calculate payout amount for verified event using proper queries"""
        try:
            # Query for payout eligibility
            payout_query = f"(payout-eligible {event_id} $amount)"
            result = self.run_metta_function(payout_query)
            
            if result:
                # Extract amount from result
                for res in result:
                    try:
                        if hasattr(res, 'get_children'):
                            children = res.get_children()
                            if len(children) >= 3:
                                amount_str = self._safe_atom_to_string(children[2])
                                if amount_str.replace('.', '').isdigit():
                                    amount = float(amount_str)
                                    logger.info(f"💰 Payout calculated: {amount} ETH for event {event_id}")
                                    return amount
                    except (ValueError, IndexError, TypeError) as e:
                        logger.warning(f"⚠️ Could not parse payout amount: {e}")
                        continue
            
            logger.info(f"❌ No payout eligibility found for event {event_id}")
            return None
                
        except Exception as e:
            logger.error(f"❌ Payout calculation error: {str(e)}")
            return None
    
    def query_knowledge_base(self, query: str, space: str = "default") -> List[Dict[str, Any]]:
        """Query the MeTTa knowledge base using match"""
        try:
            return self.query_atoms(query, space)
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_all_atoms_of_type(self, atom_type: str, space: str = "default") -> List[str]:
        """Get all atoms of a specific type"""
        try:
            query = f"({atom_type} $x)"
            result = self.query_atoms(query, space, query)
            return [r.get('raw', 'unknown') for r in result if 'raw' in r]
        except Exception as e:
            logger.error(f"❌ Error getting atoms of type {atom_type}: {str(e)}")
            return []
    
    def get_knowledge_base_state(self) -> Dict[str, Any]:
        """Get current state of the knowledge base"""
        # Get counts of different atom types
        user_atoms = self.get_all_atoms_of_type('user', 'trust')
        event_atoms = self.get_all_atoms_of_type('event', 'event')
        trust_atoms = self.get_all_atoms_of_type('trust-score', 'trust')
        
        return {
            'base_knowledge_loaded': True,
            'verification_rules_loaded': True,
            'loaded_metta_files': self.loaded_files,
            'total_verifications': len(self.verification_history),
            'recent_verifications': self.verification_history[-5:] if self.verification_history else [],
            'atom_counts': {
                'users': len(user_atoms),
                'events': len(event_atoms),
                'trust_scores': len(trust_atoms)
            },
            'atom_spaces': list(self.atom_spaces.keys()),
            'knowledge_base_type': 'hyperon-based'
        }

    # Advanced DAO Methods with improved error handling
    async def community_verify_event(self, event_id: str, verifier_id: str) -> dict:
        """Execute community verification using advanced MeTTa logic"""
        try:
            query = f'!(community-verify "{event_id}" "{verifier_id}")'
            result = self.metta.run(query)
            return self._process_verification_result(result, event_id, verifier_id)
        except Exception as e:
            logger.error(f"Error in community verification: {e}")
            return {"success": False, "error": str(e), "event_id": event_id}

    async def analyze_economic_impact(self, event_id: str) -> dict:
        """Analyze economic impact using MeTTa correlation logic"""
        try:
            query = f'!(analyze-economic-impact "{event_id}")'
            result = self.metta.run(query)
            return self._process_impact_analysis(result, event_id)
        except Exception as e:
            logger.error(f"Error in economic impact analysis: {e}")
            return {"success": False, "error": str(e), "event_id": event_id}

    async def check_insurance_eligibility(self, user_id: str, event_id: str) -> dict:
        """Check insurance eligibility using MeTTa smart contract logic"""
        try:
            query = f'!(check-insurance-eligibility "{user_id}" "{event_id}")'
            result = self.metta.run(query)
            return self._process_insurance_result(result, user_id, event_id)
        except Exception as e:
            logger.error(f"Error checking insurance eligibility: {e}")
            return {"success": False, "error": str(e), "user_id": user_id, "event_id": event_id}

    async def evaluate_dao_proposal(self, proposal_id: str) -> dict:
        """Evaluate DAO proposal using MeTTa governance logic"""
        try:
            query = f'!(evaluate-proposal "{proposal_id}")'
            result = self.metta.run(query)
            return self._process_proposal_result(result, proposal_id)
        except Exception as e:
            logger.error(f"Error evaluating DAO proposal: {e}")
            return {"success": False, "error": str(e), "proposal_id": proposal_id}

    async def calculate_trust_score(self, user_id: str) -> dict:
        """Calculate advanced trust score using MeTTa trust network logic"""
        try:
            query = f'!(calculate-advanced-trust-score "{user_id}")'
            result = self.metta.run(query)
            return self._process_trust_score_result(result, user_id)
        except Exception as e:
            logger.error(f"Error calculating trust score: {e}")
            return {"success": False, "error": str(e), "user_id": user_id}

    async def generate_early_warning(self, location: dict, event_types: list) -> dict:
        """Generate early warning alerts using MeTTa prediction logic"""
        try:
            lat, lng = location.get('latitude', 0), location.get('longitude', 0)
            event_types_str = ' '.join([f'"{et}"' for et in event_types])
            query = f'!(generate-early-warning {lat} {lng} ({event_types_str}))'
            result = self.metta.run(query)
            return self._process_warning_result(result, location, event_types)
        except Exception as e:
            logger.error(f"Error generating early warning: {e}")
            return {"success": False, "error": str(e), "location": location}

    # Improved result processing methods
    def _process_verification_result(self, result, event_id=None, verifier_id=None) -> dict:
        """Process community verification result with better error handling"""
        if not result:
            return {
                "success": False, 
                "verified": False, 
                "reason": "No result from MeTTa query",
                "event_id": event_id,
                "verifier_id": verifier_id
            }
        
        try:
            parsed_result = self._parse_query_result(result)
            result_str = ' '.join([r.get('raw', '') for r in parsed_result]).lower()
            
            if "eligible-verifier" in result_str:
                return {"success": True, "eligible": True, "result": parsed_result}
            elif "verified-event" in result_str:
                return {"success": True, "verified": True, "result": parsed_result}
            else:
                return {
                    "success": True, 
                    "verified": False, 
                    "result": parsed_result,
                    "raw_result": result_str
                }
        except Exception as e:
            return {
                "success": False, 
                "error": f"Error processing verification result: {str(e)}",
                "raw_result": str(result)
            }

    def _process_impact_analysis(self, result, event_id=None) -> dict:
        """Process economic impact analysis result"""
        if not result:
            return {"success": False, "impacts": [], "event_id": event_id}
        
        try:
            parsed_result = self._parse_query_result(result)
            return {
                "success": True,
                "impacts": parsed_result,
                "correlation_found": len(parsed_result) > 0,
                "event_id": event_id
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "raw_result": str(result),
                "event_id": event_id
            }

    def _process_insurance_result(self, result, user_id=None, event_id=None) -> dict:
        """Process insurance eligibility result"""
        if not result:
            return {
                "success": False, 
                "eligible": False, 
                "user_id": user_id, 
                "event_id": event_id
            }
        
        try:
            parsed_result = self._parse_query_result(result)
            result_str = ' '.join([r.get('raw', '') for r in parsed_result]).lower()
            eligible = "eligible-for-payout" in result_str
            payout_amount = 0.0
            
            # Try to extract payout amount
            for res in parsed_result:
                if 'children' in res and len(res['children']) >= 3:
                    try:
                        if res['children'][0] == "eligible-for-payout":
                            payout_str = res['children'][2]
                            if payout_str.replace('.', '').isdigit():
                                payout_amount = float(payout_str)
                                break
                    except (ValueError, IndexError):
                        continue
            
            return {
                "success": True,
                "eligible": eligible,
                "payout_amount": payout_amount,
                "result": parsed_result,
                "user_id": user_id,
                "event_id": event_id
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "raw_result": str(result),
                "user_id": user_id,
                "event_id": event_id
            }

    def _process_proposal_result(self, result, proposal_id=None) -> dict:
        """Process DAO proposal evaluation result"""
        if not result:
            return {"success": False, "status": "no_result", "proposal_id": proposal_id}
        
        try:
            parsed_result = self._parse_query_result(result)
            return {
                "success": True,
                "evaluation": parsed_result,
                "status": "evaluated",
                "proposal_id": proposal_id
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "raw_result": str(result),
                "proposal_id": proposal_id
            }

    def _process_trust_score_result(self, result, user_id=None) -> dict:
        """Process trust score calculation result"""
        if not result:
            return {"success": False, "trust_score": 0, "user_id": user_id}
        
        trust_score = 0
        try:
            parsed_result = self._parse_query_result(result)
            
            for res in parsed_result:
                if 'children' in res and len(res['children']) >= 3:
                    try:
                        if res['children'][0] == "trust-score":
                            score_str = res['children'][2]
                            if score_str.replace('.', '').isdigit():
                                trust_score = float(score_str)
                                break
                    except (ValueError, IndexError):
                        continue
        
            return {
                "success": True,
                "trust_score": trust_score,
                "result": parsed_result,
                "user_id": user_id
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "raw_result": str(result),
                "user_id": user_id
            }

    def _process_warning_result(self, result, location=None, event_types=None) -> dict:
        """Process early warning generation result"""
        if not result:
            return {
                "success": False, 
                "warnings": [], 
                "location": location,
                "event_types": event_types
            }
        
        try:
            parsed_result = self._parse_query_result(result)
            
            # Determine alert level based on number of warnings
            alert_level = "low"
            if len(parsed_result) > 2:
                alert_level = "high"
            elif len(parsed_result) > 0:
                alert_level = "medium"
            
            return {
                "success": True,
                "warnings": parsed_result,
                "alert_level": alert_level,
                "warning_count": len(parsed_result),
                "location": location,
                "event_types": event_types
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "raw_result": str(result),
                "location": location,
                "event_types": event_types
            }

    def add_to_atom_space(self, space_name: str, atom: str) -> bool:
        """Add atom to specific atom space"""
        try:
            if space_name in self.atom_spaces:
                space_ref = self.atom_spaces[space_name]
                query = f'!(add-atom {space_ref} {atom})'
                self.metta.run(query)
                return True
            else:
                logger.warning(f"Atom space {space_name} not found")
                return False
        except Exception as e:
            logger.error(f"Error adding atom to space {space_name}: {e}")
            return False

    def query_atom_space(self, space_name: str, query_pattern: str) -> List[Dict[str, Any]]:
        """Query specific atom space with pattern"""
        try:
            if space_name in self.atom_spaces:
                return self.query_atoms(query_pattern, space_name)
            else:
                logger.warning(f"Atom space {space_name} not found")
                return []
        except Exception as e:
            logger.error(f"Error querying atom space {space_name}: {e}")
            return []


_shared_knowledge_base = None

def get_shared_knowledge_base():
    """Get shared knowledge base instance to avoid thread re-start errors"""
    global _shared_knowledge_base
    if _shared_knowledge_base is None:
        if HYPERON_AVAILABLE:
            _shared_knowledge_base = ClimateWitnessKnowledgeBase()
        else:
            logger.warning("Hyperon not available, knowledge base will be None")
            _shared_knowledge_base = None
    return _shared_knowledge_base

class MeTTaService:
    """Service for handling MeTTa operations with proper Hyperon integration"""
    def __init__(self, db_path: str = "./climate_witness.db"):
        self.db_path = db_path
        if HYPERON_AVAILABLE:
            # Use a shared knowledge base instance to avoid thread re-start errors
            self.knowledge_base = get_shared_knowledge_base()
        else:
            logger.warning("Hyperon not available, using fallback MeTTa service")
            self.knowledge_base = None
        self.crud = None
    
    async def create_atoms(self, event: 'Event', user: 'User') -> list:
        """Create MeTTa knowledge atoms from an Event object and user object (no DB queries)"""
        try:
            if not HYPERON_AVAILABLE or not self.knowledge_base:
                logger.warning("Hyperon not available, skipping atom creation")
                return []
            
            # Create user atoms (adds them to MeTTa space)
            user_atoms = self.knowledge_base.create_user_atoms(user)
            # Create event atoms (adds them to MeTTa space)
            event_atoms, metta_event_id = self.knowledge_base.create_event_atoms(event, user)
            # Store atoms in database for persistence
            all_atoms = user_atoms + event_atoms
            for atom_content in all_atoms:
                atom_type = self._determine_atom_type(atom_content)
                atom = MeTTaAtom(
                    id=str(uuid.uuid4()),
                    event_id=event.id,
                    atom_type=atom_type,
                    atom_content=json.dumps({
                        'atom': atom_content,
                        'metta_event_id': metta_event_id
                    }),
                    created_at=datetime.now()
                )
                # await self.crud.create_atom(atom)
            logger.info(f"✅ Created {len(all_atoms)} MeTTa atoms for event {event.id}")
            return all_atoms
        except Exception as e:
            logger.error(f"❌ Error creating atoms: {str(e)}")
            raise
    
    def _determine_atom_type(self, atom_content: str) -> str:
        """Determine atom type from content"""
        atom_type_mapping = {
            '(user ': 'user',
            '(event ': 'event', 
            '(location ': 'location',
            '(evidence-link ': 'evidence',
            '(impact ': 'impact',
            '(verified ': 'verification',
            '(trust-score ': 'trust',
            '(reports ': 'relationship',
            '(event-type ': 'classification',
            '(timestamp ': 'temporal',
            '(gps-coords ': 'spatial',
            '(description ': 'descriptive',
            '(severity ': 'assessment',
            '(wallet-address ': 'financial'
        }
        
        for prefix, atom_type in atom_type_mapping.items():
            if atom_content.startswith(prefix):
                return atom_type
        
        return 'other'
    
    async def run_verification(self, event: 'Event', user: 'User', image_confidence: int, desc_confidence: int) -> bool:
        """Run MeTTa verification logic on an event object and user object (no DB queries)"""
        try:
            if not HYPERON_AVAILABLE or not self.knowledge_base:
                logger.warning("Hyperon not available, using fallback verification")
                # Simple fallback verification based on confidence scores
                return (image_confidence > 70 or desc_confidence > 70)
            
            logger.info(f"Starting verification for event {event.id}")
            
            # Create event atoms first
            event_atoms, metta_event_id = self.knowledge_base.create_event_atoms(event, user)
            logger.info(f"Created {len(event_atoms)} atoms for verification")
            
            # Run verification using the MeTTa event ID
            verification_result = self.knowledge_base.run_verification(
                metta_event_id, user.id, image_confidence, desc_confidence
            )
            
            # Log detailed verification result
            logger.info(f"Verification result: {verification_result['verified']} "
                       f"(method: {verification_result.get('method', 'unknown')})")
            
            return verification_result['verified']
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False
    
    def query_knowledge_base(self, query: str, space: str = "default") -> List[str]:
        """Query the MeTTa knowledge base"""
        try:
            results = self.knowledge_base.query_knowledge_base(query, space)
            return [r.get('raw', str(r)) for r in results]
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            return [f"Error: {str(e)}"]
    
    def update_trust_score(self, user_id: str, delta: int) -> int:
        """Update user trust score based on verification results"""
        try:
            # Add trust score update atom
            if delta > 0:
                trust_update = f"(increase-trust {user_id} {delta})"
            else:
                trust_update = f"(decrease-trust {user_id} {abs(delta)})"
            
            success = self.knowledge_base.add_atom(trust_update, "trust")
            if success:
                logger.info(f"Trust score updated for user {user_id}: {'+' if delta > 0 else ''}{delta}")
            return delta
        except Exception as e:
            logger.error(f"Error updating trust score: {str(e)}")
            return 0

    def get_knowledge_base_state(self) -> Dict[str, Any]:
        """Get current state of the knowledge base"""
        try:
            return self.knowledge_base.get_knowledge_base_state()
        except Exception as e:
            logger.error(f"Error getting knowledge base state: {str(e)}")
            return {
                'error': str(e),
                'base_knowledge_loaded': False,
                'verification_rules_loaded': False
            }

    # Advanced DAO Methods with improved error handling
    async def community_verify_event(self, event_id: str, verifier_id: str) -> dict:
        """Execute community verification using advanced MeTTa logic"""
        try:
            return await self.knowledge_base.community_verify_event(event_id, verifier_id)
        except Exception as e:
            logger.error(f"Community verification service error: {str(e)}")
            return {
                "success": False, 
                "error": f"Service error: {str(e)}", 
                "event_id": event_id,
                "verifier_id": verifier_id
            }

    async def analyze_economic_impact(self, event_id: str) -> dict:
        """Analyze economic impact using MeTTa correlation logic"""
        try:
            return await self.knowledge_base.analyze_economic_impact(event_id)
        except Exception as e:
            logger.error(f"Economic impact analysis service error: {str(e)}")
            return {
                "success": False, 
                "error": f"Service error: {str(e)}", 
                "event_id": event_id
            }

    async def check_insurance_eligibility(self, user_id: str, event_id: str) -> dict:
        """Check insurance eligibility using MeTTa smart contract logic"""
        try:
            if not HYPERON_AVAILABLE or not self.knowledge_base:
                return {"success": False, "error": "MeTTa not available", "user_id": user_id, "event_id": event_id}
            
            return await self.knowledge_base.check_insurance_eligibility(user_id, event_id)
        except Exception as e:
            logger.error(f"Insurance eligibility service error: {str(e)}")
            return {
                "success": False, 
                "error": f"Service error: {str(e)}", 
                "user_id": user_id, 
                "event_id": event_id
            }

    async def evaluate_dao_proposal(self, proposal_id: str) -> dict:
        """Evaluate DAO proposal using MeTTa governance logic"""
        try:
            if not HYPERON_AVAILABLE or not self.knowledge_base:
                return {"success": False, "error": "MeTTa not available", "proposal_id": proposal_id}
            
            return await self.knowledge_base.evaluate_dao_proposal(proposal_id)
        except Exception as e:
            logger.error(f"DAO proposal evaluation service error: {str(e)}")
            return {
                "success": False, 
                "error": f"Service error: {str(e)}", 
                "proposal_id": proposal_id
            }

    async def calculate_advanced_trust_score(self, user_id: str) -> dict:
        """Calculate advanced trust score using MeTTa trust network logic"""
        try:
            return await self.knowledge_base.calculate_trust_score(user_id)
        except Exception as e:
            logger.error(f"Trust score calculation service error: {str(e)}")
            return {
                "success": False, 
                "error": f"Service error: {str(e)}", 
                "user_id": user_id
            }

    async def generate_early_warning(self, location: dict, event_types: list) -> dict:
        """Generate early warning alerts using MeTTa prediction logic"""
        try:
            if not HYPERON_AVAILABLE or not self.knowledge_base:
                return {"success": False, "error": "MeTTa not available", "location": location, "event_types": event_types}
            
            return await self.knowledge_base.generate_early_warning(location, event_types)
        except Exception as e:
            logger.error(f"Early warning generation service error: {str(e)}")
            return {
                "success": False, 
                "error": f"Service error: {str(e)}", 
                "location": location,
                "event_types": event_types
            }

    def add_to_atom_space(self, space_name: str, atom: str) -> bool:
        """Add atom to specific atom space"""
        try:
            return self.knowledge_base.add_to_atom_space(space_name, atom)
        except Exception as e:
            logger.error(f"Service error adding to atom space: {str(e)}")
            return False

    def query_atom_space(self, space_name: str, query_pattern: str) -> List[Dict[str, Any]]:
        """Query specific atom space with pattern"""
        try:
            return self.knowledge_base.query_atom_space(space_name, query_pattern)
        except Exception as e:
            logger.error(f"Service error querying atom space: {str(e)}")
            return [{"error": str(e)}]

    def get_verification_history(self) -> List[Dict[str, Any]]:
        """Get verification history"""
        try:
            return self.knowledge_base.verification_history
        except Exception as e:
            logger.error(f"Error getting verification history: {str(e)}")
            return []

    def get_atom_spaces_info(self) -> Dict[str, str]:
        """Get information about available atom spaces"""
        try:
            return self.knowledge_base.atom_spaces.copy()
        except Exception as e:
            logger.error(f"Error getting atom spaces info: {str(e)}")
            return {}

    def calculate_payout(self, event_id: str) -> Optional[float]:
        """Calculate payout amount for verified event"""
        try:
            return self.knowledge_base.calculate_payout(event_id)
        except Exception as e:
            logger.error(f"Error calculating payout: {str(e)}")
            return None

# Example usage and testing functions
def create_test_service():
    """Create a test MeTTa service instance"""
    return MeTTaService()

def run_basic_tests():
    """Run basic tests on the MeTTa service"""
    try:
        service = create_test_service()
        
        # Test knowledge base state
        state = service.get_knowledge_base_state()
        print(f"Knowledge base state: {state.get('loaded_metta_files', [])}")
        
        # Test querying
        query_result = service.query_knowledge_base("(user $x)", "trust")
        print(f"Query test result: {len(query_result)} results")
        
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_basic_tests()