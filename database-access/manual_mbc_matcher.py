#!/usr/bin/env python3
"""
Merit Badge Manager - Manual MBC Matching Functions

Provides functions for manually matching unmatched MBC names to adult roster entries.
Includes fuzzy matching with confidence scoring and audit trail functionality.

Author: GitHub Copilot
Issue: #32
"""

import sqlite3
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from fuzzywuzzy import fuzz, process
import logging


class ManualMBCMatcher:
    """
    Handles manual matching of unmatched MBC names to adult roster entries.
    
    Provides fuzzy matching with confidence scoring, manual decision tracking,
    and audit trail functionality.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the manual MBC matcher.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def get_unmatched_mbc_names(self) -> List[Dict]:
        """
        Get all unmatched MBC names that need manual resolution.
        
        Returns:
            List of dictionaries containing unmatched MBC information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT *
                FROM unmatched_mbc_assignments
                WHERE manual_match_status = 'Unresolved'
                ORDER BY assignment_count DESC, mbc_name_raw
            """)
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting unmatched MBC names: {e}")
            return []
    
    def get_potential_adult_matches(self, mbc_name_raw: str, limit: int = 10) -> List[Dict]:
        """
        Get potential adult matches for an unmatched MBC name using fuzzy matching.
        
        Args:
            mbc_name_raw: The raw MBC name to match
            limit: Maximum number of potential matches to return
            
        Returns:
            List of adult records with confidence scores
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all adults who could potentially be MBCs
            cursor.execute("""
                SELECT DISTINCT a.id, a.first_name, a.last_name, a.email, a.bsa_number,
                       GROUP_CONCAT(DISTINCT amb.merit_badge_name) as merit_badges
                FROM adults a
                LEFT JOIN adult_merit_badges amb ON a.id = amb.adult_id
                GROUP BY a.id, a.first_name, a.last_name, a.email, a.bsa_number
                ORDER BY a.last_name, a.first_name
            """)
            
            adults = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Calculate fuzzy match scores
            potential_matches = []
            for adult in adults:
                full_name = f"{adult['first_name']} {adult['last_name']}"
                
                # Calculate various fuzzy match scores
                ratio_score = fuzz.ratio(mbc_name_raw.lower(), full_name.lower())
                partial_ratio = fuzz.partial_ratio(mbc_name_raw.lower(), full_name.lower())
                token_sort = fuzz.token_sort_ratio(mbc_name_raw.lower(), full_name.lower())
                token_set = fuzz.token_set_ratio(mbc_name_raw.lower(), full_name.lower())
                
                # Use the highest score as the confidence
                confidence = max(ratio_score, partial_ratio, token_sort, token_set) / 100.0
                
                # Only include matches with reasonable confidence
                if confidence >= 0.4:  # 40% minimum confidence
                    adult_copy = dict(adult)
                    adult_copy['confidence_score'] = confidence
                    adult_copy['full_name'] = full_name
                    potential_matches.append(adult_copy)
            
            # Sort by confidence score (highest first) and limit results
            potential_matches.sort(key=lambda x: x['confidence_score'], reverse=True)
            return potential_matches[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting potential matches for '{mbc_name_raw}': {e}")
            return []
    
    def record_manual_match(self, unmatched_mbc_name: str, match_action: str, 
                          matched_adult_id: Optional[int] = None, 
                          confidence_score: Optional[float] = None,
                          user_name: str = "Anonymous", notes: str = "") -> bool:
        """
        Record a manual matching decision in the database.
        
        Args:
            unmatched_mbc_name: The unmatched MBC name
            match_action: The action taken ('matched', 'skipped', 'marked_invalid', 'create_new')
            matched_adult_id: The adult ID if matched
            confidence_score: The confidence score for the match
            user_name: The user making the decision
            notes: Optional notes about the decision
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Record the manual match decision
            cursor.execute("""
                INSERT INTO mbc_manual_matches 
                (unmatched_mbc_name, matched_adult_id, match_action, confidence_score, 
                 user_name, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (unmatched_mbc_name, matched_adult_id, match_action, confidence_score,
                  user_name, notes, datetime.now()))
            
            # Update the unmatched_mbc_names table if this is a match
            if match_action == 'matched' and matched_adult_id:
                cursor.execute("""
                    UPDATE unmatched_mbc_names 
                    SET manual_match_adult_id = ?, is_resolved = 1, 
                        notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE mbc_name_raw = ?
                """, (matched_adult_id, notes, unmatched_mbc_name))
                
                # Update merit_badge_progress records to use the matched adult
                cursor.execute("""
                    UPDATE merit_badge_progress 
                    SET mbc_adult_id = ?, mbc_match_confidence = ?
                    WHERE mbc_name_raw = ? AND mbc_adult_id IS NULL
                """, (matched_adult_id, confidence_score, unmatched_mbc_name))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording manual match: {e}")
            return False
    
    def undo_manual_match(self, unmatched_mbc_name: str, user_name: str = "Anonymous") -> bool:
        """
        Undo a previous manual matching decision.
        
        Args:
            unmatched_mbc_name: The unmatched MBC name to undo
            user_name: The user undoing the decision
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the most recent non-undone decision
            cursor.execute("""
                SELECT * FROM mbc_manual_matches 
                WHERE unmatched_mbc_name = ? AND match_action != 'undone'
                ORDER BY created_at DESC
                LIMIT 1
            """, (unmatched_mbc_name,))
            
            last_decision = cursor.fetchone()
            if not last_decision:
                return False
            
            # Record the undo action
            cursor.execute("""
                INSERT INTO mbc_manual_matches 
                (unmatched_mbc_name, matched_adult_id, match_action, confidence_score, 
                 user_name, notes, original_match_id, created_at)
                VALUES (?, ?, 'undone', ?, ?, ?, ?, ?)
            """, (unmatched_mbc_name, last_decision[2], last_decision[4],
                  user_name, f"Undoing {last_decision[3]} decision", last_decision[0], datetime.now()))
            
            # Reset the unmatched_mbc_names table
            cursor.execute("""
                UPDATE unmatched_mbc_names 
                SET manual_match_adult_id = NULL, is_resolved = 0, 
                    notes = 'Decision undone', updated_at = CURRENT_TIMESTAMP
                WHERE mbc_name_raw = ?
            """, (unmatched_mbc_name,))
            
            # Reset merit_badge_progress records
            cursor.execute("""
                UPDATE merit_badge_progress 
                SET mbc_adult_id = NULL, mbc_match_confidence = NULL
                WHERE mbc_name_raw = ?
            """, (unmatched_mbc_name,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error undoing manual match: {e}")
            return False
    
    def get_matching_statistics(self) -> Dict:
        """
        Get statistics about manual matching progress.
        
        Returns:
            Dictionary with matching statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_unmatched,
                    COUNT(CASE WHEN manual_match_status = 'Manually Matched' THEN 1 END) as manually_matched,
                    COUNT(CASE WHEN manual_match_status = 'Skipped' THEN 1 END) as skipped,
                    COUNT(CASE WHEN manual_match_status = 'Marked Invalid' THEN 1 END) as marked_invalid,
                    COUNT(CASE WHEN manual_match_status = 'New Adult Needed' THEN 1 END) as create_new,
                    COUNT(CASE WHEN manual_match_status = 'Unresolved' THEN 1 END) as unresolved,
                    SUM(assignment_count) as total_assignments
                FROM unmatched_mbc_assignments
            """)
            
            stats = dict(cursor.fetchone())
            
            # Get user activity summary
            cursor.execute("""
                SELECT user_name, total_manual_decisions, unique_names_processed
                FROM mbc_manual_matches_summary
                ORDER BY total_manual_decisions DESC
            """)
            
            user_activity = [dict(row) for row in cursor.fetchall()]
            stats['user_activity'] = user_activity
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting matching statistics: {e}")
            return {}
    
    def get_confidence_color(self, confidence: float) -> str:
        """
        Get a color based on confidence score for UI display.
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            Color string for Streamlit
        """
        if confidence >= 0.9:
            return "green"
        elif confidence >= 0.8:
            return "orange"
        elif confidence >= 0.6:
            return "red"
        else:
            return "gray"
    
    def get_confidence_emoji(self, confidence: float) -> str:
        """
        Get an emoji based on confidence score for UI display.
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            Emoji string
        """
        if confidence >= 0.9:
            return "🟢"
        elif confidence >= 0.8:
            return "🟡"
        elif confidence >= 0.6:
            return "🟠"
        else:
            return "🔴"