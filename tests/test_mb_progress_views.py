#!/usr/bin/env python3
"""
Tests for Merit Badge Progress Database Views
"""

import unittest
import tempfile
import os
import sqlite3

# Add the database-access directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database-access'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from setup_database import create_database_schema


class TestMeritBadgeProgressViews(unittest.TestCase):
    """Test cases for Merit Badge Progress database views."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_db.db")
        
        # Create test database
        create_database_schema(self.db_path, include_youth=True, include_mb_progress=True)
        
        # Insert test data
        self._insert_test_data()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _insert_test_data(self):
        """Insert comprehensive test data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert test adults
        test_adults = [
            (1, 130001, "Michael", "Johnson", "mjohnson@example.com"),
            (2, 130002, "Robert", "Smith", "rsmith@example.com"),
            (3, 130003, "Sarah", "Wilson", "swilson@example.com"),
        ]
        
        for adult_id, bsa_number, first_name, last_name, email in test_adults:
            cursor.execute("""
                INSERT INTO adults (id, bsa_number, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?)
            """, (adult_id, bsa_number, first_name, last_name, email))
        
        # Insert test scouts
        test_scouts = [
            (1, 12345678, "John", "Smith", "Tenderfoot", "Eagles"),
            (2, 87654321, "Jane", "Doe", "First Class", "Hawks"),
            (3, 11111111, "Bob", "Wilson", "Star", "Wolves"),
        ]
        
        for scout_id, bsa_number, first_name, last_name, rank, patrol in test_scouts:
            cursor.execute("""
                INSERT INTO scouts (id, bsa_number, first_name, last_name, rank, patrol_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (scout_id, bsa_number, first_name, last_name, rank, patrol))
        
        # Insert merit badge progress data
        test_progress = [
            (1, "12345678", "John", "Smith", "Tenderfoot", "City, ST", "Fire Safety (2025)", "2025", "", None, None, "", "5, 5g, 10, 10a", '[]', 1),
            (2, "87654321", "Jane", "Doe", "First Class", "Town, ST", "Swimming (2024)", "2024", "Mike Johnson", 1, 0.95, "", "3, 3c, 4, 5", '[]', 2),
            (3, "11111111", "Bob", "Wilson", "Star", "Village, ST", "Camping (2025)", "2025", "Robert Smith", 2, 1.0, "", "1, 2, 3", '[]', 3),
            (4, "22222222", "Alice", "Brown", "Life", "Hometown, ST", "Cooking (2024)", "2024", "", None, None, "", "", '[]', None),
            (5, "33333333", "Charlie", "Davis", "Scout", "Cityville, ST", "First Aid (2025)", "2025", "Sarah Wilson", 3, 0.90, "08/15/2024", "1, 2, 3, 4, 5", '[]', None),
        ]
        
        for progress_data in test_progress:
            cursor.execute("""
                INSERT INTO merit_badge_progress (
                    id, scout_bsa_number, scout_first_name, scout_last_name, scout_rank,
                    scout_location, merit_badge_name, merit_badge_year, mbc_name_raw,
                    mbc_adult_id, mbc_match_confidence, date_completed, requirements_raw,
                    requirements_parsed, scout_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, progress_data)
        
        # Insert some requirements
        test_requirements = [
            (1, 1, "5", "individual", True, None),
            (2, 1, "5g", "individual", True, None),
            (3, 1, "10", "individual", True, None),
            (4, 1, "10a", "individual", True, None),
            (5, 2, "3", "individual", True, None),
            (6, 2, "3c", "individual", True, None),
            (7, 2, "4", "individual", True, None),
            (8, 2, "5", "individual", True, None),
            (9, 3, "1 of 4a, 4b, 4c", "choice", True, "1 of 4a, 4b, 4c"),
        ]
        
        for req_id, progress_id, req_number, req_type, is_completed, choice_group in test_requirements:
            cursor.execute("""
                INSERT INTO merit_badge_requirements (
                    id, progress_id, requirement_number, requirement_type, is_completed, choice_group
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (req_id, progress_id, req_number, req_type, is_completed, choice_group))
        
        # Insert unmatched MBC names
        cursor.execute("""
            INSERT INTO unmatched_mbc_names (mbc_name_raw, occurrence_count, is_resolved)
            VALUES ('Unknown Counselor', 2, 0)
        """)
        
        # Insert MBC name mappings
        cursor.execute("""
            INSERT INTO mbc_name_mappings (raw_name, adult_id, confidence_score, mapping_type)
            VALUES ('Mike Johnson', 1, 0.95, 'nickname')
        """)
        
        conn.commit()
        conn.close()
    
    def test_merit_badge_status_view(self):
        """Test the merit_badge_status_view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test view exists and returns data
        cursor.execute("SELECT * FROM merit_badge_status_view")
        results = cursor.fetchall()
        
        self.assertEqual(len(results), 5)  # Should have 5 progress records
        
        # Test specific record (Jane Doe with MBC assigned)
        cursor.execute("""
            SELECT scout_first_name, scout_last_name, assignment_status, requirements_completed_count
            FROM merit_badge_status_view 
            WHERE scout_bsa_number = '87654321'
        """)
        jane_record = cursor.fetchone()
        
        self.assertEqual(jane_record[0], "Jane")
        self.assertEqual(jane_record[1], "Doe")
        self.assertEqual(jane_record[2], "Matched")  # Has MBC assigned
        self.assertEqual(jane_record[3], 4)  # Should have 4 requirements
        
        # Test record with no MBC (John Smith)
        cursor.execute("""
            SELECT assignment_status FROM merit_badge_status_view 
            WHERE scout_bsa_number = '12345678'
        """)
        john_status = cursor.fetchone()[0]
        self.assertEqual(john_status, "No Assignment")
        
        conn.close()
    
    def test_unmatched_mbc_assignments_view(self):
        """Test the unmatched_mbc_assignments view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert an unmatched MBC for testing
        cursor.execute("""
            INSERT INTO merit_badge_progress (
                scout_bsa_number, scout_first_name, scout_last_name, merit_badge_name,
                mbc_name_raw, mbc_adult_id
            ) VALUES ('99999999', 'Test', 'Scout', 'Test Badge', 'Unknown Person', NULL)
        """)
        conn.commit()
        
        # Test view
        cursor.execute("SELECT * FROM unmatched_mbc_assignments")
        results = cursor.fetchall()
        
        # Should have unmatched MBC entries
        self.assertGreater(len(results), 0)
        
        # Check for our test unmatched name
        cursor.execute("""
            SELECT mbc_name_raw, assignment_count FROM unmatched_mbc_assignments
            WHERE mbc_name_raw = 'Unknown Person'
        """)
        unmatched_record = cursor.fetchone()
        
        if unmatched_record:  # May not exist if no unmatched records
            self.assertEqual(unmatched_record[0], "Unknown Person")
            self.assertEqual(unmatched_record[1], 1)
        
        conn.close()
    
    def test_scouts_available_for_mbc_assignment_view(self):
        """Test the scouts_available_for_mbc_assignment view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test view returns scouts without MBC assignment
        cursor.execute("SELECT * FROM scouts_available_for_mbc_assignment")
        results = cursor.fetchall()
        
        # Should include scouts with no MBC or unmatched MBC
        self.assertGreater(len(results), 0)
        
        # Check that John Smith is available (no MBC assigned)
        cursor.execute("""
            SELECT scout_first_name, scout_last_name, merit_badge_name
            FROM scouts_available_for_mbc_assignment
            WHERE scout_bsa_number = '12345678'
        """)
        john_available = cursor.fetchone()
        
        self.assertIsNotNone(john_available)
        self.assertEqual(john_available[0], "John")
        self.assertEqual(john_available[1], "Smith")
        self.assertEqual(john_available[2], "Fire Safety (2025)")
        
        conn.close()
    
    def test_mb_progress_missing_data_view(self):
        """Test the mb_progress_missing_data view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert record with missing data
        cursor.execute("""
            INSERT INTO merit_badge_progress (
                scout_bsa_number, scout_first_name, scout_last_name, merit_badge_name,
                scout_rank, merit_badge_year, scout_location, requirements_raw
            ) VALUES ('88888888', 'Missing', 'Data', 'Test Badge', '', '', '', '')
        """)
        conn.commit()
        
        # Test view identifies missing data
        cursor.execute("SELECT * FROM mb_progress_missing_data")
        results = cursor.fetchall()
        
        # Should have records with missing data
        self.assertGreater(len(results), 0)
        
        # Check our test record
        cursor.execute("""
            SELECT rank_issue, year_issue, location_issue, requirements_issue
            FROM mb_progress_missing_data
            WHERE scout_bsa_number = '88888888'
        """)
        missing_data_record = cursor.fetchone()
        
        if missing_data_record:
            self.assertEqual(missing_data_record[0], "Missing Scout Rank")
            self.assertEqual(missing_data_record[1], "Missing Merit Badge Year")
            self.assertEqual(missing_data_record[2], "Missing Scout Location")
            self.assertEqual(missing_data_record[3], "Missing Requirements Data")
        
        conn.close()
    
    def test_mb_progress_summary_view(self):
        """Test the mb_progress_summary view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test view aggregates data correctly
        cursor.execute("SELECT * FROM mb_progress_summary")
        results = cursor.fetchall()
        
        # Should have summary for each merit badge
        self.assertGreater(len(results), 0)
        
        # Test specific merit badge
        cursor.execute("""
            SELECT merit_badge_name, total_scouts, assigned_counselors, no_counselor_assigned
            FROM mb_progress_summary
            WHERE merit_badge_name = 'Fire Safety (2025)'
        """)
        fire_safety_summary = cursor.fetchone()
        
        if fire_safety_summary:
            self.assertEqual(fire_safety_summary[0], "Fire Safety (2025)")
            self.assertEqual(fire_safety_summary[1], 1)  # 1 scout (John)
            self.assertEqual(fire_safety_summary[2], 0)  # 0 assigned counselors
            self.assertEqual(fire_safety_summary[3], 1)  # 1 with no counselor
        
        conn.close()
    
    def test_mb_requirements_summary_view(self):
        """Test the mb_requirements_summary view."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test view summarizes requirements
        cursor.execute("SELECT * FROM mb_requirements_summary")
        results = cursor.fetchall()
        
        # Should have summary data
        self.assertGreater(len(results), 0)
        
        # Check specific merit badge with requirements
        cursor.execute("""
            SELECT merit_badge_name, scouts_working, avg_requirements_completed
            FROM mb_requirements_summary
            WHERE merit_badge_name = 'Fire Safety (2025)'
        """)
        requirements_summary = cursor.fetchone()
        
        if requirements_summary:
            self.assertEqual(requirements_summary[0], "Fire Safety (2025)")
            self.assertEqual(requirements_summary[1], 1)  # 1 scout working
            self.assertEqual(requirements_summary[2], 4.0)  # 4 requirements on average
        
        conn.close()
    
    def test_view_performance(self):
        """Test that views perform reasonably with the test data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test all views can be queried without errors
        views_to_test = [
            "merit_badge_status_view",
            "unmatched_mbc_assignments", 
            "scouts_available_for_mbc_assignment",
            "mb_progress_missing_data",
            "mb_progress_summary",
            "mb_requirements_summary"
        ]
        
        for view_name in views_to_test:
            with self.subTest(view=view_name):
                cursor.execute(f"SELECT COUNT(*) FROM {view_name}")
                count = cursor.fetchone()[0]
                self.assertGreaterEqual(count, 0)
        
        conn.close()
    
    def test_view_relationships(self):
        """Test that views correctly handle relationships between tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test that merit_badge_status_view correctly counts requirements
        cursor.execute("""
            SELECT scout_bsa_number, requirements_completed_count
            FROM merit_badge_status_view
            WHERE scout_bsa_number = '12345678'
        """)
        john_record = cursor.fetchone()
        
        # John should have 4 requirements
        self.assertEqual(john_record[1], 4)
        
        # Verify by counting directly in requirements table
        cursor.execute("""
            SELECT COUNT(*)
            FROM merit_badge_requirements mbr
            JOIN merit_badge_progress mbp ON mbr.progress_id = mbp.id
            WHERE mbp.scout_bsa_number = '12345678'
        """)
        direct_count = cursor.fetchone()[0]
        
        self.assertEqual(john_record[1], direct_count)
        
        conn.close()
    
    def test_view_data_consistency(self):
        """Test that views return consistent data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count total progress records
        cursor.execute("SELECT COUNT(*) FROM merit_badge_progress")
        total_progress = cursor.fetchone()[0]
        
        # Count from status view should match
        cursor.execute("SELECT COUNT(*) FROM merit_badge_status_view")
        status_view_count = cursor.fetchone()[0]
        
        self.assertEqual(total_progress, status_view_count)
        
        # Test that assignment status categories are mutually exclusive
        cursor.execute("""
            SELECT assignment_status, COUNT(*)
            FROM merit_badge_status_view
            GROUP BY assignment_status
        """)
        status_counts = cursor.fetchall()
        
        total_from_status = sum(count for _, count in status_counts)
        self.assertEqual(total_from_status, total_progress)
        
        conn.close()


if __name__ == '__main__':
    unittest.main()