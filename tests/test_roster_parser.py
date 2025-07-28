"""
Tests for the RosterParser class.
"""

import pytest
import tempfile
import csv
from pathlib import Path
from src.roster_parser import RosterParser


class TestRosterParser:
    """Test cases for RosterParser class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_roster_file(self, content: list) -> Path:
        """
        Create a test roster CSV file with given content.
        
        Args:
            content: List of rows to write to CSV
            
        Returns:
            Path to created test file
        """
        test_file = self.temp_path / "test_roster.csv"
        with open(test_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(content)
        return test_file
    
    def test_parse_basic_roster_structure(self):
        """Test parsing a basic roster with adult and youth sections."""
        test_content = [
            ['" "', 'ADULT MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'BSA Number', 'Merit Badges'],
            ['1', 'John', 'Doe', '12345', 'Camping | Hiking'],
            ['2', 'Jane', 'Smith', '67890', 'Cooking | First Aid'],
            ['" "', ''],
            ['" "', 'YOUTH MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'Rank', 'BSA Number'],
            ['1', 'Alice', 'Johnson', 'Scout', '11111'],
            ['2', 'Bob', 'Williams', 'Tenderfoot', '22222'],
        ]
        
        test_file = self.create_test_roster_file(test_content)
        parser = RosterParser(str(test_file), str(self.temp_path))
        
        adult_file, youth_file = parser.parse_roster()
        
        # Verify files were created
        assert Path(adult_file).exists()
        assert Path(youth_file).exists()
        
        # Verify adult data
        with open(adult_file, 'r', encoding='utf-8') as file:
            adult_rows = list(csv.reader(file))
            assert len(adult_rows) == 3  # Header + 2 data rows
            assert 'John' in adult_rows[1]
            assert 'Jane' in adult_rows[2]
        
        # Verify youth data
        with open(youth_file, 'r', encoding='utf-8') as file:
            youth_rows = list(csv.reader(file))
            assert len(youth_rows) == 3  # Header + 2 data rows
            assert 'Alice' in youth_rows[1]
            assert 'Bob' in youth_rows[2]
    
    def test_empty_rows_handling(self):
        """Test that empty rows are properly filtered out."""
        test_content = [
            ['" "', 'ADULT MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'BSA Number'],
            ['1', 'John', 'Doe', '12345'],
            ['', '', ''],  # Empty row
            ['2', 'Jane', 'Smith', '67890'],
            ['" "', ''],
            ['" "', 'YOUTH MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'BSA Number'],
            ['1', 'Alice', 'Johnson', '11111'],
            ['', '', ''],  # Empty row
        ]
        
        test_file = self.create_test_roster_file(test_content)
        parser = RosterParser(str(test_file), str(self.temp_path))
        
        adult_file, youth_file = parser.parse_roster()
        
        # Verify adult data (should have 2 data rows, not 3)
        with open(adult_file, 'r', encoding='utf-8') as file:
            adult_rows = list(csv.reader(file))
            assert len(adult_rows) == 3  # Header + 2 data rows (empty row filtered)
    
    def test_index_column_removal(self):
        """Test that index columns are properly removed."""
        test_content = [
            ['" "', 'ADULT MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'BSA Number'],
            ['1', 'John', 'Doe', '12345'],  # Index column should be removed
        ]
        
        test_file = self.create_test_roster_file(test_content)
        parser = RosterParser(str(test_file), str(self.temp_path))
        
        adult_file, youth_file = parser.parse_roster()
        
        # Verify index column was removed
        with open(adult_file, 'r', encoding='utf-8') as file:
            adult_rows = list(csv.reader(file))
            # First data row should start with 'John', not '1'
            assert adult_rows[1][0] == 'John'
    
    def test_file_not_found(self):
        """Test handling of missing input file."""
        parser = RosterParser("nonexistent_file.csv", str(self.temp_path))
        
        with pytest.raises(FileNotFoundError):
            parser.parse_roster()
    
    def test_parsing_summary(self):
        """Test the parsing summary functionality."""
        test_content = [
            ['" "', 'ADULT MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'BSA Number'],
            ['1', 'John', 'Doe', '12345'],
            ['" "', ''],
            ['" "', 'YOUTH MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'BSA Number'],
            ['1', 'Alice', 'Johnson', '11111'],
            ['2', 'Bob', 'Williams', '22222'],
        ]
        
        test_file = self.create_test_roster_file(test_content)
        parser = RosterParser(str(test_file), str(self.temp_path))
        
        parser.parse_roster()
        summary = parser.get_parsing_summary()
        
        assert summary['adult_records'] == 1
        assert summary['youth_records'] == 2
        assert summary['input_file'] == str(test_file)
        assert summary['adult_output_file'] is not None
        assert summary['youth_output_file'] is not None
    
    def test_quoted_field_handling(self):
        """Test proper handling of quoted CSV fields."""
        test_content = [
            ['" "', 'ADULT MEMBERS'],
            ['" "', 'First Name', 'Last Name', 'Training'],
            ['1', 'John', 'Doe', '"Training A | Training B"'],
        ]
        
        test_file = self.create_test_roster_file(test_content)
        parser = RosterParser(str(test_file), str(self.temp_path))
        
        adult_file, youth_file = parser.parse_roster()
        
        # Verify quoted fields are properly handled
        with open(adult_file, 'r', encoding='utf-8') as file:
            adult_rows = list(csv.reader(file))
            # Training field should not have surrounding quotes
            assert adult_rows[1][2] == 'Training A | Training B'
    
    def test_minimal_valid_data_row(self):
        """Test validation of minimal data rows."""
        parser = RosterParser("dummy.csv", str(self.temp_path))
        
        # Valid row with enough meaningful data
        assert parser._is_valid_data_row(['John', 'Doe', '12345']) == True
        
        # Invalid rows
        assert parser._is_valid_data_row([]) == False
        assert parser._is_valid_data_row(['', '', '']) == False
        assert parser._is_valid_data_row(['John', '']) == False
    
    def test_header_row_detection(self):
        """Test detection of header rows."""
        parser = RosterParser("dummy.csv", str(self.temp_path))
        
        # Valid header rows
        assert parser._is_header_row(['First Name', 'Last Name', 'BSA Number']) == True
        assert parser._is_header_row(['Name', 'Rank', 'Date of Birth']) == True
        
        # Invalid header rows
        assert parser._is_header_row(['John', 'Doe', '12345']) == False
        assert parser._is_header_row([]) == False
