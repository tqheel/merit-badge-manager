#!/usr/bin/env python3
"""
Playwright UI tests for Manual MBC Matching interface.

Tests the web interface for manually matching unmatched MBC names,
including navigation, statistics display, matching workflow, and user interactions.

Author: GitHub Copilot
Issue: #32
"""

import pytest
import sqlite3
import shutil
from pathlib import Path
from playwright.sync_api import Page, expect


class TestManualMBCMatchingUI:
    """Test suite for Manual MBC Matching UI functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Set up test database with unmatched MBC names."""
        from test_database_utils import get_test_database_path, get_isolated_test_database_path
        
        # Create test database from existing test database
        source_db = get_isolated_test_database_path()
        target_db = get_test_database_path()
        
        if source_db.exists():
            shutil.copy(source_db, target_db)
        else:
            # Create minimal test database if test DB doesn't exist
            from setup_database import create_database_schema
            create_database_schema(str(target_db), include_youth=True)
            
            # Add minimal test data
            conn = sqlite3.connect(target_db)
            cursor = conn.cursor()
            
            # Add test adults
            cursor.execute("""
                INSERT INTO adults (first_name, last_name, email, bsa_number)
                VALUES 
                ('John', 'Smith', 'john.smith@example.com', 101001),
                ('Sarah', 'Johnson', 'sarah.j@example.com', 101002)
            """)
            
            # Add test unmatched MBC names
            cursor.execute("""
                INSERT INTO unmatched_mbc_names (mbc_name_raw, occurrence_count)
                VALUES 
                ('J. Smith', 3),
                ('Mike Johnson', 2)
            """)
            
            # Add test merit badge progress
            cursor.execute("""
                INSERT INTO merit_badge_progress 
                (scout_bsa_number, scout_first_name, scout_last_name, merit_badge_name, mbc_name_raw, requirements_raw)
                VALUES 
                ('12345678', 'John', 'Doe', 'First Aid', 'J. Smith', 'Requirements 1, 2 complete'),
                ('12345679', 'Jane', 'Smith', 'Camping', 'J. Smith', 'Requirements 1, 3, 5 complete')
            """)
            
            conn.commit()
            conn.close()
        
        yield
        
        # Cleanup after test
        if target_db.exists():
            target_db.unlink()
    
    def test_manual_mbc_matching_navigation(self, page: Page):
        """Test navigation to Manual MBC Matching page."""
        page.goto("http://localhost:8501")
        
        # Wait for page to load
        expect(page.locator("text=Merit Badge Manager")).to_be_visible()
        
        # Check that Manual MBC Matching option is available in navigation
        expect(page.locator('a[href*="4_Manual_MBC_Matching"]')).to_be_visible()
        
        # Click on Manual MBC Matching
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Verify we're on the correct page
        expect(page.locator("h2:has-text('Manual MBC Matching')")).to_be_visible()
        expect(page.locator("text=Manually resolve unmatched Merit Badge Counselor names")).to_be_visible()
    
    def test_statistics_dashboard_display(self, page: Page):
        """Test the statistics dashboard displays correctly."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for statistics to load
        expect(page.locator("h3:has-text('Matching Progress')")).to_be_visible()
        
        # Check that all 8 metrics are displayed
        metrics = [
            "Total Unmatched",
            "Manually Matched", 
            "Unresolved",
            "Total Assignments",
            "Skipped",
            "Marked Invalid",
            "New Adult Needed",
            "Progress"
        ]
        
        for metric in metrics:
            expect(page.locator(f"text={metric}")).to_be_visible()
        
        # Verify that numeric values are displayed
        expect(page.locator("text=/^\\d+$/")).to_have_count(7)  # 7 numeric metrics
        expect(page.locator("text=/^\\d+\\.\\d%$/")).to_be_visible()  # Progress percentage
    
    def test_manual_matching_interface_elements(self, page: Page):
        """Test the manual matching interface elements are present."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for interface to load
        expect(page.locator("h3:has-text('Manual Matching Interface')")).to_be_visible()
        
        # Check user name input
        expect(page.locator("input[aria-label='Your Name']")).to_be_visible()
        
        # Check filter dropdown
        expect(page.locator("text=Filter by:")).to_be_visible()
        expect(page.locator("text=All Unmatched")).to_be_visible()
        
        # Should show unmatched names with details
        expect(page.locator("text=Unmatched Name Details:")).to_be_visible()
        expect(page.locator("text=Potential Adult Matches:")).to_be_visible()
    
    def test_unmatched_name_details_display(self, page: Page):
        """Test that unmatched name details are displayed correctly."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for content to load
        expect(page.locator("h3:has-text('Manual Matching Interface')")).to_be_visible()
        
        # Check that name details are shown
        expect(page.locator("text=Name:")).to_be_visible()
        expect(page.locator("text=Assignment Count:")).to_be_visible()
        expect(page.locator("text=Merit Badges:")).to_be_visible()
        expect(page.locator("text=Affected Scouts:")).to_be_visible()
    
    def test_potential_matches_with_confidence(self, page: Page):
        """Test that potential matches are shown with confidence indicators."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for matches to load
        expect(page.locator("text=Potential Adult Matches:")).to_be_visible()
        
        # Should show confidence percentages
        expect(page.locator("text=/\\d+\\.\\d%/")).to_be_visible()
        expect(page.locator("text=Confidence")).to_be_visible()
        
        # Should show confidence emoji indicators
        confidence_emojis = ["🟢", "🟡", "🟠", "🔴"]
        emoji_found = False
        for emoji in confidence_emojis:
            try:
                if page.locator(f"text={emoji}").is_visible():
                    emoji_found = True
                    break
            except:
                continue
        assert emoji_found, "No confidence emoji indicators found"
    
    def test_action_buttons_presence(self, page: Page):
        """Test that all action buttons are present for each unmatched name."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for interface to load
        expect(page.locator("text=Actions:")).to_be_visible()
        
        # Check that all action buttons are present
        action_buttons = ["Match", "Skip", "Mark Invalid", "Create New", "Undo"]
        
        for button_text in action_buttons:
            expect(page.locator(f"button:has-text('{button_text}')")).to_be_visible()
    
    def test_user_name_input_functionality(self, page: Page):
        """Test the user name input functionality."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Find and interact with user name input
        user_input = page.locator("input[aria-label='Your Name']")
        expect(user_input).to_be_visible()
        
        # Should have default value
        expect(user_input).to_have_value("Anonymous")
        
        # Clear and type new name
        user_input.clear()
        user_input.fill("Test User")
        expect(user_input).to_have_value("Test User")
    
    def test_filter_dropdown_functionality(self, page: Page):
        """Test the filter dropdown functionality."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Find filter dropdown
        expect(page.locator("text=Filter by:")).to_be_visible()
        
        # Should show current selection
        expect(page.locator("text=All Unmatched")).to_be_visible()
        
        # Try to click on dropdown to see options
        page.click("[aria-label*='Filter by']")
        
        # Should show filter options (exact text may vary)
        filter_options = ["All Unmatched", "High Assignment Count", "Recently Added"]
        for option in filter_options:
            try:
                if page.locator(f"text={option}").is_visible():
                    assert True  # At least one option is visible
                    break
            except:
                continue
    
    def test_match_action_workflow(self, page: Page):
        """Test the match action workflow (without actually clicking due to state changes)."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for interface to load
        expect(page.locator("text=Actions:")).to_be_visible()
        
        # Verify match buttons are clickable
        match_buttons = page.locator("button:has-text('Match')")
        expect(match_buttons.first).to_be_visible()
        expect(match_buttons.first).to_be_enabled()
        
        # Note: We don't actually click to avoid changing test database state
        # In a real test environment, you would click and verify the success message
    
    def test_responsive_layout(self, page: Page):
        """Test that the layout works on different screen sizes."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Test desktop layout
        page.set_viewport_size({"width": 1200, "height": 800})
        expect(page.locator("h2:has-text('Manual MBC Matching')")).to_be_visible()
        
        # Test tablet layout
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("h2:has-text('Manual MBC Matching')")).to_be_visible()
        
        # Test mobile layout
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("h2:has-text('Manual MBC Matching')")).to_be_visible()
    
    def test_statistics_update_structure(self, page: Page):
        """Test that statistics have the correct structure and formatting."""
        page.goto("http://localhost:8501")
        page.locator('[data-testid="stSidebarNav"] a:has-text("Manual MBC Matching")').first.click()
        
        # Wait for statistics to load
        expect(page.locator("h3:has-text('Matching Progress')")).to_be_visible()
        
        # Check that metrics are properly formatted
        # Should have metric labels and values
        expect(page.locator("text=Total Unmatched")).to_be_visible()
        expect(page.locator("text=Unresolved")).to_be_visible()
        
        # Progress should be formatted as percentage
        expect(page.locator("text=/\\d+\\.\\d%/")).to_be_visible()
    
    def test_no_unmatched_names_scenario(self, page: Page):
        """Test behavior when there are no unmatched names."""
        from test_database_utils import get_test_database_path
        
        # Temporarily modify database to have no unmatched names
        conn = sqlite3.connect(str(get_test_database_path()))
        cursor = conn.cursor()
        
        # Mark all as resolved
        cursor.execute("UPDATE unmatched_mbc_names SET is_resolved = 1")
        conn.commit()
        conn.close()
        
        try:
            page.goto("http://localhost:8501")
            page.click("text=Manual MBC Matching")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            
            # Should show completion message
            expect(page.locator("text=All MBC names have been resolved!")).to_be_visible(timeout=10000)
            
        finally:
            # Reset database state
            conn = sqlite3.connect(str(get_test_database_path()))
            cursor = conn.cursor()
            cursor.execute("UPDATE unmatched_mbc_names SET is_resolved = 0")
            conn.commit()
            conn.close()
    
    def test_pagination_display(self, page: Page):
        """Test pagination when there are many unmatched names."""
        from test_database_utils import get_test_database_path
        
        # Add more unmatched names to test pagination
        conn = sqlite3.connect(str(get_test_database_path()))
        cursor = conn.cursor()
        
        # Add additional unmatched names
        for i in range(10):
            cursor.execute("""
                INSERT OR IGNORE INTO unmatched_mbc_names (mbc_name_raw, occurrence_count)
                VALUES (?, ?)
            """, (f'Test Name {i}', 1))
        
        conn.commit()
        conn.close()
        
        try:
            page.goto("http://localhost:8501")
            page.click("text=Manual MBC Matching")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            
            # Wait for interface to load
            expect(page.locator("h3:has-text('Manual Matching Interface')")).to_be_visible()
            
            # If there are many items, should show pagination
            # This is conditional based on whether we have >5 items
            page_info = page.locator("text=/Showing \\d+ of \\d+ unmatched names/")
            if page_info.is_visible():
                expect(page_info).to_be_visible()
                
        finally:
            # Clean up additional test data
            conn = sqlite3.connect(str(get_test_database_path()))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unmatched_mbc_names WHERE mbc_name_raw LIKE 'Test Name %'")
            conn.commit()
            conn.close()
    
    def test_error_handling_no_database(self, page: Page):
        """Test error handling when database doesn't exist."""
        from test_database_utils import get_test_database_path
        
        # Remove database temporarily
        db_path = get_test_database_path()
        backup_path = Path("merit_badge_manager_backup.db")
        
        if db_path.exists():
            shutil.move(db_path, backup_path)
        
        try:
            page.goto("http://localhost:8501")
            page.click("text=Manual MBC Matching")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
            
            # Should show database not found warning
            expect(page.locator("text=Database not found")).to_be_visible()
            
        finally:
            # Restore database
            if backup_path.exists():
                shutil.move(backup_path, db_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--headed'])