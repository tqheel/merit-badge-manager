"""
Tests for the adult roster database schema creation and validation.
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime, date
import sys

# Add the project root to the Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the database setup functions directly
import subprocess


class TestDatabaseSchema:
    """Test cases for adult roster database schema creation."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_adult_roster.db")
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_database_schema(self, db_path: str) -> bool:
        """Create database schema using the setup script."""
        project_root = Path(__file__).parent.parent
        setup_script = project_root / "db-scripts" / "setup_database.py"
        
        try:
            result = subprocess.run([
                sys.executable, str(setup_script),
                "--database", db_path,
                "--force"
            ], capture_output=True, text=True, cwd=str(project_root))
            
            return result.returncode == 0
        except Exception as e:
            print(f"Error running setup script: {e}")
            return False
    
    def verify_schema(self, db_path: str) -> bool:
        """Verify database schema using the setup script."""
        project_root = Path(__file__).parent.parent
        setup_script = project_root / "db-scripts" / "setup_database.py"
        
        try:
            result = subprocess.run([
                sys.executable, str(setup_script),
                "--database", db_path,
                "--verify"
            ], capture_output=True, text=True, cwd=str(project_root))
            
            return result.returncode == 0
        except Exception as e:
            print(f"Error running verification: {e}")
            return False
    
    def test_required_tables_exist(self):
        """Test that all required tables are created."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check that all required tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['adult_merit_badges', 'adult_positions', 'adult_training', 'adults']
        for table in expected_tables:
            assert table in tables, f"Table {table} should exist in database"
        
        conn.close()
    
    def test_adults_table_structure(self):
        """Test that the adults table has correct structure."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute("PRAGMA table_info(adults)")
        columns = cursor.fetchall()
        
        # Verify key columns exist
        column_names = [col[1] for col in columns]
        required_columns = [
            'id', 'first_name', 'last_name', 'email', 'bsa_number',
            'unit_number', 'date_joined', 'created_at', 'updated_at'
        ]
        
        for col in required_columns:
            assert col in column_names, f"Column {col} should exist in adults table"
        
        # Verify primary key
        pk_columns = [col[1] for col in columns if col[5] == 1]  # pk flag is index 5
        assert 'id' in pk_columns, "id should be primary key"
        
        conn.close()
    
    def test_foreign_key_relationships(self):
        """Test that foreign key relationships are properly defined."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        cursor = conn.cursor()
        
        # Test foreign key constraints for each related table
        related_tables = ['adult_training', 'adult_merit_badges', 'adult_positions']
        
        for table in related_tables:
            # Get foreign key info
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()
            
            # Should have one foreign key pointing to adults table
            assert len(fks) == 1, f"Table {table} should have exactly one foreign key"
            assert fks[0][2] == 'adults', f"Foreign key in {table} should reference adults table"
            assert fks[0][3] == 'adult_id', f"Foreign key column should be adult_id"
            assert fks[0][4] == 'id', f"Foreign key should reference id column in adults"
        
        conn.close()
    
    def test_indexes_creation(self):
        """Test that performance indexes are created."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Get all indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Verify key indexes exist
        expected_indexes = [
            'idx_adults_bsa_number', 'idx_adults_name', 'idx_adults_email',
            'idx_adult_training_adult_id', 'idx_adult_merit_badges_adult_id',
            'idx_adult_positions_adult_id'
        ]
        
        for index in expected_indexes:
            assert index in indexes, f"Index {index} should exist"
        
        conn.close()
    
    def test_validation_views_creation(self):
        """Test that validation views are created."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Get all views
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        expected_views = [
            'adults_missing_data', 'current_positions', 
            'merit_badge_counselors', 'training_expiration_summary'
        ]
        
        for view in expected_views:
            assert view in views, f"View {view} should exist"
            
            # Test that view can be queried
            cursor.execute(f"SELECT COUNT(*) FROM {view}")
            result = cursor.fetchone()
            assert result is not None, f"View {view} should be queryable"
        
        conn.close()
    
    def test_insert_sample_adult_data(self):
        """Test inserting and querying adult data."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Insert sample adult
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number, date_joined)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('John', 'Doe', 'john.doe@example.com', 12345, 'Troop 100', '2020-01-15'))
        
        adult_id = cursor.lastrowid
        
        # Insert related training data
        cursor.execute("""
            INSERT INTO adult_training (adult_id, training_code, training_name, expiration_date)
            VALUES (?, ?, ?, ?)
        """, (adult_id, 'YPT', 'Youth Protection Training', '2025-01-15'))
        
        # Insert merit badge counselor data
        cursor.execute("""
            INSERT INTO adult_merit_badges (adult_id, merit_badge_name)
            VALUES (?, ?)
        """, (adult_id, 'Camping'))
        
        # Insert position data
        cursor.execute("""
            INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current)
            VALUES (?, ?, ?, ?)
        """, (adult_id, 'Scoutmaster', '(2y 6m)', 1))
        
        conn.commit()
        
        # Verify data was inserted correctly
        cursor.execute("SELECT COUNT(*) FROM adults")
        assert cursor.fetchone()[0] == 1, "Should have one adult record"
        
        cursor.execute("SELECT COUNT(*) FROM adult_training")
        assert cursor.fetchone()[0] == 1, "Should have one training record"
        
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        assert cursor.fetchone()[0] == 1, "Should have one merit badge record"
        
        cursor.execute("SELECT COUNT(*) FROM adult_positions")
        assert cursor.fetchone()[0] == 1, "Should have one position record"
        
        # Test foreign key constraint
        cursor.execute("SELECT first_name, last_name FROM adults WHERE id = ?", (adult_id,))
        adult = cursor.fetchone()
        assert adult[0] == 'John' and adult[1] == 'Doe', "Adult data should be retrievable"
        
        conn.close()
    
    def test_unique_constraints(self):
        """Test that unique constraints work properly."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Insert first adult
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, bsa_number)
            VALUES (?, ?, ?)
        """, ('John', 'Doe', 12345))
        
        # Try to insert another adult with same BSA number (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO adults (first_name, last_name, bsa_number)
                VALUES (?, ?, ?)
            """, ('Jane', 'Smith', 12345))
        
        conn.close()
    
    def test_cascade_delete(self):
        """Test that cascade delete works for related records."""
        self.create_database_schema(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Insert adult and related data
        cursor.execute("""
            INSERT INTO adults (first_name, last_name, bsa_number)
            VALUES (?, ?, ?)
        """, ('John', 'Doe', 12345))
        
        adult_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO adult_training (adult_id, training_code, training_name)
            VALUES (?, ?, ?)
        """, (adult_id, 'YPT', 'Youth Protection Training'))
        
        # Verify records exist
        cursor.execute("SELECT COUNT(*) FROM adults")
        assert cursor.fetchone()[0] == 1
        
        cursor.execute("SELECT COUNT(*) FROM adult_training")
        assert cursor.fetchone()[0] == 1
        
        # Delete adult (should cascade to training)
        cursor.execute("DELETE FROM adults WHERE id = ?", (adult_id,))
        
        # Verify cascade delete worked
        cursor.execute("SELECT COUNT(*) FROM adults")
        assert cursor.fetchone()[0] == 0, "Adult should be deleted"
        
        cursor.execute("SELECT COUNT(*) FROM adult_training")
        assert cursor.fetchone()[0] == 0, "Training should be cascade deleted"
        
        conn.close()


class TestFakeDataGeneration:
    """Test cases for generating fake test data."""
    
    def create_database_schema(self, db_path: str) -> bool:
        """Create database schema using the setup script."""
        project_root = Path(__file__).parent.parent
        setup_script = project_root / "db-scripts" / "setup_database.py"
        
        try:
            result = subprocess.run([
                sys.executable, str(setup_script),
                "--database", db_path,
                "--force"
            ], capture_output=True, text=True, cwd=str(project_root))
            
            return result.returncode == 0
        except Exception as e:
            print(f"Error running setup script: {e}")
            return False
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_with_data.db")
        self.create_database_schema(self.test_db_path)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def generate_fake_adult_data(self):
        """Generate fake adult roster data for testing."""
        fake_adults = [
            {
                'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@example.com',
                'bsa_number': 10001, 'unit_number': 'Troop 100', 'date_joined': '2018-05-15',
                'city': 'Springfield', 'state': 'IL', 'zip': '62701'
            },
            {
                'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@example.com',
                'bsa_number': 10002, 'unit_number': 'Troop 100', 'date_joined': '2019-03-20',
                'city': 'Springfield', 'state': 'IL', 'zip': '62702'
            },
            {
                'first_name': 'Mike', 'last_name': 'Wilson', 'email': 'mike.wilson@example.com',
                'bsa_number': 10003, 'unit_number': 'Troop 200', 'date_joined': '2020-09-10',
                'city': 'Decatur', 'state': 'IL', 'zip': '62521'
            }
        ]
        
        fake_training = [
            {'training_code': 'YPT', 'training_name': 'Youth Protection Training', 'expiration_date': '2025-05-15'},
            {'training_code': 'POS', 'training_name': 'Position Specific Training', 'expiration_date': '(does not expire)'},
            {'training_code': 'IOLS', 'training_name': 'Introduction to Outdoor Leader Skills', 'expiration_date': '2024-12-31'},
            {'training_code': 'WBLS', 'training_name': 'Wood Badge Leadership Skills', 'expiration_date': '(does not expire)'}
        ]
        
        fake_merit_badges = [
            'Camping', 'Hiking', 'First Aid', 'Cooking', 'Swimming', 'Canoeing',
            'Wilderness Survival', 'Emergency Preparedness', 'Search and Rescue',
            'Environmental Science', 'Forestry', 'Fish and Wildlife Management'
        ]
        
        fake_positions = [
            {'title': 'Scoutmaster', 'tenure': '(3y 2m 15d)'},
            {'title': 'Assistant Scoutmaster', 'tenure': '(1y 8m 22d)'},
            {'title': 'Committee Chair', 'tenure': '(2y 4m 10d)'},
            {'title': 'Merit Badge Counselor', 'tenure': '(4y 1m 5d)'}
        ]
        
        return fake_adults, fake_training, fake_merit_badges, fake_positions
    
    def test_insert_fake_data(self):
        """Test inserting comprehensive fake data into database."""
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        fake_adults, fake_training, fake_merit_badges, fake_positions = self.generate_fake_adult_data()
        
        # Insert fake adults
        adult_ids = []
        for adult in fake_adults:
            cursor.execute("""
                INSERT INTO adults (first_name, last_name, email, bsa_number, unit_number, 
                                  date_joined, city, state, zip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (adult['first_name'], adult['last_name'], adult['email'], 
                 adult['bsa_number'], adult['unit_number'], adult['date_joined'],
                 adult['city'], adult['state'], adult['zip']))
            adult_ids.append(cursor.lastrowid)
        
        # Insert training data for each adult
        for i, adult_id in enumerate(adult_ids):
            # Each adult gets 2-3 random training records
            import random
            training_count = random.randint(2, 3)
            selected_training = random.sample(fake_training, training_count)
            
            for training in selected_training:
                cursor.execute("""
                    INSERT INTO adult_training (adult_id, training_code, training_name, expiration_date)
                    VALUES (?, ?, ?, ?)
                """, (adult_id, training['training_code'], training['training_name'], 
                     training['expiration_date']))
        
        # Insert merit badge counselor data
        for i, adult_id in enumerate(adult_ids):
            # Each adult counsels 3-5 merit badges
            import random
            mb_count = random.randint(3, 5)
            selected_mbs = random.sample(fake_merit_badges, mb_count)
            
            for mb in selected_mbs:
                cursor.execute("""
                    INSERT INTO adult_merit_badges (adult_id, merit_badge_name)
                    VALUES (?, ?)
                """, (adult_id, mb))
        
        # Insert position data
        for i, adult_id in enumerate(adult_ids):
            position = fake_positions[i % len(fake_positions)]
            cursor.execute("""
                INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current)
                VALUES (?, ?, ?, ?)
            """, (adult_id, position['title'], position['tenure'], 1))
        
        conn.commit()
        
        # Verify data was inserted
        cursor.execute("SELECT COUNT(*) FROM adults")
        adults_count = cursor.fetchone()[0]
        assert adults_count == 3, f"Should have 3 adults, got {adults_count}"
        
        cursor.execute("SELECT COUNT(*) FROM adult_training")
        training_count = cursor.fetchone()[0]
        assert training_count >= 6, f"Should have at least 6 training records, got {training_count}"
        
        cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
        mb_count = cursor.fetchone()[0]
        assert mb_count >= 9, f"Should have at least 9 merit badge records, got {mb_count}"
        
        cursor.execute("SELECT COUNT(*) FROM adult_positions")
        pos_count = cursor.fetchone()[0]
        assert pos_count == 3, f"Should have 3 position records, got {pos_count}"
        
        conn.close()
    
    def test_validation_views_with_data(self):
        """Test that validation views work correctly with sample data."""
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Insert some test data first
        self.test_insert_fake_data()
        
        # Test adults_missing_data view
        cursor.execute("SELECT COUNT(*) FROM adults_missing_data")
        missing_count = cursor.fetchone()[0]
        # Should be 0 since our fake data is complete
        assert missing_count == 0, "Should have no missing data with complete fake data"
        
        # Test current_positions view
        cursor.execute("SELECT COUNT(*) FROM current_positions")
        positions_count = cursor.fetchone()[0]
        assert positions_count == 3, "Should show 3 current positions"
        
        # Test merit_badge_counselors view
        cursor.execute("SELECT merit_badge_name, counselor_count FROM merit_badge_counselors ORDER BY merit_badge_name")
        mb_counselors = cursor.fetchall()
        assert len(mb_counselors) > 0, "Should have merit badge counselor assignments"
        
        # Test training_expiration_summary view
        cursor.execute("SELECT COUNT(*) FROM training_expiration_summary")
        training_summary_count = cursor.fetchone()[0]
        assert training_summary_count > 0, "Should have training summary records"
        
        conn.close()