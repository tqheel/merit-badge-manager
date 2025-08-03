"""
Integration tests for complete user workflows through the UI.
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.ui
@pytest.mark.slow
def test_complete_data_import_workflow(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test the complete workflow from configuration to data import to viewing results."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Step 1: Configure environment (if needed)
    env_config_radio = page.locator('label:has-text("Environment Configuration")').first
    env_config_radio.click()
    time.sleep(1)
    
    # Check that configuration page loads
    expect(page.locator("text=Environment Configuration")).to_be_visible()
    
    # Step 2: Create database
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    create_btn.click()
    time.sleep(5)
    
    expect(page.locator("text=Database created successfully")).to_be_visible()
    
    # Step 3: Import CSV data
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    file_input.set_input_files(str(sample_csv_files["combined"]))
    time.sleep(2)
    
    # Validate
    validate_btn = page.locator('button:has-text("Validate")')
    validate_btn.click()
    time.sleep(3)
    
    expect(page.locator("text=Validation Results")).to_be_visible()
    
    # Import
    import_btn = page.locator('button:has-text("Import")')
    if import_btn.is_visible():
        import_btn.click()
        time.sleep(5)
        expect(page.locator("text=Import completed successfully")).to_be_visible()
    
    # Step 4: View the imported data
    db_views_radio = page.locator('label:has-text("Database Views")').first
    db_views_radio.click()
    time.sleep(1)
    
    expect(page.locator("text=Adult Views")).to_be_visible()
    expect(page.locator("text=Youth Views")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_data_management_workflow(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test database management workflow including backup and restore."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database and import data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    create_btn.click()
    time.sleep(5)
    
    # Import data
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    file_input.set_input_files(str(sample_csv_files["combined"]))
    time.sleep(2)
    
    validate_btn = page.locator('button:has-text("Validate")')
    validate_btn.click()
    time.sleep(3)
    
    import_btn = page.locator('button:has-text("Import")')
    if import_btn.is_visible():
        import_btn.click()
        time.sleep(5)
    
    # Go back to database management
    db_mgmt_radio.click()
    time.sleep(1)
    
    # Create backup
    backup_btn = page.locator('button:has-text("Create Backup")')
    if backup_btn.is_visible():
        backup_btn.click()
        time.sleep(3)
        expect(page.locator("text=Backup created")).to_be_visible()
    
    # Reset database
    reset_btn = page.locator('button:has-text("Reset Database")')
    if reset_btn.is_visible():
        reset_btn.click()
        time.sleep(3)
        expect(page.locator("text=Database reset successfully")).to_be_visible()
    
    # Restore from backup
    restore_btn = page.locator('button:has-text("Restore from Backup")')
    if restore_btn.is_visible():
        restore_btn.click()
        time.sleep(3)
        expect(page.locator("text=Database restored")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_error_recovery_workflow(page: Page, streamlit_app, tmp_path, clean_database):
    """Test error recovery workflows."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Try to import invalid CSV data
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Create invalid CSV
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("Invalid,CSV,Data\nMissing,Required,Columns")
    
    file_input = page.locator('input[type="file"]').first
    file_input.set_input_files(str(invalid_csv))
    time.sleep(2)
    
    # Try validation - should fail
    validate_btn = page.locator('button:has-text("Validate")')
    validate_btn.click()
    time.sleep(3)
    
    # Should see error messages
    expect(page.locator('[data-testid="stAlert"]')).to_be_visible()
    
    # Create database and try again with valid data
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    create_btn.click()
    time.sleep(5)
    
    # Application should recover and be functional
    expect(page.locator("text=Database created successfully")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_multi_user_simulation_workflow(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Simulate multiple user interactions to test session handling."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Simulate rapid navigation between pages (like multiple users clicking around)
    pages = [
        'label:has-text("Environment Configuration")',
        'label:has-text("CSV Import & Validation")',
        'label:has-text("Database Management")',
        'label:has-text("Database Views")'
    ]
    
    for _ in range(3):  # Cycle through pages multiple times
        for page_selector in pages:
            page_radio = page.locator(page_selector).first
            if page_radio.is_visible():
                page_radio.click()
                time.sleep(0.5)  # Quick navigation
    
    # Application should remain stable
    expect(page.locator('[data-testid="stApp"]')).to_be_visible()
    expect(page.locator("text=Merit Badge Manager")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_data_validation_and_correction_workflow(page: Page, streamlit_app, tmp_path, clean_database):
    """Test workflow of validating data, seeing errors, and correcting them."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create database first
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    create_btn.click()
    time.sleep(5)
    
    # Create CSV with potential issues
    problematic_csv = tmp_path / "problematic.csv"
    problematic_csv.write_text("""First Name,Last Name,BSA ID,Email,Position 1,Position 2,Position 3,Position 4,Position 5,Training Date,Patrol,Gender,Rank,Primary Parent/Guardian Name,Primary Parent/Guardian Email
John,Doe,12345678,john.doe@example.com,Scoutmaster,,,,,2023-01-15,Adult,M,,,
Jane,Smith,INVALID_ID,jane.smith@example.com,Committee Chair,,,,,2023-02-20,Adult,F,,,
Mike,Johnson,11111111,mike.johnson@example.com,,,,,,2023-03-10,Eagles,M,Eagle,Bob Johnson,bob.johnson@example.com
""")
    
    # Navigate to CSV Import
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload problematic file
    file_input = page.locator('input[type="file"]').first
    file_input.set_input_files(str(problematic_csv))
    time.sleep(2)
    
    # Validate and see errors
    validate_btn = page.locator('button:has-text("Validate")')
    validate_btn.click()
    time.sleep(3)
    
    # Should see validation results with errors
    expect(page.locator("text=Validation Results")).to_be_visible()
    
    # Create corrected file
    corrected_csv = tmp_path / "corrected.csv"
    corrected_csv.write_text("""First Name,Last Name,BSA ID,Email,Position 1,Position 2,Position 3,Position 4,Position 5,Training Date,Patrol,Gender,Rank,Primary Parent/Guardian Name,Primary Parent/Guardian Email
John,Doe,12345678,john.doe@example.com,Scoutmaster,,,,,2023-01-15,Adult,M,,,
Jane,Smith,87654321,jane.smith@example.com,Committee Chair,,,,,2023-02-20,Adult,F,,,
Mike,Johnson,11111111,mike.johnson@example.com,,,,,,2023-03-10,Eagles,M,Eagle,Bob Johnson,bob.johnson@example.com
""")
    
    # Upload corrected file
    file_input.set_input_files(str(corrected_csv))
    time.sleep(2)
    
    # Validate again
    validate_btn.click()
    time.sleep(3)
    
    # Should pass validation now
    import_btn = page.locator('button:has-text("Import")')
    if import_btn.is_visible():
        import_btn.click()
        time.sleep(5)
        expect(page.locator("text=Import completed successfully")).to_be_visible()


@pytest.mark.ui
def test_accessibility_workflow(page: Page, streamlit_app):
    """Test basic accessibility features across the application."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Test keyboard navigation
    page.keyboard.press("Tab")
    time.sleep(0.5)
    
    # Test with different viewport sizes
    viewports = [
        {"width": 1920, "height": 1080},  # Desktop
        {"width": 768, "height": 1024},   # Tablet
        {"width": 375, "height": 667}     # Mobile
    ]
    
    for viewport in viewports:
        page.set_viewport_size(viewport)
        time.sleep(1)
        
        # App should remain functional at all sizes
        expect(page.locator('[data-testid="stApp"]')).to_be_visible()
        expect(page.locator("text=Merit Badge Manager")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_performance_workflow(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test application performance with typical user workflows."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    start_time = time.time()
    
    # Perform typical user workflow quickly
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    create_btn.click()
    time.sleep(5)
    
    csv_import_radio = page.locator('label:has-text("CSV Import & Validation")').first
    csv_import_radio.click()
    time.sleep(1)
    
    file_input = page.locator('input[type="file"]').first
    file_input.set_input_files(str(sample_csv_files["combined"]))
    time.sleep(2)
    
    validate_btn = page.locator('button:has-text("Validate")')
    validate_btn.click()
    time.sleep(3)
    
    end_time = time.time()
    
    # Workflow should complete in reasonable time (less than 30 seconds)
    assert end_time - start_time < 30
    
    # Application should still be responsive
    expect(page.locator('[data-testid="stApp"]')).to_be_visible()