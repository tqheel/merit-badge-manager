#!/usr/bin/env python3
"""
Merit Badge Manager - Merit Badge Progress CSV Parser

Parses Merit Badge In-Progress Report CSV files from Scoutbook, handling
the specific format requirements including header cleaning and data extraction.
"""

import os
import csv
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class MeritBadgeProgressParser:
    """
    Handles parsing of Merit Badge In-Progress Report CSV files from Scoutbook.
    
    Performs the following operations:
    1. Cleans CSV file by removing metadata headers
    2. Extracts merit badge year from badge names
    3. Parses complex requirements strings
    4. Validates data format and structure
    """
    
    def __init__(self, input_file: str, output_dir: str = "output"):
        """
        Initialize the parser.
        
        Args:
            input_file: Path to the raw Merit Badge In-Progress Report CSV
            output_dir: Directory to save cleaned CSV file
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Expected headers for validation
        self.expected_headers = [
            "Member ID", "Scout First", "Scout Last", "MBC", "Rank", 
            "Location", "Merit Badge", "Date Completed", "Requirements"
        ]
        
        # Parsing statistics
        self.stats = {
            'raw_rows': 0,
            'metadata_rows_removed': 0,
            'data_rows_processed': 0,
            'mbc_assigned_count': 0,
            'mbc_unassigned_count': 0,
            'requirements_parsed': 0,
            'errors': []
        }
    
    def parse_csv(self) -> str:
        """
        Parse the Merit Badge In-Progress Report CSV file.
        
        Returns:
            Path to the cleaned CSV file
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If CSV format is invalid
        """
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        self.logger.info(f"Parsing Merit Badge In-Progress Report: {self.input_file}")
        
        # Step 1: Clean the CSV file
        cleaned_file = self._clean_csv()
        
        # Step 2: Validate the cleaned file
        self._validate_cleaned_csv(cleaned_file)
        
        # Step 3: Process data and enrich with extracted information
        final_file = self._process_data(cleaned_file)
        
        self.logger.info(f"Parsing completed. Output file: {final_file}")
        return str(final_file)
    
    def _clean_csv(self) -> Path:
        """
        Clean the raw CSV by removing metadata and empty rows.
        
        Returns:
            Path to the cleaned CSV file
        """
        cleaned_file = self.output_dir / "merit_badge_progress_cleaned.csv"
        
        with open(self.input_file, 'r', encoding='utf-8', errors='replace') as infile:
            lines = infile.readlines()
        
        self.stats['raw_rows'] = len(lines)
        data_section_started = False
        header_found = False
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            self.logger.debug(f"Processing line {i + 1}: {line[:100]}...")
            
            # Skip empty lines
            if not line:
                self.stats['metadata_rows_removed'] += 1
                continue
            
            # Skip metadata lines (timestamp, report title, troop info)
            if self._is_metadata_line(line):
                self.stats['metadata_rows_removed'] += 1
                continue
            
            # Skip section delimiter lines
            if self._is_section_delimiter(line):
                data_section_started = True
                self.stats['metadata_rows_removed'] += 1
                continue
            
            # Look for the header row
            if self._is_header_row(line) and not header_found:
                cleaned_lines.append(line)
                header_found = True
                self.logger.info(f"Found header row at line {i + 1}")
                continue
            
            # Process data rows (after header is found)
            if header_found and line:
                cleaned_lines.append(line)
                self.stats['data_rows_processed'] += 1
        
        if not header_found:
            raise ValueError("Could not find valid header row in CSV file")
        
        if self.stats['data_rows_processed'] == 0:
            self.logger.warning("No data rows found after header")
        
        # Write cleaned CSV
        with open(cleaned_file, 'w', encoding='utf-8', newline='') as outfile:
            for line in cleaned_lines:
                outfile.write(line + '\n')
        
        self.logger.info(f"Cleaned CSV saved: {cleaned_file}")
        self.logger.info(f"Removed {self.stats['metadata_rows_removed']} metadata rows")
        self.logger.info(f"Processed {self.stats['data_rows_processed']} data rows")
        
        return cleaned_file
    
    def _is_metadata_line(self, line: str) -> bool:
        """Check if a line contains metadata that should be removed."""
        metadata_patterns = [
            r'^Generated:',  # "Generated: MM/DD/YYYY HH:MM:SS"
            r'^Merit Badge In-Progress Report',  # Report title
            r'^"Troop \d+',  # Troop information
            r'^Troop \d+',   # Troop information without quotes
        ]
        
        for pattern in metadata_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _is_section_delimiter(self, line: str) -> bool:
        """Check if a line is a section delimiter."""
        return line.strip(' ",') in ['In-Progress Merit Badge', 'In Progress Merit Badge']
    
    def _is_header_row(self, line: str) -> bool:
        """Check if a line is the header row."""
        # Parse the line as CSV to check columns
        try:
            reader = csv.reader([line])
            row = next(reader)
            
            # Clean up header names
            headers = [col.strip(' "') for col in row if col.strip()]
            
            # Check if we have the expected headers
            required_headers = {"Member ID", "Scout First", "Scout Last", "Merit Badge"}
            found_headers = set(headers)
            
            return required_headers.issubset(found_headers)
        except:
            return False
    
    def _validate_cleaned_csv(self, cleaned_file: Path):
        """Validate the structure of the cleaned CSV file."""
        with open(cleaned_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Check header row
            try:
                header_row = next(reader)
                headers = [col.strip(' "') for col in header_row]
                
                self.logger.info(f"CSV headers: {headers}")
                
                # Validate required columns are present
                required_headers = {"Member ID", "Scout First", "Scout Last", "Merit Badge"}
                found_headers = set(headers)
                
                missing_headers = required_headers - found_headers
                if missing_headers:
                    raise ValueError(f"Missing required headers: {missing_headers}")
                
                # Check for at least one data row
                try:
                    next(reader)
                except StopIteration:
                    self.logger.warning("CSV file contains header but no data rows")
                
            except StopIteration:
                raise ValueError("CSV file is empty or contains no header row")
    
    def _process_data(self, cleaned_file: Path) -> Path:
        """
        Process the cleaned CSV data to extract additional information.
        
        Args:
            cleaned_file: Path to the cleaned CSV file
            
        Returns:
            Path to the final processed CSV file
        """
        processed_file = self.output_dir / "merit_badge_progress_processed.csv"
        
        with open(cleaned_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Add additional columns for processed data
            fieldnames = reader.fieldnames + [
                'Merit Badge Year', 
                'Requirements Parsed', 
                'MBC Assignment Status',
                'Processed Date'
            ]
            
            with open(processed_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    # Extract merit badge year
                    merit_badge_year = self._extract_merit_badge_year(row.get('Merit Badge', ''))
                    
                    # Parse requirements
                    requirements_parsed = self._parse_requirements(row.get('Requirements', ''))
                    
                    # Determine MBC assignment status
                    mbc_status = self._determine_mbc_status(row.get('MBC', ''))
                    if mbc_status == 'Assigned':
                        self.stats['mbc_assigned_count'] += 1
                    else:
                        self.stats['mbc_unassigned_count'] += 1
                    
                    # Add processed fields
                    row['Merit Badge Year'] = merit_badge_year
                    row['Requirements Parsed'] = json.dumps(requirements_parsed)
                    row['MBC Assignment Status'] = mbc_status
                    row['Processed Date'] = datetime.now().isoformat()
                    
                    writer.writerow(row)
                    
                    if requirements_parsed:
                        self.stats['requirements_parsed'] += 1
        
        self.logger.info(f"Processed CSV saved: {processed_file}")
        return processed_file
    
    def _extract_merit_badge_year(self, merit_badge_name: str) -> str:
        """
        Extract year from merit badge name.
        
        Examples:
            "Fire Safety (2025)" -> "2025"
            "Swimming (2024)" -> "2024"
            "Cooking" -> ""
        """
        if not merit_badge_name:
            return ""
        
        # Look for year in parentheses
        match = re.search(r'\((\d{4})\)', merit_badge_name)
        return match.group(1) if match else ""
    
    def _parse_requirements(self, requirements_str: str) -> List[Dict]:
        """
        Parse complex requirements string into structured data.
        
        Examples:
            "5, 5g, 10, 10a, " -> [{"req": "5"}, {"req": "5g"}, {"req": "10"}, {"req": "10a"}]
            "(1 of 7a, 7b, 7c)" -> [{"req": "choice", "group": "1 of 7a, 7b, 7c"}]
            "No Requirements Complete, " -> []
        """
        if not requirements_str or requirements_str.strip() in ['', 'No Requirements Complete']:
            return []
        
        parsed_requirements = []
        
        # Handle special case: "No Requirements Complete"
        if 'no requirements complete' in requirements_str.lower():
            return []
        
        # First, handle choice requirements with parentheses before splitting
        remaining_str = requirements_str
        
        # Find and process choice requirements
        choice_pattern = r'\([^)]+of[^)]+\)'
        choice_matches = re.findall(choice_pattern, requirements_str)
        
        for choice_match in choice_matches:
            # Extract the content inside parentheses
            choice_content = choice_match[1:-1]  # Remove parentheses
            parsed_requirements.append({
                "type": "choice",
                "requirement": choice_content,
                "group": choice_content
            })
            # Remove this choice requirement from the string
            remaining_str = remaining_str.replace(choice_match, '', 1)
        
        # Now split the remaining string by commas and process individual requirements
        parts = [part.strip() for part in remaining_str.split(',') if part.strip()]
        
        for part in parts:
            if not part:
                continue
            
            # Handle regular requirements
            req_match = re.match(r'^(\d+[a-z]*)', part)
            if req_match:
                parsed_requirements.append({
                    "type": "individual",
                    "requirement": req_match.group(1)
                })
            else:
                # Handle other requirement formats
                parsed_requirements.append({
                    "type": "other",
                    "requirement": part
                })
        
        return parsed_requirements
    
    def _determine_mbc_status(self, mbc_field: str) -> str:
        """
        Determine MBC assignment status.
        
        Args:
            mbc_field: The MBC field from the CSV
            
        Returns:
            'Assigned', 'Unassigned', or 'No Assignment'
        """
        if not mbc_field or mbc_field.strip() == '':
            return 'No Assignment'
        
        # Check for placeholder or invalid values
        if mbc_field.strip().lower() in ['none', 'n/a', 'tbd', 'to be determined']:
            return 'Unassigned'
        
        return 'Assigned'
    
    def get_parsing_summary(self) -> Dict:
        """Get summary statistics from the parsing process."""
        return {
            'input_file': str(self.input_file),
            'raw_rows': self.stats['raw_rows'],
            'metadata_rows_removed': self.stats['metadata_rows_removed'],
            'data_rows_processed': self.stats['data_rows_processed'],
            'mbc_assigned_count': self.stats['mbc_assigned_count'],
            'mbc_unassigned_count': self.stats['mbc_unassigned_count'],
            'requirements_parsed': self.stats['requirements_parsed'],
            'errors': self.stats['errors']
        }


def main():
    """Main function for testing the parser."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Parse Merit Badge In-Progress Report CSV file"
    )
    parser.add_argument(
        "input_file",
        help="Path to the raw Merit Badge In-Progress Report CSV file"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Output directory for cleaned CSV file (default: output)"
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
        # Create parser and process file
        mb_parser = MeritBadgeProgressParser(args.input_file, args.output_dir)
        output_file = mb_parser.parse_csv()
        
        # Print summary
        summary = mb_parser.get_parsing_summary()
        print("\n" + "=" * 60)
        print("MERIT BADGE PROGRESS PARSING SUMMARY")
        print("=" * 60)
        print(f"Input file: {summary['input_file']}")
        print(f"Raw rows: {summary['raw_rows']}")
        print(f"Metadata rows removed: {summary['metadata_rows_removed']}")
        print(f"Data rows processed: {summary['data_rows_processed']}")
        print(f"MBC assigned: {summary['mbc_assigned_count']}")
        print(f"MBC unassigned: {summary['mbc_unassigned_count']}")
        print(f"Requirements parsed: {summary['requirements_parsed']}")
        
        if summary['errors']:
            print(f"\nErrors encountered: {len(summary['errors'])}")
            for error in summary['errors']:
                print(f"  - {error}")
        
        print(f"\nOutput file: {output_file}")
        print("✅ Parsing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())