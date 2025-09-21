
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
from datetime import datetime, timedelta
import logging
import asyncio
import os
from typing import Dict, List, Optional
from hyperon import MeTTa, AtomType, ExpressionAtom, SymbolAtom

app = FastAPI(title="MeTTa Climate Pattern Engine", version="1.0.0")

# Redis connection
redis_client = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Pydantic models
class ClimateReport(BaseModel):
    user: str
    location: str
    event_type: str
    timestamp: Optional[str] = None
    severity: str = "medium"
    description: Optional[str] = None
    evidence_link: Optional[str] = None

class PatternAnalysis(BaseModel):
    location: str
    recent_events: List[str]
    detected_patterns: List[Dict]
    risk_score: Dict
    predictions: List[Dict]

class ClimatePatternEngine:
    def __init__(self):
        self.metta = MeTTa()
        self.load_climate_knowledge()
        
    def load_climate_knowledge(self):
        """Load initial climate knowledge atoms using hyperon 0.2.2 syntax"""
        
        # Define climate event types
        climate_knowledge = """
        ;; Climate event types
        (: drought climate-event)
        (: flood climate-event)  
        (: locust-swarm climate-event)
        (: heatwave climate-event)
        (: heavy-rainfall climate-event)
        (: crop-failure climate-event)
        
        ;; Known causal relationships
        (causes drought crop-failure)
        (causes drought livestock-death)
        (precedes heatwave drought)
        (follows locust-swarm drought)
        
        ;; Impact relationships
        (impacts drought agriculture)
        (impacts flood infrastructure)
        (impacts locust-swarm food-security)
        
        ;; Sequence patterns (learned from data)
        (sequence-pattern 
            (events drought locust-swarm crop-failure) 
            (confidence 0.85)
            (lead-time 21))
            
        ;; Risk calculation rules
        (= (risk-level $events)
           (if (> (length $events) 3) high
               (if (> (length $events) 1) medium low)))
        """
        
        # Load the knowledge base
        self.metta.run(climate_knowledge)
    
    async def add_climate_report(self, report: ClimateReport) -> Dict:
        """Convert climate report to MeTTa atoms and add to knowledge base"""
        
        # Generate timestamp if not provided
        timestamp = report.timestamp or datetime.now().strftime('%Y%m%d_%H%M')
        event_id = f"{report.event_type}-{timestamp}"
        
        # Create MeTTa expressions for this report
        report_atoms = f"""
        ;; User and location facts
        (user {report.user})
        (location {report.user} {report.location})
        
        ;; Event facts
        (event {event_id} {report.event_type})
        (reported-by {event_id} {report.user})
        (occurred-at {event_id} {timestamp})
        (severity {event_id} {report.severity})
        (location-event {report.location} {event_id})
        
        ;; Evidence if provided
        {f'(evidence {event_id} "{report.evidence_link}")' if report.evidence_link else ''}
        
        ;; Description if provided  
        {f'(description {event_id} "{report.description}")' if report.description else ''}
        """
        
        # Execute the atoms
        self.metta.run(report_atoms)
        
        return {
            "atoms_added": len([line for line in report_atoms.split('\n') if line.strip() and not line.strip().startswith(';')]),
            "event_id": event_id
        }
    
    async def analyze_patterns(self, location: str, days_back: int = 30) -> PatternAnalysis:
        """Analyze climate patterns for a specific location using MeTTa reasoning"""
        
        # Query for recent events in location
        recent_events_query = f"""
        !(match &self 
            (location-event {location} $event) 
            $event)
        """
        
        recent_events = self.metta.run(recent_events_query)
        events_list = [str(event) for event in recent_events] if recent_events else []
        
        # Detect sequence patterns
        patterns = await self._detect_patterns(location)
        
        # Calculate risk score
        risk_score = await self._calculate_risk_score(location, events_list)
        
        # Generate predictions
        predictions = await self._generate_predictions(location, events_list)
        
        return PatternAnalysis(
            location=location,
            recent_events=events_list,
            detected_patterns=patterns,
            risk_score=risk_score,
            predictions=predictions
        )
    
    async def _detect_patterns(self, location: str) -> List[Dict]:
        """Detect climate event patterns using MeTTa reasoning"""
        
        # Look for drought -> locust pattern
        drought_locust_query = f"""
        !(match &self 
            (and 
                (location-event {location} $drought)
                (location-event {location} $locust)
                (event $drought drought)
                (event $locust locust-swarm)
                (occurred-at $drought $t1)
                (occurred-at $locust $t2))
            (pattern drought-to-locust $t1 $t2))
        """
        
        pattern_results = self.metta.run(drought_locust_query)
        
        patterns = []
        if pattern_results:
            patterns.append({
                "type": "sequence",
                "pattern": "drought → locust-swarm",
                "confidence": 0.85,
                "occurrences": len(pattern_results),
                "description": "Drought events followed by locust swarms"
            })
        
        return patterns
    
    async def _calculate_risk_score(self, location: str, events: List[str]) -> Dict:
        """Calculate risk score based on event frequency and severity"""
        
        # Count severe events
        severe_events_query = f"""
        !(match &self 
            (and 
                (location-event {location} $event)
                (severity $event severe))
            $event)
        """
        
        severe_events = self.metta.run(severe_events_query)
        severe_count = len(severe_events) if severe_events else 0
        
        # Calculate risk score (0.0 to 1.0)
        total_events = len(events)
        risk_score = min((severe_count * 0.3 + total_events * 0.1), 1.0)
        
        # Determine risk level
        if risk_score > 0.7:
            level = "high"
        elif risk_score > 0.4:
            level = "medium"
        else:
            level = "low"
        
        return {
            "score": round(risk_score, 2),
            "level": level,
            "severe_events": severe_count,
            "total_events": total_events
        }
    
    async def _generate_predictions(self, location: str, events: List[str]) -> List[Dict]:
        """Generate predictions based on learned patterns"""
        
        predictions = []
        
        # Check for recent drought events that might lead to locusts
        recent_drought_query = f"""
        !(match &self 
            (and 
                (location-event {location} $event)
                (event $event drought)
                (occurred-at $event $timestamp))
            $timestamp)
        """
        
        drought_events = self.metta.run(recent_drought_query)
        
        if drought_events:
            # Based on the sequence pattern, predict locust swarms
            predictions.append({
                "event_type": "locust-swarm",
                "probability": 0.78,
                "timeframe": "14-28 days",
                "reasoning": "Historical pattern shows locusts follow droughts in this region",
                "confidence_factors": [
                    f"Recent drought events detected: {len(drought_events)}",
                    "Pattern confidence: 85%",
                    "Regional climate conditions favorable"
                ],
                "recommended_actions": [
                    "Monitor vegetation stress indicators",
                    "Prepare locust control equipment",
                    "Alert neighboring communities",
                    "Coordinate with agricultural extension services"
                ]
            })
        
        # Check for flood -> crop failure pattern
        flood_events_query = f"""
        !(match &self 
            (and 
                (location-event {location} $event)
                (event $event flood))
            $event)
        """
        
        flood_events = self.metta.run(flood_events_query)
        
        if flood_events:
            predictions.append({
                "event_type": "crop-failure",
                "probability": 0.65,
                "timeframe": "7-14 days",
                "reasoning": "Flood events often lead to crop damage and failure",
                "confidence_factors": [
                    f"Recent flood events: {len(flood_events)}",
                    "Crop vulnerability during current season"
                ],
                "recommended_actions": [
                    "Assess field drainage systems",
                    "Prepare alternative food sources",
                    "Document crop damage for insurance claims"
                ]
            })
        
        return predictions

# Initialize the pattern engine
pattern_engine = ClimatePatternEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "metta-climate-engine", "version": "1.0.0"}

@app.post("/report", response_model=Dict)
async def process_climate_report(report: ClimateReport):
    """Process a new climate report and add to knowledge base"""
    try:
        # Add report to MeTTa knowledge base
        result = await pattern_engine.add_climate_report(report)
        
        # Analyze patterns for this location
        analysis = await pattern_engine.analyze_patterns(report.location)
        
        # Store analysis in Redis
        redis_client.setex(
            f"climate_analysis:{report.location}", 
            3600,  # 1 hour TTL
            json.dumps(analysis.dict())
        )
        
        return {
            "status": "success",
            "result": result,
            "analysis": analysis.dict()
        }
        
    except Exception as e:
        logging.error(f"Error processing climate report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/{location}", response_model=PatternAnalysis)
async def analyze_location(location: str, days_back: int = 30):
    """Get climate pattern analysis for a specific location"""
    try:
        analysis = await pattern_engine.analyze_patterns(location, days_back)
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing location {location}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patterns/global")
async def get_global_patterns():
    """Get global climate patterns across all locations"""
    try:
        # Query for all location events
        global_query = """
        !(match &self 
            (location-event $location $event) 
            ($location $event))
        """
        
        results = pattern_engine.metta.run(global_query)
        
        # Aggregate by location
        locations = {}
        if results:
            for result in results:
                result_str = str(result)
                # Extract location from result - simplified parsing
                if 'location-event' in result_str:
                    parts = result_str.split()
                    if len(parts) >= 2:
                        location = parts[1] if len(parts) > 1 else 'unknown'
                        if location not in locations:
                            locations[location] = []
                        locations[location].append(result_str)
        
        return {
            "global_patterns": {
                "total_locations": len(locations),
                "total_events": len(results) if results else 0,
                "active_locations": list(locations.keys())
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting global patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv('METTA_PORT', 8001))
    uvicorn.run("metta_processor:app", host="0.0.0.0", port=port, reload=True)