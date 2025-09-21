#!/usr/bin/env python3
"""
Production startup script for Climate Witness Chain
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Start the production server"""
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    environment = os.getenv('ENVIRONMENT', 'production')
    
    print(f"🚀 Starting Climate Witness Chain API")
    print(f"   Environment: {environment}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print("=" * 50)
    
    # Configure uvicorn based on environment
    if environment == 'production':
        # Production configuration
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,
            workers=4,
            access_log=True,
            log_level="info"
        )
    else:
        # Development configuration
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            access_log=True,
            log_level="debug" if debug else "info"
        )

if __name__ == "__main__":
    main()