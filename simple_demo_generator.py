#!/usr/bin/env python3
"""
Simple Demo Data Generator
Creates demo data for Climate Witness Chain testing
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Simple demo data generator that doesn't depend on complex imports
class SimpleDemoGenerator:
    """Simple demo data generator for testing"""
    
    def __init__(self):
        self.demo_users = []
        self.demo_events = []
        self.demo_locations = [
            {"name": "Malawi", "lat": -15.7975, "lng": 35.0184, "region": "Southern Africa"},
            {"name": "Bangladesh", "lat": 23.6978, "lng": 90.3732, "region": "South Asia"},
            {"name": "Kenya", "lat": -0.0236, "lng": 37.9062, "region": "East Africa"},
            {"name": "Philippines", "lat": 14.5995, "lng": 120.9842, "region": "Southeast Asia"},
            {"name": "India", "lat": 20.5937, "lng": 78.9629, "region": "South Asia"}
        ]
        
        self.event_types = ["drought", "flood", "extreme_heat", "locust", "storm"]
        
    def generate_demo_users(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate demo user data"""
        users = []
        
        for i in range(count):
            user = {
                "id": f"demo_user_{i+1}",
                "name": f"Demo User {i+1}",
                "email": f"user{i+1}@demo.org",
                "trust_score": round(0.6 + (random.random() * 0.4), 2),
                "wallet_address": f"0x{''.join([random.choice('0123456789abcdef') for _ in range(40)])}",
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "role": random.choice(["farmer", "citizen_reporter", "local_official"]),
                    "location": random.choice(self.demo_locations)["name"],
                    "experience_years": random.randint(1, 20)
                }
            }
            users.append(user)
        
        self.demo_users = users
        return users
    
    def generate_demo_events(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate demo climate events"""
        events = []
        
        for i in range(count):
            location = random.choice(self.demo_locations)
            event_type = random.choice(self.event_types)
            
            # Generate timestamp within last 30 days
            days_ago = random.randint(0, 30)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            event = {
                "id": f"demo_event_{i+1}",
                "user_id": random.choice(self.demo_users)["id"] if self.demo_users else f"demo_user_{random.randint(1,5)}",
                "event_type": event_type,
                "description": self.generate_event_description(event_type, location["name"]),
                "latitude": location["lat"] + random.uniform(-0.5, 0.5),
                "longitude": location["lng"] + random.uniform(-0.5, 0.5),
                "location_name": f"{location['name']} Region",
                "timestamp": timestamp.isoformat(),
                "severity": random.choice(["low", "medium", "high"]),
                "verified": random.choice([True, False]),
                "photo_path": f"demo_{event_type}_{i+1}.jpg",
                "metadata": self.generate_event_metadata(event_type)
            }
            events.append(event)
        
        self.demo_events = events
        return events
    
    def generate_event_description(self, event_type: str, location: str) -> str:
        """Generate realistic event descriptions"""
        descriptions = {
            "drought": [
                f"Severe drought conditions reported in {location} with no rainfall for weeks",
                f"Crops failing due to prolonged dry spell in {location}",
                f"Water sources depleting rapidly in {location} area"
            ],
            "flood": [
                f"Flash flooding affecting communities in {location}",
                f"Heavy monsoon rains causing widespread flooding in {location}",
                f"River overflow displacing families in {location}"
            ],
            "extreme_heat": [
                f"Record temperatures exceeding 45°C in {location}",
                f"Heat wave affecting vulnerable populations in {location}",
                f"Extreme heat causing livestock deaths in {location}"
            ],
            "locust": [
                f"Desert locust swarms destroying crops in {location}",
                f"Massive locust invasion threatening food security in {location}",
                f"Agricultural lands under attack by locusts in {location}"
            ],
            "storm": [
                f"Cyclone causing destruction in {location}",
                f"Severe thunderstorms with damaging winds in {location}",
                f"Tropical storm bringing heavy rains to {location}"
            ]
        }
        
        return random.choice(descriptions.get(event_type, [f"Climate event reported in {location}"]))
    
    def generate_event_metadata(self, event_type: str) -> Dict[str, Any]:
        """Generate event-specific metadata"""
        base_metadata = {
            "temperature_c": random.randint(20, 45),
            "humidity_percent": random.randint(10, 90),
            "wind_speed_kmh": random.randint(0, 100)
        }
        
        if event_type == "drought":
            base_metadata.update({
                "days_without_rain": random.randint(30, 120),
                "soil_moisture_percent": random.randint(5, 25)
            })
        elif event_type == "flood":
            base_metadata.update({
                "rainfall_mm": random.randint(100, 500),
                "water_level_cm": random.randint(50, 300)
            })
        elif event_type == "extreme_heat":
            base_metadata.update({
                "max_temperature_c": random.randint(40, 50),
                "heat_index": random.randint(45, 55)
            })
        
        return base_metadata
    
    def generate_demo_insurance_policies(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate demo insurance policies"""
        policies = []
        
        for i in range(count):
            policy = {
                "id": f"policy_{i+1}",
                "user_id": random.choice(self.demo_users)["id"] if self.demo_users else f"demo_user_{i+1}",
                "premium_matic": round(random.uniform(0.01, 0.05), 3),
                "coverage_matic": round(random.uniform(0.1, 0.5), 2),
                "coverage_type": random.choice(["crop", "livestock", "property"]),
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
                "active": True,
                "payouts_processed": random.randint(0, 3)
            }
            policies.append(policy)
        
        return policies
    
    def generate_demo_statistics(self) -> Dict[str, Any]:
        """Generate demo platform statistics"""
        return {
            "total_users": len(self.demo_users),
            "total_events": len(self.demo_events),
            "verified_events": len([e for e in self.demo_events if e.get("verified")]),
            "total_payouts_matic": round(random.uniform(10, 50), 2),
            "average_trust_score": round(sum(u["trust_score"] for u in self.demo_users) / len(self.demo_users), 2) if self.demo_users else 0,
            "events_by_type": {
                event_type: len([e for e in self.demo_events if e["event_type"] == event_type])
                for event_type in self.event_types
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def save_demo_data(self, filename: str = "demo_data.json"):
        """Save all demo data to JSON file"""
        demo_data = {
            "users": self.demo_users,
            "events": self.demo_events,
            "policies": self.generate_demo_insurance_policies(),
            "statistics": self.generate_demo_statistics(),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_users": len(self.demo_users),
                "total_events": len(self.demo_events),
                "locations": self.demo_locations
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(demo_data, f, indent=2)
        
        return demo_data
    
    def print_demo_summary(self):
        """Print a summary of generated demo data"""
        print("\n" + "=" * 60)
        print(" CLIMATE WITNESS CHAIN - DEMO DATA SUMMARY")
        print("=" * 60)
        
        print(f"\n Generated Demo Data:")
        print(f"    Users: {len(self.demo_users)}")
        print(f"    Events: {len(self.demo_events)}")
        print(f"   ✅ Verified Events: {len([e for e in self.demo_events if e.get('verified')])}")
        
        print(f"\n Event Types Distribution:")
        for event_type in self.event_types:
            count = len([e for e in self.demo_events if e["event_type"] == event_type])
            print(f"   {event_type.title()}: {count}")
        
        print(f"\n Locations Covered:")
        for location in self.demo_locations:
            print(f"   {location['name']} ({location['region']})")
        
        print(f"\n⭐ Average Trust Score: {sum(u['trust_score'] for u in self.demo_users) / len(self.demo_users):.2f}")
        
        print("\n✅ Demo data ready for testing and presentation!")

def main():
    """Generate demo data for Climate Witness Chain"""
    print(" Climate Witness Chain - Demo Data Generator")
    print("Generating realistic demo data for testing...")
    
    generator = SimpleDemoGenerator()
    
    # Generate demo data
    users = generator.generate_demo_users(15)
    events = generator.generate_demo_events(30)
    
    # Save to file
    demo_data = generator.save_demo_data()
    
    # Print summary
    generator.print_demo_summary()
    
    print(f"\n Demo data saved to: demo_data.json")
    print(" Ready for demo presentation!")
    
    return demo_data

if __name__ == "__main__":
    main()
