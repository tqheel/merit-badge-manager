#!/usr/bin/env python3
"""
Validate Streamlit app structure matches test expectations.
"""

import sys
from pathlib import Path

# Add the layer directories to the Python path
sys.path.insert(0, str(Path(__file__).parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent / "database"))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def validate_app_structure():
    """Validate that the Streamlit app has expected navigation structure."""
    
    print("🔍 VALIDATING STREAMLIT APP STRUCTURE")
    print("=" * 50)
    
    # Read the main.py file and check for navigation elements
    main_py_path = Path("web-ui/main.py")
    
    if not main_py_path.exists():
        print("❌ web-ui/main.py not found!")
        return False
        
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    # Check for expected navigation labels
    expected_navigation = [
        "Database Views",
        "Settings", 
        "CSV Import"
    ]
    
    print("✅ Checking navigation structure...")
    
    navigation_found = []
    for nav_item in expected_navigation:
        if f'"{nav_item}"' in content:
            navigation_found.append(nav_item)
            print(f"   ✓ Found: {nav_item}")
        else:
            print(f"   ✗ Missing: {nav_item}")
    
    # Check for problematic old navigation that should be removed
    old_navigation = [
        "Environment Configuration",
        "CSV Import & Validation",
        "Database Management"
    ]
    
    print("\n🚫 Checking for old navigation labels...")
    old_found = []
    for old_nav in old_navigation:
        if f'"{old_nav}"' in content:
            old_found.append(old_nav)
            print(f"   ⚠️  Found old label: {old_nav}")
        else:
            print(f"   ✓ Correctly removed: {old_nav}")
    
    # Check for expected page headers
    expected_headers = [
        "Environment Settings",
        "CSV Import & Validation",
        "Database Views"
    ]
    
    print("\n📝 Checking page headers...")
    headers_found = []
    for header in expected_headers:
        if header in content:
            headers_found.append(header)
            print(f"   ✓ Found header: {header}")
        else:
            print(f"   ✗ Missing header: {header}")
    
    # Summary
    print("\n📊 VALIDATION SUMMARY:")
    print(f"   Navigation items found: {len(navigation_found)}/{len(expected_navigation)}")
    print(f"   Old labels correctly removed: {len(old_navigation) - len(old_found)}/{len(old_navigation)}")
    print(f"   Page headers found: {len(headers_found)}/{len(expected_headers)}")
    
    success = (len(navigation_found) == len(expected_navigation) and 
               len(old_found) == 0 and
               len(headers_found) >= 2)  # At least most headers should be present
    
    if success:
        print("\n✅ App structure validation PASSED!")
        print("   The Streamlit app navigation matches test expectations.")
    else:
        print("\n❌ App structure validation FAILED!")
        print("   There may be mismatches between app and test expectations.")
    
    return success

if __name__ == "__main__":
    success = validate_app_structure()
    sys.exit(0 if success else 1)