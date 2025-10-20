"""
Updated Authentication routes for Climate Witness Chain
Combines JWT token system with simplified database approach
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import aiosqlite
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets

from app.database.database import get_db
from app.utils.security import hash_password, verify_password

router = APIRouter(
    tags=["auth"]
)
security = HTTPBearer()

# Simple Token Configuration
SECRET_KEY = "climate_witness_chain_secret_key_change_in_production"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increased from 30 to 60 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    firstName: Optional[str] = None  # Accept frontend format
    lastName: Optional[str] = None   # Accept frontend format
    role: str = 'user'  # 'user' or 'researcher'
    location_region: Optional[str] = None
    locationRegion: Optional[str] = None  # Accept frontend format
    
    def get_first_name(self) -> str:
        return self.first_name or self.firstName or ""
    
    def get_last_name(self) -> str:
        return self.last_name or self.lastName or ""
    
    def get_location_region(self) -> Optional[str]:
        return self.location_region or self.locationRegion

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location_region: Optional[str] = None
    profile_image: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class OTPRequest(BaseModel):
    user_id: str
    phone_number: str

class OTPVerification(BaseModel):
    user_id: str
    otp_code: str

class LoginWithOTP(BaseModel):
    email: EmailStr
    password: str
    phone_number: str

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create simple access token"""
    user_id = data.get("sub")
    if not user_id:
        return None
    
    # Create a simple token with user_id and timestamp
    timestamp = int(datetime.utcnow().timestamp())
    token_data = f"{user_id}:{timestamp}:access"
    
    # Create a hash for security
    token_hash = hashlib.sha256(f"{token_data}:{SECRET_KEY}".encode()).hexdigest()
    return f"access_{user_id}_{timestamp}_{token_hash[:16]}"

def create_refresh_token(data: dict):
    """Create simple refresh token"""
    user_id = data.get("sub")
    if not user_id:
        return None
    
    # Create a simple token with user_id and timestamp
    timestamp = int(datetime.utcnow().timestamp())
    token_data = f"{user_id}:{timestamp}:refresh"
    
    # Create a hash for security
    token_hash = hashlib.sha256(f"{token_data}:{SECRET_KEY}".encode()).hexdigest()
    return f"refresh_{user_id}_{timestamp}_{token_hash[:16]}"

def verify_token(token: str, token_type: str = "access"):
    """Verify simple token"""
    try:
        if not token.startswith(f"{token_type}_"):
            print(f"Token doesn't start with {token_type}_: {token[:20]}...")
            return None
        
        # Parse token: type_userid_timestamp_hash
        # Remove the token type prefix first
        token_without_prefix = token[len(token_type) + 1:]  # +1 for the underscore
        
        # Split from the right to get the last two parts (timestamp and hash)
        parts = token_without_prefix.rsplit("_", 2)
        if len(parts) != 3:
            print(f"Token parts invalid: {len(parts)} parts")
            return None
        
        user_id, timestamp_str, token_hash = parts
        timestamp = int(timestamp_str)
        
        # Verify hash
        token_data = f"{user_id}:{timestamp}:{token_type}"
        expected_hash = hashlib.sha256(f"{token_data}:{SECRET_KEY}".encode()).hexdigest()[:16]
        
        if token_hash != expected_hash:
            print(f"Hash mismatch: expected {expected_hash}, got {token_hash}")
            return None
        
        # Check expiration - be more lenient with timing
        token_time = datetime.fromtimestamp(timestamp)
        now = datetime.utcnow()
        age_minutes = (now - token_time).total_seconds() / 60
        
        print(f"Token age: {age_minutes:.2f} minutes")
        
        if token_type == "access":
            # Be more lenient - allow 60 minutes instead of 30
            if age_minutes > 60:
                print(f"Access token expired: {age_minutes:.2f} > 60 minutes")
                return None
        elif token_type == "refresh":
            if age_minutes > (7 * 24 * 60):  # 7 days in minutes
                print(f"Refresh token expired: {age_minutes:.2f} > {7 * 24 * 60} minutes")
                return None
        
        print(f"Token valid for user: {user_id}")
        return {"sub": user_id, "type": token_type}
        
    except (ValueError, IndexError) as e:
        print(f"Token parsing error: {e}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    db.row_factory = aiosqlite.Row
    async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
        user = await cursor.fetchone()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return dict(user)

def user_to_dict(user) -> dict:
    """Convert user row to dictionary"""
    return {
        "id": user["id"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "role": user["role"] if "role" in user.keys() else "user",
        "wallet_address": user["wallet_address"] if "wallet_address" in user.keys() else None,
        "trust_score": user["trust_score"] if "trust_score" in user.keys() else 50,
        "location_region": user["location_region"] if "location_region" in user.keys() else None,
        "profile_image": user["profile_image"] if "profile_image" in user.keys() else None,
        "created_at": user["created_at"] if "created_at" in user.keys() else None,
        "last_login_at": user["last_login_at"] if "last_login_at" in user.keys() else None
    }

# Routes
@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Register a new user with JWT tokens"""
    try:
        # Check if user already exists
        async with db.execute("SELECT * FROM users WHERE email = ?", (user_data.email,)) as cursor:
            existing_user = await cursor.fetchone()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Hash password
        hashed_pw = await hash_password(user_data.password)
        user_id = str(uuid.uuid4())
        
        # Insert user into database with all fields
        await db.execute(
            """INSERT INTO users 
               (id, email, password_hash, first_name, last_name, role, location_region, trust_score, created_at, last_login_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                user_data.email,
                hashed_pw,
                user_data.get_first_name(),
                user_data.get_last_name(),
                user_data.role,
                user_data.get_location_region(),
                50,  # Default trust score
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ),
        )
        await db.commit()
        
        # Get the created user
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
        
        # Create tokens
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_to_dict(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_data: UserLogin,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Login user with JWT tokens"""
    try:
        # Get user by email
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE email = ?", (user_data.email,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
        
        # Verify password
        valid = await verify_password(user_data.password, user["password_hash"])
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Update last login
        await db.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now().isoformat(), user["id"])
        )
        await db.commit()
        
        # Create tokens
        access_token = create_access_token(data={"sub": user["id"]})
        refresh_token = create_refresh_token(data={"sub": user["id"]})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_to_dict(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Refresh access token"""
    try:
        payload = verify_token(token_data.refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user["id"]})
        refresh_token = create_refresh_token(data={"sub": user["id"]})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_to_dict(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return {"user": user_to_dict(current_user)}

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend is working"""
    return {"message": "Backend is working", "timestamp": datetime.now().isoformat()}

@router.get("/simple-me")
async def simple_me_endpoint(authorization: str = Header(None)):
    """Simple /me endpoint that returns unauthenticated state when no token"""
    # If no authorization header, return unauthenticated state
    if not authorization:
        return {
            "authenticated": False,
            "user": None,
            "message": "No authentication provided"
        }
    
    # If invalid format, return unauthenticated
    if not authorization.startswith("Bearer "):
        return {
            "authenticated": False,
            "user": None,
            "message": "Invalid authorization format"
        }
    
    token = authorization.replace("Bearer ", "")
    
    # If no token or invalid format, return unauthenticated
    if not token or not token.startswith("access_"):
        return {
            "authenticated": False,
            "user": None,
            "message": "Invalid or missing token"
        }
    
    # Try to validate token properly
    try:
        payload = verify_token(token)
        if payload is None:
            return {
                "authenticated": False,
                "user": None,
                "message": "Token validation failed"
            }
        
        # Token is valid, try to get user from database
        from app.database.database import get_db
        async with get_db() as db:
            db.row_factory = aiosqlite.Row
            user_id = payload.get("sub")
            async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()
                if user:
                    return {
                        "authenticated": True,
                        "user": user_to_dict(user)
                    }
                else:
                    return {
                        "authenticated": False,
                        "user": None,
                        "message": "User not found"
                    }
    except Exception as e:
        return {
            "authenticated": False,
            "user": None,
            "message": f"Authentication error: {str(e)}"
        }



@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user = Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Update user profile"""
    try:
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if profile_data.first_name is not None:
            update_fields.append("first_name = ?")
            update_values.append(profile_data.first_name)
        if profile_data.last_name is not None:
            update_fields.append("last_name = ?")
            update_values.append(profile_data.last_name)
        if profile_data.location_region is not None:
            update_fields.append("location_region = ?")
            update_values.append(profile_data.location_region)
        if profile_data.profile_image is not None:
            update_fields.append("profile_image = ?")
            update_values.append(profile_data.profile_image)
        
        if not update_fields:
            return {"user": user_to_dict(current_user)}
        
        # Add user ID to values
        update_values.append(current_user["id"])
        
        # Execute update
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        await db.execute(query, update_values)
        await db.commit()
        
        # Get updated user
        async with db.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],)) as cursor:
            updated_user = await cursor.fetchone()
        
        return {"user": user_to_dict(updated_user)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

@router.put("/password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        valid = await verify_password(password_data.current_password, current_user["password_hash"])
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = await hash_password(password_data.new_password)
        
        # Update password
        await db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password_hash, current_user["id"])
        )
        await db.commit()
        
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """Logout user (client should remove tokens)"""
    # No authentication required for logout - client handles token removal
    return {"message": "Logged out successfully"}

@router.get("/login-history")
async def get_login_history(
    current_user = Depends(get_current_user),
    limit: int = 10
):
    """Get current user's login history"""
    try:
        from app.services.event_service import EventService
        event_service = EventService()
        history = await event_service.get_user_login_history(current_user["id"], limit)
        return {"login_history": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get login history: {str(e)}"
        )

@router.get("/login-stats")
async def get_login_stats():
    """Get login statistics (admin endpoint)"""
    try:
        from app.services.event_service import EventService
        event_service = EventService()
        stats = await event_service.get_login_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get login statistics: {str(e)}"
        )
# OTP Authentication Endpoints

@router.post("/login-with-otp")
async def login_with_otp(
    user_data: LoginWithOTP,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Login user and send OTP for verification"""
    try:
        # First verify email and password
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE email = ?", (user_data.email,)) as cursor:
            user = await cursor.fetchone()
            if not user or not await verify_password(user_data.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
        
        # Generate and send OTP
        from app.services.otp_service import otp_service
        otp_result = await otp_service.create_otp(user["id"], user_data.phone_number)
        
        return {
            "message": "OTP sent successfully",
            "user_id": user["id"],
            "otp_id": otp_result["otp_id"],
            "expires_at": otp_result["expires_at"],
            "phone_number": otp_result["phone_number"],
            "sms_sent": otp_result["sms_sent"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/send-otp")
async def send_otp(
    otp_request: OTPRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Send OTP to user's phone number"""
    try:
        # Verify user exists
        async with db.execute("SELECT * FROM users WHERE id = ?", (otp_request.user_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Generate and send OTP
        from app.services.otp_service import otp_service
        otp_result = await otp_service.create_otp(otp_request.user_id, otp_request.phone_number)
        
        return {
            "message": "OTP sent successfully",
            "otp_id": otp_result["otp_id"],
            "expires_at": otp_result["expires_at"],
            "phone_number": otp_result["phone_number"],
            "sms_sent": otp_result["sms_sent"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    otp_verification: OTPVerification,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Verify OTP and complete login"""
    try:
        # Verify OTP
        from app.services.otp_service import otp_service
        verification_result = await otp_service.verify_otp(
            otp_verification.user_id, 
            otp_verification.otp_code
        )
        
        if not verification_result.get('valid'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=verification_result.get('error', 'Invalid OTP')
            )
        
        # Get user data
        async with db.execute("SELECT * FROM users WHERE id = ?", (otp_verification.user_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Update last login
        await db.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now().isoformat(), user["id"])
        )
        await db.commit()
        
        # Log login event
        try:
            from app.services.event_service import EventService
            event_service = EventService()
            await event_service.log_user_login(user["id"], "unknown")
        except Exception as e:
            print(f"Warning: Failed to log login event: {e}")
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user["id"]})
        refresh_token = create_refresh_token(data={"sub": user["id"]})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_to_dict(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )

@router.post("/resend-otp")
async def resend_otp(
    otp_request: OTPRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Resend OTP to user's phone number"""
    try:
        # Verify user exists
        async with db.execute("SELECT * FROM users WHERE id = ?", (otp_request.user_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Generate and send new OTP
        from app.services.otp_service import otp_service
        otp_result = await otp_service.create_otp(otp_request.user_id, otp_request.phone_number)
        
        return {
            "message": "OTP resent successfully",
            "otp_id": otp_result["otp_id"],
            "expires_at": otp_result["expires_at"],
            "phone_number": otp_result["phone_number"],
            "sms_sent": otp_result["sms_sent"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend OTP: {str(e)}"
        )