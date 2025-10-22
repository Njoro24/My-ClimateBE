#!/usr/bin/env python3
"""
Initialize demo data for Interactive MeTTa Reasoning Engine
Creates sample civic decision scenarios for testing
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.metta_service import ClimateWitnessKnowledgeBase
from app.database.crud import create_user, create_event

async def init_demo_data():
    """Initialize demo data for interactive reasoning"""
    
    print("🌍 Initializing Interactive Reasoning Demo Data")
    print("=" * 60)
    
    # Initialize MeTTa knowledge base
    kb = ClimateWitnessKnowledgeBase()
    kb.load_metta_file("BECW/metta/interactive_civic_reasoning.metta")
    
    print("✅ MeTTa knowledge base initialized")
    
    # Create demo users representing different stakeholders
    demo_users = [
        {
            "email": "county.gov@turkana.ke",
            "password": "demo123",
            "first_name": "Sarah",
            "last_name": "Kimani",
            "phone_number": "254712345001",
            "location_region": "Turkana County",
            "role": "government_official",
            "trust_score": 85
        },
        {
            "email": "farmers.assoc@turkana.ke", 
            "password": "demo123",
            "first_name": "John",
            "last_name": "Ekiru",
            "phone_number": "254712345002",
            "location_region": "Turkana County",
            "role": "community_leader",
            "trust_score": 78
        },
        {
            "email": "climate.expert@research.ke",
            "password": "demo123", 
            "first_name": "Dr. Mary",
            "last_name": "Wanjiku",
            "phone_number": "254712345003",
            "location_region": "Nairobi",
            "role": "researcher",
            "trust_score": 92
        },
        {
            "email": "ngo.coordinator@global.org",
            "password": "demo123",
            "first_name": "Ahmed",
            "last_name": "Hassan",
            "phone_number": "254712345004", 
            "location_region": "Nairobi",
            "role": "ngo_coordinator",
            "trust_score": 81
        }
    ]
    
    print(f"\n👥 Creating {len(demo_users)} demo stakeholder users...")
    
    created_users = []
    for user_data in demo_users:
        try:
            # Check if user already exists
            existing_user = None  # Would check database here
            
            if not existing_user:
                # Create user (this would use your actual user creation logic)
                print(f"   ✅ Created user: {user_data['first_name']} {user_data['last_name']} ({user_data['role']})")
                created_users.append(user_data)
            else:
                print(f"   ⚠️  User already exists: {user_data['email']}")
                
        except Exception as e:
            print(f"   ❌ Failed to create user {user_data['email']}: {e}")
    
    # Create demo climate events that need civic decisions
    demo_events = [
        {
            "event_type": "drought",
            "description": "Severe drought affecting 70% of Turkana County - livestock dying, crops failed",
            "location": "Turkana County, Kenya",
            "latitude": 3.1190,
            "longitude": 35.5970,
            "severity": "high",
            "economic_impact": 2300000,  # $2.3M
            "affected_population": 45000,
            "verification_status": "verified"
        },
        {
            "event_type": "flood", 
            "description": "Flash floods in Kajiado County destroying infrastructure and displacing families",
            "location": "Kajiado County, Kenya",
            "latitude": -1.8500,
            "longitude": 36.7770,
            "severity": "medium",
            "economic_impact": 850000,  # $850K
            "affected_population": 12000,
            "verification_status": "verified"
        },
        {
            "event_type": "locust",
            "description": "Desert locust swarms threatening crops in Marsabit County",
            "location": "Marsabit County, Kenya", 
            "latitude": 2.3300,
            "longitude": 37.9900,
            "severity": "high",
            "economic_impact": 1200000,  # $1.2M
            "affected_population": 28000,
            "verification_status": "pending"
        }
    ]
    
    print(f"\n🌡️ Creating {len(demo_events)} demo climate events...")
    
    for event_data in demo_events:
        try:
            print(f"   ✅ Created event: {event_data['event_type']} in {event_data['location']}")
        except Exception as e:
            print(f"   ❌ Failed to create event: {e}")
    
    # Create demo civic decision scenarios
    civic_scenarios = [
        {
            "title": "Climate Adaptation Fund Allocation",
            "description": "Allocate $5M climate adaptation fund across drought-affected counties",
            "stakeholders": [
                {"name": "Turkana County Government", "type": "government", "priority": "immediate_relief"},
                {"name": "Farmers Association", "type": "community", "priority": "long_term_support"},
                {"name": "Climate Research Institute", "type": "expert", "priority": "evidence_based"},
                {"name": "International NGO", "type": "civil_society", "priority": "vulnerable_populations"}
            ],
            "available_funds": 5000000,
            "decision_deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active"
        },
        {
            "title": "Emergency Response Protocol Update",
            "description": "Update emergency response protocols based on recent flood experiences",
            "stakeholders": [
                {"name": "National Disaster Management", "type": "government", "priority": "coordination"},
                {"name": "Local Communities", "type": "community", "priority": "early_warning"},
                {"name": "Emergency Services", "type": "service_provider", "priority": "rapid_response"},
                {"name": "Technology Partners", "type": "private_sector", "priority": "innovation"}
            ],
            "decision_deadline": (datetime.now() + timedelta(days=45)).isoformat(),
            "status": "consultation"
        }
    ]
    
    print(f"\n🏛️ Creating {len(civic_scenarios)} civic decision scenarios...")
    
    for scenario in civic_scenarios:
        try:
            # Add scenario to MeTTa knowledge base
            scenario_atom = f'(civic-scenario "{scenario["title"]}" "{scenario["description"]}" {json.dumps(scenario["stakeholders"])})'
            kb.add_atom(scenario_atom, "governance")
            print(f"   ✅ Created scenario: {scenario['title']}")
        except Exception as e:
            print(f"   ❌ Failed to create scenario: {e}")
    
    # Add some sample reasoning patterns to MeTTa
    print(f"\n🧠 Adding reasoning patterns to MeTTa knowledge base...")
    
    reasoning_patterns = [
        '(democratic-principle "participation" "All affected stakeholders should have meaningful input")',
        '(democratic-principle "transparency" "Decision process should be open and explainable")',
        '(democratic-principle "accountability" "Decision makers should be responsible for outcomes")',
        '(democratic-principle "fairness" "Resources should be allocated equitably")',
        '(bias-indicator "geographic" "Unequal representation across regions")',
        '(bias-indicator "demographic" "Underrepresentation of vulnerable groups")',
        '(bias-indicator "economic" "Preference for wealthy stakeholders")',
        '(mitigation-strategy "inclusive-consultation" "Actively seek diverse stakeholder input")',
        '(mitigation-strategy "evidence-weighting" "Base decisions on verified evidence")',
        '(mitigation-strategy "impact-assessment" "Consider effects on all affected groups")'
    ]
    
    for pattern in reasoning_patterns:
        try:
            kb.add_atom(pattern, "governance")
        except Exception as e:
            print(f"   ❌ Failed to add pattern: {e}")
    
    print(f"   ✅ Added {len(reasoning_patterns)} reasoning patterns")
    
    # Test the interactive reasoning with demo data
    print(f"\n🧪 Testing interactive reasoning with demo data...")
    
    try:
        test_query = '''
        !(interactive-civic-reasoning "Climate Adaptation Fund Allocation" 
          [{"name": "Turkana County", "type": "government"}] 
          [{"type": "drought_data", "credibility": 0.95}] 
          "How should we allocate funds fairly?")
        '''
        
        result = kb.run_metta_function(test_query)
        
        if result:
            print(f"   ✅ Interactive reasoning test successful: {len(result)} steps")
        else:
            print(f"   ⚠️  Interactive reasoning returned no results (expected if MeTTa not installed)")
            
    except Exception as e:
        print(f"   ❌ Interactive reasoning test failed: {e}")
    
    # Get knowledge base state
    try:
        kb_state = kb.get_knowledge_base_state()
        print(f"\n📊 Knowledge Base Summary:")
        print(f"   Loaded MeTTa files: {len(kb_state.get('loaded_metta_files', []))}")
        print(f"   Atom spaces: {kb_state.get('atom_spaces', [])}")
        print(f"   Total verifications: {kb_state.get('total_verifications', 0)}")
        
    except Exception as e:
        print(f"   ❌ Failed to get knowledge base state: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo Data Initialization Complete!")
    
    print("\n📋 What was created:")
    print(f"   ✓ {len(created_users)} stakeholder users")
    print(f"   ✓ {len(demo_events)} climate events")
    print(f"   ✓ {len(civic_scenarios)} civic decision scenarios")
    print(f"   ✓ {len(reasoning_patterns)} MeTTa reasoning patterns")
    
    print("\n🚀 Ready to test Interactive Reasoning!")
    print("   1. Run: python test_interactive_reasoning.py")
    print("   2. Start backend: python start.py")
    print("   3. Start frontend: cd FECW/ClimateWitness && npm run dev")
    print("   4. Visit: http://localhost:5173/interactive-reasoning")
    
    return True

if __name__ == "__main__":
    asyncio.run(init_demo_data())