#!/usr/bin/env python3
"""
Merit Badge Manager - MBC Name Fuzzy Matching

Implements fuzzy matching algorithms to match MBC names from Merit Badge
In-Progress Reports to adult roster entries.
"""

import re
import json
import sqlite3
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import logging


class MBCNameMatcher:
    """
    Handles fuzzy matching of Merit Badge Counselor names from Scoutbook reports
    to adult roster entries in the database.
    
    Implements multiple matching strategies:
    1. Exact name matching
    2. Nickname-aware matching 
    3. Fuzzy string matching with confidence scoring
    4. Soundex phonetic matching
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the MBC name matcher.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Common nickname mappings
        self.nickname_mappings = {
            'robert': ['bob', 'rob', 'bobby', 'robbie'],
            'william': ['bill', 'billy', 'will', 'willie'],
            'james': ['jim', 'jimmy', 'jamie'],
            'michael': ['mike', 'micky', 'mick'],
            'christopher': ['chris', 'christopher'],
            'matthew': ['matt', 'matthew'],
            'anthony': ['tony', 'ant'],
            'mark': ['marky'],
            'steven': ['steve', 'stevie'],
            'paul': ['paulie'],
            'andrew': ['andy', 'drew'],
            'joshua': ['josh'],
            'kenneth': ['ken', 'kenny'],
            'kevin': ['kev'],
            'brian': ['brian'],
            'george': ['george'],
            'edward': ['ed', 'eddie', 'ted'],
            'ronald': ['ron', 'ronnie'],
            'timothy': ['tim', 'timmy'],
            'jason': ['jason'],
            'jeffrey': ['jeff', 'jeffery'],
            'ryan': ['ryan'],
            'jacob': ['jake', 'jacob'],
            'gary': ['gary'],
            'nicholas': ['nick', 'nicky'],
            'eric': ['eric'],
            'jonathan': ['jon', 'johnny'],
            'stephen': ['steve', 'stevie'],
            'larry': ['lawrence', 'larry'],
            'justin': ['justin'],
            'scott': ['scott'],
            'brandon': ['brandon'],
            'benjamin': ['ben', 'benny'],
            'samuel': ['sam', 'sammy'],
            'gregory': ['greg', 'gregory'],
            'alexander': ['alex', 'alexander'],
            'patrick': ['pat', 'patrick'],
            'frank': ['frank'],
            'raymond': ['ray', 'raymond'],
            'jack': ['john', 'jack'],
            'dennis': ['denny', 'dennis'],
            'jerry': ['gerald', 'jerry'],
            'tyler': ['ty', 'tyler'],
            'aaron': ['aaron'],
            'jose': ['jose'],
            'henry': ['hank', 'henry'],
            'adam': ['adam'],
            'douglas': ['doug', 'douglas'],
            'nathan': ['nate', 'nathan'],
            'peter': ['pete', 'peter'],
            'zachary': ['zach', 'zachary'],
            'kyle': ['kyle'],
            'noah': ['noah'],
            'alan': ['al', 'alan'],
            'ethan': ['ethan'],
            'jeremy': ['jeremy'],
            'lionel': ['lion', 'lionel'],
            'wayne': ['wayne'],
            'mason': ['mason'],
            'mason': ['mason'],
            'sean': ['sean'],
            'hunter': ['hunter'],
            'eli': ['eli'],
            'jordan': ['jordan'],
            'angel': ['angel'],
            'connor': ['connor'],
            'evan': ['evan'],
            'aaron': ['aaron'],
            'jose': ['jose'],
            'henry': ['hank', 'henry'],
            'adam': ['adam'],
            'douglas': ['doug', 'douglas'],
            'nathan': ['nate', 'nathan'],
            'peter': ['pete', 'peter'],
            'zachary': ['zach', 'zachary'],
            'kyle': ['kyle']
        }
        
        # Reverse nickname mapping for lookup
        self.reverse_nicknames = {}
        for full_name, nicknames in self.nickname_mappings.items():
            for nickname in nicknames:
                if nickname not in self.reverse_nicknames:
                    self.reverse_nicknames[nickname] = []
                self.reverse_nicknames[nickname].append(full_name)
            # Also map full name to itself
            if full_name not in self.reverse_nicknames:
                self.reverse_nicknames[full_name] = []
            self.reverse_nicknames[full_name].append(full_name)
    
    def find_matches(self, mbc_name_raw: str, min_confidence: float = 0.7) -> List[Dict]:
        """
        Find potential matches for an MBC name in the adult roster.
        
        Args:
            mbc_name_raw: The raw MBC name from the Merit Badge report
            min_confidence: Minimum confidence score for matches (0.0 to 1.0)
            
        Returns:
            List of match dictionaries with adult_id, name, confidence, and match_type
        """
        if not mbc_name_raw or mbc_name_raw.strip() == '':
            return []
        
        self.logger.debug(f"Finding matches for MBC name: '{mbc_name_raw}'")
        
        matches = []
        
        # Get all adults from database
        adults = self._get_all_adults()
        
        if not adults:
            self.logger.warning("No adults found in database for matching")
            return []
        
        # Try different matching strategies
        for adult in adults:
            adult_id, first_name, last_name = adult
            full_name = f"{first_name} {last_name}".strip()
            
            # Strategy 1: Exact match
            exact_confidence = self._exact_match(mbc_name_raw, full_name, first_name, last_name)
            if exact_confidence > 0:
                matches.append({
                    'adult_id': adult_id,
                    'name': full_name,
                    'confidence': exact_confidence,
                    'match_type': 'exact'
                })
                continue  # Exact match found, skip other strategies for this adult
            
            # Strategy 2: Nickname-aware match
            nickname_confidence = self._nickname_match(mbc_name_raw, full_name, first_name, last_name)
            if nickname_confidence > 0:
                matches.append({
                    'adult_id': adult_id,
                    'name': full_name,
                    'confidence': nickname_confidence,
                    'match_type': 'nickname'
                })
                continue
            
            # Strategy 3: Fuzzy string match
            fuzzy_confidence = self._fuzzy_match(mbc_name_raw, full_name, first_name, last_name)
            if fuzzy_confidence >= min_confidence:
                matches.append({
                    'adult_id': adult_id,
                    'name': full_name,
                    'confidence': fuzzy_confidence,
                    'match_type': 'fuzzy'
                })
            
            # Strategy 4: Soundex phonetic match (for names that sound similar)
            soundex_confidence = self._soundex_match(mbc_name_raw, full_name, first_name, last_name)
            if soundex_confidence >= min_confidence:
                # Only add if not already matched by fuzzy
                existing_match = next((m for m in matches if m['adult_id'] == adult_id), None)
                if not existing_match:
                    matches.append({
                        'adult_id': adult_id,
                        'name': full_name,
                        'confidence': soundex_confidence,
                        'match_type': 'soundex'
                    })
        
        # Sort matches by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Remove duplicates (keep highest confidence)
        seen_adults = set()
        unique_matches = []
        for match in matches:
            if match['adult_id'] not in seen_adults:
                unique_matches.append(match)
                seen_adults.add(match['adult_id'])
        
        self.logger.info(f"Found {len(unique_matches)} potential matches for '{mbc_name_raw}'")
        
        return unique_matches
    
    def _get_all_adults(self) -> List[Tuple]:
        """Get all adults from the database for matching."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, first_name, last_name 
                FROM adults 
                WHERE first_name IS NOT NULL AND last_name IS NOT NULL
                ORDER BY last_name, first_name
            """)
            
            adults = cursor.fetchall()
            conn.close()
            
            return adults
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error getting adults: {e}")
            return []
    
    def _exact_match(self, mbc_name: str, full_name: str, first_name: str, last_name: str) -> float:
        """
        Check for exact name matches.
        
        Returns:
            1.0 for exact match, 0.0 for no match
        """
        mbc_clean = self._clean_name(mbc_name)
        
        # Try different combinations
        exact_matches = [
            self._clean_name(full_name),
            self._clean_name(f"{first_name} {last_name}"),
            self._clean_name(f"{last_name}, {first_name}"),
            self._clean_name(f"{last_name} {first_name}")
        ]
        
        if mbc_clean in exact_matches:
            return 1.0
        
        return 0.0
    
    def _nickname_match(self, mbc_name: str, full_name: str, first_name: str, last_name: str) -> float:
        """
        Check for nickname-aware matches.
        
        Returns:
            0.95 for nickname match, 0.0 for no match
        """
        mbc_parts = self._clean_name(mbc_name).split()
        
        if len(mbc_parts) < 2:
            return 0.0  # Need at least first and last name
        
        mbc_first = mbc_parts[0].lower()
        mbc_last = mbc_parts[-1].lower()
        
        # Check if last names match
        if mbc_last != last_name.lower():
            return 0.0
        
        # Check if first name is a nickname
        first_lower = first_name.lower()
        
        # Direct nickname match
        if mbc_first == first_lower:
            return 0.95
        
        # Check if MBC name is a known nickname for the adult's name
        if first_lower in self.nickname_mappings:
            if mbc_first in [nick.lower() for nick in self.nickname_mappings[first_lower]]:
                return 0.95
        
        # Check reverse - if adult's name is a nickname for MBC name
        if mbc_first in self.reverse_nicknames:
            if first_lower in [name.lower() for name in self.reverse_nicknames[mbc_first]]:
                return 0.95
        
        return 0.0
    
    def _fuzzy_match(self, mbc_name: str, full_name: str, first_name: str, last_name: str) -> float:
        """
        Calculate fuzzy string similarity using SequenceMatcher.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        mbc_clean = self._clean_name(mbc_name)
        
        # Try matching against different name combinations
        name_variations = [
            self._clean_name(full_name),
            self._clean_name(f"{first_name} {last_name}"),
            self._clean_name(f"{last_name}, {first_name}")
        ]
        
        max_similarity = 0.0
        
        for name_var in name_variations:
            similarity = SequenceMatcher(None, mbc_clean, name_var).ratio()
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _soundex_match(self, mbc_name: str, full_name: str, first_name: str, last_name: str) -> float:
        """
        Calculate phonetic similarity using Soundex algorithm.
        
        Returns:
            0.8 for soundex match, 0.0 for no match
        """
        mbc_parts = self._clean_name(mbc_name).split()
        
        if len(mbc_parts) < 2:
            return 0.0
        
        mbc_first_soundex = self._soundex(mbc_parts[0])
        mbc_last_soundex = self._soundex(mbc_parts[-1])
        
        adult_first_soundex = self._soundex(first_name)
        adult_last_soundex = self._soundex(last_name)
        
        # Both first and last names must have matching soundex codes
        if mbc_first_soundex == adult_first_soundex and mbc_last_soundex == adult_last_soundex:
            return 0.8
        
        return 0.0
    
    def _clean_name(self, name: str) -> str:
        """
        Clean and normalize a name for comparison.
        
        Args:
            name: Raw name string
            
        Returns:
            Cleaned name string
        """
        if not name:
            return ""
        
        # Remove extra whitespace and convert to lowercase
        cleaned = re.sub(r'\s+', ' ', name.strip().lower())
        
        # Remove parentheses and their contents (nicknames in parentheses)
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        
        # Remove common prefixes and suffixes
        prefixes = ['mr.', 'mrs.', 'ms.', 'dr.', 'prof.']
        suffixes = ['jr.', 'sr.', 'ii', 'iii', 'iv']
        
        words = cleaned.split()
        words = [w for w in words if w not in prefixes and w not in suffixes]
        
        return ' '.join(words).strip()
    
    def _soundex(self, name: str) -> str:
        """
        Generate Soundex code for phonetic matching.
        
        Args:
            name: Name to encode
            
        Returns:
            4-character Soundex code
        """
        if not name:
            return "0000"
        
        name = name.upper()
        
        # Keep first letter
        soundex = name[0]
        
        # Mapping for consonants
        mapping = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }
        
        # Convert remaining letters
        for i, char in enumerate(name[1:], 1):
            if char in mapping:
                code = mapping[char]
                # Don't add duplicate consecutive codes
                if len(soundex) == 0 or soundex[-1] != code:
                    soundex += code
            # Ignore vowels (A, E, I, O, U) and H, W, Y after first character
        
        # Pad with zeros or truncate to 4 characters
        soundex = soundex.ljust(4, '0')[:4]
        
        return soundex
    
    def store_unmatched_name(self, mbc_name_raw: str, potential_matches: List[Dict]) -> int:
        """
        Store an unmatched MBC name in the database for manual resolution.
        
        Args:
            mbc_name_raw: The raw MBC name that couldn't be matched
            potential_matches: List of potential matches found
            
        Returns:
            ID of the stored unmatched name record
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if this name already exists
            cursor.execute("""
                SELECT id, occurrence_count FROM unmatched_mbc_names 
                WHERE mbc_name_raw = ?
            """, (mbc_name_raw,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update occurrence count
                unmatched_id, count = existing
                cursor.execute("""
                    UPDATE unmatched_mbc_names 
                    SET occurrence_count = occurrence_count + 1, 
                        potential_matches = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (json.dumps(potential_matches), unmatched_id))
                
                self.logger.info(f"Updated occurrence count for unmatched MBC name: {mbc_name_raw}")
            else:
                # Insert new unmatched name
                cursor.execute("""
                    INSERT INTO unmatched_mbc_names (
                        mbc_name_raw, occurrence_count, potential_matches
                    ) VALUES (?, 1, ?)
                """, (mbc_name_raw, json.dumps(potential_matches)))
                
                unmatched_id = cursor.lastrowid
                self.logger.info(f"Stored new unmatched MBC name: {mbc_name_raw}")
            
            conn.commit()
            conn.close()
            
            return unmatched_id
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error storing unmatched name: {e}")
            return -1
    
    def store_mapping(self, raw_name: str, adult_id: int, confidence: float, mapping_type: str) -> bool:
        """
        Store a name mapping in the database.
        
        Args:
            raw_name: The raw MBC name
            adult_id: The matched adult ID
            confidence: The confidence score
            mapping_type: Type of match ('exact', 'fuzzy', 'manual')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO mbc_name_mappings (
                    raw_name, adult_id, confidence_score, mapping_type, created_by
                ) VALUES (?, ?, ?, ?, 'system')
            """, (raw_name, adult_id, confidence, mapping_type))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Stored mapping: '{raw_name}' -> adult_id {adult_id} (confidence: {confidence:.2f})")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error storing mapping: {e}")
            return False


def main():
    """Main function for testing the matcher."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test MBC name fuzzy matching"
    )
    parser.add_argument(
        "--database", "-d",
        default="merit_badge_manager.db",
        help="Path to the SQLite database"
    )
    parser.add_argument(
        "mbc_name",
        help="MBC name to test matching for"
    )
    parser.add_argument(
        "--min-confidence", "-c",
        type=float,
        default=0.7,
        help="Minimum confidence score for matches (default: 0.7)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create matcher and find matches
        matcher = MBCNameMatcher(args.database)
        matches = matcher.find_matches(args.mbc_name, args.min_confidence)
        
        print(f"\nMatching results for: '{args.mbc_name}'")
        print("=" * 60)
        
        if matches:
            for i, match in enumerate(matches, 1):
                print(f"{i}. {match['name']} (ID: {match['adult_id']})")
                print(f"   Confidence: {match['confidence']:.3f}")
                print(f"   Match Type: {match['match_type']}")
                print()
        else:
            print("No matches found.")
            
            # Store as unmatched for manual resolution
            unmatched_id = matcher.store_unmatched_name(args.mbc_name, [])
            print(f"Stored as unmatched name (ID: {unmatched_id})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    import json
    sys.exit(main())