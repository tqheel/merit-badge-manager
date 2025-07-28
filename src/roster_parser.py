"""
Roster Parser for Merit Badge Counselor Management Application

Parses Troop Roster CSV files from Scoutbook, handling the complex structure
with adult and youth member sections, index columns, and varying formats.
"""

import csv
import os
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class RosterParser:
    """
    Parses Troop Roster CSV files and generates cleaned output files for database import.
    
    Handles:
    - Index column removal
    - Section header identification and removal
    - Adult vs Youth member separation
    - Empty row filtering
    - Data validation and cleaning
    """
    
    def __init__(self, input_file_path: str, output_dir: str = "data/processed"):
        """
        Initialize the roster parser.
        
        Args:
            input_file_path: Path to the input roster CSV file
            output_dir: Directory for output files (default: data/processed)
        """
        self.input_file_path = Path(input_file_path)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Define section markers
        self.adult_section_marker = "ADULT MEMBERS"
        self.youth_section_marker = "YOUTH MEMBERS"
        
    def parse_roster(self) -> Tuple[str, str]:
        """
        Parse the roster file and generate cleaned output files.
        
        Returns:
            Tuple of (adult_file_path, youth_file_path)
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file structure is invalid
        """
        if not self.input_file_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file_path}")
            
        self.logger.info(f"Parsing roster file: {self.input_file_path}")
        
        # Read and validate the CSV file
        raw_data = self._read_csv_file()
        
        # Parse sections
        adult_data, youth_data = self._parse_sections(raw_data)
        
        # Generate output files
        adult_file_path = self._write_adult_roster(adult_data)
        youth_file_path = self._write_youth_roster(youth_data)
        
        self.logger.info(f"Generated adult roster: {adult_file_path}")
        self.logger.info(f"Generated youth roster: {youth_file_path}")
        
        return str(adult_file_path), str(youth_file_path)
    
    def _read_csv_file(self) -> List[List[str]]:
        """
        Read the CSV file and return raw data rows.
        
        Returns:
            List of rows, each row is a list of column values
        """
        try:
            with open(self.input_file_path, 'r', encoding='utf-8') as file:
                # Use csv.reader to handle quoted fields properly
                reader = csv.reader(file)
                return list(reader)
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(self.input_file_path, 'r', encoding='iso-8859-1') as file:
                reader = csv.reader(file)
                return list(reader)
    
    def _parse_sections(self, raw_data: List[List[str]]) -> Tuple[List[List[str]], List[List[str]]]:
        """
        Parse the raw data into adult and youth sections.
        
        Args:
            raw_data: Raw CSV data rows
            
        Returns:
            Tuple of (adult_rows, youth_rows)
        """
        adult_data = []
        youth_data = []
        current_section = None
        header_row = None
        
        for i, row in enumerate(raw_data):
            # Skip empty rows
            if not row or all(cell.strip() == '' for cell in row):
                continue
                
            # Remove index column (first column) if it exists
            if row and row[0].strip().isdigit() or row[0].strip() == '" "':
                row = row[1:]  # Remove index column
            
            # Check for section headers
            if len(row) >= 2 and self.adult_section_marker in str(row[1]):
                current_section = "adults"
                continue
            elif len(row) >= 2 and self.youth_section_marker in str(row[1]):
                current_section = "youth"
                continue
            
            # Capture header rows (rows with column names)
            if current_section and self._is_header_row(row):
                header_row = self._clean_row(row)
                if current_section == "adults":
                    adult_data.append(header_row)
                elif current_section == "youth":
                    youth_data.append(header_row)
                continue
            
            # Process data rows
            if current_section and not self._is_header_row(row):
                cleaned_row = self._clean_row(row)
                if self._is_valid_data_row(cleaned_row):
                    if current_section == "adults":
                        adult_data.append(cleaned_row)
                    elif current_section == "youth":
                        youth_data.append(cleaned_row)
        
        return adult_data, youth_data
    
    def _is_header_row(self, row: List[str]) -> bool:
        """
        Determine if a row is a header row based on common header indicators.
        
        Args:
            row: CSV row to check
            
        Returns:
            True if row appears to be a header
        """
        if not row:
            return False
            
        # Common header indicators
        header_indicators = [
            "First Name", "Last Name", "Email", "BSA Number", 
            "Date of Birth", "Rank", "Training", "Merit Badges"
        ]
        
        row_text = ' '.join(str(cell) for cell in row).upper()
        return any(indicator.upper() in row_text for indicator in header_indicators)
    
    def _is_valid_data_row(self, row: List[str]) -> bool:
        """
        Validate if a row contains actual member data.
        
        Args:
            row: Cleaned CSV row
            
        Returns:
            True if row contains valid member data
        """
        if not row or len(row) < 3:
            return False
            
        # Check if row has meaningful data (not just empty strings or quotes)
        meaningful_cells = [cell for cell in row if cell.strip() and cell.strip() != '""']
        return len(meaningful_cells) >= 3
    
    def _clean_row(self, row: List[str]) -> List[str]:
        """
        Clean individual row by removing quotes and trimming whitespace.
        
        Args:
            row: Raw CSV row
            
        Returns:
            Cleaned row
        """
        cleaned = []
        for cell in row:
            # Remove surrounding quotes and trim whitespace
            cleaned_cell = str(cell).strip().strip('"').strip()
            cleaned.append(cleaned_cell)
        return cleaned
    
    def _write_adult_roster(self, adult_data: List[List[str]]) -> Path:
        """
        Write cleaned adult roster data to CSV file.
        
        Args:
            adult_data: List of adult member rows
            
        Returns:
            Path to generated adult roster file
        """
        output_file = self.output_dir / "adult_roster.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(adult_data)
        
        self.logger.info(f"Wrote {len(adult_data)} adult member rows to {output_file}")
        return output_file
    
    def _write_youth_roster(self, youth_data: List[List[str]]) -> Path:
        """
        Write cleaned youth roster data to CSV file.
        
        Args:
            youth_data: List of youth member rows
            
        Returns:
            Path to generated youth roster file
        """
        output_file = self.output_dir / "scout_roster.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(youth_data)
        
        self.logger.info(f"Wrote {len(youth_data)} youth member rows to {output_file}")
        return output_file
    
    def get_parsing_summary(self) -> Dict[str, any]:
        """
        Get summary information about the last parsing operation.
        
        Returns:
            Dictionary with parsing statistics
        """
        adult_file = self.output_dir / "adult_roster.csv"
        youth_file = self.output_dir / "scout_roster.csv"
        
        summary = {
            "input_file": str(self.input_file_path),
            "adult_output_file": str(adult_file) if adult_file.exists() else None,
            "youth_output_file": str(youth_file) if youth_file.exists() else None,
            "adult_records": self._count_records(adult_file) if adult_file.exists() else 0,
            "youth_records": self._count_records(youth_file) if youth_file.exists() else 0,
        }
        
        return summary
    
    def _count_records(self, file_path: Path) -> int:
        """
        Count the number of data records in a CSV file (excluding header).
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Number of data records
        """
        if not file_path.exists():
            return 0
            
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            # Subtract 1 for header row if file has content
            return max(0, len(rows) - 1) if rows else 0


def main():
    """
    Example usage of the RosterParser class.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    input_file = "data/RosterReport_Troop0212B_Roster_by_Unit_Patrol_DOB_Scouts_and_Adults_20250727.csv"
    
    try:
        parser = RosterParser(input_file)
        adult_file, youth_file = parser.parse_roster()
        
        summary = parser.get_parsing_summary()
        print(f"Parsing Summary:")
        print(f"  Adult records: {summary['adult_records']}")
        print(f"  Youth records: {summary['youth_records']}")
        print(f"  Adult file: {summary['adult_output_file']}")
        print(f"  Youth file: {summary['youth_output_file']}")
        
    except Exception as e:
        logging.error(f"Error parsing roster: {e}")
        raise


if __name__ == "__main__":
    main()
