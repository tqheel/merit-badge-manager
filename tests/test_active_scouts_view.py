#!/usr/bin/env python3
"""
Unit tests for Active Scouts with Positions view functionality.
Tests to ensure the view is available and returns expected records.
"""

import pytest
import sqlite3
import os
import sys
from pathlib import Path

# Add the database directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))

@pytest.fixture
def db_connection():
    """Fixture to provide database connection for tests."""
    db_path = "database/merit_badge_manager.db"
    
    if not os.path.exists(db_path):
        pytest.skip(f"Database file does not exist: {db_path}")
    
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()

def test_active_scouts_view_exists(db_connection):
    """Test that the active_scouts_with_positions view exists."""
    cursor = db_connection.cursor()
    
    # Check if view exists in the database
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name='active_scouts_with_positions'
    """)
    
    result = cursor.fetchone()
    assert result is not None, "active_scouts_with_positions view does not exist"
    assert result[0] == 'active_scouts_with_positions'

def test_active_scouts_view_returns_records(db_connection):
    """Test that the active_scouts_with_positions view returns records."""
    cursor = db_connection.cursor()
    
    # Query the view
    cursor.execute("SELECT * FROM active_scouts_with_positions")
    records = cursor.fetchall()
    
    # Should have records (at least the test data we inserted)
    assert len(records) > 0, "active_scouts_with_positions view should return records"
    
    # Should have exactly 6 active scouts from our test data
    assert len(records) == 6, f"Expected 6 active scouts, got {len(records)}"

def test_active_scouts_view_structure(db_connection):
    """Test that the active_scouts_with_positions view has the expected columns."""
    cursor = db_connection.cursor()
    
    # Query to get column information
    cursor.execute("PRAGMA table_info(active_scouts_with_positions)")
    columns = cursor.fetchall()
    
    # Extract column names
    column_names = [col[1] for col in columns]
    
    # Expected columns based on the view definition
    expected_columns = [
        'first_name', 'last_name', 'bsa_number', 'rank', 
        'patrol_name', 'unit_number', 'activity_status', 
        'position_title', 'tenure_info'
    ]
    
    for expected_col in expected_columns:
        assert expected_col in column_names, f"Column '{expected_col}' missing from view"

def test_active_scouts_data_quality(db_connection):
    """Test that active scouts view data has expected quality."""
    cursor = db_connection.cursor()
    
    cursor.execute("SELECT first_name, last_name, bsa_number, activity_status FROM active_scouts_with_positions")
    records = cursor.fetchall()
    
    for record in records:
        first_name, last_name, bsa_number, activity_status = record
        
        # All records should have first and last names
        assert first_name and first_name.strip(), f"Scout has empty first name: {record}"
        assert last_name and last_name.strip(), f"Scout has empty last name: {record}"
        
        # All records should have BSA numbers
        assert bsa_number is not None, f"Scout has no BSA number: {record}"
        
        # All records should be Active (view filters for this)
        assert activity_status == 'Active', f"Scout not active in view: {record}"

def test_active_scouts_with_positions_scout_ids_available(db_connection):
    """Test that we can map scouts from the view back to scout IDs."""
    cursor = db_connection.cursor()
    
    # Get scouts from the view
    cursor.execute("""
        SELECT first_name, last_name, bsa_number 
        FROM active_scouts_with_positions 
        LIMIT 3
    """)
    view_scouts = cursor.fetchall()
    
    # For each scout in the view, verify we can find their ID in the scouts table
    for first_name, last_name, bsa_number in view_scouts:
        cursor.execute("""
            SELECT id FROM scouts 
            WHERE first_name = ? AND last_name = ? AND bsa_number = ? AND activity_status = 'Active'
        """, (first_name, last_name, bsa_number))
        
        scout_id_result = cursor.fetchone()
        assert scout_id_result is not None, f"Cannot find scout ID for {first_name} {last_name} (BSA: {bsa_number})"
        
        scout_id = scout_id_result[0]
        assert isinstance(scout_id, int), f"Scout ID should be integer, got {type(scout_id)}"
        assert scout_id > 0, f"Scout ID should be positive, got {scout_id}"

def test_scouts_table_has_active_scouts(db_connection):
    """Test that the underlying scouts table has active scouts."""
    cursor = db_connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scouts WHERE activity_status = 'Active'")
    active_count = cursor.fetchone()[0]
    
    assert active_count > 0, "No active scouts found in scouts table"
    assert active_count >= 6, f"Expected at least 6 active scouts, found {active_count}"

def test_active_scouts_for_ui_display(db_connection):
    """Test that scouts can be displayed in the UI format."""
    cursor = db_connection.cursor()
    
    # Simulate the query that the UI would use to get scout data for modal
    cursor.execute("""
        SELECT s.id, s.first_name, s.last_name, s.bsa_number
        FROM scouts s
        WHERE s.activity_status = 'Active'
    """)
    
    scouts = cursor.fetchall()
    assert len(scouts) > 0, "No scouts available for UI display"
    
    # Test that we can create the scout key mapping used by the UI
    scout_ids = {}
    for scout_id, first_name, last_name, bsa_number in scouts:
        scout_key = (first_name, last_name, bsa_number)
        scout_ids[scout_key] = scout_id
    
    assert len(scout_ids) > 0, "No scout ID mappings created"
    
    # Test a specific scout from our test data
    john_smith_key = ('John', 'Smith', 12345678)
    assert john_smith_key in scout_ids, "John Smith not found in scout mappings"
    assert scout_ids[john_smith_key] == 1, f"John Smith should have ID 1, got {scout_ids[john_smith_key]}"

def test_merit_badge_assignments_exist_for_scouts(db_connection):
    """Test that scouts have merit badge assignments for modal display."""
    cursor = db_connection.cursor()
    
    # Check if merit badge progress data exists
    cursor.execute("SELECT COUNT(*) FROM merit_badge_progress")
    mb_progress_count = cursor.fetchone()[0]
    
    assert mb_progress_count > 0, "No merit badge progress data found"
    
    # Test that at least some scouts have MBC assignments
    cursor.execute("""
        SELECT COUNT(DISTINCT scout_id) 
        FROM merit_badge_progress 
        WHERE scout_id IS NOT NULL
    """)
    scouts_with_mb = cursor.fetchone()[0]
    
    assert scouts_with_mb > 0, "No scouts have merit badge assignments"

if __name__ == "__main__":
    # Run the tests directly
    pytest.main([__file__, "-v"])