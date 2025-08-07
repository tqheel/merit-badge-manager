"""
Playwright fixtures for UI testing.
"""

import pytest
import subprocess
import time
import requests
from pathlib import Path
import sys
import os


# Add the layer directories to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))


@pytest.fixture(scope="session")
def streamlit_app():
    """Start Streamlit app for testing."""
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent.parent)
    
    # Start Streamlit server in the background
    process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "web-ui/main.py", 
        "--server.headless", "true",
        "--server.port", "8501",
        "--server.address", "localhost"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the server to start
    max_wait = 30
    for _ in range(max_wait):
        try:
            response = requests.get("http://localhost:8501/_stcore/health")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        process.terminate()
        raise RuntimeError("Streamlit server failed to start")
    
    yield "http://localhost:8501"
    
    # Clean up
    process.terminate()
    process.wait()


@pytest.fixture
def clean_database():
    """Ensure clean database state for testing."""
    db_path = Path("merit_badge_manager.db")
    backup_path = None
    
    # Backup existing database if it exists
    if db_path.exists():
        backup_path = db_path.with_suffix(".db.test_backup")
        db_path.rename(backup_path)
    
    yield
    
    # Restore original database
    if db_path.exists():
        db_path.unlink()
    if backup_path and backup_path.exists():
        backup_path.rename(db_path)


@pytest.fixture
def create_test_db():
    """Create a test database."""
    from database.setup_database import create_database_schema
    db_path = "merit_badge_manager.db"
    if Path(db_path).exists():
        Path(db_path).unlink()
    create_database_schema(db_path, include_youth=True)
    yield
    if Path(db_path).exists():
        Path(db_path).unlink()


@pytest.fixture
def sample_csv_files(tmp_path):
    """Create sample CSV files for testing."""
    # Create sample adult roster CSV
    adult_csv = tmp_path / "adult_roster.csv"
    adult_csv.write_text("""First Name,Last Name,BSA ID,Email,Position 1,Position 2,Position 3,Position 4,Position 5,Training Date,Patrol,Gender
John,Doe,12345678,john.doe@example.com,Scoutmaster,,,,,2023-01-15,Adult,M
Jane,Smith,87654321,jane.smith@example.com,Committee Chair,,,,,2023-02-20,Adult,F
""")
    
    # Create sample youth roster CSV  
    youth_csv = tmp_path / "youth_roster.csv"
    youth_csv.write_text("""First Name,Last Name,BSA ID,Email,Rank,Patrol,Gender,Primary Parent/Guardian Name,Primary Parent/Guardian Email
Mike,Johnson,11111111,mike.johnson@example.com,Eagle,Eagles,M,Bob Johnson,bob.johnson@example.com
Sarah,Williams,22222222,sarah.williams@example.com,Star,Stars,F,Lisa Williams,lisa.williams@example.com
""")
    
    # Create combined roster file (what users typically upload)
    combined_csv = tmp_path / "combined_roster.csv"
    combined_csv.write_text("""First Name,Last Name,BSA ID,Email,Position 1,Position 2,Position 3,Position 4,Position 5,Training Date,Patrol,Gender,Rank,Primary Parent/Guardian Name,Primary Parent/Guardian Email
John,Doe,12345678,john.doe@example.com,Scoutmaster,,,,,2023-01-15,Adult,M,,,
Jane,Smith,87654321,jane.smith@example.com,Committee Chair,,,,,2023-02-20,Adult,F,,,
Mike,Johnson,11111111,mike.johnson@example.com,,,,,,2023-03-10,Eagles,M,Eagle,Bob Johnson,bob.johnson@example.com
Sarah,Williams,22222222,sarah.williams@example.com,,,,,,2023-04-05,Stars,F,Star,Lisa Williams,lisa.williams@example.com
""")
    
    return {
        "adult": adult_csv,
        "youth": youth_csv, 
        "combined": combined_csv
    }