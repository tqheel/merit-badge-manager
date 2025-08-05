#!/usr/bin/env python3
"""
Test script to verify integrated validation functionality including MB Progress.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent / "web-ui"))

# Mock streamlit for testing
class MockStreamlit:
    def error(self, msg):
        print(f"ERROR: {msg}")

sys.modules['streamlit'] = MockStreamlit()

from main import run_validation_only, load_env_file

def test_integrated_validation():
    """Test integrated validation functionality."""
    print("Testing integrated validation functionality...")
    
    # Test with valid files
    print("\n1. Testing with valid files:")
    roster_path = Path("data/roster_report.csv")
    if roster_path.exists():
        overall_valid, results = run_validation_only(roster_path)
        print(f"   Overall valid: {overall_valid}")
        print(f"   Results: {list(results.keys())}")
        
        for file_type, result in results.items():
            print(f"   {file_type}:")
            print(f"     Valid: {result.is_valid}")
            print(f"     Rows: {result.row_count}")
            print(f"     Errors: {len(result.errors)}")
            print(f"     Warnings: {len(result.warnings)}")
            print(f"     Skipped: {len(result.skipped_records)}")
    else:
        print(f"   Roster file not found: {roster_path}")
    
    # Test with invalid MB progress file
    print("\n2. Testing with invalid MB progress file:")
    # Temporarily replace the valid file with invalid one
    valid_mb_file = Path("data/merit_badge_progress.csv")
    invalid_mb_file = Path("data/merit_badge_progress_invalid.csv")
    backup_file = Path("data/merit_badge_progress.csv.backup")
    
    if valid_mb_file.exists():
        valid_mb_file.rename(backup_file)
    if invalid_mb_file.exists():
        invalid_mb_file.rename(valid_mb_file)
    
    try:
        overall_valid, results = run_validation_only(roster_path)
        print(f"   Overall valid: {overall_valid}")
        print(f"   Results: {list(results.keys())}")
        
        for file_type, result in results.items():
            print(f"   {file_type}:")
            print(f"     Valid: {result.is_valid}")
            print(f"     Rows: {result.row_count}")
            print(f"     Errors: {len(result.errors)}")
            if result.errors:
                print(f"     First few errors:")
                for error in result.errors[:3]:
                    print(f"       - {error}")
    finally:
        # Restore files
        if valid_mb_file.exists():
            valid_mb_file.rename(invalid_mb_file)
        if backup_file.exists():
            backup_file.rename(valid_mb_file)

if __name__ == "__main__":
    test_integrated_validation()