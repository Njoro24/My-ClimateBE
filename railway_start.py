#!/usr/bin/env python3
"""
Railway deployment startup script for Climate Witness Chain
"""

import os
import sys
import asyncio
import uvicorn
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def initialize_database():
    """Initialize database on startup"""
    try:
        print("🔧 Initializing database for Railway...")
        
        # Use proper database migrations
        from app.database.migrations import create_tables, insert_sample_data
        
        # Get database path
        db_path = os.getenv('DATABASE_URL', './climate_witness.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
        
        # Create tables using proper migrations
        await create_tables(db_path)
        print("✅ Database tables created")
        
        # Check if we need sample data
        import aiosqlite
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                count = (await cursor.fetchone())[0]
                
            if count == 0:
                print("🔧 Creating sample data...")
                await insert_sample_data(db_path)
                print("✅ Sample data created")
            else:
                print(f"✅ Database ready with {count} users")
                
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        # Don't fail deployment if database init fails

def wait_for_port(port, timeout=60):
    """Wait for port to be available"""
    import socket
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('0.0.0.0', port))
            sock.close()
            if result != 0:  # Port is available
                return True
            time.sleep(1)
        except:
            time.sleep(1)
    return False

def main():
    """Start the production server for Railway"""
    
    # Railway automatically sets PORT environment variable
    port = int(os.getenv('PORT', 8000))
    host = '0.0.0.0'
    
    print(f"🚀 Starting Climate Witness Chain API for Railway")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"   Railway Domain: {os.getenv('RAILWAY_PUBLIC_DOMAIN', 'Not set')}")
    print("=" * 50)
    
    # Initialize database
    try:
        asyncio.run(initialize_database())
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("Continuing with server startup...")
    
    # Wait a moment for any cleanup
    time.sleep(2)
    
    # Start the server with Railway-optimized settings
    # Use simple_main for reliable deployment
    app_module = 'simple_main:app'
    
    print(f"🚀 Starting app module: {app_module}")
    
    uvicorn.run(
        app_module,
        host=host,
        port=port,
        reload=False,
        workers=1,  # Railway works well with 1 worker
        access_log=True,
        log_level="info",
        timeout_keep_alive=120,
        timeout_graceful_shutdown=30
    )

if __name__ == "__main__":
    main()