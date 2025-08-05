#!/usr/bin/env python3
"""
Direct database test to verify Active Scouts view
"""

import sqlite3
import os
from pathlib import Path

def test_active_scouts_view():
    """Test the active scouts view directly"""
    
    db_path = "database/merit_badge_manager.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file does not exist: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test the view query
        cursor.execute("SELECT * FROM active_scouts_with_positions")
        rows = cursor.fetchall()
        
        print(f"✅ Active Scouts with Positions view returned {len(rows)} records")
        print("\nRecords:")
        for i, row in enumerate(rows, 1):
            print(f"  {i}. {row}")
        
        # Test individual components
        cursor.execute("SELECT COUNT(*) FROM scouts WHERE activity_status = 'Active'")
        active_count = cursor.fetchone()[0]
        print(f"\n📊 Active scouts in scouts table: {active_count}")
        
        # Test scout details
        cursor.execute("SELECT id, first_name, last_name, bsa_number, rank FROM scouts WHERE activity_status = 'Active' LIMIT 3")
        scout_details = cursor.fetchall()
        print(f"\n👤 Sample scout details:")
        for scout in scout_details:
            print(f"  ID: {scout[0]}, Name: {scout[1]} {scout[2]}, BSA: {scout[3]}, Rank: {scout[4]}")
        
        return len(rows) > 0
        
    except Exception as e:
        print(f"❌ Error testing view: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_active_scouts_view()
    exit(0 if success else 1)