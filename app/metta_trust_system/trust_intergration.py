"""
Python Integration Layer for MeTTa Trust Score Engine
Connects the MeTTa trust engine with your existing emergency reporting system
"""

from hyperon import MeTTa, Environment, Atom, AtomType
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class MeTTaTrustEngine:
    """
    Python wrapper for MeTTa trust score management system
    """
    
    def __init__(self, metta_file_path: str = "trust_engine.metta"):
        """Initialize MeTTa environment and load trust engine"""
        self.metta = MeTTa()
        self.env = Environment()
        
        # Load the trust engine MeTTa file
        try:
            with open(metta_file_path, 'r') as f:
                metta_code = f.read()
            self.metta.run(metta_code)
            logging.info("MeTTa trust engine loaded successfully")
        except FileNotFoundError:
            logging.error(f"MeTTa file not found: {metta_file_path}")
            raise
        except Exception as e:
            logging.error(f"Error loading MeTTa engine: {e}")
            raise
    
    def register_user(self, user_id: str) -> int:
        """
        Register a new user with initial trust score of 50
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Initial trust score (50)
        """
        try:
            result = self.metta.run(f"!(register-user {user_id})")
            logging.info(f"User {user_id} registered with trust score 50")
            return 50
        except Exception as e:
            logging.error(f"Error registering user {user_id}: {e}")
            raise
    
    def get_trust_score(self, user_id: str) -> Optional[int]:
        """
        Get current trust score for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Current trust score or None if user not found
        """
        try:
            result = self.metta.run(f"!(get-trust-score {user_id})")
            if result:
                return int(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting trust score for {user_id}: {e}")
            return None
    
    def handle_verified_report(self, user_id: str, event_id: str) -> int:
        """
        Process a verified legitimate report (+15 points)
        
        Args:
            user_id: User who submitted the report
            event_id: Unique event identifier
            
        Returns:
            New trust score
        """
        try:
            result = self.metta.run(f"!(handle-verified-report {user_id} {event_id})")
            new_score = int(result[0]) if result else self.get_trust_score(user_id)
            logging.info(f"Verified report processed. User {user_id} new score: {new_score}")
            return new_score
        except Exception as e:
            logging.error(f"Error processing verified report: {e}")
            raise
    
    def handle_false_report(self, user_id: str, event_id: str) -> int:
        """
        Process a false report (-10 points, potential warning)
        
        Args:
            user_id: User who submitted the false report
            event_id: Unique event identifier
            
        Returns:
            New trust score
        """
        try:
            result = self.metta.run(f"!(handle-false-report {user_id} {event_id})")
            new_score = int(result[0]) if result else self.get_trust_score(user_id)
            logging.warning(f"False report processed. User {user_id} new score: {new_score}")
            return new_score
        except Exception as e:
            logging.error(f"Error processing false report: {e}")
            raise
    
    def handle_malicious_report(self, user_id: str, event_id: str) -> int:
        """
        Process a malicious/severely false report (-25 points, potential suspension)
        
        Args:
            user_id: User who submitted the malicious report
            event_id: Unique event identifier
            
        Returns:
            New trust score
        """
        try:
            result = self.metta.run(f"!(handle-malicious-report {user_id} {event_id})")
            new_score = int(result[0]) if result else self.get_trust_score(user_id)
            logging.critical(f"Malicious report processed. User {user_id} new score: {new_score}")
            return new_score
        except Exception as e:
            logging.error(f"Error processing malicious report: {e}")
            raise
    
    def can_submit_report(self, user_id: str) -> bool:
        """
        Check if user is authorized to submit reports
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user can submit reports, False otherwise
        """
        try:
            result = self.metta.run(f"!(can-submit-report {user_id})")
            return bool(result[0]) if result else False
        except Exception as e:
            logging.error(f"Error checking submission authorization for {user_id}: {e}")
            return False
    
    def get_user_status(self, user_id: str) -> str:
        """
        Get current user status (active, warned, suspended)
        
        Args:
            user_id: User identifier
            
        Returns:
            User status string
        """
        try:
            result = self.metta.run(f"!(get-user-status {user_id})")
            return str(result[0]) if result else "unknown"
        except Exception as e:
            logging.error(f"Error getting user status for {user_id}: {e}")
            return "error"
    
    def calculate_reliability(self, user_id: str) -> float:
        """
        Calculate user reliability percentage
        
        Args:
            user_id: User identifier
            
        Returns:
            Reliability percentage (0-100)
        """
        try:
            result = self.metta.run(f"!(calculate-reliability {user_id})")
            return float(result[0]) if result else 0.0
        except Exception as e:
            logging.error(f"Error calculating reliability for {user_id}: {e}")
            return 0.0
    
    def get_users_needing_review(self) -> List[str]:
        """
        Get list of users with low trust scores needing review
        
        Returns:
            List of user IDs
        """
        try:
            result = self.metta.run("!(get-users-needing-review)")
            return [str(user) for user in result] if result else []
        except Exception as e:
            logging.error(f"Error getting users needing review: {e}")
            return []
    
    def get_top_trusted_users(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get top trusted users
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of tuples (user_id, trust_score)
        """
        try:
            result = self.metta.run(f"!(get-top-trusted-users {limit})")
            return [(str(user), int(score)) for user, score in result] if result else []
        except Exception as e:
            logging.error(f"Error getting top trusted users: {e}")
            return []
    
    def process_report_batch(self, reports: List[Dict]) -> List[int]:
        """
        Process multiple reports in batch
        
        Args:
            reports: List of report dictionaries with keys:
                    - type: 'verified', 'false', or 'malicious'
                    - user_id: User identifier
                    - event_id: Event identifier
        
        Returns:
            List of new trust scores
        """
        results = []
        for report in reports:
            try:
                report_type = report['type']
                user_id = report['user_id']
                event_id = report['event_id']
                
                if report_type == 'verified':
                    score = self.handle_verified_report(user_id, event_id)
                elif report_type == 'false':
                    score = self.handle_false_report(user_id, event_id)
                elif report_type == 'malicious':
                    score = self.handle_malicious_report(user_id, event_id)
                else:
                    logging.error(f"Unknown report type: {report_type}")
                    continue
                
                results.append(score)
            except Exception as e:
                logging.error(f"Error processing report batch item: {e}")
                continue
        
        return results
    
    def apply_time_bonus(self, user_id: str, days_since_last_false: int) -> int:
        """
        Apply time-based trust recovery bonus
        
        Args:
            user_id: User identifier
            days_since_last_false: Days since last false report
            
        Returns:
            New trust score
        """
        try:
            result = self.metta.run(f"!(apply-time-bonus {user_id} {days_since_last_false})")
            new_score = int(result[0]) if result else self.get_trust_score(user_id)
            logging.info(f"Time bonus applied to {user_id}. New score: {new_score}")
            return new_score
        except Exception as e:
            logging.error(f"Error applying time bonus to {user_id}: {e}")
            raise
    
    def get_user_summary(self, user_id: str) -> Dict:
        """
        Get comprehensive user summary
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user stats
        """
        return {
            'user_id': user_id,
            'trust_score': self.get_trust_score(user_id),
            'status': self.get_user_status(user_id),
            'reliability': self.calculate_reliability(user_id),
            'can_submit': self.can_submit_report(user_id)
        }


class TrustEngineAPI:
    """
    REST API wrapper for the MeTTa Trust Engine
    Use this with Flask/FastAPI for web integration
    """
    
    def __init__(self):
        self.engine = MeTTaTrustEngine()
    
    def handle_user_login(self, user_id: str) -> Dict:
        """
        Handle user login - register if new, return current status
        
        Args:
            user_id: User identifier
            
        Returns:
            User status dictionary
        """
        current_score = self.engine.get_trust_score(user_id)
        
        if current_score is None:
            # New user - register with initial score
            self.engine.register_user(user_id)
            return self.engine.get_user_summary(user_id)
        else:
            # Existing user - return current status
            return self.engine.get_user_summary(user_id)
    
    def process_report_verification(self, user_id: str, event_id: str, 
                                  verification_result: str) -> Dict:
        """
        Process report verification result
        
        Args:
            user_id: User who submitted report
            event_id: Event identifier
            verification_result: 'verified', 'false', or 'malicious'
            
        Returns:
            Updated user status
        """
        if verification_result == 'verified':
            self.engine.handle_verified_report(user_id, event_id)
        elif verification_result == 'false':
            self.engine.handle_false_report(user_id, event_id)
        elif verification_result == 'malicious':
            self.engine.handle_malicious_report(user_id, event_id)
        else:
            raise ValueError(f"Invalid verification result: {verification_result}")
        
        return self.engine.get_user_summary(user_id)


# Example usage
if __name__ == "__main__":
    # Initialize the trust engine
    trust_engine = MeTTaTrustEngine()
    
    # Example user flow
    user_id = "e8fa252d-a4da-4264-bff5-6af483e0c195"
    
    # Register user (automatically gets 50 points)
    initial_score = trust_engine.register_user(user_id)
    print(f"User registered with score: {initial_score}")
    
    # User submits verified report (+15 points)
    new_score = trust_engine.handle_verified_report(user_id, "locust_b37cad91")
    print(f"After verified report: {new_score}")
    
    # User submits false report (-10 points, potential warning)
    new_score = trust_engine.handle_false_report(user_id, "fake_event_001")
    print(f"After false report: {new_score}")
    
    # Check if user can still submit reports
    can_submit = trust_engine.can_submit_report(user_id)
    print(f"Can submit reports: {can_submit}")
    
    # Get user summary
    summary = trust_engine.get_user_summary(user_id)
    print(f"User summary: {json.dumps(summary, indent=2)}")