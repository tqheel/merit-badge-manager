"""
Unit tests for scout position parsing functionality.

Tests the position parsing logic added to address GitHub Issue #52:
Bug: Scout Position Data Not Parsed During Roster Import
"""

import unittest
import tempfile
import os
import sqlite3
from pathlib import Path

# Import the position parsing functionality
from roster_parser import RosterParser
from import_roster import RosterImporter


class TestScoutPositionParsing(unittest.TestCase):
    """Test the scout position parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = RosterParser("dummy.csv", "dummy_output")
    
    def test_parse_simple_position(self):
        """Test parsing a simple position like 'Webmaster (5m 9d)'."""
        positions = self.parser.parse_scout_positions("Webmaster (5m 9d)")
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['position_title'], "Webmaster")
        self.assertEqual(positions[0]['patrol_name'], "")
        self.assertEqual(positions[0]['tenure_info'], "(5m 9d)")
    
    def test_parse_position_with_patrol(self):
        """Test parsing position with patrol name like 'Patrol Leader [ Anonymous Message] Patrol (5m 9d)'."""
        positions = self.parser.parse_scout_positions("Patrol Leader [ Anonymous Message] Patrol (5m 9d)")
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['position_title'], "Patrol Leader")
        self.assertEqual(positions[0]['patrol_name'], "Anonymous Message")
        self.assertEqual(positions[0]['tenure_info'], "(5m 9d)")
    
    def test_parse_assistant_patrol_leader(self):
        """Test parsing assistant patrol leader position."""
        positions = self.parser.parse_scout_positions("Assistant Patrol Leader [ Anonymous Message] Patrol (5m 9d)")
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['position_title'], "Assistant Patrol Leader")
        self.assertEqual(positions[0]['patrol_name'], "Anonymous Message")
        self.assertEqual(positions[0]['tenure_info'], "(5m 9d)")
    
    def test_parse_multiple_positions(self):
        """Test parsing multiple positions separated by pipes."""
        positions_raw = "Senior Patrol Leader (2y 3m) | Scribe [Dragon Fruit Patrol] (11m 3d)"
        positions = self.parser.parse_scout_positions(positions_raw)
        
        self.assertEqual(len(positions), 2)
        
        # First position
        self.assertEqual(positions[0]['position_title'], "Senior Patrol Leader")
        self.assertEqual(positions[0]['patrol_name'], "")
        self.assertEqual(positions[0]['tenure_info'], "(2y 3m)")
        
        # Second position
        self.assertEqual(positions[1]['position_title'], "Scribe")
        self.assertEqual(positions[1]['patrol_name'], "Dragon Fruit Patrol")
        self.assertEqual(positions[1]['tenure_info'], "(11m 3d)")
    
    def test_filter_non_leadership_positions(self):
        """Test that non-leadership positions are filtered out."""
        # This should be filtered out as it's basic patrol membership, not leadership
        positions = self.parser.parse_scout_positions("Scouts BSA [ 2025 Inactive and Aged Out] Patrol (5m 24d)")
        
        self.assertEqual(len(positions), 0, "Non-leadership positions should be filtered out")
    
    def test_empty_position_data(self):
        """Test handling of empty or None position data."""
        self.assertEqual(self.parser.parse_scout_positions(""), [])
        self.assertEqual(self.parser.parse_scout_positions("   "), [])
        self.assertEqual(self.parser.parse_scout_positions(None), [])
    
    def test_position_with_no_tenure(self):
        """Test parsing position with no tenure information."""
        positions = self.parser.parse_scout_positions("Webmaster")
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['position_title'], "Webmaster")
        self.assertEqual(positions[0]['patrol_name'], "")
        self.assertEqual(positions[0]['tenure_info'], "")
    
    def test_real_examples_from_test_data(self):
        """Test parsing with real examples from test data."""
        test_cases = [
            ("Patrol Leader (6m)", "Patrol Leader", "", "(6m)"),
            ("Assistant Patrol Leader (1y)", "Assistant Patrol Leader", "", "(1y)"),
            ("Senior Patrol Leader (2y 3m)", "Senior Patrol Leader", "", "(2y 3m)"),
        ]
        
        for position_raw, expected_title, expected_patrol, expected_tenure in test_cases:
            with self.subTest(position_raw=position_raw):
                positions = self.parser.parse_scout_positions(position_raw)
                self.assertEqual(len(positions), 1)
                self.assertEqual(positions[0]['position_title'], expected_title)
                self.assertEqual(positions[0]['patrol_name'], expected_patrol)
                self.assertEqual(positions[0]['tenure_info'], expected_tenure)

    def test_leadership_position_identification(self):
        """Test the logic for identifying leadership positions."""
        # Leadership positions - should return True
        leadership_positions = [
            "Patrol Leader",
            "Assistant Patrol Leader", 
            "Senior Patrol Leader",
            "Scribe",
            "Historian",
            "Librarian",
            "Webmaster",
            "Quartermaster",
            "Bugler",
            "Chaplain Aide",
            "Den Chief",
            "Instructor",
            "Troop Guide",
            "OA Representative",
            "Junior Assistant Scoutmaster"
        ]
        
        for position in leadership_positions:
            with self.subTest(position=position):
                self.assertTrue(self.parser._is_leadership_position(position), 
                              f"{position} should be identified as a leadership position")
        
        # Non-leadership positions - should return False
        non_leadership_positions = [
            "Scouts BSA",
            "Scout", 
            "Member",
            "Patrol Member"
        ]
        
        for position in non_leadership_positions:
            with self.subTest(position=position):
                self.assertFalse(self.parser._is_leadership_position(position),
                               f"{position} should NOT be identified as a leadership position")


class TestScoutPositionImport(unittest.TestCase):
    """Test the integration of position parsing with the roster import."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # Create a test database with scout_positions table
        self._create_test_database()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def _create_test_database(self):
        """Create a minimal test database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create scouts table
        cursor.execute("""
            CREATE TABLE scouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                bsa_number INTEGER UNIQUE NOT NULL,
                positions_tenure TEXT
            )
        """)
        
        # Create scout_positions table
        cursor.execute("""
            CREATE TABLE scout_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scout_id INTEGER NOT NULL,
                position_title TEXT NOT NULL,
                patrol_name TEXT,
                tenure_info TEXT,
                is_current BOOLEAN DEFAULT 1,
                FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def test_import_scout_positions_integration(self):
        """Test the integration of position parsing with database import."""
        # Insert a test scout
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scouts (first_name, last_name, bsa_number, positions_tenure)
            VALUES (?, ?, ?, ?)
        """, ("Test", "Scout", 12345678, "Patrol Leader (6m) | Scribe [Eagles Patrol] (1y)"))
        
        scout_id = cursor.lastrowid
        
        # Create importer and test position import
        importer = RosterImporter(ui_mode=True)  # UI mode to avoid interactive prompts
        
        # Test the position import method
        importer._import_scout_positions(
            cursor, 
            scout_id, 
            "Patrol Leader (6m) | Scribe [Eagles Patrol] (1y)",
            "Test", 
            "Scout"
        )
        
        conn.commit()
        
        # Verify positions were imported
        cursor.execute("""
            SELECT position_title, patrol_name, tenure_info, is_current 
            FROM scout_positions 
            WHERE scout_id = ?
            ORDER BY position_title
        """, (scout_id,))
        
        positions = cursor.fetchall()
        
        self.assertEqual(len(positions), 2, "Should have imported 2 positions")
        
        # Check first position (Patrol Leader)
        self.assertEqual(positions[0][0], "Patrol Leader")
        self.assertIsNone(positions[0][1], "No patrol name for this position should be None")  # patrol_name can be None
        self.assertEqual(positions[0][2], "(6m)")
        self.assertEqual(positions[0][3], 1)  # is_current should be True
        
        # Check second position (Scribe)
        self.assertEqual(positions[1][0], "Scribe")
        self.assertEqual(positions[1][1], "Eagles Patrol")
        self.assertEqual(positions[1][2], "(1y)")
        self.assertEqual(positions[1][3], 1)  # is_current should be True
        
        conn.close()


if __name__ == '__main__':
    unittest.main()