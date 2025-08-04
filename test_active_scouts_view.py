#!/usr/bin/env python3
"""
Quick test script to verify the Active Scouts view is working
"""

import os
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent / "database"))
sys.path.insert(0, str(Path(__file__).parent / "web-ui"))

from main import get_database_connection

def test_active_scouts_view():
    """Test the active scouts view directly"""
    
    # Test database connection
    conn = get_database_connection()
    if not conn:
        print("❌ Database connection failed")
        return False
    
    try:
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
        
        return len(rows) > 0
        
    except Exception as e:
        print(f"❌ Error testing view: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_active_scouts_view()
    exit(0 if success else 1)