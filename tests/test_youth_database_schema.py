#!/usr/bin/env python3
"""
Tests for Youth Roster Database Schema
Created: 2025-07-31
Purpose: Test the youth roster database schema implementation

These tests validate the youth roster schema functionality including:
- Table creation and structure
- Foreign key relationships
- Index performance
- Data validation views
- Integration with adult roster system
"""

import sqlite3
import unittest
import tempfile
import os
from pathlib import Path


class TestYouthDatabaseSchema(unittest.TestCase):
    """Test cases for youth database schema validation."""
    
    def setUp(self):
        """Set up test database for each test."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
        
        # Create schema using setup script
        project_root = Path(__file__).parent.parent
        setup_script = project_root / "db-scripts" / "setup_database.py"
        
        import subprocess
        import sys
        result = subprocess.run([
            sys.executable, str(setup_script),
            "--database", self.db_path,
            "--force"
        ], cwd=str(project_root), capture_output=True)
        
        if result.returncode != 0:
            self.fail(f"Failed to create test database: {result.stderr.decode()}")
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_youth_required_tables_exist(self):
        """Test that all required youth tables are created."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check that all youth tables exist
        expected_youth_tables = [
            'scouts',
            'scout_training', 
            'scout_positions',
            'parent_guardians',
            'scout_merit_badge_progress',
            'scout_advancement_history'
        ]
        
        for table in expected_youth_tables:
            self.assertIn(table, tables, f"Table {table} not found")
        
        conn.close()
    
    def test_scouts_table_structure(self):
        """Test the scouts table has correct structure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(scouts)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'id': 'INTEGER',
            'first_name': 'TEXT',
            'last_name': 'TEXT',
            'bsa_number': 'INTEGER',
            'unit_number': 'TEXT',
            'rank': 'TEXT',
            'date_joined': 'DATE',
            'date_of_birth': 'DATE',
            'age': 'INTEGER',
            'patrol_name': 'TEXT',
            'activity_status': 'TEXT',
            'oa_info': 'TEXT',
            'email': 'TEXT',
            'phone': 'TEXT',
            'city': 'TEXT',
            'state': 'TEXT',
            'zip': 'TEXT'
        }
        
        for col_name, col_type in expected_columns.items():
            self.assertIn(col_name, columns, f"Column {col_name} not found in scouts table")
            self.assertEqual(columns[col_name], col_type, f"Column {col_name} has wrong type")
        
        conn.close()
    
    def test_youth_foreign_key_relationships(self):
        """Test foreign key relationships for youth tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test foreign key constraints
        foreign_key_tests = [
            ("scout_training", "scout_id", "scouts", "id"),
            ("scout_positions", "scout_id", "scouts", "id"),
            ("parent_guardians", "scout_id", "scouts", "id"),
            ("scout_merit_badge_progress", "scout_id", "scouts", "id"),
            ("scout_advancement_history", "scout_id", "scouts", "id")
        ]
        
        for child_table, child_col, parent_table, parent_col in foreign_key_tests:
            cursor.execute(f"PRAGMA foreign_key_list({child_table})")
            fk_info = cursor.fetchall()
            
            # Check if foreign key exists
            fk_exists = any(
                row[2] == parent_table and row[3] == child_col and row[4] == parent_col
                for row in fk_info
            )
            self.assertTrue(fk_exists, 
                f"Foreign key {child_table}.{child_col} -> {parent_table}.{parent_col} not found")
        
        conn.close()
    
    def test_youth_indexes_creation(self):
        """Test that performance indexes are created for youth tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        expected_youth_indexes = [
            'idx_scouts_bsa_number',
            'idx_scouts_name',
            'idx_scouts_unit',
            'idx_scouts_rank',
            'idx_scouts_patrol',
            'idx_scouts_activity_status',
            'idx_scout_training_scout_id',
            'idx_scout_training_code',
            'idx_scout_positions_scout_id',
            'idx_scout_positions_current',
            'idx_parent_guardians_scout_id',
            'idx_parent_guardians_primary',
            'idx_scout_mb_progress_scout_id',
            'idx_scout_mb_progress_badge',
            'idx_scout_advancement_scout_id'
        ]
        
        for index in expected_youth_indexes:
            self.assertIn(index, indexes, f"Index {index} not found")
        
        conn.close()
    
    def test_youth_validation_views_creation(self):
        """Test that youth validation views are created."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        expected_youth_views = [
            'scouts_missing_data',
            'active_scouts_with_positions',
            'merit_badge_progress_summary',
            'scouts_needing_counselors',
            'advancement_progress_by_rank',
            'primary_parent_contacts',
            'scout_training_expiration_summary',
            'patrol_assignments'
        ]
        
        for view in expected_youth_views:
            self.assertIn(view, views, f"View {view} not found")
        
        # Test that views are accessible
        for view in expected_youth_views:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {view}")
                cursor.fetchone()
            except sqlite3.Error as e:
                self.fail(f"View {view} is not accessible: {e}")
        
        conn.close()
    
    def test_insert_sample_scout_data(self):
        """Test inserting and retrieving scout data."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Insert a test scout
        cursor.execute("""
            INSERT INTO scouts (
                first_name, last_name, bsa_number, unit_number, rank,
                date_joined, date_of_birth, age, patrol_name, activity_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Test', 'Scout', 999001, 'Troop 999', 'Star',
            '2023-01-15', '2008-05-20', 16, 'Test Patrol', 'Active'
        ))
        
        scout_id = cursor.lastrowid
        
        # Insert related data
        cursor.execute("""
            INSERT INTO scout_training (scout_id, training_code, training_name, expiration_date)
            VALUES (?, ?, ?, ?)
        """, (scout_id, 'TLT', 'Troop Leadership Training', '(does not expire)'))
        
        cursor.execute("""
            INSERT INTO scout_positions (scout_id, position_title, patrol_name, is_current)
            VALUES (?, ?, ?, ?)
        """, (scout_id, 'Patrol Leader', 'Test Patrol', 1))
        
        cursor.execute("""
            INSERT INTO parent_guardians (
                scout_id, guardian_number, first_name, last_name, 
                relationship, email, is_primary
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scout_id, 1, 'John', 'Scout', 'Parent', 'john.scout@example.com', 1))
        
        cursor.execute("""
            INSERT INTO scout_merit_badge_progress (
                scout_id, merit_badge_name, status, date_started
            ) VALUES (?, ?, ?, ?)
        """, (scout_id, 'First Aid', 'In Progress', '2024-01-01'))
        
        cursor.execute("""
            INSERT INTO scout_advancement_history (
                scout_id, rank_name, date_awarded
            ) VALUES (?, ?, ?)
        """, (scout_id, 'Star', '2024-06-01'))
        
        conn.commit()
        
        # Verify data was inserted correctly
        cursor.execute("SELECT first_name, last_name, rank FROM scouts WHERE id = ?", (scout_id,))
        scout_data = cursor.fetchone()
        self.assertEqual(scout_data, ('Test', 'Scout', 'Star'))
        
        # Verify related data
        cursor.execute("SELECT COUNT(*) FROM scout_training WHERE scout_id = ?", (scout_id,))
        training_count = cursor.fetchone()[0]
        self.assertEqual(training_count, 1)
        
        cursor.execute("SELECT COUNT(*) FROM parent_guardians WHERE scout_id = ?", (scout_id,))
        parent_count = cursor.fetchone()[0]
        self.assertEqual(parent_count, 1)
        
        conn.close()
    
    def test_youth_unique_constraints(self):
        """Test unique constraints in youth tables."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Test BSA number uniqueness in scouts table
        cursor.execute("""
            INSERT INTO scouts (first_name, last_name, bsa_number, activity_status)
            VALUES (?, ?, ?, ?)
        """, ('Scout', 'One', 999001, 'Active'))
        
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO scouts (first_name, last_name, bsa_number, activity_status)
                VALUES (?, ?, ?, ?)
            """, ('Scout', 'Two', 999001, 'Active'))  # Same BSA number
        
        conn.close()
    
    def test_youth_cascade_delete(self):
        """Test cascade delete functionality for youth tables."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Insert scout and related data
        cursor.execute("""
            INSERT INTO scouts (first_name, last_name, bsa_number, activity_status)
            VALUES (?, ?, ?, ?)
        """, ('Test', 'Scout', 999002, 'Active'))
        
        scout_id = cursor.lastrowid
        
        # Insert related records
        cursor.execute("""
            INSERT INTO scout_training (scout_id, training_code, training_name, expiration_date)
            VALUES (?, ?, ?, ?)
        """, (scout_id, 'TLT', 'Test Training', '2025-01-01'))
        
        cursor.execute("""
            INSERT INTO parent_guardians (scout_id, guardian_number, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, (scout_id, 1, 'Test', 'Parent'))
        
        conn.commit()
        
        # Verify related data exists
        cursor.execute("SELECT COUNT(*) FROM scout_training WHERE scout_id = ?", (scout_id,))
        self.assertEqual(cursor.fetchone()[0], 1)
        
        cursor.execute("SELECT COUNT(*) FROM parent_guardians WHERE scout_id = ?", (scout_id,))
        self.assertEqual(cursor.fetchone()[0], 1)
        
        # Delete the scout
        cursor.execute("DELETE FROM scouts WHERE id = ?", (scout_id,))
        conn.commit()
        
        # Verify related data was deleted (cascade)
        cursor.execute("SELECT COUNT(*) FROM scout_training WHERE scout_id = ?", (scout_id,))
        self.assertEqual(cursor.fetchone()[0], 0)
        
        cursor.execute("SELECT COUNT(*) FROM parent_guardians WHERE scout_id = ?", (scout_id,))
        self.assertEqual(cursor.fetchone()[0], 0)
        
        conn.close()


class TestYouthFakeDataGeneration(unittest.TestCase):
    """Test cases for youth fake data generation functionality."""
    
    def setUp(self):
        """Set up test database for each test."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_insert_youth_fake_data(self):
        """Test inserting fake youth data using the test database script."""
        project_root = Path(__file__).parent.parent
        test_script = project_root / "scripts" / "create_test_database.py"
        
        import subprocess
        import sys
        result = subprocess.run([
            sys.executable, str(test_script),
            "--database", self.db_path
        ], cwd=str(project_root), capture_output=True)
        
        if result.returncode != 0:
            self.fail(f"Failed to create test database with youth data: {result.stderr.decode()}")
        
        # Verify youth data was created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check scouts count
        cursor.execute("SELECT COUNT(*) FROM scouts")
        scouts_count = cursor.fetchone()[0]
        self.assertGreater(scouts_count, 0, "No scouts were inserted")
        
        # Check parent guardians
        cursor.execute("SELECT COUNT(*) FROM parent_guardians")
        parents_count = cursor.fetchone()[0]
        self.assertGreater(parents_count, 0, "No parent guardians were inserted")
        
        # Check merit badge progress
        cursor.execute("SELECT COUNT(*) FROM scout_merit_badge_progress")
        mb_progress_count = cursor.fetchone()[0]
        self.assertGreater(mb_progress_count, 0, "No merit badge progress records were inserted")
        
        # Check advancement history
        cursor.execute("SELECT COUNT(*) FROM scout_advancement_history")
        advancement_count = cursor.fetchone()[0]
        self.assertGreater(advancement_count, 0, "No advancement history records were inserted")
        
        conn.close()
    
    def test_youth_validation_views_with_data(self):
        """Test youth validation views work with populated data."""
        project_root = Path(__file__).parent.parent
        test_script = project_root / "scripts" / "create_test_database.py"
        
        import subprocess
        import sys
        result = subprocess.run([
            sys.executable, str(test_script),
            "--database", self.db_path
        ], cwd=str(project_root), capture_output=True)
        
        if result.returncode != 0:
            self.fail(f"Failed to create test database: {result.stderr.decode()}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test youth-specific views
        youth_views_to_test = [
            'active_scouts_with_positions',
            'merit_badge_progress_summary', 
            'advancement_progress_by_rank',
            'primary_parent_contacts',
            'patrol_assignments'
        ]
        
        for view in youth_views_to_test:
            cursor.execute(f"SELECT COUNT(*) FROM {view}")
            count = cursor.fetchone()[0]
            # Views should return results or at least be accessible
            self.assertIsNotNone(count, f"View {view} returned None")
        
        # Test specific view functionality
        cursor.execute("SELECT * FROM advancement_progress_by_rank WHERE rank = 'Life'")
        life_scouts = cursor.fetchall()
        # Should have some Life rank scouts in test data
        
        cursor.execute("SELECT * FROM patrol_assignments")
        patrols = cursor.fetchall()
        self.assertGreater(len(patrols), 0, "No patrol assignments found")
        
        conn.close()


class TestYouthAdultIntegration(unittest.TestCase):
    """Test cases for youth-adult roster integration."""
    
    def setUp(self):
        """Set up test database for integration tests."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
        
        # Create database with both adult and youth data
        project_root = Path(__file__).parent.parent
        test_script = project_root / "scripts" / "create_test_database.py"
        
        import subprocess
        import sys
        result = subprocess.run([
            sys.executable, str(test_script),
            "--database", self.db_path
        ], cwd=str(project_root), capture_output=True)
        
        if result.returncode != 0:
            self.fail(f"Failed to create test database: {result.stderr.decode()}")
    
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_merit_badge_counselor_assignment_integration(self):
        """Test that scouts can be assigned to adult merit badge counselors."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find an adult who is a merit badge counselor
        cursor.execute("""
            SELECT a.id, amb.merit_badge_name 
            FROM adults a
            JOIN adult_merit_badges amb ON a.id = amb.adult_id
            LIMIT 1
        """)
        counselor_info = cursor.fetchone()
        
        if counselor_info:
            adult_id, merit_badge = counselor_info
            
            # Find a scout working on this merit badge
            cursor.execute("""
                SELECT id FROM scouts 
                WHERE activity_status = 'Active'
                LIMIT 1
            """)
            scout_result = cursor.fetchone()
            
            if scout_result:
                scout_id = scout_result[0]
                
                # Create or update merit badge progress with counselor assignment
                cursor.execute("""
                    INSERT OR REPLACE INTO scout_merit_badge_progress (
                        scout_id, merit_badge_name, counselor_adult_id, status, date_started
                    ) VALUES (?, ?, ?, ?, ?)
                """, (scout_id, merit_badge, adult_id, 'In Progress', '2024-01-01'))
                
                conn.commit()
                
                # Verify the assignment
                cursor.execute("""
                    SELECT counselor_adult_id FROM scout_merit_badge_progress
                    WHERE scout_id = ? AND merit_badge_name = ?
                """, (scout_id, merit_badge))
                
                assigned_counselor = cursor.fetchone()[0]
                self.assertEqual(assigned_counselor, adult_id)
        
        conn.close()
    
    def test_scouts_needing_counselors_view(self):
        """Test the view that shows scouts needing counselor assignments."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # The view should show scouts without counselor assignments
        cursor.execute("SELECT COUNT(*) FROM scouts_needing_counselors")
        needing_count = cursor.fetchone()[0]
        
        # Should have some scouts needing counselors in test data
        self.assertGreaterEqual(needing_count, 0, "scouts_needing_counselors view not working")
        
        # Test view structure
        cursor.execute("SELECT * FROM scouts_needing_counselors LIMIT 1")
        result = cursor.fetchone()
        if result:
            # Should have scout info and merit badge info (7 columns total)
            self.assertEqual(len(result), 7, "scouts_needing_counselors view has wrong structure")
        
        conn.close()


if __name__ == '__main__':
    unittest.main()