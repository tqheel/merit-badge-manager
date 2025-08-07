import streamlit as st
import os
import sys
from pathlib import Path
from typing import Dict, Tuple
import shutil
from datetime import datetime

# Add the new layer directories to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from csv_validator import CSVValidator, ValidationResult
from roster_parser import RosterParser
from setup_database import create_database_schema

def load_env_file() -> Dict[str, str]:
    """Load existing .env file if it exists."""
    env_vars = {}
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def backup_database(db_path: str = "merit_badge_manager.db") -> str | None:
    """
    Create a backup of the current database.
    
    Returns:
        Path to backup file if successful, None otherwise
    """
    if not Path(db_path).exists():
        return None
    
    try:
        # Ensure backups directory exists
        backups_dir = Path("backups")
        backups_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{Path(db_path).name}.backup_{timestamp}"
        backup_path = backups_dir / backup_filename
        shutil.copy2(db_path, backup_path)
        return str(backup_path)
    except Exception as e:
        st.error(f"Error creating database backup: {e}")
        return None

def restore_database(backup_path: str, db_path: str = "merit_badge_manager.db") -> bool:
    """
    Restore database from backup.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if Path(backup_path).exists():
            shutil.copy2(backup_path, db_path)
            return True
        return False
    except Exception as e:
        st.error(f"Error restoring database: {e}")
        return False

def recreate_database_safely(db_path: str = "merit_badge_manager.db") -> bool:
    """
    Safely recreate the database by handling file locks and ensuring clean deletion.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import time
        import sqlite3
        
        # First, try to close any existing connections by attempting a dummy connection
        # This helps ensure no lingering connections are holding locks
        if Path(db_path).exists():
            try:
                # Try to connect and immediately close to flush any pending operations
                conn = sqlite3.connect(db_path, timeout=1.0)
                conn.close()
                time.sleep(0.1)  # Brief pause to allow cleanup
            except:
                pass  # Ignore connection errors, we're just trying to clean up
            
            # Remove the existing database file
            try:
                Path(db_path).unlink()
                time.sleep(0.1)  # Brief pause after deletion
            except FileNotFoundError:
                pass  # File already gone, that's fine
            except PermissionError as e:
                st.error(f"❌ Cannot delete database file (file may be in use): {e}")
                return False
            except Exception as e:
                st.error(f"❌ Error deleting database file: {e}")
                return False
        
        # Create the new database schema
        success = create_database_schema(db_path, include_youth=True)
        if not success:
            st.error("❌ Database schema creation failed")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"❌ Unexpected error during database recreation: {e}")
        return False

def display_validation_results(results: Dict[str, ValidationResult]) -> bool:
    """
    Display validation results in Streamlit format.
    
    Returns:
        True if all validations passed, False otherwise
    """
    overall_valid = True
    total_errors = 0
    total_warnings = 0
    
    st.subheader("📋 Validation Results")
    
    for file_type, result in results.items():
        # Create expandable section for each file type
        with st.expander(f"{'✅' if result.is_valid else '❌'} {file_type} - {'PASS' if result.is_valid else 'FAIL'}", expanded=not result.is_valid):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Rows Processed", result.row_count)
            with col2:
                st.metric("Valid Rows", result.valid_rows)
            with col3:
                st.metric("Skipped Rows", len(result.skipped_records), delta=None if len(result.skipped_records) == 0 else f"-{len(result.skipped_records)}")
            with col4:
                st.metric("Errors", len(result.errors), delta=None if len(result.errors) == 0 else f"-{len(result.errors)}")
            with col5:
                st.metric("Warnings", len(result.warnings), delta=None if len(result.warnings) == 0 else f"-{len(result.warnings)}")
            
            # Show skipped records
            if result.skipped_records:
                st.info("**Records skipped (duplicates):**")
                for skipped in result.skipped_records:
                    st.info(f"• {skipped}")
            
            # Show errors
            if result.errors:
                st.error("**Errors found:**")
                for error in result.errors:
                    st.error(f"• {error}")
            
            # Show warnings
            if result.warnings:
                st.warning("**Warnings found:**")
                for warning in result.warnings:
                    st.warning(f"• {warning}")
        
        if not result.is_valid:
            overall_valid = False
        
        total_errors += len(result.errors)
        total_warnings += len(result.warnings)
    
    # Overall summary
    if overall_valid:
        st.success(f"🎉 **All validations passed!** Total warnings: {total_warnings}")
    else:
        st.error(f"❌ **Validation failed!** Total errors: {total_errors}, Total warnings: {total_warnings}")
        st.error("🚨 Cannot proceed with import - Please fix validation errors first!")
    
    return overall_valid

def run_validation_only(roster_file_path: Path) -> Tuple[bool, Dict[str, ValidationResult]]:
    """
    Run validation on roster files and merit badge progress file and return results.
    
    Returns:
        Tuple of (overall_valid, results_dict)
    """
    try:
        # Parse the roster file to get adult and youth sections
        parser = RosterParser(str(roster_file_path), "output")
        adult_file, youth_file = parser.parse_roster()
        
        # Validate the parsed output files
        validator = CSVValidator()
        results = {}
        
        if os.path.exists(adult_file):
            results["Adult Roster"] = validator.validate_adult_roster(adult_file)
        
        if os.path.exists(youth_file):
            results["Youth Roster"] = validator.validate_youth_roster(youth_file)
        
        # Also validate Merit Badge Progress file if it exists
        current_env = load_env_file()
        mb_progress_file = current_env.get('MB_PROGRESS_CSV_FILE', 'merit_badge_progress.csv')
        data_dir = Path("data")
        mb_progress_path = data_dir / mb_progress_file
        
        if mb_progress_path.exists():
            # Parse and clean the MB progress file first (like we do with roster files)
            from mb_progress_parser import MeritBadgeProgressParser
            mb_parser = MeritBadgeProgressParser(str(mb_progress_path), "output")
            cleaned_mb_file = mb_parser._clean_csv()  # Use the cleaning method directly
            results["Merit Badge Progress"] = validator.validate_mb_progress(str(cleaned_mb_file))
        
        # Calculate overall validity
        overall_valid = all(result.is_valid for result in results.values())
        
        return overall_valid, results
        
    except Exception as e:
        st.error(f"Validation error: {e}")
        return False, {}

st.header("📁 CSV Import & Validation")

# Check if .env file exists
if not Path(".env").exists():
    st.warning("⚠️ Please configure settings first!")
    st.stop()

# Load environment variables
current_env = load_env_file()
roster_file = current_env.get('ROSTER_CSV_FILE', 'roster_report.csv')
mb_progress_file = current_env.get('MB_PROGRESS_CSV_FILE', 'merit_badge_progress.csv')

st.subheader("📋 Import Status")

# Check if data directory exists
data_dir = Path("data")
if not data_dir.exists():
    st.info("Creating data directory...")
    data_dir.mkdir()

# Display expected file locations
st.write("**Expected file locations:**")
st.write(f"- Roster CSV: `data/{roster_file}`")
st.write(f"- Merit Badge Progress CSV: `data/{mb_progress_file}`")

# Check file existence
roster_path = data_dir / roster_file
mb_progress_path = data_dir / mb_progress_file

roster_exists = roster_path.exists()
mb_progress_exists = mb_progress_path.exists()

col1, col2 = st.columns(2)

with col1:
    st.write("**Roster File:**")
    if roster_exists:
        st.success("✅ Found")
    else:
        st.error("❌ Not found")

with col2:
    st.write("**Merit Badge Progress File:**")
    if mb_progress_exists:
        st.success("✅ Found")
    else:
        st.warning("⚠️ Not found (optional)")

# Validation results storage in session state
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None
if 'validation_passed' not in st.session_state:
    st.session_state.validation_passed = False
if 'db_backup_path' not in st.session_state:
    st.session_state.db_backup_path = None

# Import options
st.subheader("🚀 Import Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Validate Only", disabled=not roster_exists):
        with st.spinner("Validating CSV files..."):
            validation_passed, validation_results = run_validation_only(roster_path)
            st.session_state.validation_results = validation_results
            st.session_state.validation_passed = validation_passed

# Display validation results if available
if st.session_state.validation_results:
    validation_passed = display_validation_results(st.session_state.validation_results)
    st.session_state.validation_passed = validation_passed

    # Show import options based on validation results
    if not validation_passed:
        st.subheader("🛠️ Import Options")
        st.warning("⚠️ Validation failed. Choose how to proceed:")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("🔧 Force Import (Skip Validation)", type="secondary"):
                with st.spinner("Creating database backup and importing data..."):
                    try:
                        # Create backup before import
                        backup_path = backup_database()
                        if backup_path:
                            st.session_state.db_backup_path = backup_path
                            st.info(f"✅ Database backed up to: {backup_path}")

                        # Create/recreate database
                        st.info("Setting up database...")
                        success = recreate_database_safely("merit_badge_manager.db")
                        if not success:
                            st.error("❌ Failed to create database schema!")
                        else:
                            # Import roster data with force flag
                            from import_roster import RosterImporter
                            importer = RosterImporter(ui_mode=True)

                            st.info("Importing roster data (skipping validation)...")
                            success = importer.run_import(force=True)

                            if success:
                                # Import merit badge progress data if file exists
                                mb_progress_path = data_dir / mb_progress_file
                                if mb_progress_path.exists():
                                    st.info("Importing merit badge progress data...")
                                    try:
                                        from import_mb_progress import MeritBadgeProgressImporter
                                        mb_importer = MeritBadgeProgressImporter("merit_badge_manager.db")
                                        mb_success = mb_importer.import_csv(str(mb_progress_path))

                                        if mb_success:
                                            stats = mb_importer.get_import_summary()
                                            st.info(f"✅ Merit Badge Progress imported: {stats['imported_records']} records")
                                        else:
                                            st.warning("⚠️ Merit Badge Progress import failed, but roster import succeeded")

                                    except Exception as e:
                                        st.warning(f"⚠️ Merit Badge Progress import error: {e}")
                                else:
                                    st.info(f"ℹ️ No merit badge progress file found at: data/{mb_progress_file}")

                                st.success("✅ Data imported successfully (with validation errors)!")
                                st.balloons()
                                # Clear validation results
                                st.session_state.validation_results = None
                            else:
                                st.error("❌ Import failed!")
                                # Restore backup if available
                                if st.session_state.db_backup_path:
                                    if restore_database(st.session_state.db_backup_path):
                                        st.info("🔄 Database restored from backup")

                    except Exception as e:
                        st.error(f"Import error occurred during forced import: {e}")
                        # Restore backup if available
                        if st.session_state.db_backup_path:
                            if restore_database(st.session_state.db_backup_path):
                                st.info("🔄 Database restored from backup")

        with col_b:
            if st.button("❌ Abort Import", type="secondary"):
                st.session_state.validation_results = None
                st.session_state.validation_passed = False
                st.info("Import aborted. Please fix validation errors and try again.")
                st.rerun()

with col2:
    # Only enable import if validation passed or no validation has been run
    import_disabled = roster_exists and st.session_state.validation_results is not None and not st.session_state.validation_passed

    if st.button("Import Data", disabled=not roster_exists or import_disabled):
        with st.spinner("Validating and importing data..."):
            try:
                # Run validation first
                validation_passed, validation_results = run_validation_only(roster_path)

                if not validation_passed:
                    st.session_state.validation_results = validation_results
                    st.session_state.validation_passed = validation_passed
                    st.error("❌ Validation failed! Please review errors above and choose how to proceed.")
                    st.rerun()

                # Create backup before import
                backup_path = backup_database()
                if backup_path:
                    st.session_state.db_backup_path = backup_path
                    st.info(f"✅ Database backed up to: {backup_path}")

                # Create/recreate database
                st.info("Setting up database...")
                success = recreate_database_safely("merit_badge_manager.db")
                if not success:
                    st.error("❌ Failed to create database schema!")
                else:
                    # Import roster data
                    from import_roster import RosterImporter
                    importer = RosterImporter(ui_mode=True)

                    st.info("Importing roster data...")
                    success = importer.run_import()

                    if success:
                        # Import merit badge progress data if file exists
                        mb_progress_path = data_dir / mb_progress_file
                        if mb_progress_path.exists():
                            st.info("Importing merit badge progress data...")
                            try:
                                from import_mb_progress import MeritBadgeProgressImporter
                                mb_importer = MeritBadgeProgressImporter("merit_badge_manager.db")
                                mb_success = mb_importer.import_csv(str(mb_progress_path))

                                if mb_success:
                                    stats = mb_importer.get_import_summary()
                                    st.info(f"✅ Merit Badge Progress imported: {stats['imported_records']} records")
                                else:
                                    st.warning("⚠️ Merit Badge Progress import failed, but roster import succeeded")

                            except Exception as e:
                                st.warning(f"⚠️ Merit Badge Progress import error: {e}")
                        else:
                            st.info(f"ℹ️ No merit badge progress file found at: data/{mb_progress_file}")

                        st.success("✅ Data imported successfully!")
                        st.balloons()
                        # Clear validation results
                        st.session_state.validation_results = None
                    else:
                        st.error("❌ Import failed!")
                        # Restore backup if available
                        if st.session_state.db_backup_path:
                            if restore_database(st.session_state.db_backup_path):
                                st.info("🔄 Database restored from backup")

            except Exception as e:
                st.error(f"Import error occurred during normal import: {e}")
                # Restore backup if available
                if st.session_state.db_backup_path:
                    if restore_database(st.session_state.db_backup_path):
                        st.info("🔄 Database restored from backup")

with col3:
    if st.button("Reset Database"):
        with st.spinner("Resetting database..."):
            try:
                # Create backup before reset
                backup_path = backup_database()
                if backup_path:
                    st.info(f"✅ Database backed up to: {backup_path}")

                # Remove existing database
                db_path = Path("merit_badge_manager.db")
                if db_path.exists():
                    db_path.unlink()

                # Recreate schema
                create_database_schema("merit_badge_manager.db", include_youth=True)
                st.success("✅ Database reset successfully!")

                # Clear session state
                st.session_state.validation_results = None
                st.session_state.validation_passed = False

            except Exception as e:
                st.error(f"Database reset error occurred: {e}")

# Show backup information if available
if st.session_state.db_backup_path:
    st.info(f"💾 **Current backup:** `{st.session_state.db_backup_path}`")

    col_restore, col_cleanup = st.columns(2)
    with col_restore:
        if st.button("🔄 Restore from Backup"):
            if restore_database(st.session_state.db_backup_path):
                st.success("✅ Database restored from backup!")
                st.session_state.validation_results = None
                st.session_state.validation_passed = False
                st.rerun()
            else:
                st.error("❌ Failed to restore from backup")

    with col_cleanup:
        if st.button("🗑️ Remove Backup"):
            try:
                Path(st.session_state.db_backup_path).unlink()
                st.session_state.db_backup_path = None
                st.success("✅ Backup file removed")
                st.rerun()
            except Exception as e:
                st.error(f"Error removing backup: {e}")
