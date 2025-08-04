#!/usr/bin/env python3
"""
Simple test runner to verify our test imports and basic structure without requiring Playwright browsers.
"""

import sys
from pathlib import Path
import importlib.util

def test_imports():
    """Test that all test modules can be imported successfully."""
    test_files = [
        "ui-tests/test_basic_ui.py",
        "ui-tests/test_csv_import.py", 
        "ui-tests/test_database_management.py",
        "ui-tests/test_database_views.py",
        "ui-tests/test_environment_config.py",
        "ui-tests/test_integration_workflows.py"
    ]
    
    all_imported = True
    
    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(
                    path.stem, path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                print(f"✓ {test_file}: Imported successfully")
                
                # Count test functions
                test_funcs = [name for name in dir(module) if name.startswith('test_')]
                skip_funcs = [func for func in test_funcs 
                             if hasattr(getattr(module, func), 'pytestmark')
                             and any(mark.name == 'skip' for mark in getattr(module, func).pytestmark if hasattr(mark, 'name'))]
                
                active_tests = len(test_funcs) - len(skip_funcs)
                print(f"  - Total test functions: {len(test_funcs)}")
                print(f"  - Skipped tests: {len(skip_funcs)}")
                print(f"  - Active tests: {active_tests}")
                
            except Exception as e:
                print(f"✗ {test_file}: Import failed - {e}")
                all_imported = False
        else:
            print(f"✗ {test_file}: File not found")
            all_imported = False
    
    return all_imported

def main():
    """Run import tests."""
    print("Testing UI test module imports...")
    
    if test_imports():
        print("\n✅ All test modules imported successfully!")
        return 0
    else:
        print("\n❌ Some test modules failed to import!")
        return 1

if __name__ == "__main__":
    sys.exit(main())