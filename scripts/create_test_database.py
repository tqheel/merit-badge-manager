#!/usr/bin/env python3
"""
Merit Badge Manager - Test Database Generator
Created: 2025-07-28
Purpose: Create a test database with fake adult roster data to fulfill acceptance criteria

This script creates a test database with comprehensive fake data to demonstrate
the adult roster schema functionality and meet the acceptance criteria.
"""

import sqlite3
import sys
import random
from pathlib import Path
from datetime import datetime, date, timedelta


def create_test_database_with_fake_data(db_path: str = "test_merit_badge_manager.db"):
    """
    Create a test database with comprehensive fake adult roster data.
    
    Args:
        db_path: Path to the test database file
    """
    
    # First, create the schema using the existing setup script
    project_root = Path(__file__).parent.parent
    setup_script = project_root / "db-scripts" / "setup_database.py"
    
    print(f"Creating test database with fake data: {db_path}")
    
    # Run the database setup script
    import subprocess
    result = subprocess.run([
        sys.executable, str(setup_script),
        "--database", db_path,
        "--force"
    ], cwd=str(project_root))
    
    if result.returncode != 0:
        print("❌ Failed to create database schema")
        return False
    
    # Now populate with fake data
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    print("📝 Generating fake adult roster data...")
    
    # Generate fake adults data
    fake_adults = [
        {
            'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@example.com',
            'bsa_number': 101001, 'unit_number': 'Troop 100', 'date_joined': '2018-05-15',
            'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'age_category': 'Adult',
            'oa_info': 'Order of the Arrow member', 'health_form_status': 'Current',
            'swim_class': 'Swimmer', 'swim_class_date': '2024-06-01'
        },
        {
            'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@example.com',
            'bsa_number': 101002, 'unit_number': 'Troop 100', 'date_joined': '2019-03-20',
            'city': 'Springfield', 'state': 'IL', 'zip': '62702', 'age_category': 'Adult',
            'oa_info': '', 'health_form_status': 'Current', 'swim_class': 'Beginner',
            'swim_class_date': '2024-05-15'
        },
        {
            'first_name': 'Mike', 'last_name': 'Wilson', 'email': 'mike.wilson@example.com',
            'bsa_number': 101003, 'unit_number': 'Troop 200', 'date_joined': '2020-09-10',
            'city': 'Decatur', 'state': 'IL', 'zip': '62521', 'age_category': 'Adult',
            'oa_info': 'Vigil Honor', 'health_form_status': 'Current',
            'swim_class': 'Swimmer', 'swim_class_date': '2024-07-01'
        },
        {
            'first_name': 'Lisa', 'last_name': 'Davis', 'email': 'lisa.davis@example.com',
            'bsa_number': 101004, 'unit_number': 'Troop 100', 'date_joined': '2017-11-05',
            'city': 'Springfield', 'state': 'IL', 'zip': '62703', 'age_category': 'Adult',
            'oa_info': 'Brotherhood', 'health_form_status': 'Expired',
            'swim_class': 'Non-swimmer', 'swim_class_date': '2023-06-15'
        },
        {
            'first_name': 'Tom', 'last_name': 'Anderson', 'email': 'tom.anderson@example.com',
            'bsa_number': 101005, 'unit_number': 'Troop 200', 'date_joined': '2021-01-12',
            'city': 'Champaign', 'state': 'IL', 'zip': '61820', 'age_category': 'Adult',
            'oa_info': '', 'health_form_status': 'Current', 'swim_class': 'Swimmer',
            'swim_class_date': '2024-04-20'
        }
    ]
    
    # Training data
    training_options = [
        {'code': 'YPT', 'name': 'Youth Protection Training', 'expires': True, 'years': 2},
        {'code': 'POS', 'name': 'Position Specific Training', 'expires': False},
        {'code': 'IOLS', 'name': 'Introduction to Outdoor Leader Skills', 'expires': False},
        {'code': 'WBLS', 'name': 'Wood Badge Leadership Skills', 'expires': False},
        {'code': 'HAZWX', 'name': 'Hazardous Weather Training', 'expires': True, 'years': 3},
        {'code': 'CLIMB', 'name': 'Climbing/Rappelling Training', 'expires': True, 'years': 3},
        {'code': 'SAFE', 'name': 'Safety Afloat Training', 'expires': True, 'years': 3}
    ]
    
    # Merit badge options
    merit_badges = [
        'Camping', 'Hiking', 'First Aid', 'Cooking', 'Swimming', 'Canoeing',
        'Wilderness Survival', 'Emergency Preparedness', 'Search and Rescue',
        'Environmental Science', 'Forestry', 'Fish and Wildlife Management',
        'Astronomy', 'Weather', 'Geology', 'Nature', 'Bird Study', 'Mammal Study',
        'Archery', 'Rifle Shooting', 'Shotgun Shooting', 'Electronics', 'Robotics',
        'Programming', 'Digital Technology', 'Aviation', 'Space Exploration'
    ]
    
    # Position options
    positions = [
        'Scoutmaster', 'Assistant Scoutmaster', 'Committee Chair', 'Committee Member',
        'Merit Badge Counselor', 'Chartered Organization Representative',
        'Advancement Chair', 'Training Chair', 'Activities Chair'
    ]
    
    print("👥 Inserting adult members...")
    
    # Insert adults
    adult_ids = []
    for adult in fake_adults:
        cursor.execute("""
            INSERT INTO adults (
                first_name, last_name, email, bsa_number, unit_number, date_joined,
                city, state, zip, age_category, oa_info, health_form_status,
                swim_class, swim_class_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            adult['first_name'], adult['last_name'], adult['email'], 
            adult['bsa_number'], adult['unit_number'], adult['date_joined'],
            adult['city'], adult['state'], adult['zip'], adult['age_category'],
            adult['oa_info'], adult['health_form_status'], adult['swim_class'],
            adult['swim_class_date']
        ))
        adult_ids.append(cursor.lastrowid)
    
    print(f"✅ Inserted {len(adult_ids)} adult members")
    
    print("🎓 Inserting training records...")
    
    # Insert training data for each adult
    training_count = 0
    for adult_id in adult_ids:
        # Each adult gets 2-4 random training records
        num_trainings = random.randint(2, 4)
        selected_trainings = random.sample(training_options, num_trainings)
        
        for training in selected_trainings:
            if training['expires']:
                # Generate expiration date
                base_date = datetime.now()
                years_offset = random.randint(0, training['years'])
                months_offset = random.randint(0, 11)
                exp_date = (base_date + timedelta(days=365*years_offset + 30*months_offset)).strftime('%Y-%m-%d')
            else:
                exp_date = '(does not expire)'
            
            cursor.execute("""
                INSERT OR IGNORE INTO adult_training (adult_id, training_code, training_name, expiration_date)
                VALUES (?, ?, ?, ?)
            """, (adult_id, training['code'], training['name'], exp_date))
            training_count += 1
    
    print(f"✅ Inserted {training_count} training records")
    
    print("🏅 Inserting merit badge counselor assignments...")
    
    # Insert merit badge counselor data
    mb_count = 0
    for adult_id in adult_ids:
        # Each adult counsels 3-8 merit badges
        num_mbs = random.randint(3, 8)
        selected_mbs = random.sample(merit_badges, num_mbs)
        
        for mb in selected_mbs:
            cursor.execute("""
                INSERT OR IGNORE INTO adult_merit_badges (adult_id, merit_badge_name)
                VALUES (?, ?)
            """, (adult_id, mb))
            mb_count += 1
    
    print(f"✅ Inserted {mb_count} merit badge counselor assignments")
    
    print("👔 Inserting position assignments...")
    
    # Insert position data
    pos_count = 0
    for i, adult_id in enumerate(adult_ids):
        # Each adult has 1-2 positions
        num_positions = random.randint(1, 2)
        
        for j in range(num_positions):
            position = positions[i % len(positions)]
            
            # Generate tenure info
            years = random.randint(0, 5)
            months = random.randint(0, 11)
            days = random.randint(0, 29)
            tenure = f"({years}y {months}m {days}d)"
            
            is_current = 1 if j == 0 else random.choice([0, 1])  # First position is usually current
            
            cursor.execute("""
                INSERT INTO adult_positions (adult_id, position_title, tenure_info, is_current)
                VALUES (?, ?, ?, ?)
            """, (adult_id, position, tenure, is_current))
            pos_count += 1
    
    print(f"✅ Inserted {pos_count} position assignments")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Test database created successfully!")
    print(f"📁 Database file: {Path(db_path).absolute()}")
    
    # Display summary statistics
    print("\n📊 Database Summary:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM adults")
    adults_count = cursor.fetchone()[0]
    print(f"   👥 Adults: {adults_count}")
    
    cursor.execute("SELECT COUNT(*) FROM adult_training")
    training_count = cursor.fetchone()[0]
    print(f"   🎓 Training records: {training_count}")
    
    cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
    mb_count = cursor.fetchone()[0]
    print(f"   🏅 Merit badge counselor assignments: {mb_count}")
    
    cursor.execute("SELECT COUNT(*) FROM adult_positions")
    pos_count = cursor.fetchone()[0]
    print(f"   👔 Position assignments: {pos_count}")
    
    # Show sample validation view data
    print("\n🔍 Sample validation views:")
    
    cursor.execute("SELECT COUNT(*) FROM current_positions")
    current_pos = cursor.fetchone()[0]
    print(f"   📋 Current positions: {current_pos}")
    
    cursor.execute("SELECT merit_badge_name, counselor_count FROM merit_badge_counselors ORDER BY counselor_count DESC LIMIT 3")
    top_mbs = cursor.fetchall()
    print("   🥇 Top merit badges by counselor count:")
    for mb, count in top_mbs:
        print(f"      - {mb}: {count} counselors")
    
    conn.close()
    
    print("\n💡 Next steps:")
    print("1. Use this database to test adult roster functionality")
    print("2. Verify data integrity using validation views")
    print("3. Test merit badge counselor assignment features")
    print(f"4. Database file can be found at: {Path(db_path).absolute()}")
    
    return True


def main():
    """Main function to handle command line arguments and run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create test database with fake adult roster data"
    )
    parser.add_argument(
        "--database", "-d",
        default="test_merit_badge_manager.db",
        help="Test database file path (default: test_merit_badge_manager.db)"
    )
    
    args = parser.parse_args()
    
    success = create_test_database_with_fake_data(args.database)
    
    if not success:
        print("❌ Failed to create test database")
        sys.exit(1)
    
    print("\n✅ Test database creation completed successfully!")


if __name__ == "__main__":
    main()