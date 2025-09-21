import httpx
import asyncio
from typing import Dict, Optional, List
import logging
import os
from app.models.climatemodels import ClimateReportCreate, LocationAnalysisResponse

class MeTTaClimateClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('METTA_SERVICE_URL', 'http://localhost:8001')
        self.timeout = 30.0
        
    async def submit_climate_report(self, report: ClimateReportCreate) -> Dict:
        """Submit a climate report to MeTTa for pattern analysis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Convert enums to strings for JSON serialization
                report_data = report.dict()
                report_data['event_type'] = report_data['event_type'].value
                report_data['severity'] = report_data['severity'].value
                
                response = await client.post(
                    f"{self.base_url}/report",
                    json=report_data
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logging.error(f"MeTTa service returned error: {e.response.status_code} - {e.response.text}")
            return {'error': f"Service error: {e.response.status_code}", 'status': 'failed'}
        except httpx.RequestError as e:
            logging.error(f"Failed to submit climate report to MeTTa: {str(e)}")
            return {'error': 'Service unavailable', 'status': 'failed'}
    
    async def get_location_analysis(self, location: str, days_back: int = 30) -> Optional[LocationAnalysisResponse]:
        """Get climate pattern analysis for a specific location"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/analyze/{location}",
                    params={'days_back': days_back}
                )
                response.raise_for_status()
                data = response.json()
                return LocationAnalysisResponse(**data)
                
        except httpx.RequestError as e:
            logging.error(f"Failed to get location analysis from MeTTa: {str(e)}")
            return None
    
    async def get_global_patterns(self) -> Dict:
        """Get global climate patterns across all locations"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/patterns/global")
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logging.error(f"Failed to get global patterns from MeTTa: {str(e)}")
            return {'patterns': {}, 'error': str(e)}
    
    async def health_check(self) -> bool:
        """Check if MeTTa service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
                
        except httpx.RequestError:
            return False