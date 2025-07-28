#!/usr/bin/env python3
"""
Merit Badge Manager - Database Schema Setup Script
Created: 2025-07-28
Purpose: Create and initialize the adult roster database schema

This script creates the SQLite database schema for storing adult roster data
as specified in docs/create-db-schema-for-adult-roster.md
"""

import sqlite3
import sys
from pathlib import Path

def create_database_schema(db_path: str = "merit_badge_manager.db"):
    """
    Create the adult roster database schema.
    
    Args:
        db_path: Path to the SQLite database file
    """
    
    # Get the SQL script path
    script_dir = Path(__file__).parent
    sql_file = script_dir / "create_adult_roster_schema.sql"
    
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL script not found: {sql_file}")
    
    # Read the SQL script
    with open(sql_file, 'r') as f:
        sql_script = f.read()
    
    try:
        # Connect to database (creates file if it doesn't exist)
        print(f"Creating database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Execute the schema creation script
        print("Executing schema creation script...")
        cursor.executescript(sql_script)
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print(f"\n✅ Database schema created successfully!")
        print(f"📁 Database file: {db_path}")
        print(f"📋 Tables created: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verify indexes were created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        indexes = cursor.fetchall()
        
        print(f"🔍 Indexes created: {len(indexes)}")
        for index in indexes:
            print(f"   - {index[0]}")
        
        # Verify views were created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        views = cursor.fetchall()
        
        print(f"👁️  Views created: {len(views)}")
        for view in views:
            print(f"   - {view[0]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_schema(db_path: str):
    """
    Verify the database schema is correctly created.
    
    Args:
        db_path: Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verifying database schema: {db_path}")
        
        # Check foreign key constraints are enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"Foreign key constraints: {'✅ Enabled' if fk_status else '❌ Disabled'}")
        
        # Test basic queries on each table
        test_queries = [
            ("adults", "SELECT COUNT(*) FROM adults"),
            ("adult_training", "SELECT COUNT(*) FROM adult_training"),
            ("adult_merit_badges", "SELECT COUNT(*) FROM adult_merit_badges"),
            ("adult_positions", "SELECT COUNT(*) FROM adult_positions")
        ]
        
        for table_name, query in test_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"Table {table_name}: ✅ Accessible (0 records)")
            except sqlite3.Error as e:
                print(f"Table {table_name}: ❌ Error - {e}")
        
        # Test views
        view_queries = [
            ("adults_missing_data", "SELECT COUNT(*) FROM adults_missing_data"),
            ("training_expiration_summary", "SELECT COUNT(*) FROM training_expiration_summary"),
            ("merit_badge_counselors", "SELECT COUNT(*) FROM merit_badge_counselors"),
            ("current_positions", "SELECT COUNT(*) FROM current_positions")
        ]
        
        for view_name, query in view_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"View {view_name}: ✅ Accessible")
            except sqlite3.Error as e:
                print(f"View {view_name}: ❌ Error - {e}")
        
        print("✅ Schema verification completed!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during verification: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during verification: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Main function to handle command line arguments and run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create Merit Badge Manager adult roster database schema"
    )
    parser.add_argument(
        "--database", "-d",
        default="merit_badge_manager.db",
        help="Database file path (default: merit_badge_manager.db)"
    )
    parser.add_argument(
        "--verify", "-v",
        action="store_true",
        help="Verify schema after creation"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force recreation even if database exists"
    )
    
    args = parser.parse_args()
    
    db_path = Path(args.database)
    
    # Check if database already exists
    if db_path.exists() and not args.force:
        print(f"⚠️  Database already exists: {db_path}")
        print("Use --force to recreate or choose a different filename")
        sys.exit(1)
    
    # Create the schema
    success = create_database_schema(str(db_path))
    
    if not success:
        print("❌ Failed to create database schema")
        sys.exit(1)
    
    # Verify if requested
    if args.verify:
        verify_success = verify_schema(str(db_path))
        if not verify_success:
            print("❌ Schema verification failed")
            sys.exit(1)
    
    print(f"\n🎉 Database setup completed successfully!")
    print(f"📁 Database: {db_path.absolute()}")
    print("\n💡 Next steps:")
    print("1. Import adult roster CSV data")
    print("2. Verify data integrity using the validation views")
    print("3. Begin using the database for merit badge counselor assignments")

if __name__ == "__main__":
    main()
