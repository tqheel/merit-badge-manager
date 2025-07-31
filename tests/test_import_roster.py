"""
Unit tests for the roster import functionality.

Tests the import script with validation and database recreation.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after setting path
from import_roster import RosterImporter


class TestRosterImporter(unittest.TestCase):
    """Test the RosterImporter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(__file__).parent / "test_data" / "validation"
        
        # Create test .env file
        self.env_file = os.path.join(self.test_dir, ".env")
        with open(self.env_file, 'w') as f:
            f.write("ROSTER_CSV_FILE=roster_report_valid.csv\n")
            f.write("MB_PROGRESS_CSV_FILE=merit_badge_progress.csv\n")
            f.write("VALIDATE_BEFORE_IMPORT=true\n")
            f.write("GENERATE_VALIDATION_REPORTS=true\n")
            f.write("VALIDATION_REPORTS_DIR=logs\n")
        
        # Change to test directory
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create data directory and copy test file
        os.makedirs("data", exist_ok=True)
        shutil.copy(
            self.test_data_dir / "roster_report_valid.csv",
            "data/roster_report_valid.csv"
        )
        
        # Create importer
        self.importer = RosterImporter(self.env_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_importer_initialization(self):
        """Test RosterImporter initialization."""
        self.assertEqual(self.importer.roster_csv_file, "roster_report_valid.csv")
        self.assertEqual(self.importer.mb_progress_csv_file, "merit_badge_progress.csv")
        self.assertTrue(self.importer.validate_before_import)
        self.assertTrue(self.importer.generate_validation_reports)
        self.assertEqual(self.importer.validation_reports_dir, "logs")
    
    def test_missing_roster_file(self):
        """Test behavior when roster file is missing."""
        # Remove the roster file
        os.remove("data/roster_report_valid.csv")
        
        success = self.importer.run_import()
        self.assertFalse(success, "Import should fail when roster file is missing")
    
    @patch('import_roster.RosterImporter._recreate_database')
    def test_validation_with_valid_data(self, mock_recreate_db):
        """Test validation process with valid data."""
        mock_recreate_db.return_value = True
        
        success = self.importer.run_import()
        self.assertTrue(success, "Import should succeed with valid data")
        mock_recreate_db.assert_called_once()
    
    @patch('import_roster.RosterImporter._recreate_database')
    def test_validation_with_invalid_data(self, mock_recreate_db):
        """Test validation process with invalid data."""
        # Replace valid file with invalid one
        os.remove("data/roster_report_valid.csv")
        shutil.copy(
            self.test_data_dir / "roster_report_invalid.csv",
            "data/roster_report_valid.csv"
        )
        
        success = self.importer.run_import()
        self.assertFalse(success, "Import should fail with invalid data")
        mock_recreate_db.assert_not_called()
    
    @patch('import_roster.RosterImporter._recreate_database')
    def test_force_import_skips_validation(self, mock_recreate_db):
        """Test that force import skips validation."""
        mock_recreate_db.return_value = True
        
        # Replace valid file with invalid one
        os.remove("data/roster_report_valid.csv")
        shutil.copy(
            self.test_data_dir / "roster_report_invalid.csv",
            "data/roster_report_valid.csv"
        )
        
        success = self.importer.run_import(force=True)
        self.assertTrue(success, "Force import should succeed even with invalid data")
        mock_recreate_db.assert_called_once()
    
    def test_validation_disabled_in_config(self):
        """Test behavior when validation is disabled in config."""
        # Create new env file with validation disabled
        env_file_no_validation = os.path.join(self.test_dir, ".env_no_validation")
        with open(env_file_no_validation, 'w') as f:
            f.write("ROSTER_CSV_FILE=roster_report_valid.csv\n")
            f.write("VALIDATE_BEFORE_IMPORT=false\n")
        
        with patch('import_roster.RosterImporter._recreate_database') as mock_recreate_db:
            mock_recreate_db.return_value = True
            
            importer = RosterImporter(env_file_no_validation)
            success = importer.run_import()
            
            self.assertTrue(success, "Import should succeed when validation is disabled")
            mock_recreate_db.assert_called_once()
    
    @patch('import_roster.create_database_schema')
    @patch('import_roster.verify_schema')
    def test_database_recreation(self, mock_verify, mock_create):
        """Test database recreation functionality."""
        mock_create.return_value = True
        mock_verify.return_value = True
        
        success = self.importer._recreate_database()
        self.assertTrue(success, "Database recreation should succeed")
        
        mock_create.assert_called_once()
        mock_verify.assert_called_once()
    
    @patch('import_roster.create_database_schema')
    def test_database_recreation_failure(self, mock_create):
        """Test database recreation failure handling."""
        mock_create.return_value = False
        
        success = self.importer._recreate_database()
        self.assertFalse(success, "Database recreation should fail when create_database_schema fails")
    
    def test_validation_report_generation(self):
        """Test that validation reports are generated."""
        # Replace valid file with invalid one to trigger report generation
        os.remove("data/roster_report_valid.csv")
        shutil.copy(
            self.test_data_dir / "roster_report_invalid.csv",
            "data/roster_report_valid.csv"
        )
        
        success = self.importer.run_import()
        self.assertFalse(success, "Import should fail with invalid data")
        
        # Check that logs directory was created and contains reports
        logs_dir = Path("logs")
        self.assertTrue(logs_dir.exists(), "Logs directory should be created")
        
        report_files = list(logs_dir.glob("validation_report_*.txt"))
        self.assertGreater(len(report_files), 0, "Validation report should be generated")


class TestImportScriptCommandLine(unittest.TestCase):
    """Test the command-line interface of the import script."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(__file__).parent / "test_data" / "validation"
        
        # Create test .env file
        self.env_file = os.path.join(self.test_dir, ".env")
        with open(self.env_file, 'w') as f:
            f.write("ROSTER_CSV_FILE=roster_report_valid.csv\n")
            f.write("MB_PROGRESS_CSV_FILE=merit_badge_progress.csv\n")
            f.write("VALIDATE_BEFORE_IMPORT=true\n")
            f.write("GENERATE_VALIDATION_REPORTS=true\n")
            f.write("VALIDATION_REPORTS_DIR=logs\n")
        
        # Change to test directory
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create data directory and copy test file
        os.makedirs("data", exist_ok=True)
        shutil.copy(
            self.test_data_dir / "roster_report_valid.csv",
            "data/roster_report_valid.csv"
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_missing_config_file(self):
        """Test behavior when config file is missing."""
        # Remove the .env file
        os.remove(self.env_file)
        
        with patch('sys.argv', ['import_roster.py', '--config', 'nonexistent.env']):
            with patch('sys.exit') as mock_exit:
                try:
                    from import_roster import main
                    main()
                except SystemExit:
                    pass
                mock_exit.assert_called_with(1)
    
    @patch('import_roster.RosterImporter._recreate_database')
    def test_validate_only_mode(self, mock_recreate_db):
        """Test validate-only mode."""
        mock_recreate_db.return_value = True
        
        with patch('sys.argv', ['import_roster.py', '--config', self.env_file, '--validate-only']):
            with patch('sys.exit') as mock_exit:
                try:
                    from import_roster import main
                    main()
                except SystemExit:
                    pass
                
                # Should exit with 0 for valid data
                mock_exit.assert_called_with(0)
                # Database should not be recreated in validate-only mode
                mock_recreate_db.assert_not_called()
    
    def test_validate_only_with_invalid_data(self):
        """Test validate-only mode with invalid data."""
        # Replace valid file with invalid one
        os.remove("data/roster_report_valid.csv")
        shutil.copy(
            self.test_data_dir / "roster_report_invalid.csv",
            "data/roster_report_valid.csv"
        )
        
        with patch('sys.argv', ['import_roster.py', '--config', self.env_file, '--validate-only']):
            with patch('sys.exit') as mock_exit:
                try:
                    from import_roster import main
                    main()
                except SystemExit:
                    pass
                
                # Should exit with 1 for invalid data
                mock_exit.assert_called_with(1)


if __name__ == '__main__':
    unittest.main()