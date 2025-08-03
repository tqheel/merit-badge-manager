"""
Demo test to validate UI test setup without requiring browser installation.
"""

import pytest
from pathlib import Path
import sys

# Add the layer directories to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))


def test_ui_test_setup():
    """Test that UI test infrastructure is properly set up."""
    # Verify that required modules can be imported
    try:
        import pytest_playwright
        playwright_available = True
    except ImportError:
        playwright_available = False
    
    assert playwright_available, "pytest-playwright should be installed"
    
    # Verify that our test modules can be imported
    test_modules = [
        "test_basic_ui",
        "test_csv_import", 
        "test_database_management",
        "test_database_views",
        "test_environment_config",
        "test_integration_workflows"
    ]
    
    for module_name in test_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")


def test_ui_test_fixtures():
    """Test that UI test fixtures are properly configured."""
    from conftest import sample_csv_files, clean_database
    
    # Verify fixtures exist
    assert sample_csv_files is not None
    assert clean_database is not None


def test_streamlit_imports():
    """Test that Streamlit and related modules can be imported."""
    try:
        import streamlit
        import pandas
        from csv_validator import CSVValidator
        from roster_parser import RosterParser
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_ui_test_structure():
    """Test that UI test directory structure is correct."""
    ui_tests_dir = Path(__file__).parent
    
    # Check that all expected test files exist
    expected_files = [
        "test_basic_ui.py",
        "test_csv_import.py",
        "test_database_management.py", 
        "test_database_views.py",
        "test_environment_config.py",
        "test_integration_workflows.py",
        "conftest.py",
        "__init__.py",
        "README.md"
    ]
    
    for filename in expected_files:
        file_path = ui_tests_dir / filename
        assert file_path.exists(), f"Expected file {filename} not found"


def test_sample_data_generation(tmp_path):
    """Test that sample data can be generated for testing."""
    # Create sample CSV content
    adult_csv_content = """First Name,Last Name,BSA ID,Email,Position 1,Position 2,Position 3,Position 4,Position 5,Training Date,Patrol,Gender
John,Doe,12345678,john.doe@example.com,Scoutmaster,,,,,2023-01-15,Adult,M
"""
    
    youth_csv_content = """First Name,Last Name,BSA ID,Email,Rank,Patrol,Gender,Primary Parent/Guardian Name,Primary Parent/Guardian Email
Mike,Johnson,11111111,mike.johnson@example.com,Eagle,Eagles,M,Bob Johnson,bob.johnson@example.com
"""
    
    # Write sample files
    adult_file = tmp_path / "adult_sample.csv"
    youth_file = tmp_path / "youth_sample.csv"
    
    adult_file.write_text(adult_csv_content)
    youth_file.write_text(youth_csv_content)
    
    # Verify files were created
    assert adult_file.exists()
    assert youth_file.exists()
    assert len(adult_file.read_text()) > 0
    assert len(youth_file.read_text()) > 0


@pytest.mark.ui  
def test_ui_marker():
    """Test that UI marker is properly configured."""
    # This test has the @pytest.mark.ui marker
    # It should be discoverable by pytest -m ui
    assert True  # Simple assertion to verify the test runs


def test_playwright_config_exists():
    """Test that Playwright configuration file exists."""
    config_file = Path(__file__).parent.parent / "playwright.config.py"
    assert config_file.exists(), "playwright.config.py should exist in project root"


def test_run_ui_tests_script_exists():
    """Test that the UI test runner script exists and is executable."""
    script_file = Path(__file__).parent.parent / "run_ui_tests.py"
    assert script_file.exists(), "run_ui_tests.py should exist in project root"
    
    # Check if it's executable (on Unix systems)
    import stat
    file_stat = script_file.stat()
    is_executable = bool(file_stat.st_mode & stat.S_IEXEC)
    assert is_executable, "run_ui_tests.py should be executable"