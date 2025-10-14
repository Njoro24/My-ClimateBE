"""
Payment API routes for Climate Witness Chain
Handles M-Pesa and other payment integrations
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
import aiosqlite
from app.database.database import get_db
from app.api.routes.auth import get_current_user
from app.services.payment_service import payment_service

router = APIRouter(tags=["payments"])

# Pydantic models
class PaymentRequest(BaseModel):
    phone_number: str
    amount: float
    description: Optional[str] = "Climate Witness Chain Donation"
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, v))
        
        # Validate Kenyan phone number format
        if phone.startswith('0') and len(phone) == 10:
            return phone
        elif phone.startswith('254') and len(phone) == 12:
            return phone
        elif phone.startswith('+254') and len(phone) == 13:
            return phone[1:]  # Remove the +
        else:
            raise ValueError('Invalid phone number format. Use format: 0712345678 or 254712345678')
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 70000:  # M-Pesa limit
            raise ValueError('Amount cannot exceed KES 70,000')
        return round(v, 2)

class PaymentResponse(BaseModel):
    success: bool
    message: str
    transaction_id: Optional[str] = None
    checkout_request_id: Optional[str] = None
    customer_message: Optional[str] = None

class TransactionStatusResponse(BaseModel):
    found: bool
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    phone_number: Optional[str] = None
    mpesa_receipt_number: Optional[str] = None
    created_at: Optional[str] = None

@router.post("/mpesa/initiate", response_model=PaymentResponse)
async def initiate_mpesa_payment(
    payment_request: PaymentRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Initiate M-Pesa STK Push payment"""
    try:
        # Create account reference with timestamp for demo
        account_reference = f"CWC_DEMO_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Customize transaction description
        transaction_desc = f"Donation to Climate Witness Chain - {payment_request.description}"
        
        # Initiate STK Push
        result = await payment_service.initiate_stk_push(
            phone_number=payment_request.phone_number,
            amount=payment_request.amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc
        )
        
        if result['success']:
            return PaymentResponse(
                success=True,
                message=f"Please check your phone ({payment_request.phone_number}) for the M-Pesa prompt to donate KES {payment_request.amount}",
                transaction_id=result.get('transaction_id'),
                checkout_request_id=result.get('checkout_request_id'),
                customer_message=result.get('customer_message')
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment initiation failed: {str(e)}"
        )

@router.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    """Handle M-Pesa callback"""
    try:
        callback_data = await request.json()
        result = await payment_service.handle_callback(callback_data)
        
        return {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }
        
    except Exception as e:
        print(f"❌ Callback processing failed: {e}")
        return {
            "ResultCode": 1,
            "ResultDesc": f"Failed: {str(e)}"
        }

@router.get("/transaction/{transaction_id}", response_model=TransactionStatusResponse)
async def get_transaction_status(
    transaction_id: str,
    current_user = Depends(get_current_user)
):
    """Get transaction status"""
    try:
        result = await payment_service.get_transaction_status(transaction_id)
        
        if result['found']:
            return TransactionStatusResponse(
                found=True,
                transaction_id=result['transaction_id'],
                status=result['status'],
                amount=result['amount'],
                phone_number=result['phone_number'],
                mpesa_receipt_number=result.get('mpesa_receipt_number'),
                created_at=result['created_at']
            )
        else:
            return TransactionStatusResponse(found=False)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction status: {str(e)}"
        )

@router.get("/transactions")
async def get_user_transactions(
    current_user = Depends(get_current_user)
):
    """Get user's transaction history"""
    try:
        transactions = await payment_service.get_user_transactions(current_user['id'])
        
        return {
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transactions: {str(e)}"
        )

@router.get("/test")
async def test_payment_service():
    """Test M-Pesa service configuration and connectivity"""
    try:
        # Test access token generation
        access_token = await payment_service.get_access_token()
        
        return {
            "status": "M-Pesa service is configured and connected",
            "environment": payment_service.environment,
            "business_short_code": payment_service.business_short_code,
            "callback_url": payment_service.callback_url,
            "token_obtained": bool(access_token),
            "ready_for_payments": True
        }
        
    except Exception as e:
        return {
            "status": "M-Pesa service configuration error",
            "error": str(e),
            "message": "Please check your M-Pesa API credentials",
            "ready_for_payments": False
        }