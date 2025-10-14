"""
Payment Service for Climate Witness Chain
Handles M-Pesa and other payment integrations
"""

import os
import base64
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import aiosqlite
from app.database.database import get_db

# Use requests only - it's reliable and always available
import requests
import concurrent.futures
HTTP_CLIENT = 'requests'

class PaymentService:
    def __init__(self):
        # M-Pesa Daraja API Configuration
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.business_short_code = os.getenv('MPESA_BUSINESS_SHORT_CODE', '174379')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL', 'https://your-domain.com/api/payments/mpesa/callback')
        
        # Check if M-Pesa credentials are real (not placeholders)
        placeholder_values = [
            'your_mpesa_consumer_key_here',
            'your_mpesa_consumer_secret_here', 
            'your_mpesa_passkey_here'
        ]
        
        self.credentials_available = (
            all([self.consumer_key, self.consumer_secret, self.passkey]) and
            self.consumer_key not in placeholder_values and
            self.consumer_secret not in placeholder_values and
            self.passkey not in placeholder_values
        )
        
        if not self.credentials_available:
            print("⚠️ M-Pesa credentials are set to placeholder values.")
            print(f"⚠️ Current values: KEY={self.consumer_key[:20]}..., SECRET={self.consumer_secret[:20]}..., PASSKEY={self.passkey[:20]}...")
            print("⚠️ Replace with real credentials from https://developer.safaricom.co.ke/")
        
        # Environment configuration
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox').lower()
        self.currency = os.getenv('PAYMENT_CURRENCY', 'KES')
        self.min_amount = float(os.getenv('MIN_PAYMENT_AMOUNT', '1.0'))
        self.max_amount = float(os.getenv('MAX_PAYMENT_AMOUNT', '70000.0'))
        
        if self.credentials_available:
            # API URLs based on environment
            if self.environment == 'production':
                self.base_url = 'https://api.safaricom.co.ke'
            else:
                self.base_url = 'https://sandbox.safaricom.co.ke'
                
            self.auth_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
            self.stk_push_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            print(f"💳 M-Pesa Payment service initialized ({self.environment} mode)")
            print(f"💳 Business Short Code: {self.business_short_code}")
            print(f"💳 Callback URL: {self.callback_url}")
        else:
            print("💳 M-Pesa Payment service initialized in configuration mode")
        
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """Get M-Pesa access token"""
        if not self.credentials_available:
            raise Exception("M-Pesa credentials not configured")
            
        # Check if token is still valid
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        try:
            # Use requests with basic auth in thread pool for async compatibility
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor, 
                    lambda: requests.get(
                        self.auth_url, 
                        auth=(self.consumer_key, self.consumer_secret),
                        timeout=30
                    )
                )
                response.raise_for_status()
                data = response.json()
            
            self.access_token = data['access_token']
            expires_in = int(data['expires_in'])
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 minute early
            
            print("✅ M-Pesa access token obtained")
            return self.access_token
            
        except Exception as e:
            if hasattr(e, 'response'):
                print(f"❌ M-Pesa API returned error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"M-Pesa authentication failed: {e.response.status_code}")
            else:
                print(f"❌ Failed to get M-Pesa access token: {e}")
                raise Exception(f"Authentication failed: {str(e)}")
    
    async def initiate_stk_push(
        self, 
        phone_number: str, 
        amount: float, 
        account_reference: str,
        transaction_desc: str = "Climate Witness Chain Donation"
    ) -> Dict[str, Any]:
        """Initiate M-Pesa STK Push"""
        
        # Check if credentials are available
        if not self.credentials_available:
            return {
                'success': False,
                'message': 'M-Pesa credentials not configured',
                'error': 'CREDENTIALS_MISSING',
                'setup_required': True,
                'instructions': {
                    'step1': 'Get M-Pesa credentials from https://developer.safaricom.co.ke/',
                    'step2': 'Set environment variables: MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_PASSKEY',
                    'step3': 'Restart the application',
                    'step4': 'Test with /api/payments/test endpoint'
                }
            }
        
        try:
            # Get access token
            access_token = await self.get_access_token()
            
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Generate password
            password_string = f"{self.business_short_code}{self.passkey}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode()
            
            # Format phone number (ensure it starts with 254)
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_short_code,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use requests in thread pool for async compatibility
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor, 
                    lambda: requests.post(self.stk_push_url, json=payload, headers=headers, timeout=30)
                )
                response.raise_for_status()
                result = response.json()
            
            # Store transaction in database
            transaction_id = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{phone_number[-4:]}"
            try:
                await self.store_transaction(
                    transaction_id=transaction_id,
                    phone_number=phone_number,
                    amount=amount,
                    account_reference=account_reference,
                    checkout_request_id=result.get('CheckoutRequestID'),
                    merchant_request_id=result.get('MerchantRequestID'),
                    status='pending'
                )
            except Exception as e:
                print(f"⚠️ Could not store transaction: {e}")
            
            return {
                'success': True,
                'message': 'STK Push initiated successfully',
                'transaction_id': transaction_id,
                'checkout_request_id': result.get('CheckoutRequestID'),
                'merchant_request_id': result.get('MerchantRequestID'),
                'customer_message': result.get('CustomerMessage', 'Please check your phone for the M-Pesa prompt'),
                'response_code': result.get('ResponseCode'),
                'response_description': result.get('ResponseDescription')
            }
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ M-Pesa API returned error: {e.response.status_code} - {e.response.text}")
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
            
            return {
                'success': False,
                'message': error_data.get('errorMessage', f'M-Pesa API error: {e.response.status_code}'),
                'error_code': error_data.get('errorCode'),
                'response_code': str(e.response.status_code)
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ M-Pesa API request failed: {e}")
            return {
                'success': False,
                'message': 'Network error connecting to M-Pesa. Please try again.',
                'error': str(e)
            }
        except Exception as e:
            print(f"❌ STK Push failed: {e}")
            return {
                'success': False,
                'message': f'Payment initialization failed: {str(e)}',
                'error': str(e)
            }
    

    
    async def store_transaction(
        self,
        transaction_id: str,
        phone_number: str,
        amount: float,
        account_reference: str,
        checkout_request_id: str = None,
        merchant_request_id: str = None,
        status: str = 'pending'
    ):
        """Store transaction in database"""
        try:
            async for db in get_db():
                # Create table if it doesn't exist
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS payment_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_id TEXT UNIQUE,
                        phone_number TEXT,
                        amount REAL,
                        account_reference TEXT,
                        checkout_request_id TEXT,
                        merchant_request_id TEXT,
                        status TEXT,
                        result_code INTEGER,
                        result_description TEXT,
                        mpesa_receipt_number TEXT,
                        transaction_date TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
                
                await db.execute("""
                    INSERT OR REPLACE INTO payment_transactions 
                    (transaction_id, phone_number, amount, account_reference, 
                     checkout_request_id, merchant_request_id, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction_id, phone_number, amount, account_reference,
                    checkout_request_id, merchant_request_id, status, datetime.now().isoformat()
                ))
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️ Failed to store transaction: {e}")
            # Continue without storing - don't fail the payment
    
    async def handle_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle M-Pesa callback"""
        try:
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Extract callback metadata
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            metadata = {}
            for item in callback_metadata:
                name = item.get('Name')
                value = item.get('Value')
                if name and value is not None:
                    metadata[name] = value
            
            # Update transaction status
            status = 'completed' if result_code == 0 else 'failed'
            
            async for db in get_db():
                await db.execute("""
                    UPDATE payment_transactions 
                    SET status = ?, result_code = ?, result_description = ?,
                        mpesa_receipt_number = ?, transaction_date = ?, updated_at = ?
                    WHERE checkout_request_id = ?
                """, (
                    status, result_code, result_desc,
                    metadata.get('MpesaReceiptNumber'),
                    metadata.get('TransactionDate'),
                    datetime.now().isoformat(),
                    checkout_request_id
                ))
                await db.commit()
                break
            
            print(f"✅ Transaction {checkout_request_id} updated: {status}")
            
            return {
                'success': True,
                'status': status,
                'result_code': result_code,
                'result_description': result_desc,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"❌ Callback handling failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction status"""
        async for db in get_db():
            async with db.execute("""
                SELECT * FROM payment_transactions WHERE transaction_id = ?
            """, (transaction_id,)) as cursor:
                transaction = await cursor.fetchone()
                if transaction:
                    return {
                        'found': True,
                        'transaction_id': transaction['transaction_id'],
                        'status': transaction['status'],
                        'amount': transaction['amount'],
                        'phone_number': transaction['phone_number'],
                        'result_code': transaction.get('result_code'),
                        'result_description': transaction.get('result_description'),
                        'mpesa_receipt_number': transaction.get('mpesa_receipt_number'),
                        'created_at': transaction['created_at'],
                        'updated_at': transaction.get('updated_at')
                    }
                else:
                    return {'found': False}
            break
    
    async def get_user_transactions(self, user_id: str) -> list:
        """Get user's transaction history"""
        async for db in get_db():
            async with db.execute("""
                SELECT * FROM payment_transactions 
                WHERE account_reference LIKE ? 
                ORDER BY created_at DESC
            """, (f"%{user_id}%",)) as cursor:
                transactions = await cursor.fetchall()
                return [dict(transaction) for transaction in transactions]
            break

# Global payment service instance
payment_service = PaymentService()