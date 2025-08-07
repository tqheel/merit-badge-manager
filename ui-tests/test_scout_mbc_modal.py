"""
Test Scout MBC Modal functionality.

Tests for Issue #37: View Scout's MBCs and Workload in Modal
"""

import pytest
from playwright.sync_api import Page, expect
import time
import sqlite3
from pathlib import Path


@pytest.fixture
def sample_data_loaded(create_test_db):
    """Load sample data for testing the Scout MBC modal functionality."""
    db_path = "merit_badge_manager.db"
    
    # Create the database schema first
    from database.setup_database import create_database_schema
    create_database_schema(db_path, include_youth=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add sample adults (MBCs)
        cursor.execute('''
        INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number)
        VALUES 
            ('John', 'Smith', 'john.smith@example.com', '12345', 101),
            ('Mary', 'Johnson', 'mary.johnson@example.com', '23456', 101),
            ('Bob', 'Wilson', 'bob.wilson@example.com', '34567', 101)
        ''')
        
        # Add sample scouts
        cursor.execute('''
        INSERT INTO scouts (first_name, last_name, bsa_number, rank, patrol_name, unit_number, activity_status)
        VALUES 
            ('Tom', 'Anderson', 98001, 'Eagle', 'Eagle Patrol', 101, 'Active'),
            ('Sarah', 'Brown', 98002, 'Life', 'Tiger Patrol', 101, 'Active'),
            ('Mike', 'Davis', 98003, 'Star', 'Wolf Patrol', 101, 'Active')
        ''')
        
        # Add sample merit badge progress with different statuses
        cursor.execute('''
        INSERT INTO merit_badge_progress (scout_id, mbc_adult_id, scout_first_name, scout_last_name, scout_bsa_number, scout_rank, merit_badge_name, merit_badge_year, mbc_name_raw, requirements_raw, date_completed)
        VALUES 
            (1, 1, 'Tom', 'Anderson', 98001, 'Eagle', 'Camping', '2024', 'John Smith', 'Requirements 1-3 completed', NULL),
            (1, 2, 'Tom', 'Anderson', 98001, 'Eagle', 'Hiking', '2024', 'Mary Johnson', 'Requirements 1-5 completed', NULL),
            (1, 1, 'Tom', 'Anderson', 98001, 'Eagle', 'First Aid', '2024', 'John Smith', 'All requirements complete', '2024-01-15'),
            (2, 1, 'Sarah', 'Brown', 98002, 'Life', 'Camping', '2024', 'John Smith', 'Requirements 1-2 completed', NULL),
            (2, 3, 'Sarah', 'Brown', 98002, 'Life', 'Cooking', '2024', 'Bob Wilson', 'No Requirements Complete', NULL),
            (3, 2, 'Mike', 'Davis', 98003, 'Star', 'Hiking', '2024', 'Mary Johnson', 'Requirements 1-4 completed', NULL)
        ''')
        
        conn.commit()
        
    finally:
        conn.close()
    
    yield
    
    # Cleanup
    if Path(db_path).exists():
        Path(db_path).unlink()


@pytest.mark.ui
def test_scout_modal_opens_from_roster(page: Page, streamlit_app, sample_data_loaded):
    """Test that clicking a Scout in the roster opens the modal."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to Database Views -> Youth Views -> Active Scouts
    page.click('label:has-text("Database Views")')
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Wait for the scouts roster to load
    expect(page.locator("text=Click on a Scout name to view their MBC assignments")).to_be_visible()
    
    # Click on Tom Anderson
    page.click('button:has-text("👤 Tom Anderson")')
    time.sleep(120)
    
    # Verify the modal opened
    expect(page.locator("text=🎯 MBC Assignments for Tom Anderson")).to_be_visible()
    expect(page.locator("text=Scout: Tom Anderson (BSA #98001)")).to_be_visible()


@pytest.mark.ui 
def test_scout_modal_displays_correct_mbc_data(page: Page, streamlit_app, sample_data_loaded):
    """Test that the modal displays all MBCs for the selected Scout with correct workload data."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster
    page.locator('a[href*="3_Database_Views"]').first.click()
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Click on Tom Anderson (who has 3 merit badge assignments with 2 MBCs)
    page.click('button:has-text("👤 Tom Anderson")')
    time.sleep(120)
    
    # Verify modal shows correct summary
    expect(page.locator("text=Total MBCs: 2")).to_be_visible()
    expect(page.locator("text=Total Merit Badge Assignments: 3")).to_be_visible()
    
    # Verify John Smith MBC section is shown (has 2 merit badges with Tom)
    expect(page.locator("text=👤 John Smith - john.smith@example.com")).to_be_visible()
    
    # Verify Mary Johnson MBC section is shown (has 1 merit badge with Tom)
    expect(page.locator("text=👤 Mary Johnson - mary.johnson@example.com")).to_be_visible()
    
    # Verify MBC workload data is displayed
    expect(page.locator("text=📊 MBC Current Workload")).to_be_visible()
    expect(page.locator("text=Total Scouts")).to_be_visible()
    expect(page.locator("text=Active Assignments")).to_be_visible()
    expect(page.locator("text=Completed Assignments")).to_be_visible()
    expect(page.locator("text=Merit Badges")).to_be_visible()


@pytest.mark.ui
def test_scout_modal_shows_merit_badge_details(page: Page, streamlit_app, sample_data_loaded):
    """Test that the modal shows merit badge details for each MBC."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster and open Tom Anderson's modal
    page.locator('[data-testid="stSidebarNav"] a:has-text("Database Views")').first.click()
    page.wait_for_load_state("networkidle")
    page.click('label:has-text("Youth Views")')
    page.wait_for_load_state("networkidle")
    page.click('button:has-text("👤 Tom Anderson")')
    page.wait_for_load_state("networkidle")
    
    # Verify merit badge details are shown
    expect(page.locator("text=🏅 Merit Badges with Tom Anderson")).to_be_visible()
    expect(page.locator("text=Camping (2024)")).to_be_visible()
    expect(page.locator("text=Hiking (2024)")).to_be_visible()
    expect(page.locator("text=First Aid (2024)")).to_be_visible()
    
    # Verify status indicators
    expect(page.locator("text=In Progress")).to_be_visible()
    expect(page.locator("text=Completed")).to_be_visible()
    
    # Verify requirements are shown
    expect(page.locator("text=Requirements: Requirements 1-3 completed")).to_be_visible()
    expect(page.locator("text=Requirements: Requirements 1-5 completed")).to_be_visible()


@pytest.mark.ui
def test_scout_modal_closes_correctly(page: Page, streamlit_app, sample_data_loaded):
    """Test that clicking the Close button closes the modal."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster and open modal
    page.locator('[data-testid="stSidebarNav"] a:has-text("Database Views")').first.click()
    page.wait_for_load_state("networkidle")
    page.click('label:has-text("Youth Views")')
    page.wait_for_load_state("networkidle")
    page.click('button:has-text("👤 Sarah Brown")')
    page.wait_for_load_state("networkidle")
    
    # Verify modal is open
    expect(page.locator("text=🎯 MBC Assignments for Sarah Brown")).to_be_visible()
    
    # Click the Close button
    page.click('button:has-text("✖️ Close")')
    time.sleep(120)
    
    # Verify modal is closed and we're back to the roster
    expect(page.locator("text=🎯 MBC Assignments for Sarah Brown")).not_to_be_visible()
    expect(page.locator("text=Click on a Scout name to view their MBC assignments")).to_be_visible()
    expect(page.locator('button:has-text("👤 Sarah Brown")')).to_be_visible()


@pytest.mark.ui
def test_different_scouts_show_different_data(page: Page, streamlit_app, sample_data_loaded):
    """Test that different scouts show different MBC data in their modals."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster
    page.locator('a[href*="3_Database_Views"]').first.click()
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Test Sarah Brown (has 2 MBCs)
    page.click('button:has-text("👤 Sarah Brown")')
    time.sleep(120)
    
    expect(page.locator("text=🎯 MBC Assignments for Sarah Brown")).to_be_visible()
    expect(page.locator("text=Total MBCs: 2")).to_be_visible()
    expect(page.locator("text=Total Merit Badge Assignments: 2")).to_be_visible()
    expect(page.locator("text=👤 Bob Wilson - bob.wilson@example.com")).to_be_visible()
    
    # Close modal and test Mike Davis (has 1 MBC)
    page.click('button:has-text("✖️ Close")')
    time.sleep(120)
    
    page.click('button:has-text("👤 Mike Davis")')
    time.sleep(120)
    
    expect(page.locator("text=🎯 MBC Assignments for Mike Davis")).to_be_visible()
    expect(page.locator("text=Total MBCs: 1")).to_be_visible()
    expect(page.locator("text=Total Merit Badge Assignments: 1")).to_be_visible()
    expect(page.locator("text=👤 Mary Johnson - mary.johnson@example.com")).to_be_visible()


@pytest.mark.ui
def test_scout_modal_workload_numbers_accurate(page: Page, streamlit_app, sample_data_loaded):
    """Test that MBC workload numbers are accurate in the modal."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster and open Tom Anderson's modal
    page.locator('[data-testid="stSidebarNav"] a:has-text("Database Views")').first.click()
    page.wait_for_load_state("networkidle")
    page.click('label:has-text("Youth Views")')
    page.wait_for_load_state("networkidle")
    page.click('button:has-text("👤 Tom Anderson")')
    page.wait_for_load_state("networkidle")
    
    # Verify John Smith's workload (works with Tom and Sarah)
    john_smith_section = page.locator('text=👤 John Smith - john.smith@example.com').locator('xpath=following-sibling::*[1]')
    
    # John Smith should have: 2 total scouts (Tom, Sarah), 2 active, 1 completed, 2 merit badges (Camping, First Aid)
    expect(john_smith_section.locator("text=2").first).to_be_visible()  # Total Scouts
    
    # Close and check Mary Johnson with Mike Davis
    page.click('button:has-text("✖️ Close")')
    time.sleep(120)
    page.click('button:has-text("👤 Mike Davis")')
    time.sleep(120)
    
    # Mary Johnson should have: 2 total scouts (Tom, Mike), 2 active, 0 completed, 1 merit badge (Hiking)
    mary_section = page.locator('text=👤 Mary Johnson - mary.johnson@example.com').locator('xpath=following-sibling::*[1]')
    expect(mary_section.locator("text=2").first).to_be_visible()  # Total Scouts


@pytest.mark.ui
def test_scout_modal_accessibility_features(page: Page, streamlit_app, sample_data_loaded):
    """Test accessibility features of the Scout modal."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster
    page.locator('a[href*="3_Database_Views"]').first.click()
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Test that Scout buttons have proper aria labels or help text
    tom_button = page.locator('button:has-text("👤 Tom Anderson")')
    expect(tom_button).to_be_visible()
    
    # Open modal
    tom_button.click()
    time.sleep(120)
    
    # Test keyboard navigation to close button
    page.keyboard.press('Tab')
    page.keyboard.press('Tab')
    page.keyboard.press('Tab')
    
    # Find and test close button
    close_button = page.locator('button:has-text("✖️ Close")')
    expect(close_button).to_be_visible()
    expect(close_button).to_be_enabled()
    
    # Test that modal content is properly structured with headings
    expect(page.locator("h3:has-text('🎯 MBC Assignments for Tom Anderson')")).to_be_visible()
    expect(page.locator("h3:has-text('📊 MBC Current Workload')")).to_be_visible()
    expect(page.locator("h3:has-text('🏅 Merit Badges with Tom Anderson')")).to_be_visible()


@pytest.mark.ui
def test_scout_modal_handles_no_mbcs(page: Page, streamlit_app, clean_database):
    """Test that the modal handles scouts with no MBC assignments gracefully."""
    db_path = "merit_badge_manager.db"
    
    # Create database with only scouts, no merit badge progress
    from database.setup_database import create_database_schema
    create_database_schema(db_path, include_youth=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add only a scout with no MBC assignments
        cursor.execute('''
        INSERT INTO scouts (first_name, last_name, bsa_number, rank, patrol_name, unit_number, activity_status)
        VALUES ('Empty', 'Scout', 99999, 'Scout', 'Test Patrol', 101, 'Active')
        ''')
        conn.commit()
    finally:
        conn.close()
    
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster
    page.locator('a[href*="3_Database_Views"]').first.click()
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Click on the scout with no assignments
    page.click('button:has-text("👤 Empty Scout")')
    time.sleep(120)
    
    # Should show appropriate message
    expect(page.locator("text=No MBC assignments found for Empty Scout")).to_be_visible()
    expect(page.locator('button:has-text("Close")')).to_be_visible()
    
    # Close should work
    page.click('button:has-text("Close")')
    time.sleep(120)
    expect(page.locator("text=No MBC assignments found")).not_to_be_visible()
    
    # Cleanup
    if Path(db_path).exists():
        Path(db_path).unlink()