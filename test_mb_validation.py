#!/usr/bin/env python3
"""
Test script to verify MB Progress validation functionality.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent / "web-ui"))

from csv_validator import CSVValidator

def test_mb_progress_validation():
    """Test MB Progress validation functionality."""
    print("Testing MB Progress CSV validation...")
    
    validator = CSVValidator()
    
    # Test valid file
    print("\n1. Testing valid MB Progress file:")
    valid_file = "data/merit_badge_progress.csv"
    if os.path.exists(valid_file):
        result = validator.validate_mb_progress(valid_file)
        print(f"   Valid: {result.is_valid}")
        print(f"   Rows: {result.row_count}")
        print(f"   Valid rows: {result.valid_rows}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Warnings: {len(result.warnings)}")
        
        if result.errors:
            print("   Error details:")
            for error in result.errors:
                print(f"     - {error}")
    else:
        print(f"   File not found: {valid_file}")
    
    # Test invalid file
    print("\n2. Testing invalid MB Progress file:")
    invalid_file = "data/merit_badge_progress_invalid.csv"
    if os.path.exists(invalid_file):
        result = validator.validate_mb_progress(invalid_file)
        print(f"   Valid: {result.is_valid}")
        print(f"   Rows: {result.row_count}")
        print(f"   Valid rows: {result.valid_rows}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Warnings: {len(result.warnings)}")
        
        if result.errors:
            print("   Error details:")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"     - {error}")
                
        if result.warnings:
            print("   Warning details:")
            for warning in result.warnings:
                print(f"     - {warning}")
    else:
        print(f"   File not found: {invalid_file}")

if __name__ == "__main__":
    test_mb_progress_validation()