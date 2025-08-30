"""
Database utility functions for the Merit Badge Manager web UI.

This module provides centralized database path management to ensure
all web UI components use the same database location.
"""

from pathlib import Path
import sqlite3
import streamlit as st

def get_database_path() -> Path:
    """Get the path to the Merit Badge Manager database."""
    return Path(__file__).parent.parent / "database" / "merit_badge_manager.db"

def get_database_connection():
    """Get SQLite database connection."""
    db_path = get_database_path()
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def database_exists() -> bool:
    """Check if the database file exists."""
    return get_database_path().exists()
