#!/usr/bin/env python3
"""
Integration Tests for Merit Badge Progress Import
"""

import unittest
import tempfile
import os
import sqlite3
import csv

# Add the database-access directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database-access'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from import_mb_progress import MeritBadgeProgressImporter
from setup_database import create_database_schema
from test_data.mb_progress_test_data import SAMPLE_MB_PROGRESS_CSV, SAMPLE_ADULT_CSV, SAMPLE_YOUTH_CSV


class TestMeritBadgeProgressImport(unittest.TestCase):
    """Integration test cases for Merit Badge Progress import."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_db.db")
        
        # Create test database
        create_database_schema(self.db_path, include_youth=True, include_mb_progress=True)
        
        # Create test CSV files
        self.mb_progress_csv = os.path.join(self.temp_dir, "mb_progress.csv")
        with open(self.mb_progress_csv, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_MB_PROGRESS_CSV)
        
        self.adult_csv = os.path.join(self.temp_dir, "adults.csv")
        with open(self.adult_csv, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_ADULT_CSV)
        
        self.youth_csv = os.path.join(self.temp_dir, "youth.csv")
        with open(self.youth_csv, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_YOUTH_CSV)
        
        # Import test data
        self._import_test_adults()
        self._import_test_scouts()
        
        # Create importer
        self.importer = MeritBadgeProgressImporter(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _import_test_adults(self):
        """Import test adult data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        with open(self.adult_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO adults (bsa_number, first_name, last_name, email)
                    VALUES (?, ?, ?, ?)
                """, (
                    int(row['BSA Number']),
                    row['First Name'].strip('"'),
                    row['Last Name'].strip('"'),
                    row['Email'].strip('"')
                ))
        
        conn.commit()
        conn.close()
    
    def _import_test_scouts(self):
        """Import test scout data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        with open(self.youth_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO scouts (bsa_number, first_name, last_name, rank, patrol_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(row['BSA Number']),
                    row['First Name'].strip('"'),
                    row['Last Name'].strip('"'),
                    row['Rank'].strip('"'),
                    row['Patrol Name'].strip('"')
                ))
        
        conn.commit()
        conn.close()
    
    def test_full_import_process(self):
        """Test the complete import process."""
        # Run the import
        success = self.importer.import_csv(self.mb_progress_csv, auto_match_threshold=0.9)
        self.assertTrue(success)
        
        # Check import statistics
        stats = self.importer.get_import_summary()
        self.assertEqual(stats['total_records'], 5)  # 5 scouts in test data
        self.assertEqual(stats['imported_records'], 5)
        self.assertEqual(stats['skipped_records'], 0)
        
        # Verify data was imported
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check merit badge progress records
        cursor.execute("SELECT COUNT(*) FROM merit_badge_progress")
        progress_count = cursor.fetchone()[0]
        self.assertEqual(progress_count, 5)
        
        # Check specific record (John Smith)
        cursor.execute("""
            SELECT scout_first_name, scout_last_name, merit_badge_name, merit_badge_year
            FROM merit_badge_progress 
            WHERE scout_bsa_number = '12345678'
        """)
        john_record = cursor.fetchone()
        self.assertIsNotNone(john_record)
        self.assertEqual(john_record[0], "John")
        self.assertEqual(john_record[1], "Smith")
        self.assertEqual(john_record[2], "Fire Safety (2025)")
        self.assertEqual(john_record[3], "2025")
        
        conn.close()
    
    def test_mbc_matching(self):
        """Test MBC name matching functionality."""
        success = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success)
        
        stats = self.importer.get_import_summary()
        
        # Should have some exact or fuzzy matches
        total_matches = stats['mbc_exact_matches'] + stats['mbc_fuzzy_matches']
        self.assertGreater(total_matches, 0)
        
        # Check that some MBCs were matched
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM merit_badge_progress 
            WHERE mbc_adult_id IS NOT NULL
        """)
        matched_count = cursor.fetchone()[0]
        self.assertGreater(matched_count, 0)
        
        conn.close()
    
    def test_scout_matching(self):
        """Test Scout BSA number matching to youth roster."""
        success = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success)
        
        stats = self.importer.get_import_summary()
        
        # Should match most scouts (4 out of 5 are in youth roster)
        self.assertEqual(stats['scout_matches'], 4)
        self.assertEqual(stats['scout_unmatched'], 1)  # Charlie Davis not in youth roster
        
        # Verify scout_id is set for matched scouts
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM merit_badge_progress 
            WHERE scout_id IS NOT NULL
        """)
        scout_matched_count = cursor.fetchone()[0]
        self.assertEqual(scout_matched_count, 4)
        
        conn.close()
    
    def test_requirements_parsing(self):
        """Test that requirements are parsed and stored."""
        success = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success)
        
        # Check that requirements were parsed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM merit_badge_requirements")
        requirements_count = cursor.fetchone()[0]
        self.assertGreater(requirements_count, 0)
        
        # Check specific requirements for John Smith (Fire Safety)
        cursor.execute("""
            SELECT req.requirement_number, req.requirement_type
            FROM merit_badge_requirements req
            JOIN merit_badge_progress mbp ON req.progress_id = mbp.id
            WHERE mbp.scout_bsa_number = '12345678'
        """)
        john_requirements = cursor.fetchall()
        
        # Should have 4 requirements: 5, 5g, 10, 10a
        self.assertEqual(len(john_requirements), 4)
        
        requirement_numbers = [req[0] for req in john_requirements]
        self.assertIn('5', requirement_numbers)
        self.assertIn('5g', requirement_numbers)
        self.assertIn('10', requirement_numbers)
        self.assertIn('10a', requirement_numbers)
        
        conn.close()
    
    def test_choice_requirements_parsing(self):
        """Test that choice requirements are parsed correctly."""
        success = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success)
        
        # Check Bob Wilson's camping requirements which include choice
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT req.requirement_number, req.requirement_type, req.choice_group
            FROM merit_badge_requirements req
            JOIN merit_badge_progress mbp ON req.progress_id = mbp.id
            WHERE mbp.scout_bsa_number = '11111111'
        """)
        bob_requirements = cursor.fetchall()
        
        # Should have choice requirement
        choice_requirements = [req for req in bob_requirements if req[1] == 'choice']
        self.assertGreater(len(choice_requirements), 0)
        
        # Check choice group content
        choice_req = choice_requirements[0]
        self.assertIn('1 of 4a, 4b, 4c', choice_req[2])
        
        conn.close()
    
    def test_unmatched_mbc_storage(self):
        """Test that unmatched MBC names are stored for manual review."""
        success = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success)
        
        # Should have some unmatched MBC names
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM unmatched_mbc_names")
        unmatched_count = cursor.fetchone()[0]
        self.assertGreaterEqual(unmatched_count, 0)
        
        conn.close()
    
    def test_views_work_with_data(self):
        """Test that the database views work correctly with imported data."""
        success = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test merit_badge_status_view
        cursor.execute("SELECT COUNT(*) FROM merit_badge_status_view")
        status_view_count = cursor.fetchone()[0]
        self.assertEqual(status_view_count, 5)
        
        # Test scouts_available_for_mbc_assignment
        cursor.execute("SELECT COUNT(*) FROM scouts_available_for_mbc_assignment")
        available_count = cursor.fetchone()[0]
        self.assertGreaterEqual(available_count, 0)
        
        # Test mb_progress_summary
        cursor.execute("SELECT COUNT(*) FROM mb_progress_summary")
        summary_count = cursor.fetchone()[0]
        self.assertGreater(summary_count, 0)
        
        conn.close()
    
    def test_error_handling_invalid_csv(self):
        """Test error handling for invalid CSV files."""
        # Create invalid CSV
        invalid_csv = os.path.join(self.temp_dir, "invalid.csv")
        with open(invalid_csv, 'w') as f:
            f.write("Invalid CSV content\nwith no proper headers\n")
        
        success = self.importer.import_csv(invalid_csv)
        self.assertFalse(success)
        
        # Check that errors were recorded
        stats = self.importer.get_import_summary()
        self.assertGreater(len(stats['errors']), 0)
    
    def test_duplicate_handling(self):
        """Test that duplicate entries are handled correctly."""
        # Import once
        success1 = self.importer.import_csv(self.mb_progress_csv)
        self.assertTrue(success1)
        
        # Import again (should update existing records)
        importer2 = MeritBadgeProgressImporter(self.db_path)
        success2 = importer2.import_csv(self.mb_progress_csv)
        self.assertTrue(success2)
        
        # Should still have only 5 records
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM merit_badge_progress")
        progress_count = cursor.fetchone()[0]
        self.assertEqual(progress_count, 5)
        conn.close()


if __name__ == '__main__':
    unittest.main()