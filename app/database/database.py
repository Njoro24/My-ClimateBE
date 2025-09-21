import aiosqlite
import os
from typing import AsyncGenerator
from .migrations import create_tables, seed_sample_data


DATABASE_URL = "sqlite:///./climate_witness.db"
DATABASE_PATH = "./climate_witness.db"

async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get database connection"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    """Initialize database with tables and sample data"""
    print(" Initializing Climate Witness Chain database...")
    
    # Create tables
    await create_tables(DATABASE_PATH)
    
    # Seed sample data for demo
    await seed_sample_data(DATABASE_PATH)
    
    print("✅ Database initialization complete!")

async def reset_db():
    """Reset database (useful for development)"""
    from .migrations import reset_database
    await reset_database(DATABASE_PATH)

# Updated migrations.py functions for your project
async def create_users_table(db_path: str):
    """Create users table with first_name and last_name columns"""
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                wallet_address TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create climate_reports table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS climate_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                location TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                description TEXT,
                evidence_link TEXT,
                latitude REAL,
                longitude REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create climate_alerts table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS climate_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create pattern_cache table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pattern_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        ''')
        
        await db.commit()
        print("✅ All tables created successfully!")

# Quick fix function to add missing columns to existing database
async def add_missing_columns():
    """Add first_name and last_name columns to existing users table"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            await db.execute('ALTER TABLE users ADD COLUMN first_name TEXT')
            await db.execute('ALTER TABLE users ADD COLUMN last_name TEXT')
            await db.commit()
            print("✅ Added missing columns to users table!")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✅ Columns already exist!")
            else:
                print(f"❌ Error adding columns: {e}")

# Helper function to check if columns exist
async def check_table_schema():
    """Check the current schema of users table"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = await cursor.fetchall()
        print("Current users table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")