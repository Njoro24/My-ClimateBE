#!/usr/bin/env python3
"""
Simplified Render startup script for Climate Witness Chain
"""

import os
import sys
import uvicorn

def main():
    """Start the server for Render with minimal configuration"""
    
    # Get port from Render environment
    port = int(os.getenv('PORT', 10000))
    host = '0.0.0.0'
    
    print(f"🚀 Starting Climate Witness Chain API")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    
    # Start with minimal configuration for reliability
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,
        log_level="info",
        access_log=False  # Disable access logs to reduce noise
    )

if __name__ == "__main__":
    main()