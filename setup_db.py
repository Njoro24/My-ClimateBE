#!/usr/bin/env python3
"""
Setup database for Climate Witness Chain
"""

import asyncio
import sys
import os

async def setup_database():
    """Setup the database"""
    try:
        print(" Setting up Climate Witness Chain database...")
        
        # Import after ensuring we're in the right directory
        from app.database.migrations import reset_database
        
        # Reset and initialize database
        await reset_database()
        
        print("✅ Database setup completed successfully!")
        print(" Sample users created:")
        print("   - amina@example.com (password: demo123)")
        print("   - john@example.com (password: demo123)")
        print("   - mary@example.com (password: demo123)")
        print()
        print(" You can now start the server with: python start_server.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    if not success:
        sys.exit(1)