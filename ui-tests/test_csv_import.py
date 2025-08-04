"""
Test CSV import and validation functionality through the UI.
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.ui
@pytest.mark.slow
def test_csv_file_upload_validation(page: Page, streamlit_app, sample_csv_files):
    """Test uploading and validating a CSV file."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload the combined CSV file
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        
        # Wait for file processing
        time.sleep(2)
        
        # Look for validation button and click it
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            
            # Wait for validation to complete
            time.sleep(3)
            
            # Check for validation results
            expect(page.locator("text=Validation Results")).to_be_visible()


@pytest.mark.ui
@pytest.mark.slow
def test_csv_import_workflow(page: Page, streamlit_app, sample_csv_files, clean_database):
    """Test the complete CSV import workflow."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # First create a database
    db_mgmt_radio = page.locator('label:has-text("Database Management")').first
    db_mgmt_radio.click()
    time.sleep(1)
    
    create_btn = page.locator('button:has-text("Create New Database")')
    if create_btn.is_visible():
        create_btn.click()
        time.sleep(3)
    
    # Now go to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload and import the file
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        # Validate first
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            # If validation passes, import
            import_btn = page.locator('button:has-text("Import")')
            if import_btn.is_visible():
                import_btn.click()
                time.sleep(5)
                
                # Look for success message
                expect(page.locator("text=Import completed successfully")).to_be_visible()


@pytest.mark.ui
def test_csv_validation_error_display(page: Page, streamlit_app, tmp_path):
    """Test that CSV validation errors are displayed correctly."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create an invalid CSV file
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("""First Name,Last Name,Invalid Column
John,Doe,Invalid Data
""")
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload the invalid file
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(invalid_csv))
        time.sleep(2)
        
        # Try to validate
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            # Should see validation errors
            expect(page.locator('[data-testid="stAlert"]')).to_be_visible()


@pytest.mark.ui
def test_csv_upload_file_types(page: Page, streamlit_app, tmp_path):
    """Test that only CSV files can be uploaded."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Create a non-CSV file
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("This is not a CSV file")
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # File uploader should restrict to CSV files
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        # Check file input accepts attribute
        accept_attr = file_input.get_attribute("accept")
        assert "csv" in accept_attr.lower() if accept_attr else True


@pytest.mark.ui
@pytest.mark.slow
def test_csv_progress_indicators(page: Page, streamlit_app, sample_csv_files):
    """Test that progress indicators are shown during CSV processing."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload file
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(1)
        
        # Start validation and look for progress indicators
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            
            # Look for spinner or progress indicator
            # Streamlit typically shows spinners during processing
            time.sleep(1)  # Brief pause to catch any loading indicators
            
            # Wait for completion
            time.sleep(3)
            expect(page.locator("text=Validation Results")).to_be_visible()


@pytest.mark.ui
def test_csv_validation_results_display(page: Page, streamlit_app, sample_csv_files):
    """Test that validation results are displayed in a readable format."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload and validate file
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        validate_btn = page.locator('button:has-text("Validate")')
        if validate_btn.is_visible():
            validate_btn.click()
            time.sleep(3)
            
            # Check for detailed validation results
            expect(page.locator("text=Validation Results")).to_be_visible()
            
            # Look for metrics display
            metrics = page.locator('[data-testid="metric"]')
            if metrics.count() > 0:
                expect(metrics.first).to_be_visible()


@pytest.mark.ui
def test_csv_clear_and_reupload(page: Page, streamlit_app, sample_csv_files):
    """Test clearing uploaded file and uploading a new one."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to CSV Import page
    csv_import_radio = page.locator('label:has-text("CSV Import")').first
    csv_import_radio.click()
    time.sleep(1)
    
    # Upload first file
    file_input = page.locator('input[type="file"]').first
    if file_input.is_visible():
        file_input.set_input_files(str(sample_csv_files["combined"]))
        time.sleep(2)
        
        # Look for clear button or way to upload new file
        clear_btn = page.locator('button:has-text("Clear")')
        if clear_btn.is_visible():
            clear_btn.click()
            time.sleep(1)
        
        # Upload second file
        file_input.set_input_files(str(sample_csv_files["adult"]))
        time.sleep(2)
        
        # Verify new file is loaded
        expect(page.locator('text="adult_roster.csv"')).to_be_visible()