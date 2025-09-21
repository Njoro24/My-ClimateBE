"""
OTP Service for Climate Witness Chain
Handles OTP generation, validation, and SMS sending
"""

import random
import string
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import aiosqlite
import os
from app.database.database import get_db

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️ Twilio not available, using fallback OTP service")

class OTPService:
    def __init__(self):
        self.otp_storage = {}  # In-memory storage for development
        
        # Configuration from environment variables
        self.otp_length = int(os.getenv('OTP_LENGTH', '6'))
        self.otp_expiry_minutes = int(os.getenv('OTP_EXPIRY_MINUTES', '5'))
        self.max_attempts = int(os.getenv('OTP_MAX_ATTEMPTS', '3'))
        
        # Twilio configuration (optional)
        self.twilio_client = None
        self.sms_available = False
        
        if TWILIO_AVAILABLE:
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            if account_sid and auth_token and self.twilio_phone:
                try:
                    self.twilio_client = Client(account_sid, auth_token)
                    self.sms_available = True
                    print("✅ Twilio SMS service initialized")
                except Exception as e:
                    print(f"⚠️ Twilio initialization failed: {e}")
            else:
                print("⚠️ Twilio credentials incomplete, using fallback SMS")
        else:
            print("⚠️ Twilio not available, using fallback OTP service")
    
    def generate_otp(self, length: int = None) -> str:
        """Generate a random OTP"""
        if length is None:
            length = self.otp_length
        return ''.join(random.choices(string.digits, k=length))
    
    async def create_otp(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """Create and store OTP for user"""
        otp_code = self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        
        # Store OTP in memory (in production, use Redis or database)
        self.otp_storage[user_id] = {
            'code': otp_code,
            'phone_number': phone_number,
            'expires_at': expires_at,
            'attempts': 0,
            'verified': False
        }
        
        # Also store in database for persistence
        async for db in get_db():
            await db.execute("""
                INSERT OR REPLACE INTO otp_codes 
                (user_id, code, phone_number, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, otp_code, phone_number, expires_at.isoformat(), datetime.now().isoformat()))
            await db.commit()
            break
        
        # Send OTP via SMS
        sms_sent = await self.send_otp_sms(phone_number, otp_code)
        
        return {
            'otp_id': user_id,
            'expires_at': expires_at.isoformat(),
            'sms_sent': sms_sent,
            'phone_number': phone_number[-4:].rjust(len(phone_number), '*')  # Mask phone number
        }
    
    async def send_otp_sms(self, phone_number: str, otp_code: str) -> bool:
        """Send OTP via SMS using Twilio or fallback"""
        message = f"Your Climate Witness Chain verification code is: {otp_code}. Valid for {self.otp_expiry_minutes} minutes."
        
        if self.sms_available and self.twilio_client and self.twilio_phone:
            try:
                # Format phone number for Twilio (must include country code)
                formatted_phone = phone_number
                if phone_number.startswith('0'):
                    formatted_phone = '+254' + phone_number[1:]
                elif phone_number.startswith('254'):
                    formatted_phone = '+' + phone_number
                elif not phone_number.startswith('+'):
                    formatted_phone = '+' + phone_number
                
                message_obj = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=formatted_phone
                )
                print(f"✅ SMS sent successfully: {message_obj.sid}")
                return True
            except Exception as e:
                print(f"❌ SMS sending failed: {e}")
                # Fall back to console logging
                print(f"📱 SMS Fallback - Phone: {phone_number}")
                print(f"📱 Message: {message}")
                return True
        else:
            # Fallback: Print to console for development
            print(f"📱 SMS Fallback - Phone: {phone_number}")
            print(f"📱 Message: {message}")
            print(f"📱 OTP Code: {otp_code}")
            return True
    
    async def verify_otp(self, user_id: str, otp_code: str) -> Dict[str, Any]:
        """Verify OTP code"""
        # Check in-memory storage first
        if user_id in self.otp_storage:
            stored_otp = self.otp_storage[user_id]
        else:
            # Check database
            async for db in get_db():
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT code, phone_number, expires_at, attempts 
                    FROM otp_codes 
                    WHERE user_id = ? AND verified = 0
                    ORDER BY created_at DESC LIMIT 1
                """, (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return {'valid': False, 'error': 'No OTP found'}
                    
                    stored_otp = {
                        'code': row['code'],
                        'phone_number': row['phone_number'],
                        'expires_at': datetime.fromisoformat(row['expires_at']),
                        'attempts': row['attempts'] or 0
                    }
                break
        
        # Check if OTP is expired
        if datetime.now() > stored_otp['expires_at']:
            return {'valid': False, 'error': 'OTP expired'}
        
        # Check attempts limit
        if stored_otp['attempts'] >= self.max_attempts:
            return {'valid': False, 'error': 'Too many attempts'}
        
        # Verify OTP code
        if otp_code == stored_otp['code']:
            # Mark as verified
            if user_id in self.otp_storage:
                self.otp_storage[user_id]['verified'] = True
            
            # Update database
            async for db in get_db():
                await db.execute("""
                    UPDATE otp_codes 
                    SET verified = 1, verified_at = ?
                    WHERE user_id = ? AND code = ?
                """, (datetime.now().isoformat(), user_id, otp_code))
                await db.commit()
                break
            
            return {'valid': True, 'message': 'OTP verified successfully'}
        else:
            # Increment attempts
            stored_otp['attempts'] += 1
            
            # Update database
            async for db in get_db():
                await db.execute("""
                    UPDATE otp_codes 
                    SET attempts = ?
                    WHERE user_id = ? AND code = ?
                """, (stored_otp['attempts'], user_id, stored_otp['code']))
                await db.commit()
                break
            
            return {'valid': False, 'error': f'Invalid OTP. {self.max_attempts - stored_otp["attempts"]} attempts remaining'}
    
    async def cleanup_expired_otps(self):
        """Clean up expired OTPs"""
        current_time = datetime.now()
        
        # Clean memory storage
        expired_keys = [
            key for key, value in self.otp_storage.items()
            if current_time > value['expires_at']
        ]
        for key in expired_keys:
            del self.otp_storage[key]
        
        # Clean database
        async for db in get_db():
            await db.execute("""
                DELETE FROM otp_codes 
                WHERE expires_at < ?
            """, (current_time.isoformat(),))
            await db.commit()
            break

# Global OTP service instance
otp_service = OTPService()