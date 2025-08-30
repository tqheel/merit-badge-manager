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
        
        # Add adult merit badges (counselor qualifications) 
        cursor.execute('''
        INSERT INTO adult_merit_badges (adult_id, merit_badge_name)
        VALUES 
            (1, 'Camping'),
            (1, 'First Aid'),
            (2, 'Hiking'), 
            (2, 'Cooking'),
            (3, 'Camping'),
            (3, 'Swimming')
        ''')
        
        # Add sample scouts
        cursor.execute('''
        INSERT INTO scouts (first_name, last_name, bsa_number, rank, patrol_name, unit_number, activity_status)
        VALUES 
            ('Tom', 'Anderson', 98001, 'Eagle', 'Eagle Patrol', 101, 'Active'),
            ('Sarah', 'Brown', 98002, 'Life', 'Tiger Patrol', 101, 'Active'),
            ('Mike', 'Davis', 98003, 'Star', 'Wolf Patrol', 101, 'Active')
        ''')
        
        # Add sample scout merit badge progress (using youth roster table) 
        cursor.execute('''
        INSERT INTO scout_merit_badge_progress (scout_id, merit_badge_name, counselor_adult_id, status, date_started, requirements_completed, notes)
        VALUES 
            -- Tom Anderson: mix of assigned and unassigned, only in-progress should show
            (1, 'Camping', 1, 'In Progress', '2024-01-01', 'Requirements 1-3 completed', 'Working with John'),
            (1, 'Hiking', 2, 'In Progress', '2024-02-01', 'Requirements 1-5 completed', 'Working with Mary'),
            (1, 'First Aid', 1, 'Completed', '2024-01-15', 'All requirements complete', 'Badge earned'),
            (1, 'Swimming', NULL, 'In Progress', '2024-03-01', 'Just started', 'Needs counselor assignment'),
            
            -- Sarah Brown: mix of statuses
            (2, 'Camping', 1, 'In Progress', '2024-02-15', 'Requirements 1-2 completed', 'Working with John'),
            (2, 'Cooking', NULL, 'In Progress', '2024-03-01', 'No Requirements Complete', 'Looking for counselor'),
            
            -- Mike Davis: has assignments
            (3, 'Hiking', 2, 'In Progress', '2024-01-01', 'Requirements 1-4 completed', 'Working with Mary')
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
    
    # Verify the modal opened with new title
    expect(page.locator("text=🎯 Merit Badges in Progress for Tom Anderson")).to_be_visible()


@pytest.mark.ui 
def test_scout_modal_displays_correct_in_progress_badges(page: Page, streamlit_app, sample_data_loaded):
    """Test that the modal displays only in-progress merit badges (not completed ones)."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster
    page.locator('a[href*="3_Database_Views"]').first.click()
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Click on Tom Anderson (who has 3 in-progress + 1 completed badge)
    page.click('button:has-text("👤 Tom Anderson")')
    time.sleep(120)
    
    # Verify modal shows correct title and count (should be 3 in-progress, not 4 total)
    expect(page.locator("text=🎯 Merit Badges in Progress for Tom Anderson")).to_be_visible()
    expect(page.locator("text=Merit Badges in Progress: 3")).to_be_visible()
    
    # Verify in-progress badges are shown
    expect(page.locator("text=🏅 Camping")).to_be_visible()
    expect(page.locator("text=🏅 Hiking")).to_be_visible()
    expect(page.locator("text=🏅 Swimming")).to_be_visible()
    
    # Verify completed badge (First Aid) is NOT shown
    expect(page.locator("text=🏅 First Aid")).not_to_be_visible()
    
    # Verify counselor assignment info
    expect(page.locator("text=👤 John Smith")).to_be_visible()  # Camping counselor
    expect(page.locator("text=👤 Mary Johnson")).to_be_visible()  # Hiking counselor
    expect(page.locator("text=⚠️ No counselor assigned")).to_be_visible()  # Swimming has no counselor


@pytest.mark.ui
def test_scout_modal_assign_counselor_button(page: Page, streamlit_app, sample_data_loaded):
    """Test that unassigned merit badges show the 'Assign Counselor' button."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster and open Tom Anderson's modal
    page.locator('[data-testid="stSidebarNav"] a:has-text("Database Views")').first.click()
    page.wait_for_load_state("networkidle")
    page.click('label:has-text("Youth Views")')
    page.wait_for_load_state("networkidle")
    page.click('button:has-text("👤 Tom Anderson")')
    page.wait_for_load_state("networkidle")
    
    # Verify Swimming badge has no counselor and shows assign button
    expect(page.locator("text=🏅 Swimming")).to_be_visible()
    expect(page.locator("text=⚠️ No counselor assigned")).to_be_visible()
    expect(page.locator("text=🔗 Assign Counselor")).to_be_visible()
    
    # Verify assigned badges don't show the assign button (they show counselor info instead)
    expect(page.locator("text=👤 John Smith")).to_be_visible()  # Camping has counselor
    expect(page.locator("text=👤 Mary Johnson")).to_be_visible()  # Hiking has counselor


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
    
    # Verify the modal opened with new title
    expect(page.locator("text=🎯 Merit Badges in Progress for Sarah Brown")).to_be_visible()
    
    # Click the Close button
    page.click('button:has-text("✖️ Close")')
    time.sleep(120)
    
    # Verify modal is closed and we're back to the roster
    expect(page.locator("text=🎯 Merit Badges in Progress for Sarah Brown")).not_to_be_visible()
    expect(page.locator("text=Click on a Scout name to view their MBC assignments")).to_be_visible()
    expect(page.locator('button:has-text("👤 Sarah Brown")')).to_be_visible()


@pytest.mark.ui
def test_different_scouts_show_different_data(page: Page, streamlit_app, sample_data_loaded):
    """Test that different scouts show different in-progress merit badge data."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster
    page.locator('a[href*="3_Database_Views"]').first.click()
    time.sleep(120)
    page.click('label:has-text("Youth Views")')
    time.sleep(120)
    
    # Test Sarah Brown (has 2 in-progress badges)
    page.click('button:has-text("👤 Sarah Brown")')
    time.sleep(120)
    
    expect(page.locator("text=🎯 Merit Badges in Progress for Sarah Brown")).to_be_visible()
    expect(page.locator("text=Merit Badges in Progress: 2")).to_be_visible()
    expect(page.locator("text=🏅 Camping")).to_be_visible()
    expect(page.locator("text=🏅 Cooking")).to_be_visible()
    
    # Close modal and test Mike Davis (has 1 in-progress badge)
    page.click('button:has-text("✖️ Close")')
    time.sleep(120)
    
    page.click('button:has-text("👤 Mike Davis")')
    time.sleep(120)
    
    expect(page.locator("text=🎯 Merit Badges in Progress for Mike Davis")).to_be_visible()
    expect(page.locator("text=Merit Badges in Progress: 1")).to_be_visible()
    expect(page.locator("text=🏅 Hiking")).to_be_visible()
    expect(page.locator("text=👤 Mary Johnson")).to_be_visible()



@pytest.mark.ui
def test_scout_modal_handles_no_in_progress_badges(page: Page, streamlit_app, clean_database):
    """Test that the modal handles scouts with no in-progress merit badges gracefully."""
    db_path = "merit_badge_manager.db"
    
    # Create database with scout that has only completed badges
    from database.setup_database import create_database_schema
    create_database_schema(db_path, include_youth=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add scout with only completed merit badges (no in-progress)
        cursor.execute('''
        INSERT INTO scouts (first_name, last_name, bsa_number, rank, patrol_name, unit_number, activity_status)
        VALUES ('Empty', 'Scout', 99999, 'Scout', 'Test Patrol', 101, 'Active')
        ''')
        
        cursor.execute('''
        INSERT INTO scout_merit_badge_progress (scout_id, merit_badge_name, counselor_adult_id, status, date_completed)
        VALUES (1, 'Swimming', 1, 'Completed', '2024-01-01')
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
    
    # Click on the scout with no in-progress badges
    page.click('button:has-text("👤 Empty Scout")')
    time.sleep(120)
    
    # Should show appropriate message
    expect(page.locator("text=No Merit Badges in progress for Empty Scout")).to_be_visible()
    expect(page.locator('button:has-text("Close")')).to_be_visible()
    
    # Close should work
    page.click('button:has-text("Close")')
    time.sleep(120)
    expect(page.locator("text=No Merit Badges in progress")).not_to_be_visible()
    
    # Cleanup
    if Path(db_path).exists():
        Path(db_path).unlink()


@pytest.mark.ui
def test_counselor_assignment_workflow(page: Page, streamlit_app, sample_data_loaded):
    """Test the counselor assignment workflow for unassigned merit badges."""
    page.goto(streamlit_app)
    page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
    
    # Navigate to scouts roster and open Tom Anderson's modal
    page.locator('[data-testid="stSidebarNav"] a:has-text("Database Views")').first.click()
    page.wait_for_load_state("networkidle")
    page.click('label:has-text("Youth Views")')
    page.wait_for_load_state("networkidle")
    page.click('button:has-text("👤 Tom Anderson")')
    page.wait_for_load_state("networkidle")
    
    # Find and click the "Assign Counselor" button for Swimming badge
    expect(page.locator("text=🏅 Swimming")).to_be_visible()
    expect(page.locator("text=🔗 Assign Counselor")).to_be_visible()
    page.click('button:has-text("🔗 Assign Counselor")')
    page.wait_for_load_state("networkidle")
    
    # Should now show counselor assignment interface
    expect(page.locator("text=🔗 Assign Counselor for Swimming")).to_be_visible()
    expect(page.locator("text=Available Counselors for Swimming")).to_be_visible()
    
    # Should show available counselors (Bob Wilson counsels Swimming)
    expect(page.locator("text=👤 Bob Wilson")).to_be_visible()
    
    # Should have back button to return to badges view
    expect(page.locator("text=← Back to Merit Badges")).to_be_visible()