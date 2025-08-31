"""
Database utility functions for UI testing.

This module provides database utilities specifically for UI tests,
ensuring test isolation and proper database path management.
"""

import sys
from pathlib import Path
import sqlite3

# Add parent directories to path so we can import from web-ui and database
sys.path.insert(0, str(Path(__file__).parent.parent / "web-ui"))
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))

def get_test_database_path() -> Path:
    """Get the path for a test-specific database."""
    return Path(__file__).parent.parent / "database" / "merit_badge_manager.db"

def get_isolated_test_database_path() -> Path:
    """Get the path for an isolated test database (for tests that need clean state)."""
    return Path(__file__).parent / "test_merit_badge_manager.db"

def get_test_database_connection(isolated=False):
    """Get SQLite database connection for testing.
    
    Args:
        isolated: If True, use isolated test database instead of main database
    """
    if isolated:
        db_path = get_isolated_test_database_path()
    else:
        db_path = get_test_database_path()
    
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def create_isolated_test_database():
    """Create an isolated test database with schema."""
    try:
        from database.setup_database import create_database_schema
        db_path = get_isolated_test_database_path()
        
        # Remove existing test database
        if db_path.exists():
            db_path.unlink()
            
        # Create new test database
        create_database_schema(str(db_path), include_youth=True)
        return True
    except Exception as e:
        print(f"Error creating isolated test database: {e}")
        return False

def cleanup_isolated_test_database():
    """Clean up isolated test database."""
    db_path = get_isolated_test_database_path()
    if db_path.exists():
        db_path.unlink()

def test_database_exists(isolated=False) -> bool:
    """Check if the test database file exists."""
    if isolated:
        return get_isolated_test_database_path().exists()
    else:
        return get_test_database_path().exists()