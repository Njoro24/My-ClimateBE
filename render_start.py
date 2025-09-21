#!/usr/bin/env python3
"""
Render deployment startup script for Climate Witness Chain
"""

import os
import sys
import asyncio
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def initialize_database():
    """Initialize database on startup"""
    try:
        from app.database.migrations import create_tables
        print("🔧 Initializing database...")
        
        # Create database tables
        await create_tables()
        print("✅ Database initialized successfully")
        
        # Check if we need to create sample data
        import aiosqlite
        async with aiosqlite.connect(os.getenv('DATABASE_URL', './climate_witness.db')) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                count = (await cursor.fetchone())[0]
                
            if count == 0:
                print("🔧 Creating sample data...")
                from app.database.migrations import insert_sample_data
                await insert_sample_data()
                print("✅ Sample data created")
            else:
                print(f"✅ Database has {count} users")
                
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        # Don't fail deployment if database init fails

def main():
    """Start the production server for Render"""
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 10000))  # Render uses port 10000 by default
    
    print(f"🚀 Starting Climate Witness Chain API for Render")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print("=" * 50)
    
    # Initialize database
    asyncio.run(initialize_database())
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,  # Render free tier works better with 1 worker
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()