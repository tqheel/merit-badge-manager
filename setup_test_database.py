#!/usr/bin/env python3
"""
Setup test database with sample data for Active Scouts view testing.
This script creates the database schema and populates it with test data.
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add the database directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "database"))
sys.path.insert(0, str(Path(__file__).parent / "tests" / "test_data"))

from setup_database import create_database_schema
import mb_progress_test_data

def create_test_database(db_path: str = "database/merit_badge_manager.db"):
    """Create the database with test data."""
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create the database schema
    print(f"Creating database schema at: {db_path}")
    create_database_schema(db_path, include_youth=True, include_mb_progress=True)
    
    # Connect to the database and populate with test data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Insert test adult roster data
        print("Inserting test adult data...")
        adult_data = [
            (130001, 'Michael', 'Johnson', 'mjohnson@example.com', 'Austin', 'TX', '78701', 'Adult'),
            (130002, 'Robert', 'Smith', 'rsmith@example.com', 'Austin', 'TX', '78702', 'Adult'),
            (130003, 'Sarah', 'Wilson', 'swilson@example.com', 'Austin', 'TX', '78703', 'Adult'),
            (130004, 'William', 'Jones', 'wjones@example.com', 'Austin', 'TX', '78704', 'Adult'),
            (130005, 'Susan', 'Brown', 'sbrown@example.com', 'Austin', 'TX', '78705', 'Adult'),
            (130006, 'Bob', 'Wilson', 'bwilson@example.com', 'Austin', 'TX', '78706', 'Adult')
        ]
        
        cursor.executemany("""
            INSERT INTO adults (bsa_number, first_name, last_name, email, city, state, zip, age_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, adult_data)
        
        # Insert merit badge counselor data
        print("Inserting merit badge counselor data...")
        mbc_data = [
            (1, 'Swimming'),
            (1, 'Lifesaving'),
            (1, 'Water Sports'),
            (2, 'Fire Safety'),
            (2, 'Emergency Preparedness'),
            (2, 'Safety'),
            (3, 'First Aid'),
            (3, 'Medicine'),
            (3, 'Health Care Professions'),
            (4, 'Camping'),
            (4, 'Backpacking'),
            (4, 'Hiking'),
            (5, 'Cooking'),
            (5, 'Nutrition'),
            (5, 'Food Science'),
            (6, 'Cooking')
        ]
        
        cursor.executemany("""
            INSERT INTO adult_merit_badges (adult_id, merit_badge_name)
            VALUES (?, ?)
        """, mbc_data)
        
        # Insert test youth roster data
        print("Inserting test youth data...")
        youth_data = [
            (12345678, 'John', 'Smith', 'Tenderfoot', 'Eagles', 'Active', '2023-09-01', '2008-05-15', 123),
            (87654321, 'Jane', 'Doe', 'First Class', 'Hawks', 'Active', '2023-09-01', '2008-03-22', 123),
            (11111111, 'Bob', 'Wilson', 'Star', 'Wolves', 'Active', '2023-09-01', '2008-07-10', 123),
            (22222222, 'Alice', 'Brown', 'Life', 'Eagles', 'Active', '2023-09-01', '2008-11-05', 123),
            (33333333, 'Charlie', 'Davis', 'Scout', 'Hawks', 'Active', '2023-09-01', '2008-01-18', 123),
            (99999999, 'David', 'Miller', 'Second Class', 'Eagles', 'Active', '2023-09-01', '2008-09-30', 123),
            (55555555, 'Sarah', 'Brown', 'Tenderfoot', 'Hawks', 'Inactive', '2023-09-01', '2008-12-12', 123)
        ]
        
        cursor.executemany("""
            INSERT INTO scouts (bsa_number, first_name, last_name, rank, patrol_name, activity_status, date_joined, date_of_birth, unit_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, youth_data)
        
        # Add some scout positions
        print("Inserting scout positions...")
        position_data = [
            (1, 'Senior Patrol Leader', 'Current position', 1),  # John Smith
            (2, 'Patrol Leader', 'Eagles Patrol Leader', 1),    # Jane Doe
            (3, 'Assistant Senior Patrol Leader', 'Current position', 1),  # Bob Wilson
            (4, 'Scribe', 'Current position', 1),               # Alice Brown
        ]
        
        cursor.executemany("""
            INSERT INTO scout_positions (scout_id, position_title, tenure_info, is_current)
            VALUES (?, ?, ?, ?)
        """, position_data)
        
        # Insert merit badge progress data
        print("Inserting merit badge progress data...")
        mb_progress_data = [
            ('12345678', 'John', 'Smith', 'Tenderfoot', 'Fire Safety', '2025', 'Robert Smith', 2, 0.95, '', '5, 5g, 10, 10a', 1),
            ('87654321', 'Jane', 'Doe', 'First Class', 'Swimming', '2024', 'Michael Johnson', 1, 0.95, '', '3, 3c, 4, 4a, 5, 5b, 7, 7a, 7b', 2),
            ('11111111', 'Bob', 'Wilson', 'Star', 'Camping', '2025', 'William Jones', 4, 0.95, '', '1, 2, 2a, 3', 3),
            ('22222222', 'Alice', 'Brown', 'Life', 'Cooking', '2024', 'Susan Brown', 5, 0.95, '', 'No Requirements Complete', 4),
            ('33333333', 'Charlie', 'Davis', 'Scout', 'First Aid', '2025', 'Sarah Wilson', 3, 0.95, '08/15/2024', '1, 2, 3, 4, 5, 6, 7, 8, 9, 10', 5),
            ('11111111', 'Bob', 'Wilson', 'Star', 'Cooking', '2024', 'Bob Wilson', 6, 0.95, '', '1, 2, 3a, 4', 3),
        ]
        
        cursor.executemany("""
            INSERT INTO merit_badge_progress (scout_bsa_number, scout_first_name, scout_last_name, scout_rank, merit_badge_name, merit_badge_year, mbc_name_raw, mbc_adult_id, mbc_match_confidence, date_completed, requirements_raw, scout_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, mb_progress_data)
        
        conn.commit()
        print("Test data inserted successfully!")
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM scouts WHERE activity_status = 'Active'")
        active_scouts = cursor.fetchone()[0]
        print(f"Active scouts in database: {active_scouts}")
        
        cursor.execute("SELECT COUNT(*) FROM active_scouts_with_positions")
        view_records = cursor.fetchone()[0]
        print(f"Records in active_scouts_with_positions view: {view_records}")
        
        # Show sample records from the view
        cursor.execute("SELECT first_name, last_name, rank, patrol_name, position_title FROM active_scouts_with_positions LIMIT 5")
        records = cursor.fetchall()
        print("Sample records from active_scouts_with_positions view:")
        for record in records:
            print(f"  {record[0]} {record[1]} - {record[2]} ({record[3]}) - {record[4] or 'No Position'}")
        
    except Exception as e:
        print(f"Error inserting test data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print(f"Test database setup complete: {db_path}")

if __name__ == "__main__":
    create_test_database()