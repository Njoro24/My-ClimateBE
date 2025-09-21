"""
Payment Service for Climate Witness Chain
Handles M-Pesa and other payment integrations
"""

import os
import base64
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import aiosqlite
from app.database.database import get_db

class PaymentService:
    def __init__(self):
        # M-Pesa Daraja API Configuration
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.business_short_code = os.getenv('MPESA_BUSINESS_SHORT_CODE', '174379')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL', 'https://your-domain.com/api/payments/mpesa/callback')
        
        # Check if M-Pesa credentials are available
        self.mpesa_available = bool(self.consumer_key and self.consumer_secret and self.passkey)
        
        # Environment configuration
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox').lower()
        self.currency = os.getenv('PAYMENT_CURRENCY', 'KES')
        self.min_amount = float(os.getenv('MIN_PAYMENT_AMOUNT', '1.0'))
        self.max_amount = float(os.getenv('MAX_PAYMENT_AMOUNT', '70000.0'))
        
        if self.mpesa_available:
            # API URLs based on environment
            if self.environment == 'production':
                self.base_url = 'https://api.safaricom.co.ke'
            else:
                self.base_url = 'https://sandbox.safaricom.co.ke'
                
            self.auth_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
            self.stk_push_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            print(f"💳 Payment service initialized with M-Pesa credentials ({self.environment} mode)")
        else:
            print("⚠️ Payment service initialized in demo mode (M-Pesa credentials not configured)")
        
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """Get M-Pesa access token"""
        if not self.mpesa_available:
            raise Exception("M-Pesa credentials not configured")
            
        # Check if token is still valid
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        try:
            # Create credentials
            credentials = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            expires_in = int(data['expires_in'])
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 minute early
            
            print("✅ M-Pesa access token obtained")
            return self.access_token
            
        except Exception as e:
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
        
        # If M-Pesa is not available, use demo mode
        if not self.mpesa_available:
            return await self.demo_stk_push(phone_number, amount, account_reference, transaction_desc)
        
        try:
            # Get access token (will fall back to demo if credentials not available)
            try:
                access_token = await self.get_access_token()
            except Exception as auth_error:
                print(f"⚠️ M-Pesa authentication failed, using demo mode: {auth_error}")
                return await self.demo_stk_push(phone_number, amount, account_reference, transaction_desc)
            
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
            
            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Store transaction in database
            transaction_id = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{phone_number[-4:]}"
            await self.store_transaction(
                transaction_id=transaction_id,
                phone_number=phone_number,
                amount=amount,
                account_reference=account_reference,
                checkout_request_id=result.get('CheckoutRequestID'),
                merchant_request_id=result.get('MerchantRequestID'),
                status='pending'
            )
            
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
            
        except requests.exceptions.RequestException as e:
            print(f"❌ M-Pesa API request failed: {e}")
            return {
                'success': False,
                'message': f'Payment request failed: {str(e)}',
                'error': str(e)
            }
        except Exception as e:
            print(f"❌ STK Push failed: {e}")
            return {
                'success': False,
                'message': f'Payment initialization failed: {str(e)}',
                'error': str(e)
            }
    
    async def demo_stk_push(
        self, 
        phone_number: str, 
        amount: float, 
        account_reference: str,
        transaction_desc: str
    ) -> Dict[str, Any]:
        """Demo STK Push for development/testing"""
        try:
            # Generate demo transaction ID
            transaction_id = f"demo_txn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{phone_number[-4:]}"
            checkout_request_id = f"ws_CO_DMZ_{datetime.now().strftime('%Y%m%d%H%M%S')}_demo"
            merchant_request_id = f"demo_merchant_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Store demo transaction
            await self.store_transaction(
                transaction_id=transaction_id,
                phone_number=phone_number,
                amount=amount,
                account_reference=account_reference,
                checkout_request_id=checkout_request_id,
                merchant_request_id=merchant_request_id,
                status='demo_pending'
            )
            
            print(f"📱 DEMO M-Pesa STK Push")
            print(f"📱 Phone: {phone_number}")
            print(f"📱 Amount: KES {amount}")
            print(f"📱 Description: {transaction_desc}")
            print(f"📱 Transaction ID: {transaction_id}")
            
            # Simulate successful response
            return {
                'success': True,
                'message': f'DEMO: STK Push initiated successfully for {phone_number}',
                'transaction_id': transaction_id,
                'checkout_request_id': checkout_request_id,
                'merchant_request_id': merchant_request_id,
                'customer_message': f'DEMO: Check your phone ({phone_number}) for M-Pesa prompt to donate KES {amount}',
                'response_code': '0',
                'response_description': 'Success. Request accepted for processing'
            }
            
        except Exception as e:
            print(f"❌ Demo STK Push failed: {e}")
            return {
                'success': False,
                'message': f'Demo payment failed: {str(e)}',
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
        async for db in get_db():
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