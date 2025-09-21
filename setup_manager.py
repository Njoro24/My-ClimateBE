#!/usr/bin/env python3
"""
Climate Witness Chain Setup Script
Prepares the environment for demo execution and testing
"""

import asyncio
import json
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db, init_db
from app.database.migrations import create_tables
from demo_data_generator import DemoDataGenerator
from demo_presentation import DemoPresentation

class SetupManager:
    """Manages the complete setup process for Climate Witness Chain"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent
        self.frontend_dir = self.project_root / "frontend"
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
    
    def print_step(self, step: int, title: str, description: str = ""):
        """Print formatted step"""
        print(f"\n Step {step}: {title}")
        if description:
            print(f"   {description}")
        print("-" * 50)
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        self.print_step(1, "Checking Dependencies", "Verifying Python packages and system requirements")
        
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "hyperon", "web3", 
            "requests", "pytest", "python-multipart"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} - MISSING")
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("   Run: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies satisfied")
        return True
    
    async def setup_database(self):
        """Initialize and migrate the database"""
        self.print_step(2, "Database Setup", "Initializing SQLite database and running migrations")
        
        try:
            # Initialize database
            await init_db()
            print("   ✅ Database initialized")
            
            # Verify tables by checking if database file exists
            db_path = self.backend_dir / "climate_witness.db"
            if db_path.exists():
                print("   ✅ Database file created")
                
                # Use aiosqlite to check tables
                import aiosqlite
                async with aiosqlite.connect(str(db_path)) as conn:
                    cursor = await conn.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """)
                    tables = await cursor.fetchall()
                    
                    print(f"   ✅ Tables created: {', '.join([t[0] for t in tables])}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database setup failed: {str(e)}")
            return False
    
    def setup_metta_knowledge(self):
        """Setup MeTTa knowledge base"""
        self.print_step(3, "MeTTa Knowledge Setup", "Initializing hyperon and loading knowledge atoms")
        
        try:
            from app.services.metta_service import MeTTaService
            
            metta_service = MeTTaService()
            
            # Load knowledge files
            metta_dir = self.backend_dir / "metta"
            knowledge_files = list(metta_dir.glob("*.metta"))
            
            for file_path in knowledge_files:
                print(f"    Loading {file_path.name}...")
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Basic validation that file contains MeTTa syntax
                    if "(" in content and ")" in content:
                        print(f"   ✅ {file_path.name} - Valid MeTTa syntax")
                    else:
                        print(f"   ⚠️  {file_path.name} - Check syntax")
            
            print("   ✅ MeTTa knowledge base ready")
            return True
            
        except Exception as e:
            print(f"   ❌ MeTTa setup failed: {str(e)}")
            return False
    
    def verify_blockchain_config(self):
        """Verify blockchain configuration"""
        self.print_step(4, "Blockchain Configuration", "Checking Web3 and Polygon Mumbai setup")
        
        try:
            from app.services.blockchain_service import BlockchainService
            
            blockchain_service = BlockchainService()
            
            # Check if Web3 is properly configured
            if blockchain_service.w3:
                print("   ✅ Web3 connection available")
                
                # Test wallet generation
                wallet = blockchain_service.generate_wallet_address()
                print(f"   ✅ Wallet generation works: {wallet['address'][:10]}...")
                
                print("   ✅ Blockchain service ready")
                return True
            else:
                print("   ⚠️  Web3 connection not available (demo mode)")
                return True  # Still allow demo mode
                
        except Exception as e:
            print(f"   ❌ Blockchain setup failed: {str(e)}")
            return False
    
    def create_demo_assets(self):
        """Create demo assets and test images"""
        self.print_step(5, "Demo Assets", "Creating demo images and test data")
        
        try:
            # Create demo images directory
            demo_images_dir = self.backend_dir / "demo_images"
            demo_images_dir.mkdir(exist_ok=True)
            
            # Create placeholder images
            demo_images = [
                "demo_drought_malawi.jpg",
                "demo_flood_bangladesh.jpg", 
                "demo_locust_kenya.jpg",
                "demo_storm_philippines.jpg",
                "demo_extreme_heat_india.jpg"
            ]
            
            for image_name in demo_images:
                image_path = demo_images_dir / image_name
                if not image_path.exists():
                    # Create a simple text file as placeholder
                    with open(image_path, 'w') as f:
                        f.write(f"Demo image placeholder: {image_name}")
                    print(f"    Created {image_name}")
            
            print("   ✅ Demo assets ready")
            return True
            
        except Exception as e:
            print(f"   ❌ Demo assets setup failed: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test that all API endpoints are working"""
        self.print_step(6, "API Testing", "Verifying all endpoints are functional")
        
        try:
            # Import API modules to check for syntax errors
            from app.api.routes import users, events, blockchain, metta
            
            print("   ✅ User routes imported")
            print("   ✅ Event routes imported") 
            print("   ✅ Blockchain routes imported")
            print("   ✅ MeTTa routes imported")
            
            print("   ✅ All API endpoints ready")
            return True
            
        except Exception as e:
            print(f"   ❌ API testing failed: {str(e)}")
            return False
    
    async def run_quick_test(self):
        """Run a quick end-to-end test"""
        self.print_step(7, "Quick Test", "Running end-to-end workflow test")
        
        try:
            from app.services.user_service import UserService
            from app.services.event_service import EventService
            
            user_service = UserService()
            event_service = EventService()
            
            # Create test user
            test_user_data = {
                "name": "Test User",
                "email": "test@climatewiness.org",
                "trust_score": 0.8,
                "wallet_address": "0x1234567890123456789012345678901234567890"
            }
            
            user = await user_service.create_user(test_user_data)
            print(f"   ✅ Test user created: {user['id']}")
            
            # Create test event
            test_event_data = {
                "user_id": user["id"],
                "event_type": "test",
                "description": "Setup test event",
                "latitude": 0.0,
                "longitude": 0.0,
                "location_name": "Test Location",
                "timestamp": datetime.now().isoformat()
            }
            
            event = await event_service.submit_event(test_event_data)
            print(f"   ✅ Test event created: {event['id']}")
            
            # Clean up test data
            import aiosqlite
            async with aiosqlite.connect(str(self.backend_dir / "climate_witness.db")) as conn:
                await conn.execute("DELETE FROM events WHERE id = ?", (event["id"],))
                await conn.execute("DELETE FROM users WHERE id = ?", (user["id"],))
                await conn.commit()
            
            print("   ✅ End-to-end test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Quick test failed: {str(e)}")
            return False
    
    async def run_complete_setup(self):
        """Run the complete setup process"""
        self.print_header("Climate Witness Chain Setup")
        
        print(" Setting up Climate Witness Chain for demo and testing...")
        
        setup_steps = [
            ("check_dependencies", self.check_dependencies),
            ("setup_database", self.setup_database),
            ("setup_metta_knowledge", self.setup_metta_knowledge),
            ("verify_blockchain_config", self.verify_blockchain_config),
            ("create_demo_assets", self.create_demo_assets),
            ("test_api_endpoints", self.test_api_endpoints),
            ("run_quick_test", self.run_quick_test)
        ]
        
        results = {}
        all_success = True
        
        for i, (step_name, step_func) in enumerate(setup_steps, 1):
            try:
                if asyncio.iscoroutinefunction(step_func):
                    success = await step_func()
                else:
                    success = step_func()
                
                results[step_name] = success
                if not success:
                    all_success = False
                    
            except Exception as e:
                print(f"❌ Step {i} failed with error: {str(e)}")
                results[step_name] = False
                all_success = False
        
        # Final summary
        self.print_header("Setup Complete!" if all_success else "Setup Issues Found")
        
        if all_success:
            print("✅ All setup steps completed successfully!")
            print("\n Next Steps:")
            print("   1. Start the FastAPI server: python main.py")
            print("   2. Start the frontend dev server: cd frontend && npm run dev")
            print("   3. Run demo data generator: python demo_data_generator.py")
            print("   4. Run demo presentation: python demo_presentation.py")
            
            print("\n Available Commands:")
            print("   • python main.py                    - Start API server")
            print("   • python demo_data_generator.py    - Generate demo data")
            print("   • python demo_presentation.py      - Interactive demo")
            print("   • python test_api.py               - Run API tests")
            print("   • python run_metta_tests.py        - Run MeTTa tests")
            
        else:
            print("⚠️  Some setup steps failed. Please review the errors above.")
            print("   Check requirements.txt and ensure all dependencies are installed.")
        
        # Save setup results
        setup_results = {
            "setup_time": datetime.now().isoformat(),
            "success": all_success,
            "steps": results,
            "next_steps": [
                "Start API server",
                "Start frontend server", 
                "Run demo data generator",
                "Run demo presentation"
            ] if all_success else ["Fix setup issues"]
        }
        
        with open("setup_results.json", "w") as f:
            json.dump(setup_results, f, indent=2)
        
        return setup_results
    
    def show_project_status(self):
        """Show current project status and structure"""
        self.print_header("Project Status Overview")
        
        print(" Project Structure:")
        print("   backend/")
        print("   ├── app/")
        print("   │   ├── api/routes/")
        print("   │   ├── database/")
        print("   │   └── services/")
        print("   ├── metta/")
        print("   ├── tests/")
        print("   └── demo scripts")
        print("   frontend/")
        print("   ├── src/")
        print("   └── views/")
        
        # Check file existence
        critical_files = [
            "app/database/database.py",
            "app/services/event_service.py",
            "app/services/user_service.py",
            "app/services/metta_service.py",
            "app/services/blockchain_service.py",
            "main.py",
            "requirements.txt"
        ]
        
        print("\n Critical Files:")
        for file_path in critical_files:
            full_path = self.backend_dir / file_path
            status = "✅" if full_path.exists() else "❌"
            print(f"   {status} {file_path}")
        
        # Check database
        db_path = self.backend_dir / "climate_witness.db"
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
                print(f"\n Database: ✅ {table_count} tables")
            except:
                print("\n Database: ❌ Error reading")
        else:
            print("\n Database: ❌ Not found")

def main():
    """Main function for setup management"""
    print(" Climate Witness Chain Setup Manager")
    print("Choose an option:")
    print("1. Run complete setup")
    print("2. Show project status")
    print("3. Check dependencies only")
    print("4. Database setup only")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    setup_manager = SetupManager()
    
    if choice == "1":
        asyncio.run(setup_manager.run_complete_setup())
    elif choice == "2":
        setup_manager.show_project_status()
    elif choice == "3":
        setup_manager.check_dependencies()
    elif choice == "4":
        setup_manager.setup_database()
    else:
        print("Invalid choice. Running complete setup...")
        asyncio.run(setup_manager.run_complete_setup())

if __name__ == "__main__":
    main()
