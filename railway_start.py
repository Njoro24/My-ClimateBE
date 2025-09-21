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
        
        # Simple database initialization - create basic tables
        import sqlite3
        db_path = os.getenv('DATABASE_URL', './climate_witness.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
        
        # Create basic tables if they don't exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create a basic admin user if none exists
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("🔧 Creating admin user...")
            # Simple password hash for demo (in production, use proper hashing)
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, is_active, is_verified)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin@climatewitness.com', 'admin123', 'Admin User', 1, 1))
            
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
                
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
    # Use simple_main for initial deployment, then switch to main:app
    app_module = os.getenv('APP_MODULE', 'simple_main:app')
    
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