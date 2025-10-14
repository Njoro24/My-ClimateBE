import requests
import asyncio
import concurrent.futures
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
            # Convert enums to strings for JSON serialization
            report_data = report.dict()
            report_data['event_type'] = report_data['event_type'].value
            report_data['severity'] = report_data['severity'].value
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: requests.post(
                        f"{self.base_url}/report",
                        json=report_data,
                        timeout=self.timeout
                    )
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.HTTPError as e:
            logging.error(f"MeTTa service returned error: {e.response.status_code} - {e.response.text}")
            return {'error': f"Service error: {e.response.status_code}", 'status': 'failed'}
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to submit climate report to MeTTa: {str(e)}")
            return {'error': 'Service unavailable', 'status': 'failed'}
    
    async def get_location_analysis(self, location: str, days_back: int = 30) -> Optional[LocationAnalysisResponse]:
        """Get climate pattern analysis for a specific location"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: requests.get(
                        f"{self.base_url}/analyze/{location}",
                        params={'days_back': days_back},
                        timeout=self.timeout
                    )
                )
                response.raise_for_status()
                data = response.json()
                return LocationAnalysisResponse(**data)
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get location analysis from MeTTa: {str(e)}")
            return None
    
    async def get_global_patterns(self) -> Dict:
        """Get global climate patterns across all locations"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: requests.get(f"{self.base_url}/patterns/global", timeout=self.timeout)
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get global patterns from MeTTa: {str(e)}")
            return {'patterns': {}, 'error': str(e)}
    
    async def health_check(self) -> bool:
        """Check if MeTTa service is healthy"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: requests.get(f"{self.base_url}/health", timeout=5.0)
                )
                return response.status_code == 200
                
        except requests.exceptions.RequestException:
            return False