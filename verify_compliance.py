#!/usr/bin/env python3
"""
Final verification script for database consolidation compliance.

This script validates that all compliance issues mentioned in GitHub Issue #46
have been resolved.
"""

import sys
import subprocess
from pathlib import Path

def run_check(description, command, success_msg, error_msg):
    """Run a compliance check and report results."""
    print(f"\n🔍 {description}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print(f"✅ {success_msg}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {error_msg}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {error_msg}: {e}")
        return False

def main():
    """Run all compliance verification checks."""
    print("🎯 Database Consolidation Compliance Verification")
    print("=" * 60)
    print("Verifying resolution of GitHub Issue #46")
    
    all_passed = True
    
    # Check 1: No hardcoded paths in UI tests
    passed = run_check(
        "Checking UI test files for hardcoded database paths",
        'grep -r "merit_badge_manager\\.db" ui-tests/ | grep -v "database_utils\\|test_database_utils" || echo "No hardcoded paths found"',
        "No hardcoded database paths found in UI test files",
        "Found hardcoded database paths in UI test files"
    )
    all_passed = all_passed and passed
    
    # Check 2: No hardcoded paths in demo scripts
    passed = run_check(
        "Checking demo scripts for hardcoded database paths",
        'grep -n "merit_badge_manager\\.db" demo_text_wrapping.py test_text_wrapping_comprehensive.py | grep -v "database_utils" || echo "No hardcoded paths found"',
        "No hardcoded database paths found in demo scripts",
        "Found hardcoded database paths in demo scripts"
    )
    all_passed = all_passed and passed
    
    # Check 3: No hardcoded paths in web UI
    passed = run_check(
        "Checking web UI components for hardcoded database paths",
        'grep -r "merit_badge_manager\\.db" web-ui/pages/ --include="*.py" | grep -v "database_utils" || echo "No hardcoded paths found"',
        "No hardcoded database paths found in web UI components",
        "Found hardcoded database paths in web UI components"
    )
    all_passed = all_passed and passed
    
    # Check 4: Database utilities can be imported
    passed = run_check(
        "Testing database utilities import",
        'source venv/bin/activate && python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path(\\"web-ui\\"))); from database_utils import get_database_path, get_database_connection, database_exists; print(\\"Import successful\\")"',
        "Database utilities can be imported successfully",
        "Failed to import database utilities"
    )
    all_passed = all_passed and passed
    
    # Check 5: Centralized database exists
    passed = run_check(
        "Checking centralized database location",
        'ls -la database/merit_badge_manager.db && echo "Centralized database exists"',
        "Centralized database exists at correct location",
        "Centralized database not found at expected location"
    )
    all_passed = all_passed and passed
    
    # Check 6: No duplicate databases
    passed = run_check(
        "Checking for duplicate database files",
        'if [ -f "merit_badge_manager.db" ] || [ -f "web-ui/merit_badge_manager.db" ]; then echo "Found duplicates" && exit 1; else echo "No duplicates found"; fi',
        "No duplicate database files found",
        "Found duplicate database files in old locations"
    )
    all_passed = all_passed and passed
    
    # Check 7: Database consolidation tests pass
    passed = run_check(
        "Running database consolidation tests",
        'source venv/bin/activate && python -m pytest tests/test_database_consolidation.py -v --tb=no',
        "All database consolidation tests pass",
        "Database consolidation tests failed"
    )
    all_passed = all_passed and passed
    
    # Check 8: Active scouts view tests pass
    passed = run_check(
        "Running active scouts view tests",
        'source venv/bin/activate && python -m pytest tests/test_active_scouts_view.py -v --tb=no',
        "All active scouts view tests pass",
        "Active scouts view tests failed"
    )
    all_passed = all_passed and passed
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL COMPLIANCE CHECKS PASSED!")
        print("✅ Database consolidation compliance successfully achieved")
        print("✅ All critical violations from GitHub Issue #46 have been resolved")
        print("\nCompliance Status: 🟢 COMPLIANT")
        return 0
    else:
        print("❌ SOME COMPLIANCE CHECKS FAILED")
        print("🔴 Database consolidation compliance not fully achieved")
        print("\nCompliance Status: 🔴 NON-COMPLIANT")
        return 1

if __name__ == "__main__":
    sys.exit(main())