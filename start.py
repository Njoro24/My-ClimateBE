#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    print("🌍 Starting Climate Witness Chain API...")
    print("=" * 50)
    
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found in current directory")
        print("Please run this script from the BECW directory")
        sys.exit(1)
    try:
        print("🚀 Launching main.py...")
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()