#!/usr/bin/env python3
"""
Test script to verify the run_validation_only function includes MB Progress.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "database-access"))

from csv_validator import CSVValidator
from roster_parser import RosterParser

def load_env_file():
    """Load .env file (simplified version)."""
    env_vars = {}
    env_path = Path(".env")
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    return env_vars

def run_validation_only_test(roster_file_path: Path):
    """
    Test version of run_validation_only function.
    """
    try:
        # Parse the roster file to get adult and youth sections
        parser = RosterParser(str(roster_file_path), "output")
        adult_file, youth_file = parser.parse_roster()
        
        # Validate the parsed output files
        validator = CSVValidator()
        results = {}
        
        if os.path.exists(adult_file):
            results["Adult Roster"] = validator.validate_adult_roster(adult_file)
        
        if os.path.exists(youth_file):
            results["Youth Roster"] = validator.validate_youth_roster(youth_file)
        
        # Also validate Merit Badge Progress file if it exists
        current_env = load_env_file()
        mb_progress_file = current_env.get('MB_PROGRESS_CSV_FILE', 'merit_badge_progress.csv')
        data_dir = Path("data")
        mb_progress_path = data_dir / mb_progress_file
        
        if mb_progress_path.exists():
            results["Merit Badge Progress"] = validator.validate_mb_progress(str(mb_progress_path))
        
        # Calculate overall validity
        overall_valid = all(result.is_valid for result in results.values())
        
        return overall_valid, results
        
    except Exception as e:
        print(f"Validation error: {e}")
        return False, {}

def test_validation_with_mb_progress():
    """Test that validation includes MB Progress file."""
    print("Testing validation with MB Progress inclusion...")
    
    roster_path = Path("data/roster_report.csv")
    if not roster_path.exists():
        print(f"Roster file not found: {roster_path}")
        return
    
    # Test with valid files
    print("\n1. Testing with valid files:")
    overall_valid, results = run_validation_only_test(roster_path)
    print(f"   Overall valid: {overall_valid}")
    print(f"   Files validated: {list(results.keys())}")
    
    # Check if Merit Badge Progress is included
    if "Merit Badge Progress" in results:
        print("   ✅ Merit Badge Progress file IS included in validation")
        mb_result = results["Merit Badge Progress"]
        print(f"      Valid: {mb_result.is_valid}")
        print(f"      Rows: {mb_result.row_count}")
        print(f"      Errors: {len(mb_result.errors)}")
        print(f"      Warnings: {len(mb_result.warnings)}")
    else:
        print("   ❌ Merit Badge Progress file is NOT included in validation")
    
    for file_type, result in results.items():
        print(f"   {file_type}: {'✅ PASS' if result.is_valid else '❌ FAIL'}")

if __name__ == "__main__":
    test_validation_with_mb_progress()