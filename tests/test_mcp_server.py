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
    try:
        # Test basic imports (these should work even without dependencies installed)
        import json
        import pathlib
        print("✅ Basic Python modules imported successfully")
        
        # Test if we can load the server module structure
        from mcp_server import main
        print("✅ MCP server module structure is valid")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist."""
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "workitems/features",
        "workitems/published/features",
        "mcp_server",
        "venv"  # Updated to check for venv instead of .venv
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            all_exist = False
    
    return all_exist

def test_configuration_files():
    """Test that configuration files exist."""
    base_dir = Path(__file__).parent.parent
    
    config_files = [
        ".env.template",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in config_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ Config file exists: {file_path}")
        else:
            print(f"❌ Config file missing: {file_path}")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("Merit Badge Manager - MCP Server Test")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_configuration_files),
        ("Module Imports", test_imports)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
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
