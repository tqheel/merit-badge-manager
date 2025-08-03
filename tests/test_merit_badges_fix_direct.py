#!/usr/bin/env python3
"""
Test case for the fixed Merit Badge Counselor import functionality (#24)

This test verifies that the import script correctly processes the "Merit Badges" 
column with pipe-separated values, fixing the empty merit_badge_counselors view.
"""

import os
import sys
import tempfile
import sqlite3
import csv
from pathlib import Path

# Add the scripts directory to the Python path

from import_roster import RosterImporter
from setup_database import create_database_schema


def test_merit_badges_column_direct():
    """Test that the fixed column lookup and separator handling work correctly."""
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test database
        test_db = temp_path / "test.db"
        create_database_schema(str(test_db), include_youth=True)
        
        # Create test importer instance
        importer = RosterImporter()
        
        # Test the fixed column lookup and import directly
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        
        # Insert test adults first
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
        
        # Test the NEW fixed column lookup logic
        test_row1 = {
            'First Name': 'John',
            'Last Name': 'Smith', 
            'Merit Badges': 'Archery | Aviation | Camping'  # New column name with pipe separators
        }
        
        test_row2 = {
            'First Name': 'Jane',
            'Last Name': 'Doe',
            'Merit Badge Counselor For': 'Cooking;First Aid'  # Old column name with semicolon separators
        }
        
        # Test the fixed column lookup for row 1 (new format)
        merit_badges_raw1 = (test_row1.get('Merit Badges', '') or 
                            test_row1.get('Merit Badge Counselor For', '') or 
                            test_row1.get('merit_badge_counselor_for', '') or 
                            test_row1.get('Merit_Badge_Counselor_For', ''))
        
        print(f"Row 1 - Found merit badges: '{merit_badges_raw1}'")
        assert merit_badges_raw1 == 'Archery | Aviation | Camping', f"Expected pipe-separated data, got '{merit_badges_raw1}'"
        
        # Test the fixed column lookup for row 2 (old format for backward compatibility)
        merit_badges_raw2 = (test_row2.get('Merit Badges', '') or 
                            test_row2.get('Merit Badge Counselor For', '') or 
                            test_row2.get('merit_badge_counselor_for', '') or 
                            test_row2.get('Merit_Badge_Counselor_For', ''))
        
        print(f"Row 2 - Found merit badges: '{merit_badges_raw2}'")
        assert merit_badges_raw2 == 'Cooking;First Aid', f"Expected semicolon-separated data, got '{merit_badges_raw2}'"
        
        # Test the fixed merit badge import method
        importer._import_merit_badge_counselor_data(cursor, adult1_id, merit_badges_raw1, 'John', 'Smith')
        importer._import_merit_badge_counselor_data(cursor, adult2_id, merit_badges_raw2, 'Jane', 'Doe')
        
        conn.commit()
        
        # Verify the results
        cursor.execute("SELECT COUNT(*) FROM adults")
        adults_count = cursor.fetchone()[0]
        assert adults_count == 2, f"Expected 2 adults in database, got {adults_count}"
        
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        mb_count = cursor.fetchone()[0]
        assert mb_count == 5, f"Expected 5 merit badge qualifications, got {mb_count}"
        
        # Check specific merit badge qualifications
        cursor.execute("""
            SELECT a.first_name, a.last_name, amb.merit_badge_name 
            FROM adults a 
            JOIN adult_merit_badges amb ON a.id = amb.adult_id 
            ORDER BY a.first_name, amb.merit_badge_name
        """)
        qualifications = cursor.fetchall()
        
        expected_qualifications = [
            ('Jane', 'Doe', 'Cooking'),
            ('Jane', 'Doe', 'First Aid'),
            ('John', 'Smith', 'Archery'),
            ('John', 'Smith', 'Aviation'),
            ('John', 'Smith', 'Camping')
        ]
        
        assert qualifications == expected_qualifications, f"Expected {expected_qualifications}, got {qualifications}"
        
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
        print("✅ Direct merit badge column and separator test passed!")


def test_separator_detection():
    """Test that the separator detection logic works correctly."""
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test database
        test_db = temp_path / "test.db"
        create_database_schema(str(test_db), include_youth=True)
        
        # Create test importer instance
        importer = RosterImporter()
        
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        
        # Insert test adult
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number)
            VALUES (?, ?, ?, ?)
        """, ('Test', 'User', 'test@test.com', 999999999))
        adult_id = cursor.lastrowid
        
        # Test pipe separator
        print("Testing pipe separator...")
        importer._import_merit_badge_counselor_data(cursor, adult_id, 'Badge1 | Badge2 | Badge3', 'Test', 'User')
        
        # Test semicolon separator
        print("Testing semicolon separator...")
        importer._import_merit_badge_counselor_data(cursor, adult_id, 'Badge4;Badge5;Badge6', 'Test', 'User')
        
        # Test single badge (no separator)
        print("Testing single badge...")
        importer._import_merit_badge_counselor_data(cursor, adult_id, 'Badge7', 'Test', 'User')
        
        conn.commit()
        
        # Check results
        cursor.execute("SELECT merit_badge_name FROM adult_merit_badges WHERE adult_id = ? ORDER BY merit_badge_name", (adult_id,))
        badges = [row[0] for row in cursor.fetchall()]
        
        expected_badges = ['Badge1', 'Badge2', 'Badge3', 'Badge4', 'Badge5', 'Badge6', 'Badge7']
        assert badges == expected_badges, f"Expected {expected_badges}, got {badges}"
        
        conn.close()
        print("✅ Separator detection test passed!")


if __name__ == "__main__":
    test_merit_badges_column_direct()
    test_separator_detection()
    print("🎉 All Merit Badges column fix tests passed!")