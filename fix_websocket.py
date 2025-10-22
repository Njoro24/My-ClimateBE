#!/usr/bin/env python3
"""
Fix WebSocket dependencies for Climate Witness backend
"""

import subprocess
import sys
import os

def install_websocket_dependencies():
    """Install required WebSocket dependencies"""
    try:
        print("Installing WebSocket dependencies...")
        
        # Install websockets library
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets>=11.0.0"])
        
        # Reinstall uvicorn with standard dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "uvicorn[standard]>=0.20.0"])
        
        print("✅ WebSocket dependencies installed successfully!")
        print("🔄 Please restart your server to apply changes.")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_websocket_support():
    """Verify WebSocket support is available"""
    try:
        import websockets
        import uvicorn
        print("✅ WebSocket libraries are available")
        print(f"   - websockets version: {websockets.__version__}")
        print(f"   - uvicorn version: {uvicorn.__version__}")
        return True
    except ImportError as e:
        print(f"❌ WebSocket libraries not available: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Climate Witness WebSocket Fix")
    print("=" * 40)
    
    # Check current directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the BECW directory")
        sys.exit(1)
    
    # Install dependencies
    if install_websocket_dependencies():
        # Verify installation
        if verify_websocket_support():
            print("\n🎉 WebSocket fix completed successfully!")
            print("\nNext steps:")
            print("1. Restart your FastAPI server")
            print("2. WebSocket connections should now work properly")
            print("3. Check browser console for successful WebSocket connections")
        else:
            print("\n⚠️  Installation completed but verification failed")
            print("You may need to restart your Python environment")
    else:
        print("\n❌ WebSocket fix failed")
        print("Please install dependencies manually:")
        print("  pip install websockets>=11.0.0")
        print("  pip install --upgrade uvicorn[standard]>=0.20.0")