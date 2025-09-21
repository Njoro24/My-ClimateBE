#!/usr/bin/env python3
"""
MeTTa Test Runner for Climate Witness Chain
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run MeTTa tests"""
    print(" Climate Witness Chain - MeTTa Test Runner")
    print("=" * 60)
    
    try:
        # Import and run tests
        from tests.test_metta_service import run_tests
        run_tests()
        
        print("\n All tests completed successfully!")
        print("MeTTa integration is ready for the Climate Witness Chain.")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure hyperon is installed: pip install hyperon")
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()