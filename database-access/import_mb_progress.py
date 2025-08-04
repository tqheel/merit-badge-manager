#!/usr/bin/env python3
"""
Merit Badge Manager - Merit Badge Progress Import

Imports Merit Badge In-Progress Report CSV data into the database with
MBC name matching and requirement parsing.
"""

import os
import sys
import sqlite3
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add the database directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from mb_progress_parser import MeritBadgeProgressParser
from mbc_name_matcher import MBCNameMatcher


class MeritBadgeProgressImporter:
    """
    Handles the complete Merit Badge Progress import process including
    CSV parsing, MBC name matching, and database import.
    """
    
    def __init__(self, db_path: str = "merit_badge_manager.db"):
        """
        Initialize the importer.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.name_matcher = MBCNameMatcher(db_path)
        
        # Import statistics
        self.stats = {
            'total_records': 0,
            'imported_records': 0,
            'skipped_records': 0,
            'mbc_exact_matches': 0,
            'mbc_fuzzy_matches': 0,
            'mbc_unmatched': 0,
            'mbc_no_assignment': 0,
            'scout_matches': 0,
            'scout_unmatched': 0,
            'requirements_parsed': 0,
            'errors': []
        }
    
    def import_csv(self, csv_file_path: str, auto_match_threshold: float = 0.9) -> bool:
        """
        Import Merit Badge Progress data from CSV file.
        
        Args:
            csv_file_path: Path to the Merit Badge In-Progress Report CSV file
            auto_match_threshold: Confidence threshold for automatic MBC matching
            
        Returns:
            True if import successful, False otherwise
        """
        self.logger.info(f"Starting Merit Badge Progress import from: {csv_file_path}")
        
        try:
            # Step 1: Parse and clean the CSV file
            parser = MeritBadgeProgressParser(csv_file_path, "output")
            processed_file = parser.parse_csv()
            
            parsing_summary = parser.get_parsing_summary()
            self.logger.info(f"CSV parsing completed. Processed {parsing_summary['data_rows_processed']} rows")
            
            # Step 2: Import the processed data
            success = self._import_processed_csv(processed_file, auto_match_threshold)
            
            if success:
                self.logger.info("Merit Badge Progress import completed successfully")
                self._print_import_summary()
            else:
                self.logger.error("Merit Badge Progress import failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            self.stats['errors'].append(str(e))
            return False
    
    def _import_processed_csv(self, csv_file_path: str, auto_match_threshold: float) -> bool:
        """
        Import data from the processed CSV file into the database.
        
        Args:
            csv_file_path: Path to the processed CSV file
            auto_match_threshold: Confidence threshold for automatic matching
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"Processed CSV file not found: {csv_file_path}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, 1):
                    self.stats['total_records'] += 1
                    
                    try:
                        success = self._process_row(cursor, row, auto_match_threshold)
                        if success:
                            self.stats['imported_records'] += 1
                        else:
                            self.stats['skipped_records'] += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error processing row {row_num}: {e}")
                        self.stats['errors'].append(f"Row {row_num}: {e}")
                        self.stats['skipped_records'] += 1
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Database import failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def _process_row(self, cursor, row: Dict, auto_match_threshold: float) -> bool:
        """
        Process a single row from the CSV file.
        
        Args:
            cursor: Database cursor
            row: CSV row data
            auto_match_threshold: Threshold for automatic MBC matching
            
        Returns:
            True if row processed successfully, False otherwise
        """
        # Extract required fields
        scout_bsa_number = row.get('Member ID', '').strip()
        scout_first_name = row.get('Scout First', '').strip()
        scout_last_name = row.get('Scout Last', '').strip()
        merit_badge_name = row.get('Merit Badge', '').strip()
        
        # Validate required fields
        if not all([scout_bsa_number, scout_first_name, scout_last_name, merit_badge_name]):
            self.logger.warning(f"Skipping row with missing required fields: {row}")
            return False
        
        # Convert BSA number to integer
        try:
            scout_bsa_number_int = int(scout_bsa_number)
        except ValueError:
            self.logger.warning(f"Invalid BSA number '{scout_bsa_number}' for {scout_first_name} {scout_last_name}")
            return False
        
        # Extract other fields
        mbc_name_raw = row.get('MBC', '').strip()
        scout_rank = row.get('Rank', '').strip()
        scout_location = row.get('Location', '').strip()
        date_completed = row.get('Date Completed', '').strip()
        requirements_raw = row.get('Requirements', '').strip()
        merit_badge_year = row.get('Merit Badge Year', '').strip()
        requirements_parsed = row.get('Requirements Parsed', '')
        
        # Process MBC assignment
        mbc_adult_id = None
        mbc_match_confidence = None
        
        if mbc_name_raw:
            # Try to match MBC name to adult roster
            matches = self.name_matcher.find_matches(mbc_name_raw, min_confidence=0.7)
            
            if matches:
                best_match = matches[0]
                
                if best_match['confidence'] >= auto_match_threshold:
                    # Automatic match
                    mbc_adult_id = best_match['adult_id']
                    mbc_match_confidence = best_match['confidence']
                    
                    # Store the mapping
                    self.name_matcher.store_mapping(
                        mbc_name_raw, 
                        mbc_adult_id, 
                        mbc_match_confidence, 
                        best_match['match_type']
                    )
                    
                    if best_match['match_type'] == 'exact':
                        self.stats['mbc_exact_matches'] += 1
                    else:
                        self.stats['mbc_fuzzy_matches'] += 1
                    
                    self.logger.debug(f"Matched MBC '{mbc_name_raw}' to {best_match['name']} (confidence: {mbc_match_confidence:.3f})")
                else:
                    # Store for manual review
                    self.name_matcher.store_unmatched_name(mbc_name_raw, matches)
                    self.stats['mbc_unmatched'] += 1
                    self.logger.debug(f"MBC '{mbc_name_raw}' needs manual review (best confidence: {best_match['confidence']:.3f})")
            else:
                # No matches found
                self.name_matcher.store_unmatched_name(mbc_name_raw, [])
                self.stats['mbc_unmatched'] += 1
                self.logger.debug(f"No matches found for MBC '{mbc_name_raw}'")
        else:
            # No MBC assigned
            self.stats['mbc_no_assignment'] += 1
        
        # Try to match scout to youth roster
        scout_id = self._match_scout_to_roster(cursor, scout_bsa_number_int, scout_first_name, scout_last_name)
        
        if scout_id:
            self.stats['scout_matches'] += 1
        else:
            self.stats['scout_unmatched'] += 1
        
        # Insert into merit_badge_progress table
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO merit_badge_progress (
                    scout_bsa_number, scout_first_name, scout_last_name, scout_rank,
                    scout_location, merit_badge_name, merit_badge_year, mbc_name_raw,
                    mbc_adult_id, mbc_match_confidence, date_completed, requirements_raw,
                    requirements_parsed, scout_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(scout_bsa_number_int),
                scout_first_name,
                scout_last_name,
                scout_rank or None,
                scout_location or None,
                merit_badge_name,
                merit_badge_year or None,
                mbc_name_raw or None,
                mbc_adult_id,
                mbc_match_confidence,
                date_completed or None,
                requirements_raw or None,
                requirements_parsed or None,
                scout_id
            ))
            
            # Get the progress record ID
            progress_id = cursor.lastrowid
            
            # Parse and insert requirements if available
            if requirements_parsed:
                self._insert_requirements(cursor, progress_id, requirements_parsed)
                self.stats['requirements_parsed'] += 1
            
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error inserting progress record: {e}")
            return False
    
    def _match_scout_to_roster(self, cursor, scout_bsa_number: int, first_name: str, last_name: str) -> Optional[int]:
        """
        Try to match scout to youth roster by BSA number.
        
        Args:
            cursor: Database cursor
            scout_bsa_number: Scout's BSA number
            first_name: Scout's first name
            last_name: Scout's last name
            
        Returns:
            Scout ID if found, None otherwise
        """
        try:
            cursor.execute("""
                SELECT id FROM scouts WHERE bsa_number = ?
            """, (scout_bsa_number,))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # Could implement fuzzy name matching here if BSA number doesn't match
            self.logger.debug(f"Scout not found in roster: BSA #{scout_bsa_number} {first_name} {last_name}")
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error matching scout: {e}")
            return None
    
    def _insert_requirements(self, cursor, progress_id: int, requirements_parsed_json: str):
        """
        Insert parsed requirements into the merit_badge_requirements table.
        
        Args:
            cursor: Database cursor
            progress_id: Merit badge progress record ID
            requirements_parsed_json: JSON string of parsed requirements
        """
        try:
            requirements = json.loads(requirements_parsed_json)
            
            for req in requirements:
                req_type = req.get('type', 'individual')
                req_number = req.get('requirement', '')
                choice_group = req.get('group', None)
                
                cursor.execute("""
                    INSERT OR IGNORE INTO merit_badge_requirements (
                        progress_id, requirement_number, requirement_type,
                        is_completed, choice_group
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    progress_id,
                    req_number,
                    req_type,
                    True,  # All listed requirements are completed
                    choice_group
                ))
                
        except (json.JSONDecodeError, sqlite3.Error) as e:
            self.logger.warning(f"Error inserting requirements for progress_id {progress_id}: {e}")
    
    def _print_import_summary(self):
        """Print a summary of the import process."""
        print("\n" + "=" * 60)
        print("MERIT BADGE PROGRESS IMPORT SUMMARY")
        print("=" * 60)
        print(f"Total records processed: {self.stats['total_records']}")
        print(f"Successfully imported: {self.stats['imported_records']}")
        print(f"Skipped records: {self.stats['skipped_records']}")
        print()
        print("MBC Matching Results:")
        print(f"  Exact matches: {self.stats['mbc_exact_matches']}")
        print(f"  Fuzzy matches: {self.stats['mbc_fuzzy_matches']}")
        print(f"  Unmatched (manual review): {self.stats['mbc_unmatched']}")
        print(f"  No MBC assigned: {self.stats['mbc_no_assignment']}")
        print()
        print("Scout Matching Results:")
        print(f"  Matched to roster: {self.stats['scout_matches']}")
        print(f"  Not in roster: {self.stats['scout_unmatched']}")
        print()
        print(f"Requirements parsed: {self.stats['requirements_parsed']}")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")
    
    def get_import_summary(self) -> Dict:
        """Get import statistics as a dictionary."""
        return self.stats.copy()


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Import Merit Badge In-Progress Report CSV data"
    )
    parser.add_argument(
        "csv_file",
        help="Path to the Merit Badge In-Progress Report CSV file"
    )
    parser.add_argument(
        "--database", "-d",
        default="merit_badge_manager.db",
        help="Path to the SQLite database (default: merit_badge_manager.db)"
    )
    parser.add_argument(
        "--auto-match-threshold", "-t",
        type=float,
        default=0.9,
        help="Confidence threshold for automatic MBC matching (default: 0.9)"
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
        # Check if database exists
        if not os.path.exists(args.database):
            print(f"❌ Database not found: {args.database}")
            print("Please create the database first using setup_database.py")
            return 1
        
        # Check if CSV file exists
        if not os.path.exists(args.csv_file):
            print(f"❌ CSV file not found: {args.csv_file}")
            return 1
        
        # Run the import
        importer = MeritBadgeProgressImporter(args.database)
        success = importer.import_csv(args.csv_file, args.auto_match_threshold)
        
        if success:
            print("\n✅ Merit Badge Progress import completed successfully!")
            return 0
        else:
            print("\n❌ Merit Badge Progress import failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())