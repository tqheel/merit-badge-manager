#!/usr/bin/env python3
"""
Test validation script to verify our UI test fixes are syntactically correct.
"""

import sys
import ast
from pathlib import Path

def validate_python_syntax(file_path):
    """Validate that a Python file has correct syntax."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Validate all UI test files."""
    test_files = [
        "ui-tests/test_basic_ui.py",
        "ui-tests/test_csv_import.py", 
        "ui-tests/test_database_management.py",
        "ui-tests/test_database_views.py",
        "ui-tests/test_environment_config.py",
        "ui-tests/test_integration_workflows.py"
    ]
    
    all_valid = True
    
    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            valid, message = validate_python_syntax(path)
            status = "✓" if valid else "✗"
            print(f"{status} {test_file}: {message}")
            if not valid:
                all_valid = False
        else:
            print(f"✗ {test_file}: File not found")
            all_valid = False
    
    if all_valid:
        print("\n✅ All test files have valid syntax!")
        return 0
    else:
        print("\n❌ Some test files have syntax errors!")
        return 1

if __name__ == "__main__":
    sys.exit(main())