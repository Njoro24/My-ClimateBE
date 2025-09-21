"""
Admin API routes for Climate Witness Chain
Provides analytics, user management, and system monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiosqlite
from app.database.database import get_db
from app.api.routes.auth import get_current_user

router = APIRouter(tags=["admin"])

async def require_admin(
    authorization: str = Header(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Require admin role for admin endpoints"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Import the verify_token function from auth
    from app.api.routes.auth import verify_token
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
    async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
        user = await cursor.fetchone()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Check if user has admin role
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""
    try:
        stats = {}
        
        # User statistics
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            stats["total_users"] = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')") as cursor:
            stats["new_users_today"] = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM users WHERE created_at >= DATE('now', '-7 days')") as cursor:
            stats["new_users_week"] = (await cursor.fetchone())[0]
        
        # Event statistics
        async with db.execute("SELECT COUNT(*) FROM events") as cursor:
            stats["total_events"] = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM events WHERE DATE(created_at) = DATE('now')") as cursor:
            stats["events_today"] = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM events WHERE verification_status = 'verified'") as cursor:
            stats["verified_events"] = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM events WHERE verification_status = 'pending'") as cursor:
            stats["pending_events"] = (await cursor.fetchone())[0]
        
        # Login statistics
        try:
            async with db.execute("SELECT COUNT(*) FROM login_events WHERE DATE(login_time) = DATE('now')") as cursor:
                stats["logins_today"] = (await cursor.fetchone())[0]
            
            async with db.execute("SELECT COUNT(DISTINCT user_id) FROM login_events WHERE DATE(login_time) = DATE('now')") as cursor:
                stats["active_users_today"] = (await cursor.fetchone())[0]
        except:
            stats["logins_today"] = 0
            stats["active_users_today"] = 0
        
        # Event type breakdown
        async with db.execute("""
            SELECT event_type, COUNT(*) as count 
            FROM events 
            GROUP BY event_type 
            ORDER BY count DESC
        """) as cursor:
            event_types = await cursor.fetchall()
            stats["event_types"] = [{"type": row[0], "count": row[1]} for row in event_types]
        
        # Verification rate
        if stats["total_events"] > 0:
            stats["verification_rate"] = round((stats["verified_events"] / stats["total_events"]) * 100, 2)
        else:
            stats["verification_rate"] = 0
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/users")
async def get_all_users(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get paginated list of all users"""
    try:
        offset = (page - 1) * limit
        
        # Get total count
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total = (await cursor.fetchone())[0]
        
        # Get users with pagination
        async with db.execute("""
            SELECT id, email, first_name, last_name, role, trust_score, 
                   location_region, is_active, is_verified, created_at, last_login_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset)) as cursor:
            users = await cursor.fetchall()
        
        user_list = []
        for user in users:
            user_dict = dict(user)
            # Get user's event count
            async with db.execute("SELECT COUNT(*) FROM events WHERE user_id = ?", (user["id"],)) as cursor:
                user_dict["event_count"] = (await cursor.fetchone())[0]
            user_list.append(user_dict)
        
        return {
            "users": user_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.get("/events")
async def get_all_events(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None)
):
    """Get paginated list of all events with filters"""
    try:
        offset = (page - 1) * limit
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if status_filter:
            where_conditions.append("verification_status = ?")
            params.append(status_filter)
        
        if event_type:
            where_conditions.append("event_type = ?")
            params.append(event_type)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM events {where_clause}"
        async with db.execute(count_query, params) as cursor:
            total = (await cursor.fetchone())[0]
        
        # Get events with pagination
        events_query = f"""
            SELECT e.*, u.first_name, u.last_name, u.email
            FROM events e
            LEFT JOIN users u ON e.user_id = u.id
            {where_clause}
            ORDER BY e.created_at DESC 
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        async with db.execute(events_query, params) as cursor:
            events = await cursor.fetchall()
        
        event_list = [dict(event) for event in events]
        
        return {
            "events": event_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.get("/analytics/users")
async def get_user_analytics(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get user registration analytics over time"""
    try:
        # Get daily user registrations for the last N days
        async with db.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users 
            WHERE created_at >= DATE('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """.format(days)) as cursor:
            daily_registrations = await cursor.fetchall()
        
        # Get user distribution by role
        async with db.execute("""
            SELECT role, COUNT(*) as count
            FROM users 
            GROUP BY role
        """) as cursor:
            role_distribution = await cursor.fetchall()
        
        # Get user distribution by region
        async with db.execute("""
            SELECT location_region, COUNT(*) as count
            FROM users 
            WHERE location_region IS NOT NULL
            GROUP BY location_region
            ORDER BY count DESC
            LIMIT 10
        """) as cursor:
            region_distribution = await cursor.fetchall()
        
        return {
            "daily_registrations": [{"date": row[0], "count": row[1]} for row in daily_registrations],
            "role_distribution": [{"role": row[0], "count": row[1]} for row in role_distribution],
            "region_distribution": [{"region": row[0], "count": row[1]} for row in region_distribution]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")

@router.get("/analytics/events")
async def get_event_analytics(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get event analytics over time"""
    try:
        # Get daily event submissions
        async with db.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM events 
            WHERE created_at >= DATE('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """.format(days)) as cursor:
            daily_events = await cursor.fetchall()
        
        # Get event verification trends
        async with db.execute("""
            SELECT DATE(created_at) as date, 
                   verification_status,
                   COUNT(*) as count
            FROM events 
            WHERE created_at >= DATE('now', '-{} days')
            GROUP BY DATE(created_at), verification_status
            ORDER BY date, verification_status
        """.format(days)) as cursor:
            verification_trends = await cursor.fetchall()
        
        # Get event type trends
        async with db.execute("""
            SELECT event_type, COUNT(*) as count
            FROM events 
            WHERE created_at >= DATE('now', '-{} days')
            GROUP BY event_type
            ORDER BY count DESC
        """.format(days)) as cursor:
            type_trends = await cursor.fetchall()
        
        return {
            "daily_events": [{"date": row[0], "count": row[1]} for row in daily_events],
            "verification_trends": [{"date": row[0], "status": row[1], "count": row[2]} for row in verification_trends],
            "type_trends": [{"type": row[0], "count": row[1]} for row in type_trends]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event analytics: {str(e)}")

@router.get("/analytics/activity")
async def get_activity_analytics(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db),
    days: int = Query(7, ge=1, le=30)
):
    """Get user activity analytics"""
    try:
        # Get daily login activity
        login_activity = []
        try:
            async with db.execute("""
                SELECT DATE(login_time) as date, COUNT(*) as logins, COUNT(DISTINCT user_id) as unique_users
                FROM login_events 
                WHERE login_time >= DATE('now', '-{} days')
                GROUP BY DATE(login_time)
                ORDER BY date
            """.format(days)) as cursor:
                login_data = await cursor.fetchall()
                login_activity = [{"date": row[0], "logins": row[1], "unique_users": row[2]} for row in login_data]
        except:
            # If login_events table doesn't exist or has no data
            pass
        
        # Get most active users
        async with db.execute("""
            SELECT u.first_name, u.last_name, u.email, COUNT(e.id) as event_count
            FROM users u
            LEFT JOIN events e ON u.id = e.user_id
            GROUP BY u.id
            ORDER BY event_count DESC
            LIMIT 10
        """) as cursor:
            active_users = await cursor.fetchall()
        
        return {
            "login_activity": login_activity,
            "most_active_users": [
                {
                    "name": f"{row[0]} {row[1]}",
                    "email": row[2],
                    "event_count": row[3]
                } for row in active_users
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity analytics: {str(e)}")

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Update user active status"""
    try:
        await db.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (is_active, user_id)
        )
        await db.commit()
        
        return {"message": f"User status updated successfully", "user_id": user_id, "is_active": is_active}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user status: {str(e)}")

@router.put("/events/{event_id}/verification")
async def update_event_verification(
    event_id: str,
    verification_status: str,
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Update event verification status"""
    try:
        valid_statuses = ["pending", "verified", "rejected", "manual_review"]
        if verification_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        await db.execute(
            "UPDATE events SET verification_status = ? WHERE id = ?",
            (verification_status, event_id)
        )
        await db.commit()
        
        return {"message": "Event verification updated successfully", "event_id": event_id, "status": verification_status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event verification: {str(e)}")

@router.get("/system/health")
async def get_system_health(
    admin_user = Depends(require_admin),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Get system health metrics"""
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "services": {}
        }
        
        # Check database
        try:
            async with db.execute("SELECT 1") as cursor:
                await cursor.fetchone()
            health["database"] = "connected"
        except:
            health["database"] = "error"
            health["status"] = "degraded"
        
        # Check table sizes
        tables = ["users", "events", "metta_atoms"]
        for table in tables:
            try:
                async with db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                    count = (await cursor.fetchone())[0]
                    health["services"][f"{table}_count"] = count
            except:
                health["services"][f"{table}_count"] = "error"
        
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")