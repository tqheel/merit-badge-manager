#!/usr/bin/env python3
"""
Test Manual MBC Matcher functionality.

Tests the manual matching of unmatched MBC names to adult roster entries,
including fuzzy matching, confidence scoring, and audit trail functionality.

Author: GitHub Copilot
Issue: #32
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
import sys

# Add the database-access layer to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))

from manual_mbc_matcher import ManualMBCMatcher
from setup_database import create_database_schema


class TestManualMBCMatcher:
    """Test suite for ManualMBCMatcher class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        # Create temporary database file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
        os.close(temp_fd)
        
        try:
            # Create database schema
            create_database_schema(temp_path, include_youth=True)
            
            # Add test data
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            # Add test adults
            cursor.execute("""
                INSERT INTO adults (first_name, last_name, email, bsa_number)
                VALUES 
                ('John', 'Smith', 'john.smith@example.com', 101001),
                ('Sarah', 'Johnson', 'sarah.j@example.com', 101002),
                ('Mike', 'Wilson', 'mike.wilson@example.com', 101003),
                ('Lisa', 'Davis', 'lisa.davis@example.com', 101004)
            """)
            
            # Add test merit badge counselor assignments
            cursor.execute("""
                INSERT INTO adult_merit_badges (adult_id, merit_badge_name)
                VALUES 
                (1, 'First Aid'),
                (1, 'Camping'),
                (2, 'Cooking'),
                (2, 'Swimming'),
                (3, 'Electronics'),
                (4, 'Environmental Science')
            """)
            
            # Add test unmatched MBC names
            cursor.execute("""
                INSERT INTO unmatched_mbc_names (mbc_name_raw, occurrence_count)
                VALUES 
                ('J. Smith', 3),
                ('Mike Johnson', 2),
                ('S. Johnson', 1),
                ('Invalid Name', 1)
            """)
            
            # Add test merit badge progress with unmatched names
            cursor.execute("""
                INSERT INTO merit_badge_progress 
                (scout_bsa_number, scout_first_name, scout_last_name, merit_badge_name, mbc_name_raw, requirements_raw)
                VALUES 
                ('12345678', 'John', 'Doe', 'First Aid', 'J. Smith', 'Requirements 1, 2 complete'),
                ('12345679', 'Jane', 'Smith', 'Camping', 'J. Smith', 'Requirements 1, 3, 5 complete'),
                ('12345680', 'Bob', 'Wilson', 'Cooking', 'Mike Johnson', 'Requirements 1-4 complete'),
                ('12345681', 'Alice', 'Brown', 'Swimming', 'S. Johnson', 'Requirements 1, 2, 6 complete')
            """)
            
            conn.commit()
            conn.close()
            
            yield temp_path
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_initialization(self, temp_db):
        """Test ManualMBCMatcher initialization."""
        matcher = ManualMBCMatcher(temp_db)
        assert matcher.db_path == temp_db
        assert matcher.logger is not None
    
    def test_get_unmatched_mbc_names(self, temp_db):
        """Test retrieval of unmatched MBC names."""
        matcher = ManualMBCMatcher(temp_db)
        unmatched = matcher.get_unmatched_mbc_names()
        
        # Should find all unmatched names
        assert len(unmatched) >= 3
        
        # Check structure of returned data
        for item in unmatched:
            assert 'mbc_name_raw' in item
            assert 'assignment_count' in item
            assert 'merit_badges' in item
            assert 'scouts' in item
        
        # Check that items are ordered by assignment count (descending)
        counts = [item['assignment_count'] for item in unmatched]
        assert counts == sorted(counts, reverse=True)
    
    def test_get_potential_adult_matches(self, temp_db):
        """Test fuzzy matching to find potential adult matches."""
        matcher = ManualMBCMatcher(temp_db)
        
        # Test exact-ish match
        matches = matcher.get_potential_adult_matches('J. Smith')
        assert len(matches) > 0
        
        # Should find John Smith with high confidence
        john_smith_match = next((m for m in matches if m['first_name'] == 'John' and m['last_name'] == 'Smith'), None)
        assert john_smith_match is not None
        assert john_smith_match['confidence_score'] > 0.8  # Should be high confidence
        
        # Test partial match
        matches = matcher.get_potential_adult_matches('Mike Johnson')
        assert len(matches) > 0
        
        # Should find some matches (maybe Sarah Johnson, Mike Wilson)
        assert any(m['confidence_score'] > 0.4 for m in matches)
        
        # Test no match
        matches = matcher.get_potential_adult_matches('Completely Unknown Name')
        # May return some low-confidence matches or empty list
        assert isinstance(matches, list)
    
    def test_record_manual_match(self, temp_db):
        """Test recording a manual match decision."""
        matcher = ManualMBCMatcher(temp_db)
        
        # Test successful match
        success = matcher.record_manual_match(
            unmatched_mbc_name='J. Smith',
            match_action='matched',
            matched_adult_id=1,
            confidence_score=0.85,
            user_name='Test User',
            notes='Test match'
        )
        
        assert success is True
        
        # Verify the match was recorded in the database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check mbc_manual_matches table
        cursor.execute("""
            SELECT * FROM mbc_manual_matches 
            WHERE unmatched_mbc_name = ? AND match_action = ?
        """, ('J. Smith', 'matched'))
        
        match_record = cursor.fetchone()
        assert match_record is not None
        
        # Check that unmatched_mbc_names was updated
        cursor.execute("""
            SELECT manual_match_adult_id, is_resolved 
            FROM unmatched_mbc_names 
            WHERE mbc_name_raw = ?
        """, ('J. Smith',))
        
        unmatched_record = cursor.fetchone()
        assert unmatched_record[0] == 1  # matched_adult_id
        assert unmatched_record[1] == 1  # is_resolved
        
        # Check that merit_badge_progress was updated
        cursor.execute("""
            SELECT mbc_adult_id, mbc_match_confidence 
            FROM merit_badge_progress 
            WHERE mbc_name_raw = ?
        """, ('J. Smith',))
        
        progress_records = cursor.fetchall()
        assert len(progress_records) > 0
        for record in progress_records:
            assert record[0] == 1  # mbc_adult_id
            assert record[1] == 0.85  # mbc_match_confidence
        
        conn.close()
    
    def test_record_skip_action(self, temp_db):
        """Test recording a skip action."""
        matcher = ManualMBCMatcher(temp_db)
        
        success = matcher.record_manual_match(
            unmatched_mbc_name='Mike Johnson',
            match_action='skipped',
            user_name='Test User',
            notes='Will review later'
        )
        
        assert success is True
        
        # Verify the skip was recorded
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT match_action, notes FROM mbc_manual_matches 
            WHERE unmatched_mbc_name = ?
        """, ('Mike Johnson',))
        
        record = cursor.fetchone()
        assert record[0] == 'skipped'
        assert 'Will review later' in record[1]
        
        conn.close()
    
    def test_record_invalid_action(self, temp_db):
        """Test recording an invalid name action."""
        matcher = ManualMBCMatcher(temp_db)
        
        success = matcher.record_manual_match(
            unmatched_mbc_name='Invalid Name',
            match_action='marked_invalid',
            user_name='Test User',
            notes='Not a real MBC'
        )
        
        assert success is True
        
        # Verify the invalid action was recorded
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT match_action, notes FROM mbc_manual_matches 
            WHERE unmatched_mbc_name = ?
        """, ('Invalid Name',))
        
        record = cursor.fetchone()
        assert record[0] == 'marked_invalid'
        assert 'Not a real MBC' in record[1]
        
        conn.close()
    
    def test_undo_manual_match(self, temp_db):
        """Test undoing a previous manual match decision."""
        matcher = ManualMBCMatcher(temp_db)
        
        # First, create a match to undo
        matcher.record_manual_match(
            unmatched_mbc_name='S. Johnson',
            match_action='matched',
            matched_adult_id=2,
            confidence_score=0.75,
            user_name='Test User',
            notes='Initial match'
        )
        
        # Now undo it
        success = matcher.undo_manual_match('S. Johnson', 'Test User')
        assert success is True
        
        # Verify the undo was recorded
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT match_action FROM mbc_manual_matches 
            WHERE unmatched_mbc_name = ? 
            ORDER BY created_at DESC
            LIMIT 1
        """, ('S. Johnson',))
        
        latest_record = cursor.fetchone()
        assert latest_record[0] == 'undone'
        
        # Verify unmatched_mbc_names was reset
        cursor.execute("""
            SELECT manual_match_adult_id, is_resolved 
            FROM unmatched_mbc_names 
            WHERE mbc_name_raw = ?
        """, ('S. Johnson',))
        
        unmatched_record = cursor.fetchone()
        assert unmatched_record[0] is None  # manual_match_adult_id reset
        assert unmatched_record[1] == 0  # is_resolved reset
        
        conn.close()
    
    def test_get_matching_statistics(self, temp_db):
        """Test retrieval of matching statistics."""
        matcher = ManualMBCMatcher(temp_db)
        
        # Add some manual matches first
        matcher.record_manual_match('J. Smith', 'matched', 1, 0.85, 'User1', 'Test match')
        matcher.record_manual_match('Mike Johnson', 'skipped', user_name='User1', notes='Skip test')
        matcher.record_manual_match('Invalid Name', 'marked_invalid', user_name='User2', notes='Invalid test')
        
        stats = matcher.get_matching_statistics()
        
        # Check overall statistics
        assert 'total_unmatched' in stats
        assert 'manually_matched' in stats
        assert 'skipped' in stats
        assert 'marked_invalid' in stats
        assert 'unresolved' in stats
        assert 'total_assignments' in stats
        
        # Check user activity
        assert 'user_activity' in stats
        assert isinstance(stats['user_activity'], list)
        
        # Should have entries for User1 and User2
        user_names = [activity['user_name'] for activity in stats['user_activity']]
        assert 'User1' in user_names
        assert 'User2' in user_names
    
    def test_confidence_indicators(self, temp_db):
        """Test confidence indicator functions."""
        matcher = ManualMBCMatcher(temp_db)
        
        # Test color indicators
        assert matcher.get_confidence_color(0.95) == "green"
        assert matcher.get_confidence_color(0.85) == "orange"
        assert matcher.get_confidence_color(0.65) == "red"
        assert matcher.get_confidence_color(0.35) == "gray"
        
        # Test emoji indicators
        assert matcher.get_confidence_emoji(0.95) == "🟢"
        assert matcher.get_confidence_emoji(0.85) == "🟡"
        assert matcher.get_confidence_emoji(0.65) == "🟠"
        assert matcher.get_confidence_emoji(0.35) == "🔴"
    
    def test_fuzzy_matching_algorithms(self, temp_db):
        """Test that fuzzy matching uses multiple algorithms correctly."""
        matcher = ManualMBCMatcher(temp_db)
        
        # Test with a name that should use different fuzzy algorithms
        matches = matcher.get_potential_adult_matches('Johnny Smith')  # Should match John Smith
        
        # Should find at least one match
        assert len(matches) > 0
        
        # The best match should have reasonable confidence
        best_match = matches[0]  # Should be sorted by confidence
        assert best_match['confidence_score'] > 0.4
        
        # Test with reversed name order
        matches = matcher.get_potential_adult_matches('Smith, John')
        assert len(matches) > 0
        
        # Should still find John Smith
        john_match = next((m for m in matches if 'John' in m['full_name'] and 'Smith' in m['full_name']), None)
        assert john_match is not None
    
    def test_merit_badge_context_in_matches(self, temp_db):
        """Test that merit badge information is included in potential matches."""
        matcher = ManualMBCMatcher(temp_db)
        
        matches = matcher.get_potential_adult_matches('J. Smith')
        
        for match in matches:
            assert 'merit_badges' in match
            assert 'full_name' in match
            assert 'confidence_score' in match
            assert 'id' in match
            assert 'email' in match
            assert 'bsa_number' in match
    
    def test_database_error_handling(self):
        """Test error handling for database operations."""
        # Test with non-existent database
        matcher = ManualMBCMatcher('/nonexistent/path/database.db')
        
        # Should return empty results rather than crash
        unmatched = matcher.get_unmatched_mbc_names()
        assert unmatched == []
        
        matches = matcher.get_potential_adult_matches('Test Name')
        assert matches == []
        
        success = matcher.record_manual_match('Test', 'matched', 1, 0.8, 'User')
        assert success is False
        
        stats = matcher.get_matching_statistics()
        assert stats == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])