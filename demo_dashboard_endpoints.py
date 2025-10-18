#!/usr/bin/env python3
"""
Demo endpoints for dashboard functionality
Add these to simple_main.py to support the dashboard
"""

from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import random
import json

def add_dashboard_endpoints(app: FastAPI):
    """Add dashboard endpoints to the FastAPI app"""
    
    # User endpoints
    @app.get("/users/{user_id}/stats")
    async def get_user_stats(user_id: str):
        """Get user statistics"""
        return {
            "stats": {
                "user_id": user_id,
                "trust_score": random.randint(60, 95),
                "location_region": random.choice(["Nairobi", "Mombasa", "Kisumu", "Nakuru"]),
                "member_since": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                "total_events": random.randint(5, 25),
                "verified_events": random.randint(3, 20),
                "verification_rate": round(random.uniform(0.7, 0.95), 2),
                "total_payouts": random.randint(0, 500),
                "trust_level": random.choice(["Excellent", "High", "Good"])
            }
        }
    
    @app.get("/users/{user_id}")
    async def get_user_profile(user_id: str):
        """Get user profile"""
        return {
            "user": {
                "id": user_id,
                "firstName": "Demo",
                "lastName": "User",
                "email": "demo@example.com",
                "role": "user",
                "locationRegion": random.choice(["Nairobi", "Mombasa", "Kisumu"]),
                "trust_score": random.randint(60, 95),
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
            }
        }
    
    @app.get("/users/{user_id}/history")
    async def get_user_history(user_id: str):
        """Get user event history"""
        events = []
        for i in range(random.randint(3, 8)):
            events.append({
                "event_id": f"event_{i+1}",
                "event_type": random.choice(["drought", "flood", "locust_swarm", "extreme_heat"]),
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "verification_status": random.choice(["verified", "pending", "rejected"]),
                "payout_amount": random.randint(0, 100) if random.random() > 0.5 else None,
                "location": f"({random.uniform(-5, 5):.4f}, {random.uniform(34, 42):.4f})"
            })
        
        return {
            "history": events,
            "total_events": len(events)
        }
    
    # Insurance endpoints
    @app.get("/insurance/user/{user_id}/policies")
    async def get_user_policies(user_id: str):
        """Get user insurance policies"""
        policies = []
        if random.random() > 0.3:  # 70% chance of having a policy
            policies.append({
                "id": f"policy_{user_id}",
                "user_id": user_id,
                "status": "active",
                "coverage_amount": 1000,
                "premium_paid": 50,
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
            })
        
        return {
            "policies": policies,
            "total_policies": len(policies)
        }
    
    @app.get("/insurance/user/{user_id}/payouts")
    async def get_user_payouts(user_id: str):
        """Get user insurance payouts"""
        payouts = []
        total_received = 0
        
        for i in range(random.randint(0, 3)):
            amount = random.randint(50, 200)
            payouts.append({
                "id": f"payout_{i+1}",
                "user_id": user_id,
                "event_id": f"event_{i+1}",
                "amount": amount,
                "status": "completed",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
            })
            total_received += amount
        
        return {
            "payouts": payouts,
            "total_amount_received": total_received,
            "total_payouts": len(payouts)
        }
    
    @app.get("/insurance/stats")
    async def get_insurance_stats():
        """Get insurance system statistics"""
        return {
            "statistics": {
                "total_policies": random.randint(100, 500),
                "active_policies": random.randint(80, 400),
                "total_payouts": random.randint(50, 200),
                "fund_balance": random.randint(10000, 50000),
                "total_claims": random.randint(30, 150)
            }
        }
    
    # DAO Governance endpoints
    @app.get("/dao-governance/proposals/active")
    async def get_active_proposals():
        """Get active DAO proposals"""
        proposals = []
        for i in range(random.randint(2, 5)):
            proposals.append({
                "id": f"proposal_{i+1}",
                "title": f"Climate Action Proposal #{i+1}",
                "description": f"Funding request for climate monitoring in region {i+1}",
                "status": "active",
                "requested_amount": random.randint(1000, 10000),
                "yes_votes": random.randint(10, 50),
                "no_votes": random.randint(2, 15),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
        
        return {
            "proposals": proposals
        }
    
    @app.get("/dao-governance/stats")
    async def get_dao_stats():
        """Get DAO statistics"""
        return {
            "active_proposals": random.randint(3, 8),
            "treasury_balance": random.randint(50000, 200000),
            "total_members": random.randint(500, 2000),
            "total_distributed": random.randint(10000, 100000)
        }
    
    # Alerts endpoints
    @app.get("/alerts/user/{user_id}")
    async def get_user_alerts(user_id: str):
        """Get user alerts"""
        alerts = []
        for i in range(random.randint(2, 6)):
            alerts.append({
                "id": f"alert_{i+1}",
                "alert_type": random.choice(["early_warning", "weather", "emergency"]),
                "severity": random.choice(["high", "medium", "low"]),
                "message": f"Climate alert #{i+1} - {random.choice(['Drought warning', 'Flood risk', 'Temperature alert'])}",
                "location": {"latitude": random.uniform(-5, 5), "longitude": random.uniform(34, 42)},
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "actionable_guidance": [
                    "Monitor weather conditions",
                    "Prepare emergency supplies",
                    "Stay informed through official channels"
                ]
            })
        
        return {
            "alerts": alerts,
            "total": len(alerts)
        }
    
    @app.get("/alerts/location")
    async def get_location_alerts(latitude: float, longitude: float, radius: float = 50):
        """Get location-based alerts"""
        alerts = []
        for i in range(random.randint(1, 4)):
            alerts.append({
                "id": f"location_alert_{i+1}",
                "alert_type": random.choice(["weather", "emergency", "early_warning"]),
                "severity": random.choice(["high", "medium", "low"]),
                "message": f"Regional alert - {random.choice(['Heavy rainfall expected', 'Drought conditions', 'Locust activity'])}",
                "location": {"latitude": latitude + random.uniform(-0.5, 0.5), "longitude": longitude + random.uniform(-0.5, 0.5)},
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            })
        
        return {
            "alerts": alerts,
            "total": len(alerts)
        }
    
    @app.get("/alerts/stats")
    async def get_alert_stats():
        """Get alert system statistics"""
        return {
            "total_alerts": random.randint(100, 500),
            "active_alerts": random.randint(10, 50),
            "high_priority": random.randint(5, 20),
            "medium_priority": random.randint(15, 40),
            "low_priority": random.randint(20, 60)
        }
    
    # Community Verification endpoints
    @app.get("/community-verification/assignments/{verifier_id}")
    async def get_verification_assignments(verifier_id: str):
        """Get verification assignments"""
        assignments = []
        for i in range(random.randint(1, 4)):
            assignments.append({
                "event_id": f"event_{i+1}",
                "event_type": random.choice(["drought", "flood", "locust_swarm"]),
                "description": f"Climate event requiring verification #{i+1}",
                "location": {"latitude": random.uniform(-5, 5), "longitude": random.uniform(34, 42)},
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat(),
                "photo_path": f"/uploads/event_{i+1}.jpg" if random.random() > 0.5 else None,
                "assigned_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                "deadline": (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat()
            })
        
        return assignments
    
    @app.get("/community-verification/verifier-stats/{verifier_id}")
    async def get_verifier_stats(verifier_id: str):
        """Get verifier statistics"""
        total_verifications = random.randint(5, 50)
        correct_verifications = random.randint(int(total_verifications * 0.7), total_verifications)
        
        return {
            "verifier_id": verifier_id,
            "trust_score": random.randint(60, 95),
            "verifier_weight": round(random.uniform(0.7, 1.0), 2),
            "total_verifications": total_verifications,
            "correct_verifications": correct_verifications,
            "accuracy": round(correct_verifications / max(total_verifications, 1), 2),
            "status": "active",
            "recent_activity": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat()
        }
    
    @app.get("/community-verification/leaderboard")
    async def get_verifier_leaderboard(limit: int = 10):
        """Get verifier leaderboard"""
        leaderboard = []
        for i in range(min(limit, 10)):
            total_verifications = random.randint(10, 100)
            accuracy = round(random.uniform(0.8, 0.98), 2)
            leaderboard.append({
                "verifier_id": f"verifier_{i+1}",
                "wallet_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                "trust_score": random.randint(80, 98),
                "total_verifications": total_verifications,
                "accuracy": accuracy,
                "verifier_weight": round(random.uniform(0.8, 1.0), 2),
                "status": "active"
            })
        
        # Sort by trust score
        leaderboard.sort(key=lambda x: x["trust_score"], reverse=True)
        
        return {
            "leaderboard": leaderboard,
            "total_verifiers": len(leaderboard)
        }
    
    # Events endpoints
    @app.get("/events/user/{user_id}")
    async def get_user_events(user_id: str):
        """Get user events"""
        events = []
        for i in range(random.randint(3, 8)):
            events.append({
                "id": f"event_{i+1}",
                "user_id": user_id,
                "event_type": random.choice(["drought", "flood", "locust_swarm", "extreme_heat"]),
                "description": f"Climate event report #{i+1}",
                "latitude": random.uniform(-5, 5),
                "longitude": random.uniform(34, 42),
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "verification_status": random.choice(["verified", "pending", "rejected"]),
                "payout_amount": random.randint(50, 200) if random.random() > 0.6 else None
            })
        
        return {
            "events": events,
            "total": len(events)
        }
    
    print("✅ Dashboard demo endpoints added")

if __name__ == "__main__":
    # This can be used to test the endpoints
    from fastapi import FastAPI
    app = FastAPI()
    add_dashboard_endpoints(app)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)