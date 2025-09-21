from typing import List, Dict, Optional, Tuple
import uuid
import os
from datetime import datetime
from app.database.crud import *
from app.database.models import Event, User
from app.services.user_service import UserService

class EventService:
    """Enhanced service for handling climate event operations"""
    
    def __init__(self, db_path: str = "./climate_witness.db"):
        self.db_path = db_path
        self.crud = None
        self.user_service = UserService(db_path)
        
        # Import blockchain service here to avoid circular imports
        self.blockchain_service = None
        self._init_blockchain_service()
    
    def _init_blockchain_service(self):
        """Initialize blockchain service with lazy loading"""
        try:
            from app.services.blockchain_service import BlockchainService
            self.blockchain_service = BlockchainService()
        except Exception as e:
            print(f"⚠️ Blockchain service not available: {str(e)}")
            self.blockchain_service = None
    
    async def submit_event(
        self, 
        event_data: dict, 
        photo_file: bytes = None, 
        gps_coords: tuple = None
    ) -> str:
        """Submit a new climate event with photo evidence"""
        event_id = str(uuid.uuid4())
        
        # Create event object
        event = Event(
            id=event_id,
            user_id=event_data.get('user_id'),
            event_type=event_data.get('event_type'),
            description=event_data.get('description', ''),
            latitude=gps_coords[0] if gps_coords else event_data.get('latitude'),
            longitude=gps_coords[1] if gps_coords else event_data.get('longitude'),
            photo_path=event_data.get('photo_path'),
            timestamp=datetime.now(),
            verification_status='pending'
        )
        
        # Save to database
        success = await self.crud.create_event(event)
        if not success:
            raise ValueError("Failed to create event")
        
        # Register event on blockchain if blockchain service is available
        if self.blockchain_service:
            try:
                blockchain_data = {
                    'event_id': event_id,
                    'event_type': event_data.get('event_type'),
                    'latitude': event.latitude,
                    'longitude': event.longitude,
                    'description': event.description,
                    'photo_path': event.photo_path,
                    'timestamp': event.timestamp.isoformat(),
                    'user_address': event_data.get('user_address', 'unknown')
                }
                blockchain_result = await self.blockchain_service.register_event_on_blockchain(blockchain_data)
                print(f" Event registered on blockchain: {blockchain_result.get('transaction_hash', 'N/A')}")
            except Exception as e:
                print(f"⚠️ Failed to register event on blockchain: {str(e)}")
        
        return event_id
    
    async def verify_event_with_metta(self, event_id: str) -> Dict[str, any]:
        """Verify an event using MeTTa logic"""
        from app.services.metta_service import MeTTaService
        
        metta_service = MeTTaService(self.db_path)
        
        # Run MeTTa verification
        is_verified = await metta_service.run_verification(event_id)
        
        # Get updated event
        event = await self.crud.get_event_by_id(event_id)
        
        # Update user trust score based on verification result
        if event:
            await self.user_service.process_verification_feedback(
                event.user_id, 
                is_verified, 
                1.0  # Full consensus for auto-verification
            )
        
        # Trigger blockchain verification if event is verified and blockchain service is available
        if is_verified and self.blockchain_service:
            try:
                # Determine severity based on event type
                severity_map = {
                    'drought': 'high',
                    'flood': 'high', 
                    'extreme_heat': 'medium',
                    'locust': 'medium',
                    'storms': 'high'
                }
                severity = severity_map.get(event.event_type.lower(), 'medium')
                
                blockchain_result = await self.blockchain_service.verify_event_on_blockchain(event_id, severity)
                print(f" Event verified on blockchain: {blockchain_result.get('transaction_hash', 'N/A')}")
                
                # Trigger automatic payout if verification successful
                if blockchain_result.get('success') and event.user_id:
                    user = await self.crud.get_user_by_id(event.user_id)
                    if user and hasattr(user, 'wallet_address') and user.wallet_address:
                        try:
                            payout_result = await self.blockchain_service.process_payout(event_id, user.wallet_address)
                            print(f" Automatic payout triggered: {payout_result.get('transaction_hash', 'N/A')}")
                        except Exception as e:
                            print(f"⚠️ Failed to process automatic payout: {str(e)}")
                
            except Exception as e:
                print(f"⚠️ Failed to verify event on blockchain: {str(e)}")
        
        return {
            'event_id': event_id,
            'verified': is_verified,
            'event': event.to_dict() if event else None
        }
    
    async def get_events_by_region(self, bounds: dict) -> List[Event]:
        """Get all events within geographic bounds"""
        return await self.crud.get_events_by_region(
            bounds['min_lat'], bounds['max_lat'],
            bounds['min_lng'], bounds['max_lng']
        )
    
    async def trigger_smart_contract(self, event_id: str) -> Dict[str, any]:
        """Trigger smart contract payout for verified event"""
        event = await self.crud.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        
        if event.verification_status != 'verified':
            raise ValueError("Event must be verified before triggering payout")
        
        # Use blockchain service to process payout
        if self.blockchain_service:
            try:
                # Get user wallet address
                user = await self.crud.get_user_by_id(event.user_id)
                if not user or not hasattr(user, 'wallet_address') or not user.wallet_address:
                    raise ValueError("User wallet address not found")
                
                # Process payout via blockchain service
                payout_result = await self.blockchain_service.process_payout(event_id, user.wallet_address)
                
                if payout_result.get('success'):
                    return {
                        'success': True,
                        'message': f"Smart contract payout triggered for event {event_id}",
                        'transaction_hash': payout_result.get('transaction_hash'),
                        'payout_amount': payout_result.get('payout_amount'),
                        'recipient': user.wallet_address
                    }
                else:
                    raise ValueError(payout_result.get('error', 'Payout failed'))
                    
            except Exception as e:
                return {
                    'success': False,
                    'message': f"Failed to trigger smart contract: {str(e)}"
                }
        else:
            return {
                'success': False,
                'message': "Blockchain service not available"
            }
    
    async def get_all_events(self) -> List[Event]:
        """Get all events"""
        return await self.crud.get_all_events()
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get specific event by ID"""
        return await self.crud.get_event_by_id(event_id)
    
    async def get_events_by_user(self, user_id: str) -> List[Event]:
        """Get all events by a specific user"""
        return await self.crud.get_events_by_user(user_id)
    
    async def get_pending_events(self) -> List[Event]:
        """Get all pending events that need verification"""
        all_events = await self.get_all_events()
        return [event for event in all_events if event.verification_status == 'pending']
    
    async def get_verified_events(self) -> List[Event]:
        """Get all verified events"""
        all_events = await self.get_all_events()
        return [event for event in all_events if event.verification_status == 'verified']
    
    async def get_events_with_payouts(self) -> List[Event]:
        """Get all events that have received payouts"""
        all_events = await self.get_all_events()
        return [event for event in all_events if event.payout_amount and event.payout_amount > 0]
    
    async def get_event_statistics(self) -> Dict[str, any]:
        """Get comprehensive event statistics"""
        all_events = await self.get_all_events()
        
        # Basic counts
        total_events = len(all_events)
        verified_events = len([e for e in all_events if e.verification_status == 'verified'])
        pending_events = len([e for e in all_events if e.verification_status == 'pending'])
        rejected_events = len([e for e in all_events if e.verification_status == 'rejected'])
        
        # Payout statistics
        events_with_payouts = [e for e in all_events if e.payout_amount and e.payout_amount > 0]
        total_payout_amount = sum(e.payout_amount for e in events_with_payouts)
        
        # Event type breakdown
        event_types = {}
        for event in all_events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        # Verification rate
        verification_rate = verified_events / total_events if total_events > 0 else 0
        
        return {
            'total_events': total_events,
            'verified_events': verified_events,
            'pending_events': pending_events,
            'rejected_events': rejected_events,
            'verification_rate': verification_rate,
            'total_payouts': len(events_with_payouts),
            'total_payout_amount': total_payout_amount,
            'event_types': event_types,
            'average_payout': total_payout_amount / len(events_with_payouts) if events_with_payouts else 0
        }
    
    async def save_photo(self, photo_file, event_id: str) -> str:
        """Save uploaded photo and return path"""
        if not photo_file:
            return None
        
        # Create uploads directory
        os.makedirs("uploads", exist_ok=True)
        
        # Generate filename
        filename = f"{event_id}_{photo_file.filename}"
        file_path = f"uploads/{filename}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await photo_file.read()
            buffer.write(content)
        
        return file_path
    
    async def get_recent_events(self, limit: int = 10) -> List[Event]:
        """Get most recent events"""
        all_events = await self.get_all_events()
        return all_events[:limit]  
    
    async def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get events of a specific type"""
        all_events = await self.get_all_events()
        return [event for event in all_events if event.event_type == event_type]
    
    async def log_user_login(self, user_id: str, ip_address: str = "unknown") -> bool:
        """Log user login event for tracking and analytics"""
        try:
            from app.database.database import get_db
            import aiosqlite
            
            # Create login_events table if it doesn't exist
            async for db in get_db():
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS login_events (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT,
                        success BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Insert login event
                login_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO login_events (id, user_id, login_time, ip_address, success)
                    VALUES (?, ?, ?, ?, ?)
                """, (login_id, user_id, datetime.now().isoformat(), ip_address, True))
                
                await db.commit()
                print(f"✅ Login event logged for user {user_id}")
                return True
                
        except Exception as e:
            print(f"⚠️ Failed to log login event: {e}")
            return False
    
    async def get_user_login_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's recent login history"""
        try:
            from app.database.database import get_db
            
            async for db in get_db():
                async with db.execute("""
                    SELECT * FROM login_events 
                    WHERE user_id = ? 
                    ORDER BY login_time DESC 
                    LIMIT ?
                """, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            "id": row["id"],
                            "user_id": row["user_id"],
                            "login_time": row["login_time"],
                            "ip_address": row["ip_address"],
                            "success": bool(row["success"])
                        }
                        for row in rows
                    ]
                    
        except Exception as e:
            print(f"⚠️ Failed to get login history: {e}")
            return []
    
    async def get_login_statistics(self) -> Dict[str, any]:
        """Get login statistics for analytics"""
        try:
            from app.database.database import get_db
            
            async for db in get_db():
                # Total logins today
                async with db.execute("""
                    SELECT COUNT(*) FROM login_events 
                    WHERE DATE(login_time) = DATE('now')
                """) as cursor:
                    today_logins = (await cursor.fetchone())[0]
                
                # Total logins this week
                async with db.execute("""
                    SELECT COUNT(*) FROM login_events 
                    WHERE login_time >= DATE('now', '-7 days')
                """) as cursor:
                    week_logins = (await cursor.fetchone())[0]
                
                # Unique users today
                async with db.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM login_events 
                    WHERE DATE(login_time) = DATE('now')
                """) as cursor:
                    unique_users_today = (await cursor.fetchone())[0]
                
                return {
                    "logins_today": today_logins,
                    "logins_this_week": week_logins,
                    "unique_users_today": unique_users_today,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"⚠️ Failed to get login statistics: {e}")
            return {
                "logins_today": 0,
                "logins_this_week": 0,
                "unique_users_today": 0,
                "error": str(e)
            }