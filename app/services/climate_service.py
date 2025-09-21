from sqlalchemy.orm import Session
from app.models.database import ClimateReport, ClimateAlert, PatternCache, get_session, get_db
from app.models.climatemodels import ClimateReportCreate, ClimateReportResponse, AlertResponse, ReportStatsResponse
from app.services.metta_client import MeTTaClimateClient
from typing import List, Optional, Dict
import json
from datetime import datetime, timedelta
import logging
from sqlalchemy import func

class ClimateService:
    def __init__(self):
        self.metta_client = MeTTaClimateClient()
    
    async def create_climate_report(self, report_data: ClimateReportCreate) -> ClimateReportResponse:
        """Create a new climate report and trigger MeTTa analysis"""
        db = get_session()
        try:
            # Save to database
            db_report = ClimateReport(
                user=report_data.user,
                location=report_data.location,
                event_type=report_data.event_type.value,
                severity=report_data.severity.value,
                description=report_data.description,
                evidence_link=report_data.evidence_link,
                latitude=report_data.latitude,
                longitude=report_data.longitude
            )
            db.add(db_report)
            db.commit()
            db.refresh(db_report)
            
            # Submit to MeTTa service asynchronously
            metta_result = await self.metta_client.submit_climate_report(report_data)
            
            # Check for high-risk predictions and create alerts
            if 'analysis' in metta_result and 'predictions' in metta_result['analysis']:
                await self._process_predictions(report_data.location, metta_result['analysis']['predictions'])
            
            return ClimateReportResponse(
                id=db_report.id,
                user=db_report.user,
                location=db_report.location,
                event_type=db_report.event_type.value,
                severity=db_report.severity.value,
                description=db_report.description,
                evidence_link=db_report.evidence_link,
                latitude=db_report.latitude,
                longitude=db_report.longitude,
                timestamp=db_report.timestamp,
                verified=db_report.verified
            )
            
        except Exception as e:
            db.rollback()
            logging.error(f"Error creating climate report: {str(e)}")
            raise
        finally:
            db.close()
    
    async def get_location_analysis(self, location: str) -> Optional[Dict]:
        """Get climate analysis for a location (with caching)"""
        db = get_session()
        try:
            # Check cache first
            cache_entry = db.query(PatternCache).filter(
                PatternCache.location == location,
                PatternCache.expires_at > datetime.utcnow()
            ).first()
            
            if cache_entry:
                return json.loads(cache_entry.analysis_data)
            
            # Get fresh analysis from MeTTa
            analysis = await self.metta_client.get_location_analysis(location)
            
            if analysis:
                # Cache the results
                cache_entry = PatternCache(
                    location=location,
                    analysis_data=json.dumps(analysis.dict()),
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                db.add(cache_entry)
                db.commit()
                
                return analysis.dict()
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting location analysis: {str(e)}")
            return None
        finally:
            db.close()
    
    async def get_climate_alerts(self, location: str) -> List[AlertResponse]:
        """Get active climate alerts for a location"""
        db = get_session()
        try:
            alerts = db.query(ClimateAlert).filter(
                ClimateAlert.location == location,
                ClimateAlert.active == True
            ).order_by(ClimateAlert.created_at.desc()).limit(10).all()
            
            return [
                AlertResponse(
                    id=alert.id,
                    location=alert.location,
                    alert_type=alert.alert_type,
                    message=alert.message,
                    severity=alert.severity.value,
                    created_at=alert.created_at,
                    active=alert.active
                )
                for alert in alerts
            ]
            
        except Exception as e:
            logging.error(f"Error getting climate alerts: {str(e)}")
            return []
        finally:
            db.close()
    
    async def _process_predictions(self, location: str, predictions: List[Dict]):
        """Process predictions and create alerts for high-risk events"""
        db = get_session()
        try:
            for prediction in predictions:
                # Check if this is a high-risk prediction (probability > 0.7)
                probability = prediction.get('probability', 0)
                if probability > 0.7:
                    event_type = prediction.get('event_type', 'unknown')
                    reasoning = prediction.get('reasoning', '')
                    timeframe = prediction.get('timeframe', 'soon')
                    
                    # Create alert message
                    message = f"High probability ({probability:.0%}) of {event_type} in {timeframe}. {reasoning}"
                    
                    # Determine severity based on probability
                    if probability > 0.9:
                        severity = "severe"
                    elif probability > 0.8:
                        severity = "high"
                    else:
                        severity = "medium"
                    
                    # Check if similar alert already exists
                    existing_alert = db.query(ClimateAlert).filter(
                        ClimateAlert.location == location,
                        ClimateAlert.alert_type == event_type,
                        ClimateAlert.active == True
                    ).first()
                    
                    if not existing_alert:
                        # Create new alert
                        alert = ClimateAlert(
                            location=location,
                            alert_type=event_type,
                            message=message,
                            severity=severity
                        )
                        db.add(alert)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logging.error(f"Error processing predictions: {str(e)}")
        finally:
            db.close()

    async def get_recent_reports(self, location: str, limit: int = 10) -> List[ClimateReportResponse]:
        """Get recent climate reports for a location"""
        db = get_session()
        try:
            reports = db.query(ClimateReport).filter(
                ClimateReport.location == location
            ).order_by(ClimateReport.timestamp.desc()).limit(limit).all()
            
            return [
                ClimateReportResponse(
                    id=report.id,
                    user=report.user,
                    location=report.location,
                    event_type=report.event_type.value,
                    severity=report.severity.value,
                    description=report.description,
                    evidence_link=report.evidence_link,
                    latitude=report.latitude,
                    longitude=report.longitude,
                    timestamp=report.timestamp,
                    verified=report.verified
                )
                for report in reports
            ]
            
        except Exception as e:
            logging.error(f"Error getting recent reports: {str(e)}")
            return []
        finally:
            db.close()

    async def verify_report(self, report_id: int, verified: bool = True) -> bool:
        """Verify or unverify a climate report"""
        db = get_session()
        try:
            report = db.query(ClimateReport).filter(ClimateReport.id == report_id).first()
            if report:
                report.verified = verified
                db.commit()
                return True
            return False
            
        except Exception as e:
            db.rollback()
            logging.error(f"Error verifying report: {str(e)}")
            return False
        finally:
            db.close()

    async def get_global_analysis(self) -> Dict:
        """Get global climate patterns analysis"""
        try:
            return await self.metta_client.get_global_patterns()
        except Exception as e:
            logging.error(f"Error getting global analysis: {str(e)}")
            return {'patterns': {}, 'error': str(e)}

    async def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data from database"""
        db = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old cache entries
            db.query(PatternCache).filter(
                PatternCache.expires_at < datetime.utcnow()
            ).delete()
            
            # Archive old alerts
            db.query(ClimateAlert).filter(
                ClimateAlert.created_at < cutoff_date
            ).update({'active': False})
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logging.error(f"Error cleaning up old data: {str(e)}")
        finally:
            db.close()

    async def get_report_stats(self, location: str) -> ReportStatsResponse:
        """Get statistics for climate reports in a location"""
        db = get_session()
        try:
            total_reports = db.query(ClimateReport).filter(
                ClimateReport.location == location
            ).count()
            
            verified_reports = db.query(ClimateReport).filter(
                ClimateReport.location == location,
                ClimateReport.verified == True
            ).count()
            
            severity_counts = db.query(
                ClimateReport.severity,
                func.count(ClimateReport.id)
            ).filter(
                ClimateReport.location == location
            ).group_by(ClimateReport.severity).all()
            
            severity_distribution = {severity.value: count for severity, count in severity_counts}
            
            return ReportStatsResponse(
                total_reports=total_reports,
                verified_reports=verified_reports,
                verification_rate=verified_reports / total_reports if total_reports > 0 else 0,
                severity_distribution=severity_distribution
            )
            
        except Exception as e:
            logging.error(f"Error getting report stats: {str(e)}")
            return ReportStatsResponse(
                total_reports=0,
                verified_reports=0,
                verification_rate=0,
                severity_distribution={}
            )
        finally:
            db.close()

    async def get_all_locations(self) -> List[str]:
        """Get all unique locations with reports"""
        db = get_session()
        try:
            locations = db.query(ClimateReport.location).distinct().all()
            return [location[0] for location in locations]
        except Exception as e:
            logging.error(f"Error getting locations: {str(e)}")
            return []
        finally:
            db.close()