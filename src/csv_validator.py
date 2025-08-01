"""
CSV Validator for Merit Badge Manager

Validates CSV files against expected database schema before import.
Provides detailed validation reports and user-friendly error messages.
"""

import csv
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.row_count = 0
        self.valid_rows = 0
        self.skipped_records = []  # List of records skipped due to duplicates
    
    def add_skipped_record(self, record_info: str):
        """Add a skipped record (doesn't affect validity)."""
        self.skipped_records.append(record_info)
    
    def add_error(self, error: str):
        """Add an error and mark validation as invalid."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning (doesn't affect validity)."""
        self.warnings.append(warning)
    
    def has_issues(self) -> bool:
        """Check if there are any errors, warnings, or skipped records."""
        return len(self.errors) > 0 or len(self.warnings) > 0 or len(self.skipped_records) > 0


class CSVValidator:
    """
    Validates CSV files against Merit Badge Manager database schemas.
    
    Supports validation for:
    - Adult roster data
    - Youth roster data
    - Future: Merit badge progress data
    """
    
    # Adult roster expected columns (based on adults table schema)
    ADULT_REQUIRED_COLUMNS = [
        'first_name', 'last_name', 'bsa_number'
    ]
    
    ADULT_OPTIONAL_COLUMNS = [
        'email', 'city', 'state', 'zip', 'age_category', 'date_joined',
        'unit_number', 'oa_info', 'health_form_status', 'swim_class',
        'swim_class_date', 'positions_tenure'
    ]
    
    # Youth roster expected columns (based on scouts table schema)
    YOUTH_REQUIRED_COLUMNS = [
        'first_name', 'last_name', 'bsa_number'
    ]
    
    YOUTH_OPTIONAL_COLUMNS = [
        'unit_number', 'rank', 'date_joined', 'date_of_birth', 'age',
        'patrol_name', 'activity_status', 'oa_info', 'email', 'phone',
        'address_line1', 'address_line2', 'city', 'state', 'zip',
        'positions_tenure', 'training_raw'
    ]
    
    # Valid rank values for youth
    VALID_YOUTH_RANKS = [
        'Scout', 'Tenderfoot', 'Second Class', 'First Class', 
        'Star', 'Life', 'Eagle', 'NO RANK', ''
    ]
    
    # Valid activity status values
    VALID_ACTIVITY_STATUS = ['Active', 'Inactive', 'Aged Out', '']
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_adult_roster(self, csv_file_path: str) -> ValidationResult:
        """
        Validate adult roster CSV file against expected schema.
        
        Args:
            csv_file_path: Path to the adult roster CSV file
            
        Returns:
            ValidationResult with validation details
        """
        return self._validate_csv_file(
            csv_file_path,
            "Adult Roster",
            self.ADULT_REQUIRED_COLUMNS,
            self.ADULT_OPTIONAL_COLUMNS,
            self._validate_adult_row
        )
    
    def validate_youth_roster(self, csv_file_path: str) -> ValidationResult:
        """
        Validate youth roster CSV file against expected schema.
        
        Args:
            csv_file_path: Path to the youth roster CSV file
            
        Returns:
            ValidationResult with validation details
        """
        return self._validate_csv_file(
            csv_file_path,
            "Youth Roster",
            self.YOUTH_REQUIRED_COLUMNS,
            self.YOUTH_OPTIONAL_COLUMNS,
            self._validate_youth_row
        )
    
    def _validate_csv_file(
        self, 
        csv_file_path: str, 
        file_type: str,
        required_columns: List[str],
        optional_columns: List[str],
        row_validator
    ) -> ValidationResult:
        """
        Generic CSV file validation.
        
        Args:
            csv_file_path: Path to CSV file
            file_type: Human-readable file type for error messages
            required_columns: List of required column names
            optional_columns: List of optional column names
            row_validator: Function to validate individual rows
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Check if file exists
        if not os.path.exists(csv_file_path):
            result.add_error(f"{file_type} file not found: {csv_file_path}")
            return result
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # Try to detect if file has content
                content = file.read()
                if not content.strip():
                    result.add_error(f"{file_type} file is empty")
                    return result
                
                # Reset file pointer
                file.seek(0)
                reader = csv.DictReader(file)
                
                # Validate headers
                headers_result = self._validate_headers(
                    reader.fieldnames, required_columns, optional_columns, file_type
                )
                result.errors.extend(headers_result.errors)
                result.warnings.extend(headers_result.warnings)
                if not headers_result.is_valid:
                    result.is_valid = False
                
                if not headers_result.is_valid:
                    return result
                
                # Validate data rows
                row_number = 1  # Start at 1 for header
                bsa_numbers_seen = {}  # Track BSA number to first occurrence info
                
                for row in reader:
                    row_number += 1
                    result.row_count += 1
                    
                    # Check for duplicate BSA numbers
                    bsa_number = self._get_normalized_value(row, 'bsa_number')
                    first_name = self._get_normalized_value(row, 'first_name')
                    last_name = self._get_normalized_value(row, 'last_name')
                    
                    if bsa_number and bsa_number in bsa_numbers_seen:
                        # Skip duplicate record and report it
                        first_occurrence = bsa_numbers_seen[bsa_number]
                        result.add_skipped_record(
                            f"Row {row_number}: Skipped duplicate BSA number '{bsa_number}' for {first_name} {last_name} "
                            f"(first occurrence: Row {first_occurrence['row']}, {first_occurrence['name']})"
                        )
                        continue
                    elif bsa_number:
                        bsa_numbers_seen[bsa_number] = {
                            'row': row_number,
                            'name': f"{first_name} {last_name}"
                        }
                    
                    # Validate individual row
                    row_result = row_validator(row, row_number)
                    result.errors.extend(row_result.errors)
                    result.warnings.extend(row_result.warnings)
                    
                    if not row_result.is_valid:
                        result.is_valid = False
                    
                    if row_result.is_valid:
                        result.valid_rows += 1
                
                # Check if we have any data rows
                if result.row_count == 0:
                    result.add_warning(f"{file_type} file contains only headers, no data rows")
                
        except UnicodeDecodeError:
            result.add_error(f"{file_type} file has encoding issues. Please save as UTF-8.")
        except csv.Error as e:
            result.add_error(f"{file_type} file CSV format error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error reading {file_type} file: {e}")
        
        return result
    
    def _validate_headers(
        self, 
        headers: List[str], 
        required_columns: List[str],
        optional_columns: List[str],
        file_type: str
    ) -> ValidationResult:
        """Validate CSV headers against expected schema."""
        result = ValidationResult()
        
        if not headers:
            result.add_error(f"{file_type} file has no headers")
            return result
        
        # Normalize headers (lowercase, strip whitespace)
        normalized_headers = [h.lower().strip().replace(' ', '_') for h in headers if h]
        all_expected_columns = required_columns + optional_columns
        
        # Create mapping from original headers to normalized
        self._header_mapping = {}
        for original, normalized in zip(headers, normalized_headers):
            if original and normalized:
                self._header_mapping[original] = normalized
        
        # Check for required columns
        missing_required = []
        for col in required_columns:
            if col not in normalized_headers:
                missing_required.append(col)
        
        if missing_required:
            result.add_error(f"{file_type} missing required columns: {', '.join(missing_required)}")
        
        # Check for unexpected columns
        unexpected_columns = []
        for header in normalized_headers:
            if header not in all_expected_columns:
                unexpected_columns.append(header)
        
        if unexpected_columns:
            result.add_warning(f"{file_type} has unexpected columns: {', '.join(unexpected_columns)}")
        
        return result
    
    def _validate_adult_row(self, row: Dict[str, str], row_number: int) -> ValidationResult:
        """Validate individual adult roster row."""
        result = ValidationResult()
        
        # Validate required fields using normalized lookups
        first_name = self._get_normalized_value(row, 'first_name')
        last_name = self._get_normalized_value(row, 'last_name')
        bsa_number = self._get_normalized_value(row, 'bsa_number')
        
        if not first_name:
            result.add_error(f"Row {row_number}: First name is required")
        
        if not last_name:
            result.add_error(f"Row {row_number}: Last name is required")
        
        if not bsa_number:
            result.add_error(f"Row {row_number}: BSA number is required")
        elif not self._is_valid_bsa_number(bsa_number):
            result.add_error(f"Row {row_number}: Invalid BSA number format '{bsa_number}'")
        
        # Validate email format if provided
        email = self._get_normalized_value(row, 'email')
        if email and not self._is_valid_email(email):
            result.add_error(f"Row {row_number}: Invalid email format '{email}'")
        
        # Validate date fields if provided
        date_joined = self._get_normalized_value(row, 'date_joined')
        if date_joined and not self._is_valid_date(date_joined):
            result.add_warning(f"Row {row_number}: Invalid date format for date_joined '{date_joined}'")
        
        swim_class_date = self._get_normalized_value(row, 'swim_class_date')
        if swim_class_date and not self._is_valid_date(swim_class_date):
            result.add_warning(f"Row {row_number}: Invalid date format for swim_class_date '{swim_class_date}'")
        
        return result
    
    def _validate_youth_row(self, row: Dict[str, str], row_number: int) -> ValidationResult:
        """Validate individual youth roster row."""
        result = ValidationResult()
        
        # Validate required fields using normalized lookups
        first_name = self._get_normalized_value(row, 'first_name')
        last_name = self._get_normalized_value(row, 'last_name')
        bsa_number = self._get_normalized_value(row, 'bsa_number')
        
        if not first_name:
            result.add_error(f"Row {row_number}: First name is required")
        
        if not last_name:
            result.add_error(f"Row {row_number}: Last name is required")
        
        if not bsa_number:
            result.add_error(f"Row {row_number}: BSA number is required")
        elif not self._is_valid_bsa_number(bsa_number):
            result.add_error(f"Row {row_number}: Invalid BSA number format '{bsa_number}'")
        
        # Validate rank if provided
        rank = self._get_normalized_value(row, 'rank')
        if rank and rank not in self.VALID_YOUTH_RANKS:
            result.add_error(f"Row {row_number}: Invalid rank '{rank}'. Valid ranks: {', '.join(self.VALID_YOUTH_RANKS)}")
        
        # Validate activity status if provided
        activity_status = self._get_normalized_value(row, 'activity_status')
        if activity_status and activity_status not in self.VALID_ACTIVITY_STATUS:
            result.add_error(f"Row {row_number}: Invalid activity status '{activity_status}'. Valid statuses: {', '.join(self.VALID_ACTIVITY_STATUS)}")
        
        # Validate email format if provided
        email = self._get_normalized_value(row, 'email')
        if email and not self._is_valid_email(email):
            result.add_error(f"Row {row_number}: Invalid email format '{email}'")
        
        # Validate date fields if provided
        date_joined = self._get_normalized_value(row, 'date_joined')
        if date_joined and not self._is_valid_date(date_joined):
            result.add_warning(f"Row {row_number}: Invalid date format for date_joined '{date_joined}'")
        
        date_of_birth = self._get_normalized_value(row, 'date_of_birth')
        if date_of_birth and not self._is_valid_date(date_of_birth):
            result.add_warning(f"Row {row_number}: Invalid date format for date_of_birth '{date_of_birth}'")
        
        # Validate age if provided
        age = self._get_normalized_value(row, 'age')
        if age:
            try:
                age_int = int(age)
                if age_int < 6 or age_int > 21:
                    result.add_warning(f"Row {row_number}: Age {age_int} seems unusual for a Scout (6-21 typical range)")
            except ValueError:
                result.add_error(f"Row {row_number}: Age must be a number, got '{age}'")
        
        # Validate phone format if provided
        phone = self._get_normalized_value(row, 'phone')
        if phone and not self._is_valid_phone(phone):
            result.add_warning(f"Row {row_number}: Phone number format may be invalid '{phone}'")
        
        return result
    
    def _is_valid_bsa_number(self, bsa_number: str) -> bool:
        """Validate BSA number format (should be numeric, typically 8-9 digits)."""
        if not bsa_number.isdigit():
            return False
        # BSA numbers are typically 8-9 digits, but allow some flexibility
        return 6 <= len(bsa_number) <= 12
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Validate date format (supports various common formats)."""
        date_formats = [
            '%Y-%m-%d',     # 2023-12-31
            '%m/%d/%Y',     # 12/31/2023
            '%m-%d-%Y',     # 12-31-2023
            '%Y/%m/%d',     # 2023/12/31
            '%d/%m/%Y',     # 31/12/2023 (international)
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        return False
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone number validation (allows various formats)."""
        # Remove common non-digit characters
        cleaned = re.sub(r'[^\d]', '', phone)
        # Should have 10-11 digits (US format)
        return 10 <= len(cleaned) <= 11
    
    def generate_validation_report(
        self, 
        results: Dict[str, ValidationResult], 
        output_dir: str = "logs"
    ) -> str:
        """
        Generate a detailed validation report file.
        
        Args:
            results: Dictionary mapping file types to ValidationResult objects
            output_dir: Directory to write the report file
            
        Returns:
            Path to the generated report file
        """
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate report filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"validation_report_{timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MERIT BADGE MANAGER - CSV VALIDATION REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            overall_valid = all(result.is_valid for result in results.values())
            f.write(f"OVERALL STATUS: {'PASS' if overall_valid else 'FAIL'}\n\n")
            
            for file_type, result in results.items():
                f.write("-" * 60 + "\n")
                f.write(f"{file_type.upper()} VALIDATION\n")
                f.write("-" * 60 + "\n")
                f.write(f"Status: {'PASS' if result.is_valid else 'FAIL'}\n")
                f.write(f"Total Rows: {result.row_count}\n")
                f.write(f"Valid Rows: {result.valid_rows}\n")
                f.write(f"Skipped Rows: {len(result.skipped_records)}\n")
                f.write(f"Errors: {len(result.errors)}\n")
                f.write(f"Warnings: {len(result.warnings)}\n\n")
                
                if result.skipped_records:
                    f.write("SKIPPED RECORDS (Duplicates):\n")
                    for skipped in result.skipped_records:
                        f.write(f"  ⏭️  {skipped}\n")
                    f.write("\n")
                
                if result.errors:
                    f.write("ERRORS:\n")
                    for error in result.errors:
                        f.write(f"  ❌ {error}\n")
                    f.write("\n")
                
                if result.warnings:
                    f.write("WARNINGS:\n")
                    for warning in result.warnings:
                        f.write(f"  ⚠️  {warning}\n")
                    f.write("\n")
            
            f.write("-" * 60 + "\n")
            f.write("RECOMMENDED ACTIONS\n")
            f.write("-" * 60 + "\n")
            
            if overall_valid:
                f.write("✅ All validation checks passed!\n")
                f.write("   You can proceed with the data import.\n\n")
            else:
                f.write("❌ Validation failed. Please address the following:\n\n")
                for file_type, result in results.items():
                    if not result.is_valid:
                        f.write(f"{file_type}:\n")
                        f.write("  1. Review and fix all error messages above\n")
                        f.write("  2. Ensure required columns are present with correct names\n")
                        f.write("  3. Check data formats (dates, emails, BSA numbers)\n")
                        f.write("  4. Remove duplicate BSA numbers\n")
                        f.write("  5. Re-run validation before importing\n\n")
            
            f.write("For assistance, refer to the database schema documentation.\n")
        
        return report_file
    
    def _normalize_key(self, key: str) -> str:
        """Normalize a column header key for consistent lookups."""
        return key.lower().strip().replace(' ', '_')
    
    def _get_normalized_value(self, row: Dict[str, str], normalized_key: str) -> str:
        """Get value from row using normalized key."""
        for original_key, value in row.items():
            if self._normalize_key(original_key) == normalized_key:
                return value.strip() if value else ""
        return ""


def print_validation_summary(results: Dict[str, ValidationResult]) -> bool:
    """
    Print a user-friendly validation summary to the terminal.
    
    Args:
        results: Dictionary mapping file types to ValidationResult objects
        
    Returns:
        True if all validations passed, False otherwise
    """
    print("\n" + "=" * 80)
    print("CSV VALIDATION SUMMARY")
    print("=" * 80)
    
    overall_valid = True
    total_errors = 0
    total_warnings = 0
    
    for file_type, result in results.items():
        status_icon = "✅" if result.is_valid else "❌"
        print(f"\n{status_icon} {file_type}: {'PASS' if result.is_valid else 'FAIL'}")
        print(f"   Rows processed: {result.row_count}")
        print(f"   Valid rows: {result.valid_rows}")
        print(f"   Skipped rows: {len(result.skipped_records)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Warnings: {len(result.warnings)}")
        
        if not result.is_valid:
            overall_valid = False
        
        total_errors += len(result.errors)
        total_warnings += len(result.warnings)
        
        # Show skipped records for immediate attention
        if result.skipped_records:
            print(f"\n   Skipped records (duplicates):")
            for skipped in result.skipped_records[:3]:
                print(f"     ⏭️  {skipped}")
            if len(result.skipped_records) > 3:
                print(f"     ... and {len(result.skipped_records) - 3} more skipped records")
        
        # Show first few errors for immediate attention
        if result.errors:
            print(f"\n   First few errors:")
            for error in result.errors[:3]:
                print(f"     ❌ {error}")
            if len(result.errors) > 3:
                print(f"     ... and {len(result.errors) - 3} more errors")
    
    print("\n" + "-" * 80)
    overall_icon = "✅" if overall_valid else "❌"
    print(f"{overall_icon} OVERALL: {'ALL VALIDATIONS PASSED' if overall_valid else 'VALIDATION FAILED'}")
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    
    if not overall_valid:
        print("\n🚨 CANNOT PROCEED WITH IMPORT - Please fix validation errors first!")
        print("💡 Run with detailed report option for complete error list and suggested fixes.")
    else:
        print("\n🎉 Ready to import! All validation checks passed.")
    
    print("=" * 80 + "\n")
    
    return overall_valid