#!/usr/bin/env python3
"""
Tests for MBC Name Fuzzy Matching functionality
"""

import unittest
import tempfile
import os
import sqlite3

# Add the database-access directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database-access'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from mbc_name_matcher import MBCNameMatcher
from setup_database import create_database_schema


class TestMBCNameMatcher(unittest.TestCase):
    """Test cases for MBC name fuzzy matching."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_db.db")
        
        # Create test database
        create_database_schema(self.db_path, include_youth=True, include_mb_progress=True)
        
        # Insert test adult data
        self._insert_test_adults()
        
        # Create matcher
        self.matcher = MBCNameMatcher(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _insert_test_adults(self):
        """Insert test adult data into the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        test_adults = [
            (130001, "Michael", "Johnson", "mjohnson@example.com"),
            (130002, "Robert", "Smith", "rsmith@example.com"),
            (130003, "Sarah", "Wilson", "swilson@example.com"),
            (130004, "William", "Jones", "wjones@example.com"),
            (130005, "Susan", "Brown", "sbrown@example.com"),
            (130006, "Christopher", "Davis", "cdavis@example.com"),
            (130007, "Matthew", "Miller", "mmiller@example.com"),
            (130008, "Anthony", "Garcia", "agarcia@example.com"),
            (130009, "Steven", "Rodriguez", "srodriguez@example.com"),
            (130010, "Andrew", "Martinez", "amartinez@example.com")
        ]
        
        for bsa_number, first_name, last_name, email in test_adults:
            cursor.execute("""
                INSERT INTO adults (bsa_number, first_name, last_name, email)
                VALUES (?, ?, ?, ?)
            """, (bsa_number, first_name, last_name, email))
        
        conn.commit()
        conn.close()
    
    def test_exact_match(self):
        """Test exact name matching."""
        # Test exact full name match
        matches = self.matcher.find_matches("Michael Johnson")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], "Michael Johnson")
        self.assertEqual(matches[0]['confidence'], 1.0)
        self.assertEqual(matches[0]['match_type'], 'exact')
        
        # Test exact match with different order
        matches = self.matcher.find_matches("Johnson, Michael")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['confidence'], 1.0)
    
    def test_nickname_matching(self):
        """Test nickname-aware matching."""
        # Test Mike -> Michael
        matches = self.matcher.find_matches("Mike Johnson")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], "Michael Johnson")
        self.assertEqual(matches[0]['confidence'], 0.95)
        self.assertEqual(matches[0]['match_type'], 'nickname')
        
        # Test Bob -> Robert
        matches = self.matcher.find_matches("Bob Smith")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], "Robert Smith")
        self.assertEqual(matches[0]['confidence'], 0.95)
        
        # Test Chris -> Christopher
        matches = self.matcher.find_matches("Chris Davis")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], "Christopher Davis")
        self.assertEqual(matches[0]['confidence'], 0.95)
        
        # Test Steve -> Steven
        matches = self.matcher.find_matches("Steve Rodriguez")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['name'], "Steven Rodriguez")
        self.assertEqual(matches[0]['confidence'], 0.95)
    
    def test_fuzzy_matching(self):
        """Test fuzzy string matching."""
        # Test with minor spelling differences
        matches = self.matcher.find_matches("Micheal Johnson")  # Misspelled Michael
        self.assertGreater(len(matches), 0)
        best_match = matches[0]
        self.assertEqual(best_match['name'], "Michael Johnson")
        self.assertGreater(best_match['confidence'], 0.8)
        
        # Test with space differences
        matches = self.matcher.find_matches("Sarah  Wilson")  # Extra space
        self.assertGreater(len(matches), 0)
        best_match = matches[0]
        self.assertEqual(best_match['name'], "Sarah Wilson")
    
    def test_soundex_matching(self):
        """Test Soundex phonetic matching."""
        matcher = self.matcher
        
        # Test Soundex algorithm
        self.assertEqual(matcher._soundex("Smith"), matcher._soundex("Smyth"))
        self.assertEqual(matcher._soundex("Johnson"), matcher._soundex("Jonson"))
        
        # Test names that sound similar
        matches = self.matcher.find_matches("Smyth")  # Sounds like Smith
        # This might match if the whole name similarity is high enough
    
    def test_confidence_thresholds(self):
        """Test different confidence thresholds."""
        # High threshold should return fewer matches
        high_threshold_matches = self.matcher.find_matches("Mchael Johnson", min_confidence=0.9)
        
        # Lower threshold should return more matches
        low_threshold_matches = self.matcher.find_matches("Mchael Johnson", min_confidence=0.7)
        
        self.assertLessEqual(len(high_threshold_matches), len(low_threshold_matches))
    
    def test_no_matches(self):
        """Test handling of names with no matches."""
        matches = self.matcher.find_matches("Nonexistent Person")
        self.assertEqual(len(matches), 0)
        
        matches = self.matcher.find_matches("XYZ ABC")
        self.assertEqual(len(matches), 0)
    
    def test_empty_input(self):
        """Test handling of empty or invalid input."""
        matches = self.matcher.find_matches("")
        self.assertEqual(len(matches), 0)
        
        matches = self.matcher.find_matches(None)
        self.assertEqual(len(matches), 0)
        
        matches = self.matcher.find_matches("   ")
        self.assertEqual(len(matches), 0)
    
    def test_name_cleaning(self):
        """Test name cleaning functionality."""
        matcher = self.matcher
        
        # Test basic cleaning
        self.assertEqual(matcher._clean_name("  John   Smith  "), "john smith")
        
        # Test parentheses removal
        self.assertEqual(matcher._clean_name("Robert (Bob) Smith"), "robert smith")
        
        # Test prefix/suffix removal
        self.assertEqual(matcher._clean_name("Dr. John Smith Jr."), "john smith")
        self.assertEqual(matcher._clean_name("Mr. William Jones II"), "william jones")
    
    def test_store_unmatched_name(self):
        """Test storing unmatched names."""
        potential_matches = [
            {'adult_id': 1, 'name': 'Similar Name', 'confidence': 0.6, 'match_type': 'fuzzy'}
        ]
        
        # Store unmatched name
        unmatched_id = self.matcher.store_unmatched_name("Unknown Person", potential_matches)
        self.assertGreater(unmatched_id, 0)
        
        # Verify it was stored
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM unmatched_mbc_names WHERE id = ?", (unmatched_id,))
        record = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(record)
        self.assertEqual(record[1], "Unknown Person")  # mbc_name_raw
        self.assertEqual(record[2], 1)  # occurrence_count
    
    def test_store_mapping(self):
        """Test storing name mappings."""
        # Store a mapping
        success = self.matcher.store_mapping("Mike Johnson", 1, 0.95, "nickname")
        self.assertTrue(success)
        
        # Verify it was stored
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mbc_name_mappings WHERE raw_name = ?", ("Mike Johnson",))
        record = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(record)
        self.assertEqual(record[2], 1)  # adult_id
        self.assertEqual(record[3], 0.95)  # confidence_score
        self.assertEqual(record[4], "nickname")  # mapping_type
    
    def test_match_prioritization(self):
        """Test that matches are prioritized correctly."""
        matches = self.matcher.find_matches("Michael Johnson")
        
        # Should find exact match first
        if matches:
            self.assertEqual(matches[0]['match_type'], 'exact')
            self.assertEqual(matches[0]['confidence'], 1.0)
    
    def test_duplicate_removal(self):
        """Test that duplicate matches are removed."""
        matches = self.matcher.find_matches("Mike Johnson")
        
        # Should not have duplicate adult_ids
        adult_ids = [match['adult_id'] for match in matches]
        self.assertEqual(len(adult_ids), len(set(adult_ids)))
    
    def test_complex_name_formats(self):
        """Test matching with complex name formats."""
        # Test names with middle initials
        matches = self.matcher.find_matches("Michael J. Johnson")
        self.assertGreater(len(matches), 0)
        
        # Test names with nicknames in parentheses
        matches = self.matcher.find_matches("Robert (Bob) Smith")
        self.assertGreater(len(matches), 0)
        
        # Test names with titles
        matches = self.matcher.find_matches("Dr. Sarah Wilson")
        self.assertGreater(len(matches), 0)


if __name__ == '__main__':
    unittest.main()