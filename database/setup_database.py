#!/usr/bin/env python3
"""
Merit Badge Manager - Database Schema Setup Script
Created: 2025-07-28
Updated: 2025-07-31
Purpose: Create and initialize the adult and youth roster database schemas

This script creates the SQLite database schema for storing adult and youth roster data
as specified in docs/create-db-schema-for-adult-roster.md and GitHub Issue #12
"""

import sqlite3
import sys
from pathlib import Path

def create_database_schema(db_path: str = "merit_badge_manager.db", include_youth: bool = True, include_mb_progress: bool = True):
    """
    Create the adult, youth roster, and merit badge progress database schemas.
    
    Args:
        db_path: Path to the SQLite database file
        include_youth: Whether to include youth schema tables
        include_mb_progress: Whether to include merit badge progress schema tables
    """
    
    # Get the SQL script paths
    script_dir = Path(__file__).parent
    adult_sql_file = script_dir / "create_adult_roster_schema.sql"
    youth_sql_file = script_dir / "youth_database_schema.sql"
    mb_progress_sql_file = script_dir / "merit_badge_progress_schema.sql"
    
    if not adult_sql_file.exists():
        raise FileNotFoundError(f"Adult SQL script not found: {adult_sql_file}")
    
    if include_youth and not youth_sql_file.exists():
        raise FileNotFoundError(f"Youth SQL script not found: {youth_sql_file}")
    
    if include_mb_progress and not mb_progress_sql_file.exists():
        raise FileNotFoundError(f"Merit Badge Progress SQL script not found: {mb_progress_sql_file}")
    
    # Read the SQL scripts
    with open(adult_sql_file, 'r') as f:
        adult_sql_script = f.read()
    
    youth_sql_script = ""
    if include_youth:
        with open(youth_sql_file, 'r') as f:
            youth_sql_script = f.read()
    
    mb_progress_sql_script = ""
    if include_mb_progress:
        with open(mb_progress_sql_file, 'r') as f:
            mb_progress_sql_script = f.read()
    
    try:
        # Connect to database (creates file if it doesn't exist)
        print(f"Creating database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Execute the adult schema creation script
        print("Executing adult roster schema creation script...")
        cursor.executescript(adult_sql_script)
        
        # Execute the youth schema creation script if requested
        if include_youth:
            print("Executing youth roster schema creation script...")
            cursor.executescript(youth_sql_script)
        
        # Execute the merit badge progress schema creation script if requested
        if include_mb_progress:
            print("Executing merit badge progress schema creation script...")
            cursor.executescript(mb_progress_sql_script)
        
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

def verify_schema(db_path: str, include_youth: bool = True, include_mb_progress: bool = True):
    """
    Verify the database schema is correctly created.
    
    Args:
        db_path: Path to the SQLite database file
        include_youth: Whether youth schema should be verified
        include_mb_progress: Whether merit badge progress schema should be verified
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verifying database schema: {db_path}")
        
        # Check foreign key constraints are enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"Foreign key constraints: {'✅ Enabled' if fk_status else '❌ Disabled'}")
        
        # Test basic queries on each adult table
        adult_test_queries = [
            ("adults", "SELECT COUNT(*) FROM adults"),
            ("adult_training", "SELECT COUNT(*) FROM adult_training"),
            ("adult_merit_badges", "SELECT COUNT(*) FROM adult_merit_badges"),
            ("adult_positions", "SELECT COUNT(*) FROM adult_positions")
        ]
        
        for table_name, query in adult_test_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"Table {table_name}: ✅ Accessible ({count} records)")
            except sqlite3.Error as e:
                print(f"Table {table_name}: ❌ Error - {e}")
        
        # Test basic queries on each youth table if included
        if include_youth:
            youth_test_queries = [
                ("scouts", "SELECT COUNT(*) FROM scouts"),
                ("scout_training", "SELECT COUNT(*) FROM scout_training"),
                ("scout_positions", "SELECT COUNT(*) FROM scout_positions"),
                ("parent_guardians", "SELECT COUNT(*) FROM parent_guardians"),
                ("scout_merit_badge_progress", "SELECT COUNT(*) FROM scout_merit_badge_progress"),
                ("scout_advancement_history", "SELECT COUNT(*) FROM scout_advancement_history")
            ]
            
            for table_name, query in youth_test_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    print(f"Table {table_name}: ✅ Accessible ({count} records)")
                except sqlite3.Error as e:
                    print(f"Table {table_name}: ❌ Error - {e}")
        
        # Test adult views
        adult_view_queries = [
            ("merit_badge_counselors", "SELECT COUNT(*) FROM merit_badge_counselors"),
            ("current_positions", "SELECT COUNT(*) FROM current_positions")
        ]
        
        for view_name, query in adult_view_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"View {view_name}: ✅ Accessible")
            except sqlite3.Error as e:
                print(f"View {view_name}: ❌ Error - {e}")
        
        # Test youth views if included
        if include_youth:
            youth_view_queries = [
                ("scouts_missing_data", "SELECT COUNT(*) FROM scouts_missing_data"),
                ("active_scouts_with_positions", "SELECT COUNT(*) FROM active_scouts_with_positions"),
                ("merit_badge_progress_summary", "SELECT COUNT(*) FROM merit_badge_progress_summary"),
                ("scouts_needing_counselors", "SELECT COUNT(*) FROM scouts_needing_counselors"),
                ("advancement_progress_by_rank", "SELECT COUNT(*) FROM advancement_progress_by_rank"),
                ("primary_parent_contacts", "SELECT COUNT(*) FROM primary_parent_contacts"),
                ("scout_training_expiration_summary", "SELECT COUNT(*) FROM scout_training_expiration_summary"),
                ("patrol_assignments", "SELECT COUNT(*) FROM patrol_assignments")
            ]
            
            for view_name, query in youth_view_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    print(f"View {view_name}: ✅ Accessible")
                except sqlite3.Error as e:
                    print(f"View {view_name}: ❌ Error - {e}")
        
        # Test merit badge progress tables if included
        if include_mb_progress:
            mb_progress_test_queries = [
                ("merit_badge_progress", "SELECT COUNT(*) FROM merit_badge_progress"),
                ("unmatched_mbc_names", "SELECT COUNT(*) FROM unmatched_mbc_names"),
                ("mbc_name_mappings", "SELECT COUNT(*) FROM mbc_name_mappings"),
                ("merit_badge_requirements", "SELECT COUNT(*) FROM merit_badge_requirements")
            ]
            
            for table_name, query in mb_progress_test_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    print(f"Table {table_name}: ✅ Accessible ({count} records)")
                except sqlite3.Error as e:
                    print(f"Table {table_name}: ❌ Error - {e}")
        
        # Test merit badge progress views if included
        if include_mb_progress:
            mb_progress_view_queries = [
                ("merit_badge_status_view", "SELECT COUNT(*) FROM merit_badge_status_view"),
                ("unmatched_mbc_assignments", "SELECT COUNT(*) FROM unmatched_mbc_assignments"),
                ("scouts_available_for_mbc_assignment", "SELECT COUNT(*) FROM scouts_available_for_mbc_assignment"),
                ("mb_progress_missing_data", "SELECT COUNT(*) FROM mb_progress_missing_data"),
                ("mb_progress_summary", "SELECT COUNT(*) FROM mb_progress_summary"),
                ("mb_requirements_summary", "SELECT COUNT(*) FROM mb_requirements_summary")
            ]
            
            for view_name, query in mb_progress_view_queries:
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
        description="Create Merit Badge Manager adult and youth roster database schemas"
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
    parser.add_argument(
        "--adults-only", "-a",
        action="store_true",
        help="Create only adult roster schema (exclude youth schema)"
    )
    parser.add_argument(
        "--no-mb-progress", 
        action="store_true",
        help="Exclude merit badge progress schema"
    )
    
    args = parser.parse_args()
    
    db_path = Path(args.database)
    include_youth = not args.adults_only
    include_mb_progress = not args.no_mb_progress
    
    # Check if database already exists
    if db_path.exists() and not args.force:
        print(f"⚠️  Database already exists: {db_path}")
        print("Use --force to recreate or choose a different filename")
        sys.exit(1)
    
    # Create the schema
    success = create_database_schema(str(db_path), include_youth, include_mb_progress)
    
    if not success:
        print("❌ Failed to create database schema")
        sys.exit(1)
    
    # Verify if requested
    if args.verify:
        verify_success = verify_schema(str(db_path), include_youth, include_mb_progress)
        if not verify_success:
            print("❌ Schema verification failed")
            sys.exit(1)
    
    print(f"\n🎉 Database setup completed successfully!")
    print(f"📁 Database: {db_path.absolute()}")
    schemas = ["Adult roster"]
    if include_youth:
        schemas.append("Youth roster")
    if include_mb_progress:
        schemas.append("Merit Badge Progress")
    print(f"📋 Schemas: {' + '.join(schemas)}")
    print("\n💡 Next steps:")
    print("1. Import adult roster CSV data")
    if include_youth:
        print("2. Import youth roster CSV data")
        if include_mb_progress:
            print("3. Import Merit Badge In-Progress Report CSV data")
            print("4. Verify data integrity using the validation views")
            print("5. Begin using the database for merit badge counselor assignments and Scout tracking")
        else:
            print("3. Verify data integrity using the validation views")
            print("4. Begin using the database for merit badge counselor assignments and Scout tracking")
    else:
        if include_mb_progress:
            print("2. Import Merit Badge In-Progress Report CSV data")
            print("3. Verify data integrity using the validation views")
            print("4. Begin using the database for merit badge counselor assignments")
        else:
            print("2. Verify data integrity using the validation views")
            print("3. Begin using the database for merit badge counselor assignments")

if __name__ == "__main__":
    main()
