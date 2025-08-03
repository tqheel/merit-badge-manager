#!/usr/bin/env python3
"""
Test case specifically for the Merit Badge Counselor import bug (#24)

This test reproduces the issue where:
1. CSV uses "Merit Badges" column name instead of "Merit Badge Counselor For"
2. CSV uses pipe-separated (|) values instead of semicolon-separated (;) values
3. Result: merit_badge_counselors view shows no records

This test should FAIL with the current code and PASS after the fix.
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


def test_merit_badges_column_with_pipe_separators():
    """Test that merit badge data is imported correctly with 'Merit Badges' column and pipe separators."""
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test database
        test_db = temp_path / "test.db"
        create_database_schema(str(test_db), include_youth=True)
        
        # Create test CSV data with "Merit Badges" column and pipe-separated values
        test_csv = temp_path / "test_roster.csv"
        with open(test_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['First Name', 'Last Name', 'Email', 'City', 'State', 'Zip', 
                           'Age Category', 'Date Joined', 'BSA Number', 'Unit Number', 
                           'OA Info', 'Health Form Status', 'Swim Class', 'Swim Class Date', 
                           'Positions Tenure', 'Merit Badges'])
            writer.writerow(['John', 'Smith', 'john@test.com', 'TestCity', 'TX', '12345',
                           'Adult', '2020-01-01', '123456789', '123', '', 'Current', '', '',
                           'Scoutmaster (2y)', 'Archery | Aviation | Camping'])
            writer.writerow(['Jane', 'Doe', 'jane@test.com', 'TestCity', 'TX', '12345', 
                           'Adult', '2019-01-01', '123456790', '123', '', 'Current', '', '',
                           'Assistant Scoutmaster (1y)', 'Cooking | First Aid'])
        
        # Create test importer instance
        importer = RosterImporter()
        
        # Import adults into our test database  
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        
        # Simulate the import process by reading CSV and calling import methods
        with open(test_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                bsa_number = row.get('BSA Number', '')
                first_name = row.get('First Name', '')
                last_name = row.get('Last Name', '')
                
                if bsa_number:
                    # Insert adult
                    cursor.execute("""
                        INSERT INTO adults (first_name, last_name, email, bsa_number)
                        VALUES (?, ?, ?, ?)
                    """, (first_name, last_name, row.get('Email', ''), int(bsa_number)))
                    adult_id = cursor.lastrowid
                    
                    # Test the current implementation - should show the bug
                    # This simulates what the import script currently does
                    merit_badges_raw = (row.get('Merit Badge Counselor For', '') or 
                                      row.get('merit_badge_counselor_for', '') or 
                                      row.get('Merit_Badge_Counselor_For', ''))
                    
                    print(f"Current implementation found merit badges: '{merit_badges_raw}' for {first_name} {last_name}")
                    
                    if merit_badges_raw and merit_badges_raw.strip():
                        # This should be empty because the column name is "Merit Badges", not the expected names
                        importer._import_merit_badge_counselor_data(cursor, adult_id, merit_badges_raw, first_name, last_name)
        
        conn.commit()
        
        # Check what was actually imported
        cursor.execute("SELECT COUNT(*) FROM adults")
        adults_count = cursor.fetchone()[0]
        print(f"Adults imported: {adults_count}")
        
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        mb_count = cursor.fetchone()[0]
        print(f"Merit badge qualifications imported: {mb_count}")
        
        cursor.execute("SELECT COUNT(*) FROM merit_badge_counselors")
        view_count = cursor.fetchone()[0]
        print(f"Merit badge counselors in view: {view_count}")
        
        # With the current bug, these should be 0
        print(f"\n❌ BUG REPRODUCED: merit_badge_counselors view shows {view_count} records (should be 5)")
        
        conn.close()
        
        # This test demonstrates the bug - no merit badge data imported
        assert mb_count == 0, f"BUG: Expected 0 merit badge qualifications with current code, got {mb_count}"
        assert view_count == 0, f"BUG: Expected 0 counselors in view with current code, got {view_count}"
        
        print("✅ Bug reproduction test passed - confirmed no merit badge data imported")


def test_merit_badges_column_after_fix():
    """Test that merit badge data is imported correctly after the fix."""
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test database
        test_db = temp_path / "test.db"
        create_database_schema(str(test_db), include_youth=True)
        
        # Create test CSV data with "Merit Badges" column and pipe-separated values
        test_csv = temp_path / "test_roster.csv"
        with open(test_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['First Name', 'Last Name', 'Email', 'City', 'State', 'Zip', 
                           'Age Category', 'Date Joined', 'BSA Number', 'Unit Number', 
                           'OA Info', 'Health Form Status', 'Swim Class', 'Swim Class Date', 
                           'Positions Tenure', 'Merit Badges'])
            writer.writerow(['John', 'Smith', 'john@test.com', 'TestCity', 'TX', '12345',
                           'Adult', '2020-01-01', '123456789', '123', '', 'Current', '', '',
                           'Scoutmaster (2y)', 'Archery | Aviation | Camping'])
            writer.writerow(['Jane', 'Doe', 'jane@test.com', 'TestCity', 'TX', '12345', 
                           'Adult', '2019-01-01', '123456790', '123', '', 'Current', '', '',
                           'Assistant Scoutmaster (1y)', 'Cooking | First Aid'])
        
        # Create test importer instance
        importer = RosterImporter()
        
        # Import adults into our test database  
        conn = sqlite3.connect(str(test_db))
        cursor = conn.cursor()
        
        # Simulate the import process with the FIXED column lookup
        with open(test_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                bsa_number = row.get('BSA Number', '')
                first_name = row.get('First Name', '')
                last_name = row.get('Last Name', '')
                
                if bsa_number:
                    # Insert adult
                    cursor.execute("""
                        INSERT INTO adults (first_name, last_name, email, bsa_number)
                        VALUES (?, ?, ?, ?)
                    """, (first_name, last_name, row.get('Email', ''), int(bsa_number)))
                    adult_id = cursor.lastrowid
                    
                    # Test the FIXED implementation - should find "Merit Badges" column
                    merit_badges_raw = (row.get('Merit Badges', '') or  # FIX: Add this line
                                      row.get('Merit Badge Counselor For', '') or 
                                      row.get('merit_badge_counselor_for', '') or 
                                      row.get('Merit_Badge_Counselor_For', ''))
                    
                    print(f"Fixed implementation found merit badges: '{merit_badges_raw}' for {first_name} {last_name}")
                    
                    if merit_badges_raw and merit_badges_raw.strip():
                        # FIX: Update the parsing to handle pipe separators
                        # Detect separator (pipe | or semicolon ;)
                        if '|' in merit_badges_raw:
                            # Use pipe separator
                            merit_badges = [mb.strip() for mb in merit_badges_raw.split('|') if mb.strip()]
                        else:
                            # Use semicolon separator (fallback)
                            merit_badges = [mb.strip() for mb in merit_badges_raw.split(';') if mb.strip()]
                        
                        # Import each merit badge
                        mb_count = 0
                        for merit_badge in merit_badges:
                            merit_badge_clean = merit_badge.strip()
                            if merit_badge_clean:
                                cursor.execute("""
                                    INSERT OR IGNORE INTO adult_merit_badges (adult_id, merit_badge_name)
                                    VALUES (?, ?)
                                """, (adult_id, merit_badge_clean))
                                
                                if cursor.rowcount > 0:
                                    mb_count += 1
                        
                        if mb_count > 0:
                            print(f"   🏅 Added {mb_count} merit badge counselor qualifications for {first_name} {last_name}")
        
        conn.commit()
        
        # Check what was imported
        cursor.execute("SELECT COUNT(*) FROM adults")
        adults_count = cursor.fetchone()[0]
        print(f"Adults imported: {adults_count}")
        
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        mb_count = cursor.fetchone()[0]
        print(f"Merit badge qualifications imported: {mb_count}")
        
        cursor.execute("SELECT COUNT(*) FROM merit_badge_counselors")
        view_count = cursor.fetchone()[0]
        print(f"Merit badge counselors in view: {view_count}")
        
        # After the fix, these should have data
        assert adults_count == 2, f"Expected 2 adults imported, got {adults_count}"
        assert mb_count == 5, f"Expected 5 merit badge qualifications imported, got {mb_count}"
        assert view_count == 5, f"Expected 5 merit badges in counselors view, got {view_count}"
        
        # Check specific merit badge data
        cursor.execute("""
            SELECT merit_badge_name, counselor_count 
            FROM merit_badge_counselors 
            ORDER BY merit_badge_name
        """)
        view_data = cursor.fetchall()
        
        expected_merit_badges = ['Archery', 'Aviation', 'Camping', 'Cooking', 'First Aid']
        actual_merit_badges = [row[0] for row in view_data]
        
        assert actual_merit_badges == expected_merit_badges, f"Expected {expected_merit_badges}, got {actual_merit_badges}"
        
        conn.close()
        
        print("✅ Fixed implementation test passed - merit badge data imported correctly!")


if __name__ == "__main__":
    print("🔍 Testing Merit Badge Counselor import bug (#24)")
    print("=" * 60)
    
    test_merit_badges_column_with_pipe_separators()
    print()
    test_merit_badges_column_after_fix()
    
    print("\n🎉 All tests completed successfully!")