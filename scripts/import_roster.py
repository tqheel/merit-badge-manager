#!/usr/bin/env python3
"""
Merit Badge Manager - Roster Import Script

Imports CSV roster data with validation and database recreation.
Reads configuration from .env file for CSV file names and validation settings.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from csv_validator import CSVValidator, ValidationResult, print_validation_summary
from roster_parser import RosterParser


class RosterImporter:
    """
    Handles the complete roster import process including validation,
    database recreation, and data import.
    """
    
    def __init__(self, config_file: str = ".env"):
        """
        Initialize the importer with configuration.
        
        Args:
            config_file: Path to environment configuration file
        """
        # Load environment configuration
        load_dotenv(config_file)
        
        self.roster_csv_file = os.getenv('ROSTER_CSV_FILE', 'roster_report.csv')
        self.mb_progress_csv_file = os.getenv('MB_PROGRESS_CSV_FILE', 'merit_badge_progress.csv')
        self.validate_before_import = os.getenv('VALIDATE_BEFORE_IMPORT', 'true').lower() == 'true'
        self.generate_validation_reports = os.getenv('GENERATE_VALIDATION_REPORTS', 'true').lower() == 'true'
        self.validation_reports_dir = os.getenv('VALIDATION_REPORTS_DIR', 'logs')
        
        # Set up directories
        self.data_dir = Path("data")
        self.output_dir = Path("output")
        self.db_scripts_dir = Path("db-scripts")
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        Path(self.validation_reports_dir).mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.validator = CSVValidator()
    
    def run_import(self, force: bool = False) -> bool:
        """
        Run the complete import process.
        
        Args:
            force: Skip validation if True
            
        Returns:
            True if import was successful, False otherwise
        """
        print("🚀 Starting Merit Badge Manager Roster Import")
        print("=" * 60)
        
        # Check for required files
        roster_file_path = self.data_dir / self.roster_csv_file
        
        if not roster_file_path.exists():
            print(f"❌ Roster file not found: {roster_file_path}")
            print(f"   Please place your roster CSV file in the data directory")
            print(f"   and update the ROSTER_CSV_FILE setting in .env")
            return False
        
        print(f"📁 Roster file: {roster_file_path}")
        
        # Run validation if enabled
        if self.validate_before_import and not force:
            print(f"\n🔍 Running CSV validation...")
            
            if not self._run_validation(roster_file_path):
                return False
        else:
            if force:
                print("\n⚠️  Skipping validation (force mode)")
            else:
                print("\n⚠️  Validation disabled in configuration")
        
        # Parse the roster file
        print(f"\n📊 Parsing roster file...")
        try:
            parser = RosterParser(str(roster_file_path), str(self.output_dir))
            adult_file, youth_file = parser.parse_roster()
            
            summary = parser.get_parsing_summary()
            print(f"   ✅ Parsed {summary['adult_records']} adult records")
            print(f"   ✅ Parsed {summary['youth_records']} youth records")
            print(f"   📄 Adult file: {adult_file}")
            print(f"   📄 Youth file: {youth_file}")
            
        except Exception as e:
            print(f"❌ Error parsing roster file: {e}")
            self.logger.error(f"Roster parsing failed: {e}")
            return False
        
        # Recreate database
        print(f"\n🗄️  Recreating database...")
        if not self._recreate_database():
            return False
        
        print(f"\n🎉 Import completed successfully!")
        print(f"   📁 Processed files in: {self.output_dir}")
        print(f"   🗄️  Database recreated with latest schema")
        
        return True
    
    def _run_validation(self, roster_file_path: Path) -> bool:
        """
        Run CSV validation on the roster file.
        
        Args:
            roster_file_path: Path to the roster CSV file
            
        Returns:
            True if validation passed, False otherwise
        """
        try:
            # For now, we'll validate the roster file as both adult and youth
            # In the future, we might separate these or auto-detect the format
            
            # First, try to parse the file to get adult and youth sections
            parser = RosterParser(str(roster_file_path), str(self.output_dir))
            adult_file, youth_file = parser.parse_roster()
            
            # Validate the parsed output files
            results = {}
            
            if os.path.exists(adult_file):
                results["Adult Roster"] = self.validator.validate_adult_roster(adult_file)
            
            if os.path.exists(youth_file):
                results["Youth Roster"] = self.validator.validate_youth_roster(youth_file)
            
            # Print validation summary
            overall_valid = print_validation_summary(results)
            
            # Generate detailed report if requested and there are issues
            if self.generate_validation_reports and any(r.has_issues() for r in results.values()):
                report_file = self.validator.generate_validation_report(results, self.validation_reports_dir)
                
                print(f"📋 Detailed validation report generated: {report_file}")
                
                # Ask user if they want to see the report
                if not overall_valid:
                    response = input("\n❓ Would you like to see the detailed validation report? (y/n): ").lower().strip()
                    if response in ['y', 'yes']:
                        self._show_validation_report(report_file)
            
            return overall_valid
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            self.logger.error(f"Validation failed: {e}")
            return False
    
    def _show_validation_report(self, report_file: str):
        """Display the validation report to the user."""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n" + "=" * 80)
            print("DETAILED VALIDATION REPORT")
            print("=" * 80)
            print(content)
        except Exception as e:
            print(f"❌ Error reading validation report: {e}")
    
    def _recreate_database(self) -> bool:
        """
        Recreate the database with the latest schema.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import the database setup script
            sys.path.insert(0, str(self.db_scripts_dir))
            from setup_database import create_database_schema, verify_schema
            
            db_path = "merit_badge_manager.db"
            
            # Remove existing database if it exists
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"   🗑️  Removed existing database: {db_path}")
            
            # Create new database with schema
            print(f"   🏗️  Creating new database schema...")
            success = create_database_schema(db_path, include_youth=True)
            
            if not success:
                print(f"❌ Failed to create database schema")
                return False
            
            # Verify the schema
            print(f"   🔍 Verifying database schema...")
            verify_success = verify_schema(db_path, include_youth=True)
            
            if not verify_success:
                print(f"❌ Database schema verification failed")
                return False
            
            print(f"   ✅ Database recreated successfully: {db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error recreating database: {e}")
            self.logger.error(f"Database recreation failed: {e}")
            return False


def main():
    """Main function to handle command line arguments and run the import."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Import roster CSV data with validation and database recreation"
    )
    parser.add_argument(
        "--config", "-c",
        default=".env",
        help="Configuration file path (default: .env)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Skip validation and force import"
    )
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Run validation only, do not import"
    )
    
    args = parser.parse_args()
    
    # Check if configuration file exists
    if not os.path.exists(args.config):
        print(f"❌ Configuration file not found: {args.config}")
        print(f"   Please copy .env.template to .env and configure your settings")
        sys.exit(1)
    
    # Create importer instance
    importer = RosterImporter(args.config)
    
    if args.validate_only:
        # Run validation only
        print("🔍 Running validation only...")
        roster_file_path = importer.data_dir / importer.roster_csv_file
        
        if not roster_file_path.exists():
            print(f"❌ Roster file not found: {roster_file_path}")
            sys.exit(1)
        
        success = importer._run_validation(roster_file_path)
        sys.exit(0 if success else 1)
    
    # Run full import
    success = importer.run_import(force=args.force)
    
    if success:
        print("\n✅ Import process completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Import process failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()