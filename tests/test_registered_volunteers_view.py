#!/usr/bin/env python3
"""
Unit tests for the registered_volunteers view functionality.

Tests the registered_volunteers view that shows all adults with BSA numbers
(registered volunteers) and their active roles.

Author: GitHub Copilot
Issue: #22
"""

import pytest
import sqlite3
import os
from pathlib import Path


class TestRegisteredVolunteersView:
    """Test the registered_volunteers view functionality."""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Create a test database with the adult roster schema."""
        db_path = tmp_path / "test_registered_volunteers.db"
        
        # Get the schema file path
        schema_path = Path(__file__).parent.parent / "database" / "create_adult_roster_schema.sql"
        
        # Create database and apply schema
        conn = sqlite3.connect(db_path)
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        
        yield conn
        conn.close()

    def test_registered_volunteers_view_exists(self, test_db):
        """Test that the registered_volunteers view exists."""
        cursor = test_db.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name='registered_volunteers'
        """)
        result = cursor.fetchone()
        assert result is not None, "registered_volunteers view should exist"
        assert result[0] == 'registered_volunteers'

    def test_registered_volunteers_with_positions(self, test_db):
        """Test registered volunteers who have current positions."""
        cursor = test_db.cursor()
        
        # Insert test data
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number) 
            VALUES ('John', 'Smith', 'john@example.com', 12345, '123')
        """)
        adult_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'Scoutmaster', '(2y)', 1)
        """, (adult_id,))
        
        test_db.commit()
        
        # Query the view
        cursor.execute("SELECT * FROM registered_volunteers WHERE bsa_number = 12345")
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == 'John'  # first_name
        assert result[1] == 'Smith'  # last_name
        assert result[2] == 12345  # bsa_number
        assert result[8] == 'Scoutmaster'  # position_title
        assert result[12] == 'Has Position'  # position_status

    def test_registered_volunteers_without_positions(self, test_db):
        """Test registered volunteers who have no current positions."""
        cursor = test_db.cursor()
        
        # Insert adult without positions
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number) 
            VALUES ('Jane', 'Doe', 'jane@example.com', 67890, '123')
        """)
        
        test_db.commit()
        
        # Query the view
        cursor.execute("SELECT * FROM registered_volunteers WHERE bsa_number = 67890")
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == 'Jane'  # first_name
        assert result[1] == 'Doe'  # last_name
        assert result[2] == 67890  # bsa_number
        assert result[8] is None  # position_title (should be None)
        assert result[12] == 'No Current Position'  # position_status

    def test_registered_volunteers_multiple_positions(self, test_db):
        """Test registered volunteers with multiple current positions."""
        cursor = test_db.cursor()
        
        # Insert adult with multiple positions
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number) 
            VALUES ('Bob', 'Johnson', 'bob@example.com', 11111, '123')
        """)
        adult_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'Committee Chair', '(1y)', 1)
        """, (adult_id,))
        
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'Merit Badge Counselor', '(6m)', 1)
        """, (adult_id,))
        
        test_db.commit()
        
        # Query the view - should return 2 rows for the same person
        cursor.execute("SELECT * FROM registered_volunteers WHERE bsa_number = 11111 ORDER BY position_title")
        results = cursor.fetchall()
        
        assert len(results) == 2
        assert results[0][0] == 'Bob'  # first_name
        assert results[0][8] == 'Committee Chair'  # first position
        assert results[1][8] == 'Merit Badge Counselor'  # second position
        assert all(result[12] == 'Has Position' for result in results)

    def test_registered_volunteers_excludes_inactive_positions(self, test_db):
        """Test that view only shows current positions, not inactive ones."""
        cursor = test_db.cursor()
        
        # Insert adult with both current and inactive positions
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number) 
            VALUES ('Alice', 'Brown', 'alice@example.com', 22222, '123')
        """)
        adult_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'Current Position', '(1y)', 1)
        """, (adult_id,))
        
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'Old Position', '(2y)', 0)
        """, (adult_id,))
        
        test_db.commit()
        
        # Query the view - should only show current position
        cursor.execute("SELECT * FROM registered_volunteers WHERE bsa_number = 22222")
        result = cursor.fetchone()
        
        assert result is not None
        assert result[8] == 'Current Position'  # only current position shown
        assert result[12] == 'Has Position'

    def test_registered_volunteers_excludes_adults_without_bsa_numbers(self, test_db):
        """Test that the database enforces BSA number requirement for adults."""
        cursor = test_db.cursor()
        
        # Attempt to insert adult without BSA number should fail
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO adults (first_name, last_name, email, unit_number) 
                VALUES ('No', 'BSA', 'nobsa@example.com', '123')
            """)

    def test_registered_volunteers_ordering(self, test_db):
        """Test that results are properly ordered by last name, first name, position title."""
        cursor = test_db.cursor()
        
        # Insert test data with specific ordering requirements
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number) 
            VALUES ('Zoe', 'Adams', 'zoe@example.com', 99999, '123')
        """)
        adult_id1 = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number) 
            VALUES ('Adam', 'Zulu', 'adam@example.com', 88888, '123')
        """)
        adult_id2 = cursor.lastrowid
        
        # Add positions
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'Z Position', '(1y)', 1)
        """, (adult_id1,))
        
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current) 
            VALUES (?, 'A Position', '(1y)', 1)
        """, (adult_id1,))
        
        test_db.commit()
        
        # Query the view
        cursor.execute("SELECT last_name, first_name, position_title FROM registered_volunteers ORDER BY last_name, first_name, position_title")
        results = cursor.fetchall()
        
        # Should be ordered: Adams (A Position), Adams (Z Position), Zulu
        assert len(results) >= 3
        adams_positions = [r for r in results if r[0] == 'Adams']
        assert len(adams_positions) == 2
        assert adams_positions[0][2] == 'A Position'  # A Position comes before Z Position
        assert adams_positions[1][2] == 'Z Position'