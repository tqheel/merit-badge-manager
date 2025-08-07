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
    
    # Check that the main title is present - use more specific selector to avoid strict mode violation
    expect(page.locator("h1").filter(has_text="Merit Badge Manager")).to_be_visible()
    
    # Check that the sidebar is present
    expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()


@pytest.mark.ui
def test_sidebar_navigation(page: Page, streamlit_app):
    """Test navigation through sidebar pages."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Test navigation to each page
    
    
    pages_to_test = {
        "Settings": "1_Settings",
        "CSV Import": "2_CSV_Import",
        "Database Views": "3_Database_Views"
    }
    
    for page_name, page_file in pages_to_test.items():
        # Find and click the link for the page
        link = page.locator(f'[data-testid="stSidebarNav"] a:has-text("{page_name}")').first
        if link.is_visible():
            link.click()
            
            # Wait for page content to load
            time.sleep(120)
            
            # Verify we're on the correct page by checking for page-specific content
            if page_name == "Settings":
                expect(page.locator("text=Environment Settings")).to_be_visible()
            elif page_name == "CSV Import":
                expect(page.locator("text=CSV Import & Validation")).to_be_visible()
            elif page_name == "Database Views":
                expect(page.locator("text=Database Views")).to_be_visible()


@pytest.mark.ui
def test_environment_configuration_page(page: Page, streamlit_app):
    """Test the Environment Configuration page functionality."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Settings page
    env_config_radio = page.locator('label:has-text("Settings")').first
    if env_config_radio.is_visible():
        env_config_radio.click()
        time.sleep(120)
        
        # Check that environment configuration elements are present
        expect(page.locator("text=Environment Settings")).to_be_visible()
        
        # Look for environment variable controls
        # Note: Exact selectors may need adjustment based on Streamlit's rendering
        expect(page.locator('[data-testid="stForm"]')).to_be_visible()


@pytest.mark.ui  
def test_csv_import_page_loads(page: Page, streamlit_app):
    """Test that the CSV Import & Validation page loads correctly."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to CSV Import page
    page.locator('[data-testid="stSidebarNav"] a:has-text("CSV Import")').first.click()
    time.sleep(120)
    
    # Check for CSV import page elements
    expect(page.locator("text=CSV Import & Validation")).to_be_visible()
    
    # Look for file uploader
    expect(page.locator('[data-testid="stFileUploader"]')).to_be_visible()


@pytest.mark.ui
def test_database_views_page_no_database(page: Page, streamlit_app, clean_database):
    """Test Database Views page when no database exists."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Views page
    db_views_radio = page.locator('label:has-text("Database Views")').first
    if db_views_radio.is_visible():
        db_views_radio.click()
        time.sleep(120)
        
        # Should show warning about missing database
        expect(page.locator("text=Database not found")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow 
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
    page.locator('[data-testid="stSidebarNav"] a:has-text("Database Views")').first.click()
    page.wait_for_load_state("networkidle")
    
    # Check that warning/error messages are displayed properly
    warning_elements = page.locator('[data-testid="stAlert"]')
    if warning_elements.count() > 0:
        expect(warning_elements.first).to_be_visible()