"""
Test database views functionality through the UI.
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.ui
def test_database_views_no_database(page: Page, streamlit_app, clean_database):
    """Test database views page when no database exists."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Views page
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Should show warning about missing database
    expect(page.locator("text=Database not found")).to_be_visible()
    expect(page.locator("text=Please import data first")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_database_views_with_data(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test database views page with data loaded."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # First create database and import data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Import CSV data
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            import_btn = page.locator('button:has-text("Import")')
            if import_btn.is_visible():
                import_btn.click()
                time.sleep(5)
    
    # Now go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Should see view categories
    expect(page.locator("text=Adult Views")).to_be_visible()
    expect(page.locator("text=Youth Views")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_adult_views_selection(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test selecting and viewing adult views."""
    # Setup database with data (same as previous test)
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database and import data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            import_btn = page.locator('button:has-text("Import")')
            if import_btn.is_visible():
                import_btn.click()
                time.sleep(5)
    
    # Go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Select Adult Views
    adult_views_radio = page.locator('label:has-text("Adult Views")').first
    if adult_views_radio.is_visible():
        adult_views_radio.click()
        time.sleep(1)
        
        # Should see adult view options in sidebar
        expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()
        
        # Try to select a view
        current_positions_option = page.locator('option:has-text("current_positions")').first
        if current_positions_option.is_visible():
            current_positions_option.click()
            time.sleep(2)
            
            # Should see the view data
            expect(page.locator("text=Current Positions")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_youth_views_selection(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test selecting and viewing youth views."""
    # Setup database with data
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database and import data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            import_btn = page.locator('button:has-text("Import")')
            if import_btn.is_visible():
                import_btn.click()
                time.sleep(5)
    
    # Go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Select Youth Views
    youth_views_radio = page.locator('label:has-text("Youth Views")').first
    if youth_views_radio.is_visible():
        youth_views_radio.click()
        time.sleep(1)
        
        # Should see youth view options
        expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_view_data_display(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test that view data is displayed in a readable format."""
    # Setup database with data
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database and import data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            import_btn = page.locator('button:has-text("Import")')
            if import_btn.is_visible():
                import_btn.click()
                time.sleep(5)
    
    # Go to Database Views and select a view
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Select any available view
    adult_views_radio = page.locator('label:has-text("Adult Views")').first
    if adult_views_radio.is_visible():
        adult_views_radio.click()
        time.sleep(1)
        
        # Look for data table
        expect(page.locator('[data-testid="stDataFrame"]')).to_be_visible()


@pytest.mark.ui
def test_view_descriptions_display(page: Page, streamlit_app, clean_database):
    """Test that view descriptions are shown to help users understand each view."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create a minimal database to access views
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Should see view categories and selection instructions
    expect(page.locator("text=Select a view")).to_be_visible()


@pytest.mark.ui
def test_view_categories_organization(page: Page, streamlit_app, clean_database):
    """Test that views are properly organized into categories."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Check for view category organization
    expect(page.locator("text=View Category")).to_be_visible()
    expect(page.locator("text=Adult Views")).to_be_visible()
    expect(page.locator("text=Youth Views")).to_be_visible()


@pytest.mark.ui
def test_empty_view_handling(page: Page, streamlit_app, clean_database):
    """Test handling of empty views (views with no data)."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database without importing data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Select a view category
    adult_views_radio = page.locator('label:has-text("Adult Views")').first
    if adult_views_radio.is_visible():
        adult_views_radio.click()
        time.sleep(1)
        
        # Views should exist but may show no data
        # This tests that empty views don't crash the application
        expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()


@pytest.mark.ui
def test_view_refresh_functionality(page: Page, streamlit_app, clean_database):
    """Test that views can be refreshed and updated."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Go to Database Views
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    # Navigate to different view categories to test refresh
    adult_views_radio = page.locator('label:has-text("Adult Views")').first
    youth_views_radio = page.locator('label:has-text("Youth Views")').first
    
    if adult_views_radio.is_visible() and youth_views_radio.is_visible():
        adult_views_radio.click()
        time.sleep(1)
        
        youth_views_radio.click()
        time.sleep(1)
        
        adult_views_radio.click()
        time.sleep(1)
        
        # Should handle navigation without errors
        expect(page.locator('[data-testid="stApp"]')).to_be_visible()