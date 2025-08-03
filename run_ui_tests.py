#!/usr/bin/env python3
"""
Playwright UI Test Runner for Merit Badge Manager

This script runs the Playwright UI tests for the Merit Badge Manager web interface.
It provides options to run different test suites and handles browser setup.
"""

import subprocess
import sys
import argparse
from pathlib import Path
import os


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Merit Badge Manager UI Tests")
    parser.add_argument(
        "--suite", 
        choices=["all", "basic", "csv", "database", "views", "config", "integration"],
        default="all",
        help="Test suite to run"
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser to use for testing"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run tests in headed mode (show browser)"
    )
    parser.add_argument(
        "--slow",
        action="store_true",
        help="Include slow tests"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Construct pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "ui-tests/",
        "-v",
        "--tb=short",
        f"--browser={args.browser}"
    ]
    
    # Add test selection based on suite
    if args.suite != "all":
        test_files = {
            "basic": ["ui-tests/test_basic_ui.py"],
            "csv": ["ui-tests/test_csv_import.py"],
            "database": ["ui-tests/test_database_management.py"],
            "views": ["ui-tests/test_database_views.py"],
            "config": ["ui-tests/test_environment_config.py"],
            "integration": ["ui-tests/test_integration_workflows.py"]
        }
        cmd.extend(test_files[args.suite])
    
    # Add headed mode if requested
    if args.headed:
        cmd.append("--headed")
    
    # Include slow tests if requested
    if not args.slow:
        cmd.extend(["-m", "not slow"])
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure pytest and pytest-playwright are installed:")
        print("pip install pytest pytest-playwright")
        return 1
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())