from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    phone: Optional[str] = None

class ContactResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime

# Email configuration (you would set these as environment variables)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "climatewitnesschain@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Use app password for Gmail
CONTACT_EMAIL = "climatewitnesschain@gmail.com"

def send_email(contact_data: ContactMessage) -> bool:
    """
    Send email notification for contact form submission.
    In production, you would use a proper email service like SendGrid, AWS SES, etc.
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = CONTACT_EMAIL
        msg['Subject'] = f"Contact Form: {contact_data.subject}"
        
        # Email body
        body = f"""
        New contact form submission:
        
        Name: {contact_data.name}
        Email: {contact_data.email}
        Subject: {contact_data.subject}
        Phone: {contact_data.phone or 'Not provided'}
        
        Message:
        {contact_data.message}
        
        Sent at: {datetime.utcnow()}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email (only if SMTP credentials are configured)
        if SMTP_PASSWORD:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(SMTP_USERNAME, CONTACT_EMAIL, text)
            server.quit()
            logger.info(f"Email sent successfully for contact from {contact_data.email}")
            return True
        else:
            logger.warning("SMTP not configured, email not sent")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

@router.post("/submit", response_model=ContactResponse)
async def submit_contact_form(contact_data: ContactMessage):
    """
    Submit a contact form message.
    """
    try:
        # Log the contact submission
        logger.info(f"Contact form submission from {contact_data.email}: {contact_data.subject}")
        
        # Send email notification
        email_sent = send_email(contact_data)
        
        # In a real application, you might also:
        # 1. Save to database
        # 2. Send auto-reply to user
        # 3. Create a ticket in support system
        # 4. Send to Slack/Discord webhook
        
        return ContactResponse(
            success=True,
            message="Thank you for your message! We'll get back to you within 24 hours." if email_sent 
                   else "Message received! We'll get back to you within 24 hours.",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit contact form")

@router.get("/info")
async def get_contact_info():
    """
    Get contact information.
    """
    return {
        "email": "climatewitnesschain@gmail.com",
        "whatsapp": "+254700000000",
        "location": "Nairobi, Kenya",
        "response_time": "Within 24 hours",
        "languages": ["English", "Kiswahili", "Gĩkũyũ", "Dholuo", "Kĩkamba"],
        "business_hours": "24/7 Support Available"
    }

@router.get("/health")
async def contact_health_check():
    """
    Health check for contact service.
    """
    return {
        "status": "healthy",
        "service": "contact",
        "timestamp": datetime.utcnow(),
        "email_configured": bool(SMTP_PASSWORD)
    }