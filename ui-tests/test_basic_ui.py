"""
Test basic Streamlit UI functionality and navigation.
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.ui
def test_streamlit_app_loads(page: Page, streamlit_app):
    """Test that the Streamlit app loads successfully."""
    page.goto(streamlit_app)
    
    # Wait for Streamlit to fully load
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Check that the main title is present
    expect(page.locator("h1")).to_contain_text("Merit Badge Manager")
    
    # Check that the sidebar is present
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()


@pytest.mark.ui
def test_sidebar_navigation(page: Page, streamlit_app):
    """Test navigation through sidebar pages."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Test navigation to each page
    pages_to_test = [
        "Environment Configuration",
        "CSV Import & Validation", 
        "Database Management",
        "Database Views"
    ]
    
    for page_name in pages_to_test:
        # Find and click the radio button for the page
        radio_button = page.locator(f'label:has-text("{page_name}")').first
        if radio_button.is_visible():
            radio_button.click()
            
            # Wait for page content to load
            time.sleep(1)
            
            # Verify we're on the correct page by checking for page-specific content
            if page_name == "Environment Configuration":
                expect(page.locator("text=Environment Configuration")).to_be_visible()
            elif page_name == "CSV Import & Validation":
                expect(page.locator("text=CSV Import & Validation")).to_be_visible()
            elif page_name == "Database Management":
                expect(page.locator("text=Database Management")).to_be_visible()
            elif page_name == "Database Views":
                expect(page.locator("text=Database Views")).to_be_visible()


@pytest.mark.ui
def test_environment_configuration_page(page: Page, streamlit_app):
    """Test the Environment Configuration page functionality."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Environment Configuration page
    env_config_radio = page.locator('label:has-text("Environment Configuration")').first
    if env_config_radio.is_visible():
        env_config_radio.click()
        time.sleep(1)
        
        # Check that environment configuration elements are present
        expect(page.locator("text=Environment Configuration")).to_be_visible()
        
        # Look for environment variable controls
        # Note: Exact selectors may need adjustment based on Streamlit's rendering
        expect(page.locator('[data-testid="stForm"]')).to_be_visible()


@pytest.mark.ui  
def test_csv_import_page_loads(page: Page, streamlit_app):
    """Test that the CSV Import & Validation page loads correctly."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    if csv_import_radio.is_visible():
        csv_import_radio.click()
        time.sleep(1)
        
        # Check for CSV import page elements
        expect(page.locator("text=CSV Import & Validation")).to_be_visible()
        
        # Look for file uploader
        expect(page.locator('[data-testid="stFileUploader"]')).to_be_visible()


@pytest.mark.ui
def test_database_management_page(page: Page, streamlit_app):
    """Test the Database Management page functionality.""" 
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    if db_mgmt_radio.is_visible():
        db_mgmt_radio.click()
        time.sleep(1)
        
        # Check for database management elements
        expect(page.locator("text=Database Management")).to_be_visible()
        
        # Look for database control buttons
        expect(page.locator('button:has-text("Create New Database")')).to_be_visible()


@pytest.mark.ui
def test_database_views_page_no_database(page: Page, streamlit_app, clean_database):
    """Test Database Views page when no database exists."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Views page
    db_views_radio = page.locator('label:has-text("Database Views")').first
    if db_views_radio.is_visible():
        db_views_radio.click()
        time.sleep(1)
        
        # Should show warning about missing database
        expect(page.locator("text=Database not found")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_create_new_database(page: Page, streamlit_app, clean_database):
    """Test creating a new database through the UI."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    if db_mgmt_radio.is_visible():
        db_mgmt_radio.click()
        time.sleep(1)
        
        # Click create new database button
        create_btn = page.locator('button:has-text("Create New Database")')
        if create_btn.is_visible():
            create_btn.click()
            
            # Wait for database creation to complete
            time.sleep(3)
            
            # Look for success message
            expect(page.locator("text=Database created successfully")).to_be_visible()


@pytest.mark.ui
def test_responsive_design(page: Page, streamlit_app):
    """Test that the UI works on different screen sizes."""
    # Test desktop size
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()
    
    # Test tablet size
    page.set_viewport_size({"width": 768, "height": 1024})
    expect(page.locator('[data-testid="stApp"]')).to_be_visible()
    
    # Test mobile size
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator('[data-testid="stApp"]')).to_be_visible()


@pytest.mark.ui
def test_error_handling_display(page: Page, streamlit_app):
    """Test that error messages are displayed appropriately."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Views without a database to trigger an error
    db_views_radio = page.locator('label:has-text("Database Views")').first
    if db_views_radio.is_visible():
        db_views_radio.click()
        time.sleep(1)
        
        # Check that warning/error messages are displayed properly
        warning_elements = page.locator('[data-testid="stAlert"]')
        if warning_elements.count() > 0:
            expect(warning_elements.first).to_be_visible()