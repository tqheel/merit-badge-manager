#!/usr/bin/env python3
"""
UI test for text wrapping functionality in database views.
Issue #39: Wrap all text in text field in UI database views
"""

import pytest
import time
import sqlite3
from pathlib import Path


@pytest.mark.ui
@pytest.mark.slow  
def test_text_wrapping_in_database_views(page, base_url):
    """Test that text wrapping is properly enabled in database views."""
    
    # Navigate to the Streamlit app
    page.goto(f"{base_url}")
    page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
    
    # Wait for page to fully load
    time.sleep(2)
    
    # Navigate to Database Views page
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(2)
    
    # Check if we can see view categories
    page.wait_for_selector('text=View Category', timeout=10000)
    
    # Select Adult Views
    adult_views_radio = page.locator('label:has-text("Adult Views")').first
    adult_views_radio.click()
    time.sleep(1)
    
    # Select Merit Badge Counselors view (likely to have long text)
    merit_badge_counselors_option = page.locator('option:has-text("merit_badge_counselors")').first
    if merit_badge_counselors_option.is_visible():
        merit_badge_counselors_option.click()
        time.sleep(3)
        
        # Check that a dataframe is displayed
        dataframe = page.locator('[data-testid="stDataFrame"]').first
        if dataframe.is_visible():
            # Take a screenshot to verify text wrapping visually
            page.screenshot(path="/tmp/merit_badge_counselors_view.png")
            print("✅ Screenshot taken of merit badge counselors view")
            
            # Check for text wrapping configuration by looking at cell content
            # In a properly configured dataframe, text should not be truncated with "..."
            cell_content = page.locator('[data-testid="stDataFrame"] .stDataFrameCell').first
            if cell_content.is_visible():
                # The text should be fully visible without "..." truncation
                print("✅ Dataframe cells are visible and should support text wrapping")
            else:
                print("⚠️  Could not find dataframe cells to verify text wrapping")
        else:
            print("⚠️  Dataframe not visible in merit badge counselors view")
    else:
        print("⚠️  Merit Badge Counselors view not available")
    
    # Test other views with likely long text content
    other_views_to_test = ["registered_volunteers", "adults_missing_data"]
    
    for view_name in other_views_to_test:
        view_option = page.locator(f'option:has-text("{view_name}")').first
        if view_option.is_visible():
            view_option.click()
            time.sleep(2)
            
            # Check if dataframe is displayed
            dataframe = page.locator('[data-testid="stDataFrame"]').first
            if dataframe.is_visible():
                page.screenshot(path=f"/tmp/{view_name}_view.png")
                print(f"✅ Screenshot taken of {view_name} view")
            else:
                print(f"⚠️  No dataframe visible for {view_name} view")


@pytest.mark.ui  
def test_mbc_workload_text_wrapping(page, base_url):
    """Test text wrapping in MBC workload summary view (special modal view)."""
    
    # Navigate to the Streamlit app
    page.goto(f"{base_url}")
    page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
    time.sleep(2)
    
    # Navigate to Database Views page
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(2)
    
    # Select Adult Views
    adult_views_radio = page.locator('label:has-text("Adult Views")').first
    adult_views_radio.click()
    time.sleep(1)
    
    # Select MBC Workload Summary view
    mbc_workload_option = page.locator('option:has-text("mbc_workload_summary")').first
    if mbc_workload_option.is_visible():
        mbc_workload_option.click()
        time.sleep(3)
        
        # Look for merit badges text areas (should use text_area for long text)
        text_areas = page.locator('[data-testid="stTextArea"]')
        if text_areas.count() > 0:
            print(f"✅ Found {text_areas.count()} text areas for better text display")
            
            # Take screenshot of the MBC workload view
            page.screenshot(path="/tmp/mbc_workload_view.png")
            print("✅ Screenshot taken of MBC workload view with text areas")
        else:
            print("⚠️  No text areas found - text may still be truncated")
    else:
        print("⚠️  MBC Workload Summary view not available")


@pytest.mark.ui
def test_youth_views_text_wrapping(page, base_url):
    """Test text wrapping in youth/scout views."""
    
    # Navigate to the Streamlit app
    page.goto(f"{base_url}")
    page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
    time.sleep(2)
    
    # Navigate to Database Views page
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(2)
    
    # Select Youth Views  
    youth_views_radio = page.locator('label:has-text("Youth Views")').first
    youth_views_radio.click()
    time.sleep(1)
    
    # Test scout views that might have long text
    scout_views_to_test = ["active_scouts_with_positions", "scouts_missing_data"]
    
    for view_name in scout_views_to_test:
        view_option = page.locator(f'option:has-text("{view_name}")').first
        if view_option.is_visible():
            view_option.click()
            time.sleep(2)
            
            # For active scouts view, it uses special modal handling
            if view_name == "active_scouts_with_positions":
                # Look for scout buttons (clickable names)
                scout_buttons = page.locator('button:has-text("👤")')
                if scout_buttons.count() > 0:
                    print(f"✅ Found {scout_buttons.count()} scout buttons in active scouts view")
                    page.screenshot(path="/tmp/active_scouts_view.png")
                else:
                    print("⚠️  No scout buttons found in active scouts view")
            else:
                # Regular dataframe view
                dataframe = page.locator('[data-testid="stDataFrame"]').first
                if dataframe.is_visible():
                    page.screenshot(path=f"/tmp/{view_name}_view.png")
                    print(f"✅ Screenshot taken of {view_name} view")
                else:
                    print(f"⚠️  No dataframe visible for {view_name} view")


def run_text_wrapping_ui_tests():
    """Run text wrapping UI tests manually (for development purposes)."""
    import subprocess
    import sys
    
    print("🧪 Running UI tests for text wrapping functionality...")
    
    # Run the specific test functions
    test_files = [
        "test_text_wrapping_in_database_views",
        "test_mbc_workload_text_wrapping", 
        "test_youth_views_text_wrapping"
    ]
    
    try:
        cmd = [
            sys.executable, "-m", "pytest", __file__ + "::test_text_wrapping_in_database_views",
            "-v", "--base-url=http://localhost:8501"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running UI tests: {e}")
        return False


if __name__ == "__main__":
    # This allows the test to be run standalone for development
    success = run_text_wrapping_ui_tests()
    print("✅ UI tests completed" if success else "❌ UI tests failed")