#!/usr/bin/env python3
"""
Simple test to validate the MCP server configuration and GitHub integration.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    # Test basic imports (these should work even without dependencies installed)
    import json
    import pathlib
    print("✅ Basic Python modules imported successfully")
    
    # Test if we can load the server module structure
    from mcp_server import main
    print("✅ MCP server module structure is valid")

def test_close_issue_request_model():
    """Test that the CloseIssueRequest model is properly defined."""
    from mcp_server.main import CloseIssueRequest
    
    # Test valid request with required fields
    request1 = CloseIssueRequest(issue_number=123)
    assert request1.issue_number == 123
    assert request1.reason == "completed"  # default value
    print("✅ CloseIssueRequest model with defaults works correctly")
    
    # Test request with custom reason
    request2 = CloseIssueRequest(issue_number=456, reason="not_planned")
    assert request2.issue_number == 456
    assert request2.reason == "not_planned"
    print("✅ CloseIssueRequest model with custom reason works correctly")

def test_directory_structure():
    """Test that required directories exist."""
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "workitems/features",
        "workitems/published/features",
        "mcp_server",
        "venv"  # Updated to check for venv instead of .venv
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        assert full_path.exists(), f"Directory missing: {dir_path}"
        print(f"✅ Directory exists: {dir_path}")

def test_configuration_files():
    """Test that configuration files exist."""
    base_dir = Path(__file__).parent.parent
    
    config_files = [
        ".env.template",
        "requirements.txt"
    ]
    
    for file_path in config_files:
        full_path = base_dir / file_path
        assert full_path.exists(), f"Config file missing: {file_path}"
        print(f"✅ Config file exists: {file_path}")

def main():
    """Run all tests."""
    print("Merit Badge Manager - MCP Server Test")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_configuration_files),
        ("Module Imports", test_imports),
        ("Close Issue Request Model", test_close_issue_request_model)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            test_func()
            print(f"✅ {test_name} test passed")
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The MCP server is ready for use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure GitHub: cp .env.template .env")
        print("3. Start server: cd mcp_server && uvicorn main:app --reload")
    else:
        print("❌ Some tests failed. Please check the configuration.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
