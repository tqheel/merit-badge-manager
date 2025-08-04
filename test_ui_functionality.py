#!/usr/bin/env python3
"""
Test the Streamlit UI active scouts functionality
"""

import sqlite3
import os
import sys
import pandas as pd
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent / "database"))

# Load environment
from dotenv import load_dotenv
load_dotenv()

def get_database_connection():
    """Get database connection using the same logic as the UI."""
    try:
        database_path = os.getenv('DATABASE_PATH', './database/merit_badge_manager.db')
        if not os.path.exists(database_path):
            print(f"Database file not found: {database_path}")
            return None
        
        conn = sqlite3.connect(database_path)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def test_ui_view_functionality():
    """Test the view functionality that the UI uses."""
    
    conn = get_database_connection()
    if not conn:
        print("❌ Database connection failed")
        return False
    
    try:
        # Test loading the view data like the UI does
        df = pd.read_sql_query("SELECT * FROM active_scouts_with_positions", conn)
        print(f"✅ Successfully loaded active_scouts_with_positions view")
        print(f"📊 Records found: {len(df)}")
        print(f"📋 Columns: {list(df.columns)}")
        
        if len(df) == 0:
            print("❌ No records found in view")
            return False
        
        # Test scout ID mapping functionality (used by the modal)
        scout_id_query = """
        SELECT s.id, s.first_name, s.last_name, s.bsa_number
        FROM scouts s
        WHERE s.activity_status = 'Active'
        """
        cursor = conn.cursor()
        cursor.execute(scout_id_query)
        scout_ids = {(row[1], row[2], row[3]): row[0] for row in cursor.fetchall()}
        
        print(f"✅ Scout ID mapping created with {len(scout_ids)} scouts")
        
        # Test that each scout in the view can be mapped to an ID
        missing_ids = 0
        for index, row in df.iterrows():
            scout_key = (row['first_name'], row['last_name'], row['bsa_number'])
            scout_id = scout_ids.get(scout_key)
            
            if not scout_id:
                print(f"⚠️  Missing scout ID for: {scout_key}")
                missing_ids += 1
            else:
                print(f"✅ Scout ID mapping: {row['first_name']} {row['last_name']} -> ID {scout_id}")
        
        if missing_ids > 0:
            print(f"❌ {missing_ids} scouts missing ID mappings")
            return False
        
        # Test sample display format
        print("\n📋 Sample display format (first 3 scouts):")
        for index, row in df.head(3).iterrows():
            scout_key = (row['first_name'], row['last_name'], row['bsa_number'])
            scout_id = scout_ids.get(scout_key)
            scout_name = f"{row['first_name']} {row['last_name']}"
            position = row['position_title'] or 'No Position'
            print(f"  👤 {scout_name} (ID: {scout_id}) - {row['rank']} ({row['patrol_name']}) - {position}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing view functionality: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_ui_view_functionality()
    if success:
        print("\n🎉 Active Scouts view is working correctly!")
        print("✅ The UI should now display scouts properly")
    else:
        print("\n❌ Active Scouts view has issues")
    exit(0 if success else 1)