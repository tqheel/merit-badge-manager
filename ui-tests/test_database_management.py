"""
Test database management functionality through the UI.
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path


@pytest.mark.ui
@pytest.mark.slow
def test_create_new_database_flow(page: Page, streamlit_app, clean_database):
    """Test creating a new database through the complete flow."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Verify no database exists initially
    expect(page.locator("text=No database found")).to_be_visible()
    
    # Click create new database
    create_btn = page.locator('button:has-text("Create New Database")')
    expect(create_btn).to_be_visible()
    create_btn.click()
    
    # Wait for database creation
    time.sleep(5)
    
    # Should see success message
    expect(page.locator("text=Database created successfully")).to_be_visible()
    
    # Database status should change
    expect(page.locator("text=Database exists")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_database_backup_and_restore(page: Page, streamlit_app, clean_database):
    """Test database backup and restore functionality."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Create a database first
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Create backup
    backup_btn = page.locator('button:has-text("Create Backup")')
    if backup_btn.is_visible():
        backup_btn.click()
        time.sleep(2)
        
        # Should see backup created message
        expect(page.locator("text=Backup created")).to_be_visible()
        
        # Should see backup information
        expect(page.locator("text=Current backup")).to_be_visible()
        
        # Test restore functionality
        restore_btn = page.locator('button:has-text("Restore from Backup")')
        if restore_btn.is_visible():
            restore_btn.click()
            time.sleep(3)
            
            # Should see restore success message
            expect(page.locator("text=Database restored")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_database_reset_functionality(page: Page, streamlit_app, clean_database):
    """Test database reset functionality."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Create a database first
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Reset database
    reset_btn = page.locator('button:has-text("Reset Database")')
    if reset_btn.is_visible():
        reset_btn.click()
        time.sleep(3)
        
        # Should see reset success message
        expect(page.locator("text=Database reset successfully")).to_be_visible()


@pytest.mark.ui
def test_database_status_display(page: Page, streamlit_app, clean_database):
    """Test that database status is correctly displayed."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Initially should show no database
    expect(page.locator("text=No database found")).to_be_visible()
    
    # Status indicators should be present
    expect(page.locator('text="Database Status"')).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_database_operations_with_data(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test database operations when database contains data."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database and import data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Create database
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
    
    # Import some data
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
    
    # Go back to database management
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Database should show as existing with data
    expect(page.locator("text=Database exists")).to_be_visible()
    
    # Test backup with data
    backup_btn = page.locator('button:has-text("Create Backup")')
    if backup_btn.is_visible():
        backup_btn.click()
        time.sleep(3)
        expect(page.locator("text=Backup created")).to_be_visible()


@pytest.mark.ui
def test_database_error_handling(page: Page, streamlit_app):
    """Test database error handling and user feedback."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Try to backup non-existent database
    backup_btn = page.locator('button:has-text("Create Backup")')
    if backup_btn.is_visible():
        backup_btn.click()
        time.sleep(2)
        
        # Should show appropriate error message
        expect(page.locator('[data-testid="stAlert"]')).to_be_visible()


@pytest.mark.ui
def test_database_management_ui_elements(page: Page, streamlit_app):
    """Test that all database management UI elements are present and functional."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Check for main UI elements
    expect(page.locator("text=Database Management")).to_be_visible()
    expect(page.locator("text=Database Status")).to_be_visible()
    
    # Check for action buttons
    expect(page.locator('button:has-text("Create New Database")')).to_be_visible()
    
    # Check for information displays
    expect(page.locator("text=Current Status")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_database_file_permissions(page: Page, streamlit_app, clean_database):
    """Test database operations respect file permissions."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Create database
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(5)
        
        # Verify database file was created
        db_path = Path("merit_badge_manager.db")
        assert db_path.exists()
        
        # Test that operations work with the created file
        backup_btn = page.locator('button:has-text("Create Backup")')
        if backup_btn.is_visible():
            backup_btn.click()
            time.sleep(3)
            expect(page.locator("text=Backup created")).to_be_visible()


@pytest.mark.ui
def test_database_management_accessibility(page: Page, streamlit_app):
    """Test database management page accessibility features."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Management page
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Check that buttons have accessible text
    buttons = page.locator('button')
    for i in range(buttons.count()):
        button = buttons.nth(i)
        if button.is_visible():
            text_content = button.text_content()
            # Buttons should have meaningful text
            assert len(text_content.strip()) > 0