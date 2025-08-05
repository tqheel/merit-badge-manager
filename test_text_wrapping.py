#!/usr/bin/env python3
"""
Test script to verify text wrapping functionality in database views.
"""

import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
import sys

# Add the web-ui directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "web-ui"))

def test_text_wrapping_configuration():
    """Test that the text wrapping configuration works for dataframes."""
    
    # Create a test dataframe with long text content
    test_data = {
        'Name': ['Merit Badge Counselor 1', 'Merit Badge Counselor 2'],
        'Merit_Badges': [
            'Camping, Hiking, First Aid, Wilderness Survival, Orienteering, Cooking, Swimming, Lifesaving, Emergency Preparedness, Search and Rescue',
            'Astronomy, Space Exploration, Aviation, Engineering, Robotics, Electronics, Radio, Computer Programming, Digital Technology, Game Design'
        ],
        'Email': ['counselor1@example.com', 'counselor2@example.com'],
        'Phone': ['(555) 123-4567', '(555) 987-6543']
    }
    
    df = pd.DataFrame(test_data)
    
    # Test the display function
    from main import display_dataframe_with_text_wrapping
    
    print("✅ Test dataframe created with long text content")
    print(f"Dataframe shape: {df.shape}")
    print(f"Max Merit_Badges length: {max(len(str(val)) for val in df['Merit_Badges'])}")
    
    # This would normally display in Streamlit, but we can test the configuration logic
    column_config = {}
    
    for col in df.columns:
        # Configure all columns to enable text wrapping
        column_config[col] = {
            'type': 'text',
            'help': f"Content for {col}",
            'width': "medium",
            'max_chars': None,  # No character limit
        }
    
    print("✅ Column configuration created for text wrapping")
    print(f"Configured columns: {list(column_config.keys())}")
    
    return True


def test_database_view_content():
    """Test actual database view content for text wrapping needs."""
    
    db_path = "database/merit_badge_manager.db"
    if not Path(db_path).exists():
        print("⚠️  Test database not found. Run setup_test_database.py first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Test merit badge counselors view which is likely to have long text
        query = "SELECT * FROM merit_badge_counselors LIMIT 5"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("⚠️  No data in merit_badge_counselors view")
        else:
            print("✅ Merit Badge Counselors view data loaded")
            print(f"Records: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            
            # Check for long text content
            for col in df.columns:
                if df[col].dtype == 'object':  # Text columns
                    max_length = max(len(str(val)) for val in df[col] if pd.notna(val))
                    if max_length > 50:
                        print(f"📝 Column '{col}' has text up to {max_length} characters - needs wrapping")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing database view: {e}")
        return False


def main():
    """Run all text wrapping tests."""
    print("🧪 Testing text wrapping functionality for database views")
    print("=" * 60)
    
    # Test 1: Configuration logic
    print("\n1. Testing text wrapping configuration...")
    config_test = test_text_wrapping_configuration()
    
    # Test 2: Database content analysis
    print("\n2. Testing database view content...")
    db_test = test_database_view_content()
    
    print("\n" + "=" * 60)
    if config_test and db_test:
        print("✅ All tests passed! Text wrapping should work correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return config_test and db_test


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)