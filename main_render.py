"""
Simplified FastAPI app for Render deployment
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Climate Witness Chain API",
    description="Community-driven climate data collection platform",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
try:
    from app.api.routes import auth, events, users, admin, payments
    
    # Include routers
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(events.router, prefix="/api/events", tags=["events"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
    
    print("✅ Core routes loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Some routes not available: {e}")

# Optional routes (load if available)
optional_routes = [
    ('metta', 'metta'),
    ('community_verification', 'community-verification'),
    ('economic_impact', 'economic-impact'),

    ('dao_governance', 'dao'),
    ('alerts', 'alerts'),
    ('plant_recommendations', 'plants'),
    ('contact', 'contact')
]

for route_name, prefix in optional_routes:
    try:
        module = __import__(f'app.api.routes.{route_name}', fromlist=[route_name])
        app.include_router(module.router, prefix=f"/api/{prefix}", tags=[prefix])
        print(f"✅ {route_name} routes loaded")
    except ImportError:
        print(f"⚠️ {route_name} routes not available")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "Climate Witness Chain API"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Climate Witness Chain API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        print("🚀 Starting Climate Witness Chain API...")
        
        # Initialize database
        from app.database.migrations import create_tables
        await create_tables()
        print("✅ Database initialized")
        
        # Create sample data if needed
        import aiosqlite
        db_path = os.getenv('DATABASE_URL', './climate_witness.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
            
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                count = (await cursor.fetchone())[0]
                
            if count == 0:
                from app.database.migrations import insert_sample_data
                await insert_sample_data(db_path)
                print("✅ Sample data created")
            else:
                print(f"✅ Database ready ({count} users)")
                
    except Exception as e:
        print(f"⚠️ Startup warning: {e}")
        # Don't fail startup if optional services fail

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)