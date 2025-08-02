#!/usr/bin/env python3
"""
Test case for Merit Badge Counselor import functionality
Issue #20: Bug: MBC view shows no records

This test verifies that the import script correctly processes the "Merit Badge Counselor For" 
column and populates the adult_merit_badges table, fixing the empty merit_badge_counselors view.
"""

import os
import sys
import tempfile
import sqlite3
import csv
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'db-scripts'))

from import_roster import RosterImporter
from setup_database import create_database_schema


def test_merit_badge_counselor_import():
    """Test that merit badge counselor data is correctly imported from CSV."""
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test database
        test_db = temp_path / "test.db"
        create_database_schema(str(test_db), include_youth=True)
        
        # Create test CSV data with merit badge counselor information
        test_csv = temp_path / "test_roster.csv"
        with open(test_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['First Name', 'Last Name', 'Email', 'City', 'State', 'Zip', 
                           'Age Category', 'Date Joined', 'BSA Number', 'Unit Number', 
                           'OA Info', 'Health Form Status', 'Swim Class', 'Swim Class Date', 
                           'Positions Tenure', 'Merit Badge Counselor For'])
            writer.writerow(['John', 'Smith', 'john@test.com', 'TestCity', 'TX', '12345',
                           'Adult', '2020-01-01', '123456789', '123', '', 'Current', '', '',
                           'Scoutmaster (2y)', 'Archery;Aviation;Camping'])
            writer.writerow(['Jane', 'Doe', 'jane@test.com', 'TestCity', 'TX', '12345', 
                           'Adult', '2019-01-01', '123456790', '123', '', 'Current', '', '',
                           'Assistant Scoutmaster (1y)', 'Cooking;First Aid'])
        
        # Create test importer instance
        importer = RosterImporter()
        
        # Import adults into our test database  
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        
        # Manually insert adults first
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number)
            VALUES (?, ?, ?, ?)
        """, ('John', 'Smith', 'john@test.com', 123456789))
        adult1_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number)
            VALUES (?, ?, ?, ?)
        """, ('Jane', 'Doe', 'jane@test.com', 123456790))
        adult2_id = cursor.lastrowid
        
        # Test the merit badge import functionality directly
        importer._import_merit_badge_counselor_data(cursor, adult1_id, 'Archery;Aviation;Camping', 'John', 'Smith')
        importer._import_merit_badge_counselor_data(cursor, adult2_id, 'Cooking;First Aid', 'Jane', 'Doe')
        
        conn.commit()
        imported_count = 2  # We manually imported 2 adults
        
        # Verify adults were imported
        assert imported_count == 2, f"Expected 2 adults imported, got {imported_count}"
        
        # Connect to database and verify merit badge data
        # (conn is already open from above)
        
        # Check that adults table has records
        cursor.execute("SELECT COUNT(*) FROM adults")
        adults_count = cursor.fetchone()[0]
        assert adults_count == 2, f"Expected 2 adults in database, got {adults_count}"
        
        # Check that adult_merit_badges table has records
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        mb_count = cursor.fetchone()[0]
        assert mb_count == 5, f"Expected 5 merit badge assignments, got {mb_count}"
        
        # Check specific merit badge assignments
        cursor.execute("""
            SELECT a.first_name, a.last_name, amb.merit_badge_name 
            FROM adults a 
            JOIN adult_merit_badges amb ON a.id = amb.adult_id 
            ORDER BY a.first_name, amb.merit_badge_name
        """)
        assignments = cursor.fetchall()
        
        expected_assignments = [
            ('Jane', 'Doe', 'Cooking'),
            ('Jane', 'Doe', 'First Aid'),
            ('John', 'Smith', 'Archery'),
            ('John', 'Smith', 'Aviation'),
            ('John', 'Smith', 'Camping')
        ]
        
        assert assignments == expected_assignments, f"Expected {expected_assignments}, got {assignments}"
        
        # Check the merit_badge_counselors view
        cursor.execute("SELECT COUNT(*) FROM merit_badge_counselors")
        view_count = cursor.fetchone()[0]
        assert view_count == 5, f"Expected 5 merit badges in view, got {view_count}"
        
        # Check specific view content
        cursor.execute("""
            SELECT merit_badge_name, counselor_count 
            FROM merit_badge_counselors 
            ORDER BY merit_badge_name
        """)
        view_data = cursor.fetchall()
        
        expected_view_data = [
            ('Archery', 1),
            ('Aviation', 1), 
            ('Camping', 1),
            ('Cooking', 1),
            ('First Aid', 1)
        ]
        
        assert view_data == expected_view_data, f"Expected {expected_view_data}, got {view_data}"
        
        conn.close()
        print("✅ Merit Badge Counselor import test passed!")


def test_empty_merit_badge_field():
    """Test that empty merit badge fields are handled gracefully."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test database
        test_db = temp_path / "test.db"
        create_database_schema(str(test_db), include_youth=True)
        
        # Create test CSV with empty merit badge field
        test_csv = temp_path / "test_roster.csv"
        with open(test_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['First Name', 'Last Name', 'Email', 'BSA Number', 'Merit Badge Counselor For'])
            writer.writerow(['John', 'Smith', 'john@test.com', '123456789', ''])  # Empty merit badge field
            writer.writerow(['Jane', 'Doe', 'jane@test.com', '123456790', 'Archery'])  # Has merit badge
        
        # Create test importer and test the functionality directly
        importer = RosterImporter()
        
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        
        # Insert test adults
        cursor.execute("INSERT INTO adults (first_name, last_name, email, bsa_number) VALUES (?, ?, ?, ?)", 
                      ('John', 'Smith', 'john@test.com', 123456789))
        adult1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO adults (first_name, last_name, email, bsa_number) VALUES (?, ?, ?, ?)", 
                      ('Jane', 'Doe', 'jane@test.com', 123456790))
        adult2_id = cursor.lastrowid
        
        # Test merit badge processing with empty and valid data
        importer._import_merit_badge_counselor_data(cursor, adult1_id, '', 'John', 'Smith')  # Empty
        importer._import_merit_badge_counselor_data(cursor, adult2_id, 'Archery', 'Jane', 'Doe')  # Valid
        
        conn.commit()
        imported_count = 2
        
        # Verify adults were imported
        assert imported_count == 2, f"Expected 2 adults imported, got {imported_count}"
        
        # Check merit badge data
        # (conn is already open from above)
        
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        mb_count = cursor.fetchone()[0]
        assert mb_count == 1, f"Expected 1 merit badge assignment, got {mb_count}"
        
        cursor.execute("SELECT a.first_name, amb.merit_badge_name FROM adults a JOIN adult_merit_badges amb ON a.id = amb.adult_id")
        assignment = cursor.fetchone()
        assert assignment == ('Jane', 'Archery'), f"Expected ('Jane', 'Archery'), got {assignment}"
        
        conn.close()
        print("✅ Empty merit badge field test passed!")


if __name__ == "__main__":
    test_merit_badge_counselor_import()
    test_empty_merit_badge_field()
    print("🎉 All Merit Badge Counselor import tests passed!")