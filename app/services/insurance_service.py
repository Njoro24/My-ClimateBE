"""
Simple Micro-Insurance Service for Climate Witness DAO
Demonstrates automated insurance payouts for verified climate events
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.services.metta_service import MeTTaService
from app.database import crud
from app.database.models import Event, User, MeTTaAtom

@dataclass
class SimpleInsurancePolicy:
    """Simple insurance policy for demonstration"""
    id: str
    user_id: str
    coverage_amount: float
    premium_paid: float
    status: str  # active, expired, claimed
    created_at: datetime
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'coverage_amount': self.coverage_amount,
            'premium_paid': self.premium_paid,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class InsurancePayout:
    """Insurance payout record"""
    id: str
    policy_id: str
    user_id: str
    event_id: str
    amount: float
    status: str  # pending, completed, failed
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'user_id': self.user_id,
            'event_id': self.event_id,
            'amount': self.amount,
            'status': self.status,
            'timestamp': self.timestamp.isoformat()
        }

class SimpleInsuranceService:
    """Simple micro-insurance service demonstrating the Climate Witness Chain concept"""
    
    def __init__(self, db_path: str = "./climate_witness.db"):
        self.db_path = db_path
        self.metta_service = MeTTaService(db_path)
    # self.crud = None
        
        # Simple insurance parameters
        self.base_premium = 50.0  # $50 USD
        self.base_coverage = 1000.0  # $1000 USD coverage
        self.payout_percentage = 0.8  # 80% of coverage amount
    
    async def create_simple_policy(self, user_id: str) -> dict:
        """Create a simple insurance policy for a user"""
        try:
            # Check if user already has an active policy
            existing_policies = await self.get_user_policies(user_id)
            active_policies = [p for p in existing_policies if p.status == 'active']
            
            if active_policies:
                return {
                    'success': False,
                    'error': 'User already has an active policy'
                }
            
            # Get user details
            user = await crud.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Check user trust score (minimum 60 required)
            if user.trust_score < 60:
                return {
                    'success': False,
                    'error': 'Minimum trust score of 60 required for insurance'
                }
            
            # Create simple policy
            policy_id = str(uuid.uuid4())
            policy = SimpleInsurancePolicy(
                id=policy_id,
                user_id=user_id,
                coverage_amount=self.base_coverage,
                premium_paid=self.base_premium,
                status='active',
                created_at=datetime.now()
            )
            
            # Store policy in database
            await self._store_policy(policy)
            
            # Add policy to MeTTa knowledge base
            policy_atom = f'(insurance-policy {user_id} {self.base_coverage} {self.base_premium} "active")'
            self.metta_service.add_to_atom_space('governance', policy_atom)
            
            return {
                'success': True,
                'policy': policy.to_dict(),
                'message': f'Insurance policy created! Coverage: ${self.base_coverage}, Premium: ${self.base_premium}'
            }
            
        except Exception as e:
            print(f"Error creating insurance policy: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_payout_eligibility(self, user_id: str, event_id: str) -> dict:
        """Check if user is eligible for insurance payout"""
        try:
            # Get user's active policy
            policies = await self.get_user_policies(user_id)
            active_policy = None
            for policy in policies:
                if policy.status == 'active':
                    active_policy = policy
                    break
            
            if not active_policy:
                return {
                    'success': False,
                    'eligible': False,
                    'reason': 'No active insurance policy found'
                }
            
            # Get event details
            event = await crud.get_event_by_id(event_id)
            if not event:
                return {
                    'success': False,
                    'eligible': False,
                    'reason': 'Event not found'
                }
            
            # Check if event is verified
            if event.verification_status != 'verified':
                return {
                    'success': False,
                    'eligible': False,
                    'reason': 'Event must be verified for payout eligibility'
                }
            
            # Check if event reporter is the policy holder
            if event.user_id != user_id:
                return {
                    'success': False,
                    'eligible': False,
                    'reason': 'Only the event reporter can claim insurance for their events'
                }
            
            # Use MeTTa to trigger micro-insurance and check eligibility
            location = (event.latitude, event.longitude)
            severity = self._calculate_event_severity(event)
            
            # Run MeTTa micro-insurance trigger
            metta_query = f'!(trigger-micro-insurance "{event_id}" ({event.latitude} {event.longitude}) {severity})'
            metta_result = self.metta_service.knowledge_base.metta.run(metta_query)
            
            # Parse MeTTa result
            eligibility_result = self._parse_metta_insurance_result(metta_result)
            
            # Calculate payout amount
            payout_amount = active_policy.coverage_amount * self.payout_percentage
            
            return {
                'success': True,
                'eligible': True,
                'policy_id': active_policy.id,
                'payout_amount': payout_amount,
                'coverage_amount': active_policy.coverage_amount,
                'event_type': event.event_type,
                'verification_status': event.verification_status
            }
            
        except Exception as e:
            print(f"Error checking payout eligibility: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_automatic_payout(self, user_id: str, event_id: str) -> dict:
        """Process automatic insurance payout for verified event"""
        try:
            # Check eligibility
            eligibility = await self.check_payout_eligibility(user_id, event_id)
            
            if not eligibility.get('eligible', False):
                return {
                    'success': False,
                    'error': eligibility.get('reason', 'Not eligible for payout')
                }
            
            policy_id = eligibility['policy_id']
            payout_amount = eligibility['payout_amount']
            
            # Create payout record
            payout_id = str(uuid.uuid4())
            payout = InsurancePayout(
                id=payout_id,
                policy_id=policy_id,
                user_id=user_id,
                event_id=event_id,
                amount=payout_amount,
                status='completed',  # Simplified - assume always successful
                timestamp=datetime.now()
            )
            
            # Store payout in database
            await crud.create_atom(payout)
            
            # Update policy status to claimed
            await self._update_policy_status(policy_id, 'claimed')
            
            # Add payout to MeTTa knowledge base
            payout_atom = f'(insurance-payout {user_id} "{event_id}" {payout_amount} "completed")'
            self.metta_service.add_to_atom_space('governance', payout_atom)
            
            # Update user's wallet balance (simplified - in reality would be blockchain transaction)
            user = await crud.get_user_by_id(user_id)
            if user:
                # In a real system, this would trigger a blockchain transaction
                print(f" Insurance payout of ${payout_amount} processed for user {user_id}")
            
            return {
                'success': True,
                'payout': payout.to_dict(),
                'message': f'Insurance payout of ${payout_amount} processed successfully!',
                'transaction_id': payout_id
            }
            
        except Exception as e:
            print(f"Error processing automatic payout: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_policies(self, user_id: str) -> List[SimpleInsurancePolicy]:
        """Get all insurance policies for a user"""
        try:
            policies = []
            atoms = await crud.get_all_atoms()
            
            for atom in atoms:
                if atom.atom_type == 'insurance_policy':
                    policy_data = json.loads(atom.atom_content)
                    if policy_data.get('user_id') == user_id:
                        policy = SimpleInsurancePolicy(
                            id=policy_data['id'],
                            user_id=policy_data['user_id'],
                            coverage_amount=policy_data['coverage_amount'],
                            premium_paid=policy_data['premium_paid'],
                            status=policy_data['status'],
                            created_at=datetime.fromisoformat(policy_data['created_at'])
                        )
                        policies.append(policy)
            
            return policies
            
        except Exception as e:
            print(f"Error getting user policies: {e}")
            return []
    
    async def get_user_payouts(self, user_id: str) -> List[InsurancePayout]:
        """Get all insurance payouts for a user"""
        try:
            payouts = []
            atoms = await crud.get_all_atoms()
            
            for atom in atoms:
                if atom.atom_type == 'insurance_payout':
                    payout_data = json.loads(atom.atom_content)
                    if payout_data.get('user_id') == user_id:
                        payout = InsurancePayout(
                            id=payout_data['id'],
                            policy_id=payout_data['policy_id'],
                            user_id=payout_data['user_id'],
                            event_id=payout_data['event_id'],
                            amount=payout_data['amount'],
                            status=payout_data['status'],
                            timestamp=datetime.fromisoformat(payout_data['timestamp'])
                        )
                        payouts.append(payout)
            
            return sorted(payouts, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            print(f"Error getting user payouts: {e}")
            return []
    
    async def get_insurance_stats(self) -> dict:
        """Get overall insurance system statistics"""
        try:
            atoms = await crud.get_all_atoms()
            
            policies = [a for a in atoms if a.atom_type == 'insurance_policy']
            payouts = [a for a in atoms if a.atom_type == 'insurance_payout']
            
            total_policies = len(policies)
            total_payouts = len(payouts)
            
            total_premiums = 0
            total_payout_amount = 0
            
            for policy_atom in policies:
                policy_data = json.loads(policy_atom.atom_content)
                total_premiums += policy_data.get('premium_paid', 0)
            
            for payout_atom in payouts:
                payout_data = json.loads(payout_atom.atom_content)
                total_payout_amount += payout_data.get('amount', 0)
            
            return {
                'total_policies': total_policies,
                'active_policies': len([p for p in policies if json.loads(p.atom_content).get('status') == 'active']),
                'total_payouts': total_payouts,
                'total_premiums_collected': total_premiums,
                'total_payouts_made': total_payout_amount,
                'fund_balance': max(0, total_premiums - total_payout_amount),
                'payout_ratio': total_payout_amount / total_premiums if total_premiums > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting insurance stats: {e}")
            return {
                'total_policies': 0,
                'active_policies': 0,
                'total_payouts': 0,
                'total_premiums_collected': 0,
                'total_payouts_made': 0,
                'fund_balance': 0,
                'payout_ratio': 0
            }
    
    # Private helper methods
    
    async def _store_policy(self, policy: SimpleInsurancePolicy):
        """Store insurance policy in database"""
        try:
            atom = MeTTaAtom(
                id=policy.id,
                event_id="",  # Not tied to specific event
                atom_type='insurance_policy',
                atom_content=json.dumps(policy.to_dict()),
                created_at=datetime.now()
            )
            await crud.create_atom(atom)
        except Exception as e:
            print(f"Error storing policy: {e}")
    
    async def _store_payout(self, payout: InsurancePayout):
        """Store insurance payout in database"""
        try:
            atom = MeTTaAtom(
                id=payout.id,
                event_id=payout.event_id,
                atom_type='insurance_payout',
                atom_content=json.dumps(payout.to_dict()),
                created_at=datetime.now()
            )
            await crud.create_atom(atom)
        except Exception as e:
            print(f"Error storing payout: {e}")
    
    async def _update_policy_status(self, policy_id: str, new_status: str):
        """Update policy status"""
        try:
            atoms = await crud.get_all_atoms()
            for atom in atoms:
                if atom.atom_type == 'insurance_policy' and atom.id == policy_id:
                    policy_data = json.loads(atom.atom_content)
                    policy_data['status'] = new_status
                    # Update the atom content
                    updated_atom = MeTTaAtom(
                        id=atom.id,
                        event_id=atom.event_id,
                        atom_type=atom.atom_type,
                        atom_content=json.dumps(policy_data),
                        created_at=atom.created_at
                    )
                    # In a real implementation, you'd update the existing atom
                    break
        except Exception as e:
            print(f"Error updating policy status: {e}")
    
    def _calculate_event_severity(self, event) -> float:
        """Calculate event severity for MeTTa processing"""
        # Simple severity calculation based on event type and description
        severity_map = {
            'drought': 0.8,
            'flood': 0.7,
            'locust': 0.9,
            'extreme_heat': 0.6,
            'wildfire': 0.9,
            'storm': 0.7
        }
        
        base_severity = severity_map.get(event.event_type, 0.5)
        
        # Adjust based on description keywords
        if event.description:
            description_lower = event.description.lower()
            if any(word in description_lower for word in ['severe', 'extreme', 'devastating', 'massive']):
                base_severity = min(1.0, base_severity + 0.2)
            elif any(word in description_lower for word in ['minor', 'small', 'light']):
                base_severity = max(0.1, base_severity - 0.2)
        
        return base_severity
    
    def _parse_metta_insurance_result(self, metta_result) -> dict:
        """Parse MeTTa insurance trigger result"""
        try:
            # Parse MeTTa result for insurance trigger
            result_data = {
                'triggered': False,
                'payout_amount': 0,
                'contract_call': None
            }
            
            if metta_result and len(metta_result) > 0:
                result_str = str(metta_result[0]) if metta_result else ""
                if "micro-insurance-triggered" in result_str:
                    result_data['triggered'] = True
                    # Extract payout amount if available
                    import re
                    numbers = re.findall(r'\d+\.?\d*', result_str)
                    if numbers:
                        result_data['payout_amount'] = float(numbers[0]) if numbers[0] else 0
            
            return result_data
            
        except Exception as e:
            print(f"Error parsing MeTTa insurance result: {e}")
            return {'triggered': False, 'payout_amount': 0, 'contract_call': None}