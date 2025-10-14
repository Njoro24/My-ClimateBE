"""
M-Pesa Integration Service for Climate Witness Chain
Handles STK Push, payment callbacks, and transaction queries
"""

import requests
import base64
import json
import asyncio
import concurrent.futures
from datetime import datetime
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        # M-Pesa API Configuration
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.business_short_code = os.getenv('MPESA_BUSINESS_SHORT_CODE', '174379')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL')
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
        
        # API URLs
        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
        
        self.auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        self.query_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        # Check if credentials are available
        self.is_configured = all([
            self.consumer_key,
            self.consumer_secret,
            self.business_short_code,
            self.passkey,
            self.callback_url
        ])
        
        if not self.is_configured:
            logger.warning("M-Pesa credentials not fully configured. Using demo mode.")

    async def get_access_token(self) -> Optional[str]:
        """Get OAuth access token from M-Pesa API"""
        if not self.is_configured:
            return None
            
        try:
            # Use requests in thread pool for async compatibility
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
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('access_token')
                else:
                    logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
                    return None
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None

    def generate_password(self) -> str:
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.business_short_code}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password, timestamp

    def format_phone_number(self, phone: str) -> str:
        """Format phone number to 254XXXXXXXXX format"""
        # Remove any spaces, dashes, or special characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Convert to 254 format
        if phone.startswith('0') and len(phone) == 10:
            return f"254{phone[1:]}"
        elif phone.startswith('254') and len(phone) == 12:
            return phone
        elif phone.startswith('+254') and len(phone) == 13:
            return phone[1:]
        else:
            raise ValueError(f"Invalid phone number format: {phone}")

    async def initiate_stk_push(self, phone: str, amount: float, account_reference: str, transaction_desc: str = None) -> Dict[str, Any]:
        """Initiate STK Push payment"""
        
        # If not configured, return demo response
        if not self.is_configured:
            return self._demo_response(phone, amount, account_reference)
        
        try:
            # Get access token
            access_token = await self.get_access_token()
            if not access_token:
                raise Exception("Failed to get access token")
            
            # Format phone number
            formatted_phone = self.format_phone_number(phone)
            
            # Generate password and timestamp
            password, timestamp = self.generate_password()
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": formatted_phone,
                "PartyB": self.business_short_code,
                "PhoneNumber": formatted_phone,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc or f"Climate Witness Chain - {account_reference}"
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Make STK push request using requests in thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: requests.post(self.stk_push_url, json=payload, headers=headers, timeout=30)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if request was successful
                    if data.get('ResponseCode') == '0':
                        return {
                            'success': True,
                            'message': 'STK push sent successfully',
                            'checkout_request_id': data.get('CheckoutRequestID'),
                            'merchant_request_id': data.get('MerchantRequestID'),
                            'response_code': data.get('ResponseCode'),
                            'response_description': data.get('ResponseDescription'),
                            'customer_message': data.get('CustomerMessage')
                        }
                    else:
                        return {
                            'success': False,
                            'message': data.get('ResponseDescription', 'STK push failed'),
                            'response_code': data.get('ResponseCode'),
                            'error_code': data.get('errorCode'),
                            'error_message': data.get('errorMessage')
                        }
                else:
                    logger.error(f"STK push failed: {response.status_code} - {response.text}")
                    return {
                        'success': False,
                        'message': f'Payment request failed: {response.status_code}',
                        'error': response.text
                    }
                
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'error_type': 'validation_error'
            }
        except Exception as e:
            logger.error(f"STK push error: {str(e)}")
            return {
                'success': False,
                'message': f'Payment system error: {str(e)}',
                'error_type': 'system_error'
            }

    async def query_transaction_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """Query the status of an STK push transaction"""
        
        if not self.is_configured:
            return {
                'success': True,
                'message': 'Demo transaction completed',
                'result_code': '0',
                'result_desc': 'Demo payment successful'
            }
        
        try:
            # Get access token
            access_token = await self.get_access_token()
            if not access_token:
                raise Exception("Failed to get access token")
            
            # Generate password and timestamp
            password, timestamp = self.generate_password()
            
            # Prepare query payload
            payload = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Make query request using requests in thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: requests.post(self.query_url, json=payload, headers=headers, timeout=30)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'result_code': data.get('ResultCode'),
                        'result_desc': data.get('ResultDesc'),
                        'merchant_request_id': data.get('MerchantRequestID'),
                        'checkout_request_id': data.get('CheckoutRequestID'),
                        'response_code': data.get('ResponseCode')
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Query failed: {response.status_code}',
                        'error': response.text
                    }
                
        except Exception as e:
            logger.error(f"Transaction query error: {str(e)}")
            return {
                'success': False,
                'message': f'Query error: {str(e)}'
            }

    def process_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process M-Pesa callback data"""
        try:
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            merchant_request_id = stk_callback.get('MerchantRequestID')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Extract callback metadata if payment was successful
            callback_metadata = {}
            if result_code == 0:  # Success
                metadata_items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in metadata_items:
                    name = item.get('Name')
                    value = item.get('Value')
                    if name and value is not None:
                        callback_metadata[name] = value
            
            return {
                'success': result_code == 0,
                'merchant_request_id': merchant_request_id,
                'checkout_request_id': checkout_request_id,
                'result_code': result_code,
                'result_desc': result_desc,
                'amount': callback_metadata.get('Amount'),
                'mpesa_receipt_number': callback_metadata.get('MpesaReceiptNumber'),
                'transaction_date': callback_metadata.get('TransactionDate'),
                'phone_number': callback_metadata.get('PhoneNumber')
            }
            
        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _demo_response(self, phone: str, amount: float, reference: str) -> Dict[str, Any]:
        """Return demo response when M-Pesa is not configured"""
        return {
            'success': True,
            'message': 'Demo STK push sent (M-Pesa not configured)',
            'checkout_request_id': f'demo_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'merchant_request_id': f'demo_merchant_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'response_code': '0',
            'response_description': 'Demo payment initiated',
            'customer_message': f'Demo: Check your phone {phone} for payment prompt',
            'demo_mode': True,
            'note': 'To enable real payments, configure M-Pesa credentials in environment variables'
        }

    def validate_phone_number(self, phone: str) -> bool:
        """Validate Kenyan phone number format"""
        try:
            formatted = self.format_phone_number(phone)
            # Check if it's a valid Kenyan mobile number (Safaricom, Airtel, Telkom)
            return formatted.startswith('2547') or formatted.startswith('2541') or formatted.startswith('2570')
        except:
            return False

    def validate_amount(self, amount: float) -> bool:
        """Validate payment amount"""
        return 1 <= amount <= 70000  # M-Pesa limits

# Create singleton instance
mpesa_service = MpesaService()