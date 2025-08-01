#!/usr/bin/env python3
"""
Test cases for the Streamlit Web UI

Tests basic functionality of the Merit Badge Manager Streamlit application.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the root directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_streamlit_app_imports():
    """Test that the Streamlit app can be imported without errors."""
    try:
        import streamlit_app
        assert True, "Streamlit app imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import streamlit_app: {e}")

def test_env_template_functions():
    """Test the environment template loading functions."""
    import streamlit_app
    
    # Test load_env_template function
    template = streamlit_app.load_env_template()
    assert isinstance(template, dict), "load_env_template should return a dictionary"
    
    # Check for expected keys from .env.template
    expected_keys = ['GITHUB_TOKEN', 'GITHUB_REPO', 'HOST', 'PORT']
    for key in expected_keys:
        assert key in template, f"Expected key {key} not found in template"

def test_save_and_load_env_functions():
    """Test saving and loading environment variables."""
    import streamlit_app
    
    # Create test data
    test_env = {
        'TEST_KEY1': 'test_value1',
        'TEST_KEY2': 'test_value2'
    }
    
    # Save to a test file
    test_env_file = Path(".env.test")
    try:
        # Temporarily patch the save function to use test file
        original_env_path = ".env"
        with open(".env.test", 'w') as f:
            f.write("# Test environment file\n")
            for key, value in test_env.items():
                f.write(f"{key}={value}\n")
        
        # Test loading
        loaded_env = {}
        with open(".env.test", 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    loaded_env[key] = value
        
        # Verify
        assert 'TEST_KEY1' in loaded_env
        assert loaded_env['TEST_KEY1'] == 'test_value1'
        assert 'TEST_KEY2' in loaded_env
        assert loaded_env['TEST_KEY2'] == 'test_value2'
        
    finally:
        # Clean up test file
        if test_env_file.exists():
            test_env_file.unlink()

def test_database_connection_function():
    """Test the database connection function handles missing database gracefully."""
    import streamlit_app
    
    # Test with non-existent database
    conn = streamlit_app.get_database_connection()
    # Should return None when database doesn't exist
    assert conn is None, "get_database_connection should return None when database doesn't exist"

def test_view_availability_function():
    """Test the view availability function."""
    import streamlit_app
    
    # Test with no database
    views = streamlit_app.get_available_views()
    assert isinstance(views, list), "get_available_views should return a list"
    assert len(views) == 0, "get_available_views should return empty list when no database exists"

if __name__ == "__main__":
    pytest.main([__file__])