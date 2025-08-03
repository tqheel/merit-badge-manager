"""
Unit tests for CSV validation functionality.

Tests validation of adult and youth roster CSV files against expected schemas.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Import validation classes (now available via conftest.py)
from csv_validator import CSVValidator, ValidationResult


class TestCSVValidator(unittest.TestCase):
    """Test the CSV validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = CSVValidator()
        self.test_data_dir = Path(__file__).parent / "test_data" / "validation"
    
    def test_adult_roster_valid(self):
        """Test validation of valid adult roster data."""
        csv_file = self.test_data_dir / "adult_roster_valid.csv"
        result = self.validator.validate_adult_roster(str(csv_file))
        
        self.assertTrue(result.is_valid, f"Valid adult roster should pass validation. Errors: {result.errors}")
        self.assertEqual(len(result.errors), 0, "Valid adult roster should have no errors")
        self.assertEqual(result.row_count, 4, "Should have 4 data rows")
        self.assertEqual(result.valid_rows, 4, "All 4 rows should be valid")
    
    def test_adult_roster_invalid(self):
        """Test validation of invalid adult roster data."""
        csv_file = self.test_data_dir / "adult_roster_invalid.csv"
        result = self.validator.validate_adult_roster(str(csv_file))
        
        self.assertFalse(result.is_valid, "Invalid adult roster should fail validation")
        self.assertGreater(len(result.errors), 0, "Invalid adult roster should have errors")
        
        # Check for specific validation errors
        error_text = " ".join(result.errors)
        self.assertIn("Invalid email format", error_text)
        self.assertIn("Invalid BSA number format", error_text)
        self.assertIn("First name is required", error_text)
        self.assertIn("Last name is required", error_text)
        
        # Check for skipped duplicate records
        skipped_text = " ".join(result.skipped_records)
        self.assertIn("Skipped duplicate BSA number", skipped_text)
    
    def test_youth_roster_valid(self):
        """Test validation of valid youth roster data."""
        csv_file = self.test_data_dir / "youth_roster_valid.csv"
        result = self.validator.validate_youth_roster(str(csv_file))
        
        self.assertTrue(result.is_valid, f"Valid youth roster should pass validation. Errors: {result.errors}")
        self.assertEqual(len(result.errors), 0, "Valid youth roster should have no errors")
        self.assertEqual(result.row_count, 4, "Should have 4 data rows")
        self.assertEqual(result.valid_rows, 4, "All 4 rows should be valid")
    
    def test_youth_roster_invalid(self):
        """Test validation of invalid youth roster data."""
        csv_file = self.test_data_dir / "youth_roster_invalid.csv"
        result = self.validator.validate_youth_roster(str(csv_file))
        
        self.assertFalse(result.is_valid, "Invalid youth roster should fail validation")
        self.assertGreater(len(result.errors), 0, "Invalid youth roster should have errors")
        
        # Check for specific validation errors
        error_text = " ".join(result.errors)
        self.assertIn("Invalid BSA number format", error_text)
        self.assertIn("Invalid rank", error_text)
        self.assertIn("Invalid email format", error_text)
        self.assertIn("First name is required", error_text)
        self.assertIn("Last name is required", error_text)
        self.assertIn("BSA number is required", error_text)
        self.assertIn("Invalid activity status", error_text)
        self.assertIn("Age must be a number", error_text)
        
        # Check for skipped duplicate records
        skipped_text = " ".join(result.skipped_records)
        self.assertIn("Skipped duplicate BSA number", skipped_text)
    
    def test_file_not_found(self):
        """Test validation when CSV file doesn't exist."""
        result = self.validator.validate_adult_roster("nonexistent_file.csv")
        
        self.assertFalse(result.is_valid, "Should fail when file doesn't exist")
        self.assertIn("file not found", result.errors[0].lower())
    
    def test_empty_file(self):
        """Test validation of empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")  # Empty file
            temp_file = f.name
        
        try:
            result = self.validator.validate_adult_roster(temp_file)
            self.assertFalse(result.is_valid, "Empty file should fail validation")
            self.assertIn("empty", result.errors[0].lower())
        finally:
            os.unlink(temp_file)
    
    def test_header_only_file(self):
        """Test validation of CSV file with headers but no data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("first_name,last_name,bsa_number\n")  # Headers only
            temp_file = f.name
        
        try:
            result = self.validator.validate_adult_roster(temp_file)
            # This should pass validation but issue a warning
            self.assertTrue(result.is_valid, "Header-only file should pass validation")
            self.assertEqual(result.row_count, 0, "Should have 0 data rows")
            self.assertGreater(len(result.warnings), 0, "Should have warnings about no data")
        finally:
            os.unlink(temp_file)
    
    def test_missing_required_columns(self):
        """Test validation when required columns are missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("first_name,email\n")  # Missing last_name and bsa_number
            f.write("John,john@email.com\n")
            temp_file = f.name
        
        try:
            result = self.validator.validate_adult_roster(temp_file)
            self.assertFalse(result.is_valid, "Should fail when required columns are missing")
            error_text = " ".join(result.errors)
            self.assertIn("missing required columns", error_text.lower())
        finally:
            os.unlink(temp_file)
    
    def test_bsa_number_validation(self):
        """Test BSA number format validation."""
        test_cases = [
            ("12345678", True),   # Valid 8-digit
            ("123456789", True),  # Valid 9-digit
            ("123456", True),     # Valid 6-digit (minimum)
            ("123", False),       # Too short
            ("1234567890123", False),  # Too long
            ("abc12345", False),  # Non-numeric
            ("", False),          # Empty
        ]
        
        for bsa_number, should_be_valid in test_cases:
            with self.subTest(bsa_number=bsa_number):
                is_valid = self.validator._is_valid_bsa_number(bsa_number)
                self.assertEqual(is_valid, should_be_valid, 
                    f"BSA number '{bsa_number}' validation failed")
    
    def test_email_validation(self):
        """Test email format validation."""
        test_cases = [
            ("john@example.com", True),
            ("user.name@domain.co.uk", True),
            ("test+tag@gmail.com", True),
            ("invalid.email", False),
            ("@domain.com", False),
            ("user@", False),
            ("", False),
        ]
        
        for email, should_be_valid in test_cases:
            with self.subTest(email=email):
                is_valid = self.validator._is_valid_email(email)
                self.assertEqual(is_valid, should_be_valid, 
                    f"Email '{email}' validation failed")
    
    def test_date_validation(self):
        """Test date format validation."""
        test_cases = [
            ("2023-12-31", True),   # ISO format
            ("12/31/2023", True),   # US format
            ("12-31-2023", True),   # US format with dashes
            ("2023/12/31", True),   # Alternative format
            ("31/12/2023", True),   # International format
            ("invalid-date", False),
            ("13/32/2023", False),  # Invalid date
            ("", False),
        ]
        
        for date_str, should_be_valid in test_cases:
            with self.subTest(date=date_str):
                is_valid = self.validator._is_valid_date(date_str)
                self.assertEqual(is_valid, should_be_valid, 
                    f"Date '{date_str}' validation failed")
    
    def test_phone_validation(self):
        """Test phone number validation."""
        test_cases = [
            ("555-123-4567", True),
            ("(555) 123-4567", True),
            ("5551234567", True),
            ("1-555-123-4567", True),
            ("555.123.4567", True),
            ("123", False),         # Too short
            ("abcd-efg-hijk", False),  # Non-numeric
            ("", False),
        ]
        
        for phone, should_be_valid in test_cases:
            with self.subTest(phone=phone):
                is_valid = self.validator._is_valid_phone(phone)
                self.assertEqual(is_valid, should_be_valid, 
                    f"Phone '{phone}' validation failed")
    
    def test_youth_rank_validation(self):
        """Test youth rank validation."""
        valid_ranks = self.validator.VALID_YOUTH_RANKS
        
        for rank in valid_ranks:
            # Create a minimal valid row with this rank
            row = {
                'first_name': 'Test',
                'last_name': 'Scout',
                'bsa_number': '12345678',
                'rank': rank
            }
            result = self.validator._validate_youth_row(row, 1)
            
            # Should not have rank-related errors
            rank_errors = [e for e in result.errors if 'rank' in e.lower()]
            self.assertEqual(len(rank_errors), 0, 
                f"Valid rank '{rank}' should not cause validation errors")
        
        # Test invalid rank
        row = {
            'first_name': 'Test',
            'last_name': 'Scout',
            'bsa_number': '12345678',
            'rank': 'Invalid Rank'
        }
        result = self.validator._validate_youth_row(row, 1)
        
        rank_errors = [e for e in result.errors if 'rank' in e.lower()]
        self.assertGreater(len(rank_errors), 0, "Invalid rank should cause validation error")
    
    def test_validation_report_generation(self):
        """Test generation of validation reports."""
        # Create some validation results
        results = {
            "Adult Roster": ValidationResult(is_valid=False, errors=["Test error 1"], warnings=["Test warning 1"]),
            "Youth Roster": ValidationResult(is_valid=True, errors=[], warnings=["Test warning 2"])
        }
        
        # Generate report in temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            report_file = self.validator.generate_validation_report(results, temp_dir)
            
            # Check that report file was created
            self.assertTrue(os.path.exists(report_file), "Report file should be created")
            
            # Check report content
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn("CSV VALIDATION REPORT", content)
            self.assertIn("OVERALL STATUS: FAIL", content)
            self.assertIn("Test error 1", content)
            self.assertIn("Test warning 1", content)
            self.assertIn("Test warning 2", content)
            self.assertIn("RECOMMENDED ACTIONS", content)


class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating ValidationResult objects."""
        # Test default creation
        result = ValidationResult()
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
        
        # Test creation with parameters
        result = ValidationResult(is_valid=False, errors=["Error 1"], warnings=["Warning 1"])
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.warnings), 1)
    
    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult()
        self.assertTrue(result.is_valid)
        
        result.add_error("Test error")
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Test error")
    
    def test_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult()
        
        result.add_warning("Test warning")
        self.assertTrue(result.is_valid)  # Warnings don't affect validity
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0], "Test warning")
    
    def test_add_skipped_record(self):
        """Test adding skipped records to ValidationResult."""
        result = ValidationResult()
        
        result.add_skipped_record("Test skipped record")
        self.assertTrue(result.is_valid)  # Skipped records don't affect validity
        self.assertEqual(len(result.skipped_records), 1)
        self.assertEqual(result.skipped_records[0], "Test skipped record")
    
    def test_has_issues(self):
        """Test has_issues method."""
        result = ValidationResult()
        self.assertFalse(result.has_issues())
        
        result.add_warning("Warning")
        self.assertTrue(result.has_issues())
        
        result = ValidationResult()
        result.add_error("Error")
        self.assertTrue(result.has_issues())
        
        result = ValidationResult()
        result.add_skipped_record("Skipped record")
        self.assertTrue(result.has_issues())


if __name__ == '__main__':
    unittest.main()