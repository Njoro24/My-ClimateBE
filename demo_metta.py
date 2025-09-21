#!/usr/bin/env python3
"""
MeTTa Demo Script for Climate Witness Chain
Demonstrates MeTTa knowledge atoms, verification logic, and reasoning
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.metta_service import ClimateWitnessKnowledgeBase, MeTTaService
from app.database.models import User, Event
from app.database.database import init_db

async def demo_metta_knowledge_base():
    """Demonstrate MeTTa knowledge base functionality"""
    print(" MeTTa Knowledge Base Demo")
    print("=" * 60)
    
    # Initialize knowledge base
    kb = ClimateWitnessKnowledgeBase()
    
    print("1. Knowledge Base State:")
    state = kb.get_knowledge_base_state()
    for key, value in state.items():
        print(f"   {key}: {value}")
    
    print("\n2. Creating Demo User and Event:")
    
    # Create demo user
    user = User(
        id="demo-user-amina",
        wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF",
        trust_score=75,
        location_region="Turkana, Kenya",
        created_at=datetime.now()
    )
    
    # Create demo event
    event = Event(
        id="demo-event-drought-001",
        user_id="demo-user-amina",
        event_type="drought",
        description="Severe drought affecting livestock in Turkana region",
        latitude=3.1190,
        longitude=35.5970,
        photo_path="uploads/drought_evidence.jpg",
        timestamp=datetime.now()
    )
    
    print(f"   User: {user.id} (Trust Score: {user.trust_score})")
    print(f"   Event: {event.event_type} at ({event.latitude}, {event.longitude})")
    
    print("\n3. Generating MeTTa Atoms:")
    
    # Create user atoms
    user_atoms = kb.create_user_atoms(user)
    print(f"   User Atoms ({len(user_atoms)}):")
    for atom in user_atoms:
        print(f"     {atom}")
    
    # Create event atoms
    event_atoms, metta_event_id = kb.create_event_atoms(event, user)
    print(f"\n   Event Atoms ({len(event_atoms)}):")
    for atom in event_atoms:
        print(f"     {atom}")
    
    print(f"\n   MeTTa Event ID: {metta_event_id}")
    
    print("\n4. Running MeTTa Verification:")
    
    # Run verification
    verification_result = kb.run_verification(event_atoms, user_atoms, metta_event_id, user.id)
    
    print(f"   Verification Result: {'✅ VERIFIED' if verification_result['verified'] else '❌ FAILED'}")
    print(f"   Atoms Created: {verification_result['atoms_created']}")
    print(f"   Verification Time: {verification_result['verification_time']}")
    
    print("\n   Reasoning:")
    for reason in verification_result['reasoning']:
        print(f"     {reason}")
    
    print("\n5. Calculating Payout:")
    
    if verification_result['verified']:
        payout_amount = kb.calculate_payout(metta_event_id)
        if payout_amount:
            print(f"    Payout Amount: {payout_amount} ETH")
        else:
            print("   ❌ No payout calculated")
    else:
        print("   ❌ Event not verified - no payout")
    
    print("\n6. Testing Knowledge Base Queries:")
    
    # Test various queries
    queries = [
        "(climate-event-type $type)",
        f"(trust-score {user.id} $score)",
        f"(verified {metta_event_id})",
        "(min-trust-score $threshold)"
    ]
    
    for query in queries:
        print(f"   Query: {query}")
        results = kb.query_knowledge_base(query)
        if results:
            for result in results[:3]:  # Show first 3 results
                print(f"     Result: {result}")
        else:
            print("     No results")
        print()

async def demo_different_scenarios():
    """Demonstrate different verification scenarios"""
    print("\n Different Verification Scenarios")
    print("=" * 60)
    
    kb = ClimateWitnessKnowledgeBase()
    
    scenarios = [
        {
            "name": "High Trust User with Complete Evidence",
            "user": User(id="user1", trust_score=85, location_region="Kenya"),
            "event": Event(id="event1", user_id="user1", event_type="flood", 
                          latitude=1.0, longitude=36.0, photo_path="photo.jpg", timestamp=datetime.now())
        },
        {
            "name": "Low Trust User with Complete Evidence", 
            "user": User(id="user2", trust_score=45, location_region="Kenya"),
            "event": Event(id="event2", user_id="user2", event_type="drought",
                          latitude=2.0, longitude=37.0, photo_path="photo.jpg", timestamp=datetime.now())
        },
        {
            "name": "High Trust User with Missing Evidence",
            "user": User(id="user3", trust_score=80, location_region="Kenya"),
            "event": Event(id="event3", user_id="user3", event_type="locust",
                          latitude=3.0, longitude=38.0, photo_path=None, timestamp=datetime.now())
        },
        {
            "name": "High Trust User with Missing GPS",
            "user": User(id="user4", trust_score=90, location_region="Kenya"),
            "event": Event(id="event4", user_id="user4", event_type="extreme_heat",
                          latitude=None, longitude=None, photo_path="photo.jpg", timestamp=datetime.now())
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}:")
        
        user_atoms = kb.create_user_atoms(scenario['user'])
        event_atoms, metta_event_id = kb.create_event_atoms(scenario['event'], scenario['user'])
        
        result = kb.run_verification(event_atoms, user_atoms, metta_event_id, scenario['user'].id)
        
        print(f"   Result: {'✅ VERIFIED' if result['verified'] else '❌ FAILED'}")
        print("   Key Reasoning:")
        for reason in result['reasoning'][:3]:  # Show first 3 reasons
            print(f"     {reason}")
        print()

async def demo_metta_service_integration():
    """Demonstrate MeTTa service integration with database"""
    print("\n MeTTa Service Integration Demo")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    await init_db()
    
    # Initialize service
    service = MeTTaService()
    
    print("2. Testing knowledge base state:")
    kb_state = service.get_knowledge_base_state()
    for key, value in kb_state.items():
        print(f"   {key}: {value}")
    
    print("\n3. Testing knowledge base queries:")
    queries = [
        "(climate-event-type Drought)",
        "(min-trust-score $threshold)",
        "(impact-category $category)"
    ]
    
    for query in queries:
        print(f"   Query: {query}")
        results = service.query_knowledge_base(query)
        if results:
            for result in results[:2]:
                print(f"     {result}")
        print()

async def main():
    """Main demo function"""
    print(" Climate Witness Chain - MeTTa Demo")
    print("=" * 80)
    
    try:
        await demo_metta_knowledge_base()
        await demo_different_scenarios()
        await demo_metta_service_integration()
        
        print("\n MeTTa Demo Complete!")
        print("The MeTTa knowledge base is working correctly and ready for integration.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())