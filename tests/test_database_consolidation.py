"""
Test database consolidation and centralized database path management.

This test validates that:
1. Only one database file exists in the correct location
2. Database utilities work correctly
3. All components access the same database
4. No hardcoded database paths in web UI components

Issue: #46
"""

import unittest
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

class TestDatabaseConsolidation(unittest.TestCase):
    """Test database consolidation compliance."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        
        # Add web-ui to path for testing
        sys.path.insert(0, str(self.project_root / "web-ui"))
        
    def test_single_database_location(self):
        """Test that only one database file exists in the correct location."""
        expected_db_path = self.project_root / "database" / "merit_badge_manager.db"
        
        # Check that the database exists in the correct location
        self.assertTrue(expected_db_path.exists(), 
                       f"Database should exist at {expected_db_path}")
        
        # Check that no database files exist in old locations
        old_locations = [
            self.project_root / "merit_badge_manager.db",
            self.project_root / "web-ui" / "merit_badge_manager.db"
        ]
        
        for old_path in old_locations:
            self.assertFalse(old_path.exists(), 
                           f"Database should NOT exist at old location: {old_path}")
    
    def test_database_utilities_import(self):
        """Test that database utilities can be imported and work correctly."""
        try:
            from database_utils import get_database_path, get_database_connection, database_exists
        except ImportError as e:
            self.fail(f"Failed to import database utilities: {e}")
        
        # Test get_database_path returns correct path
        db_path = get_database_path()
        expected_path = self.project_root / "database" / "merit_badge_manager.db"
        self.assertEqual(str(db_path), str(expected_path))
        
        # Test database_exists function
        self.assertTrue(database_exists(), "database_exists() should return True")
        
        # Test get_database_connection
        conn = get_database_connection()
        self.assertIsNotNone(conn, "get_database_connection() should return a connection")
        if conn:
            conn.close()
    
    def test_database_has_expected_data(self):
        """Test that the consolidated database contains the expected data."""
        from database_utils import get_database_connection
        
        conn = get_database_connection()
        self.assertIsNotNone(conn, "Should be able to connect to database")
        
        try:
            cursor = conn.cursor()
            
            # Check that adults_missing_data view exists and has some data
            cursor.execute("SELECT COUNT(*) FROM adults_missing_data")
            missing_adults_count = cursor.fetchone()[0]
            self.assertGreaterEqual(missing_adults_count, 0, 
                           "adults_missing_data should be accessible (could have 0 or more records)")
            
            # Check that main tables have data
            cursor.execute("SELECT COUNT(*) FROM adults")
            adults_count = cursor.fetchone()[0]
            self.assertGreater(adults_count, 0, "adults table should have records")
            
            cursor.execute("SELECT COUNT(*) FROM scouts")
            scouts_count = cursor.fetchone()[0]
            self.assertGreater(scouts_count, 0, "scouts table should have records")
            
            cursor.execute("SELECT COUNT(*) FROM merit_badge_progress")
            mb_progress_count = cursor.fetchone()[0]
            self.assertGreater(mb_progress_count, 0, "merit_badge_progress table should have records")
            
        finally:
            conn.close()
    
    def test_no_hardcoded_paths_in_web_ui(self):
        """Test that web UI components don't have hardcoded database paths."""
        web_ui_pages = [
            self.project_root / "web-ui" / "pages" / "1_Settings.py",
            self.project_root / "web-ui" / "pages" / "2_CSV_Import.py", 
            self.project_root / "web-ui" / "pages" / "3_Database_Views.py",
            self.project_root / "web-ui" / "pages" / "4_Manual_MBC_Matching.py"
        ]
        
        for page_file in web_ui_pages:
            if page_file.exists():
                with open(page_file, 'r') as f:
                    content = f.read()
                    
                # Check for hardcoded database references (excluding comments and the centralized utility)
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and the database_utils.py file itself
                    if line.strip().startswith('#') or 'database_utils.py' in str(page_file):
                        continue
                        
                    # Check for hardcoded database paths
                    if '"merit_badge_manager.db"' in line and 'database_utils.py' not in line:
                        self.fail(f"Found hardcoded database path in {page_file}:{line_num}: {line.strip()}")
    
    def test_database_utilities_prevent_hardcoding(self):
        """Test that using database utilities prevents hardcoded paths."""
        from database_utils import get_database_path, get_database_connection, database_exists
        
        # Test that functions return proper types
        self.assertIsInstance(get_database_path(), Path)
        self.assertIsInstance(database_exists(), bool)
        
        # Test that connection uses the centralized path
        conn = get_database_connection()
        if conn:
            # Verify we can query the database
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Should be able to query tables from centralized database")
            conn.close()

if __name__ == '__main__':
    unittest.main()
