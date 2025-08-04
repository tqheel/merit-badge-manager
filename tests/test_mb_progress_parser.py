#!/usr/bin/env python3
"""
Tests for Merit Badge Progress CSV Parser
"""

import unittest
import tempfile
import os
import csv
import json
from pathlib import Path

# Add the database-access directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database-access'))

from mb_progress_parser import MeritBadgeProgressParser
from test_data.mb_progress_test_data import SAMPLE_MB_PROGRESS_CSV


class TestMeritBadgeProgressParser(unittest.TestCase):
    """Test cases for Merit Badge Progress CSV parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create sample CSV file
        self.sample_csv = os.path.join(self.temp_dir, "mb_progress.csv")
        with open(self.sample_csv, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_MB_PROGRESS_CSV)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        
        self.assertEqual(str(parser.input_file), self.sample_csv)
        self.assertEqual(str(parser.output_dir), self.output_dir)
        self.assertTrue(os.path.exists(self.output_dir))
    
    def test_csv_parsing_basic(self):
        """Test basic CSV parsing functionality."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        output_file = parser.parse_csv()
        
        # Check output file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Verify parsing summary
        summary = parser.get_parsing_summary()
        self.assertEqual(summary['data_rows_processed'], 5)  # 5 scout records
        self.assertGreater(summary['metadata_rows_removed'], 0)
        self.assertEqual(summary['mbc_assigned_count'], 3)  # 3 scouts have MBC assigned
        self.assertEqual(summary['mbc_unassigned_count'], 2)  # 2 scouts have no MBC
    
    def test_header_cleaning(self):
        """Test that metadata headers are properly removed."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        output_file = parser.parse_csv()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # First line should be headers, not metadata
        first_line = lines[0].strip()
        self.assertIn('Member ID', first_line)
        self.assertNotIn('Generated:', first_line)
        self.assertNotIn('Merit Badge In-Progress Report', first_line)
    
    def test_merit_badge_year_extraction(self):
        """Test extraction of merit badge year from badge names."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        
        # Test year extraction
        self.assertEqual(parser._extract_merit_badge_year("Fire Safety (2025)"), "2025")
        self.assertEqual(parser._extract_merit_badge_year("Swimming (2024)"), "2024")
        self.assertEqual(parser._extract_merit_badge_year("Cooking"), "")
        self.assertEqual(parser._extract_merit_badge_year(""), "")
    
    def test_requirements_parsing(self):
        """Test parsing of complex requirements strings."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        
        # Test simple requirements
        simple_reqs = parser._parse_requirements("5, 5g, 10, 10a, ")
        self.assertEqual(len(simple_reqs), 4)
        self.assertEqual(simple_reqs[0]['requirement'], '5')
        self.assertEqual(simple_reqs[1]['requirement'], '5g')
        
        # Test choice requirements
        choice_reqs = parser._parse_requirements("(1 of 4a, 4b, 4c)")
        self.assertEqual(len(choice_reqs), 1)
        self.assertEqual(choice_reqs[0]['type'], 'choice')
        self.assertIn('1 of 4a, 4b, 4c', choice_reqs[0]['requirement'])
        
        # Test "No Requirements Complete"
        no_reqs = parser._parse_requirements("No Requirements Complete, ")
        self.assertEqual(len(no_reqs), 0)
        
        # Test empty requirements
        empty_reqs = parser._parse_requirements("")
        self.assertEqual(len(empty_reqs), 0)
    
    def test_mbc_status_determination(self):
        """Test MBC assignment status determination."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        
        # Test assigned MBC
        self.assertEqual(parser._determine_mbc_status("Mike Johnson"), "Assigned")
        self.assertEqual(parser._determine_mbc_status("Robert (Bob) Smith"), "Assigned")
        
        # Test unassigned MBC
        self.assertEqual(parser._determine_mbc_status(""), "No Assignment")
        self.assertEqual(parser._determine_mbc_status("   "), "No Assignment")
        self.assertEqual(parser._determine_mbc_status("TBD"), "Unassigned")
        self.assertEqual(parser._determine_mbc_status("none"), "Unassigned")
    
    def test_processed_csv_structure(self):
        """Test that processed CSV has correct structure and data."""
        parser = MeritBadgeProgressParser(self.sample_csv, self.output_dir)
        output_file = parser.parse_csv()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check headers include processed fields
            expected_headers = [
                'Member ID', 'Scout First', 'Scout Last', 'MBC', 'Rank',
                'Location', 'Merit Badge', 'Date Completed', 'Requirements',
                'Merit Badge Year', 'Requirements Parsed', 'MBC Assignment Status', 'Processed Date'
            ]
            
            for header in expected_headers:
                self.assertIn(header, reader.fieldnames)
            
            # Check data rows
            rows = list(reader)
            self.assertEqual(len(rows), 5)
            
            # Check first row (John Smith)
            john_row = rows[0]
            self.assertEqual(john_row['Member ID'], '12345678')
            self.assertEqual(john_row['Scout First'], 'John')
            self.assertEqual(john_row['Scout Last'], 'Smith')
            self.assertEqual(john_row['Merit Badge Year'], '2025')
            self.assertEqual(john_row['MBC Assignment Status'], 'No Assignment')
            
            # Verify requirements parsing
            requirements_parsed = json.loads(john_row['Requirements Parsed'])
            self.assertEqual(len(requirements_parsed), 4)
            self.assertEqual(requirements_parsed[0]['requirement'], '5')
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid input files."""
        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            parser = MeritBadgeProgressParser("nonexistent.csv", self.output_dir)
            parser.parse_csv()
    
    def test_error_handling_empty_file(self):
        """Test error handling for empty CSV file."""
        empty_csv = os.path.join(self.temp_dir, "empty.csv")
        with open(empty_csv, 'w') as f:
            f.write("")
        
        with self.assertRaises(ValueError):
            parser = MeritBadgeProgressParser(empty_csv, self.output_dir)
            parser.parse_csv()
    
    def test_error_handling_no_header(self):
        """Test error handling for CSV without proper headers."""
        no_header_csv = os.path.join(self.temp_dir, "no_header.csv")
        with open(no_header_csv, 'w') as f:
            f.write("Generated: 12/15/2024\n")
            f.write("Some random data\n")
            f.write("No proper header row\n")
        
        with self.assertRaises(ValueError):
            parser = MeritBadgeProgressParser(no_header_csv, self.output_dir)
            parser.parse_csv()


if __name__ == '__main__':
    unittest.main()