#!/usr/bin/env python3
"""
Merit Badge Manager - Test Database Generator
Created: 2025-07-28
Updated: 2025-07-31
Purpose: Create a test database with fake adult and youth roster data to fulfill acceptance criteria

This script creates a test database with comprehensive fake data to demonstrate
the adult and youth roster schema functionality and meet the acceptance criteria.
"""

import sqlite3
import sys
import random
from pathlib import Path
from datetime import datetime, date, timedelta


def create_test_database_with_fake_data(db_path: str = "test_merit_badge_manager.db", include_youth: bool = True):
    """
    Create a test database with comprehensive fake adult and youth roster data.
    
    Args:
        db_path: Path to the test database file
        include_youth: Whether to include youth data generation
    """
    
    # First, create the schema using the existing setup script
    project_root = Path(__file__).parent.parent
    setup_script = project_root / "database" / "setup_database.py"
    
    print(f"Creating test database with fake data: {db_path}")
    
    # Run the database setup script
    import subprocess
    cmd = [
        sys.executable, str(setup_script),
        "--database", db_path,
        "--force"
    ]
    if not include_youth:
        cmd.append("--adults-only")
    
    result = subprocess.run(cmd, cwd=str(project_root))
    
    if result.returncode != 0:
        print("❌ Failed to create database schema")
        return False
    
    # Now populate with fake data
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    print("📝 Generating fake adult roster data...")
    
    # Generate fake adults data (same as before)
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
    
    # Generate fake youth data if requested
    if include_youth:
        print("\n👦 Generating fake youth roster data...")
        generate_youth_data(cursor)
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Test database created successfully!")
    print(f"📁 Database file: {Path(db_path).absolute()}")
    
    # Display summary statistics
    display_database_summary(db_path, include_youth)
    
    return True


def generate_youth_data(cursor):
    """Generate comprehensive youth roster fake data."""
    
    # Generate fake scouts data
    fake_scouts = [
        {
            'first_name': 'Alex', 'last_name': 'Thompson', 'bsa_number': 201001,
            'unit_number': 'Troop 100', 'rank': 'Life', 'date_joined': '2022-01-15',
            'date_of_birth': '2008-03-20', 'age': 16, 'patrol_name': 'Eagle Patrol',
            'activity_status': 'Active', 'oa_info': 'Ordeal Member',
            'email': 'alex.thompson@student.example.com', 'phone': '555-0101',
            'city': 'Springfield', 'state': 'IL', 'zip': '62701'
        },
        {
            'first_name': 'Emma', 'last_name': 'Garcia', 'bsa_number': 201002,
            'unit_number': 'Troop 100', 'rank': 'Star', 'date_joined': '2021-09-10',
            'date_of_birth': '2007-11-15', 'age': 16, 'patrol_name': 'Eagle Patrol',
            'activity_status': 'Active', 'oa_info': '',
            'email': 'emma.garcia@student.example.com', 'phone': '555-0102',
            'city': 'Springfield', 'state': 'IL', 'zip': '62702'
        },
        {
            'first_name': 'Noah', 'last_name': 'Williams', 'bsa_number': 201003,
            'unit_number': 'Troop 100', 'rank': 'First Class', 'date_joined': '2023-02-28',
            'date_of_birth': '2009-07-08', 'age': 15, 'patrol_name': 'Dragon Fruit Patrol',
            'activity_status': 'Active', 'oa_info': '',
            'email': 'noah.williams@student.example.com', 'phone': '555-0103',
            'city': 'Springfield', 'state': 'IL', 'zip': '62703'
        },
        {
            'first_name': 'Sophia', 'last_name': 'Brown', 'bsa_number': 201004,
            'unit_number': 'Troop 200', 'rank': 'Eagle', 'date_joined': '2020-04-12',
            'date_of_birth': '2006-12-03', 'age': 17, 'patrol_name': 'Falcon Patrol',
            'activity_status': 'Active', 'oa_info': 'Brotherhood Member',
            'email': 'sophia.brown@student.example.com', 'phone': '555-0104',
            'city': 'Decatur', 'state': 'IL', 'zip': '62521'
        },
        {
            'first_name': 'Liam', 'last_name': 'Davis', 'bsa_number': 201005,
            'unit_number': 'Troop 100', 'rank': 'Second Class', 'date_joined': '2023-08-05',
            'date_of_birth': '2010-01-22', 'age': 14, 'patrol_name': 'Dragon Fruit Patrol',
            'activity_status': 'Active', 'oa_info': '',
            'email': 'liam.davis@student.example.com', 'phone': '555-0105',
            'city': 'Springfield', 'state': 'IL', 'zip': '62704'
        },
        {
            'first_name': 'Olivia', 'last_name': 'Miller', 'bsa_number': 201006,
            'unit_number': 'Troop 200', 'rank': 'Tenderfoot', 'date_joined': '2024-01-10',
            'date_of_birth': '2011-05-14', 'age': 13, 'patrol_name': 'Wolf Patrol',
            'activity_status': 'Active', 'oa_info': '',
            'email': 'olivia.miller@student.example.com', 'phone': '555-0106',
            'city': 'Champaign', 'state': 'IL', 'zip': '61820'
        },
        {
            'first_name': 'Mason', 'last_name': 'Wilson', 'bsa_number': 201007,
            'unit_number': 'Troop 100', 'rank': 'Scout', 'date_joined': '2024-03-15',
            'date_of_birth': '2012-09-30', 'age': 11, 'patrol_name': 'New Scout Patrol',
            'activity_status': 'Active', 'oa_info': '',
            'email': 'mason.wilson@student.example.com', 'phone': '555-0107',
            'city': 'Springfield', 'state': 'IL', 'zip': '62705'
        },
        {
            'first_name': 'Isabella', 'last_name': 'Anderson', 'bsa_number': 201008,
            'unit_number': 'Troop 200', 'rank': 'Life', 'date_joined': '2021-06-20',
            'date_of_birth': '2007-04-18', 'age': 17, 'patrol_name': 'Falcon Patrol',
            'activity_status': 'Active', 'oa_info': 'Ordeal Member',
            'email': 'isabella.anderson@student.example.com', 'phone': '555-0108',
            'city': 'Decatur', 'state': 'IL', 'zip': '62522'
        }
    ]
    
    print("👥 Inserting scout members...")
    
    # Insert scouts
    scout_ids = []
    for scout in fake_scouts:
        cursor.execute("""
            INSERT INTO scouts (
                first_name, last_name, bsa_number, unit_number, rank, date_joined,
                date_of_birth, age, patrol_name, activity_status, oa_info,
                email, phone, city, state, zip
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scout['first_name'], scout['last_name'], scout['bsa_number'], 
            scout['unit_number'], scout['rank'], scout['date_joined'],
            scout['date_of_birth'], scout['age'], scout['patrol_name'],
            scout['activity_status'], scout['oa_info'], scout['email'],
            scout['phone'], scout['city'], scout['state'], scout['zip']
        ))
        scout_ids.append(cursor.lastrowid)
    
    print(f"✅ Inserted {len(scout_ids)} scout members")
    
    # Youth training options
    youth_training_options = [
        {'code': 'YPT_YOUTH', 'name': 'Youth Protection Training for Youth', 'expires': True, 'years': 1},
        {'code': 'TLT', 'name': 'Troop Leadership Training', 'expires': False},
        {'code': 'NYLT', 'name': 'National Youth Leadership Training', 'expires': False},
        {'code': 'OA_ORD', 'name': 'Order of the Arrow Ordeal', 'expires': False},
        {'code': 'OA_BRO', 'name': 'Order of the Arrow Brotherhood', 'expires': False},
        {'code': 'FIRST_AID', 'name': 'First Aid Training', 'expires': True, 'years': 2},
        {'code': 'CPR', 'name': 'CPR Certification', 'expires': True, 'years': 2},
        {'code': 'WILDERNESS_FA', 'name': 'Wilderness First Aid', 'expires': True, 'years': 3}
    ]
    
    print("🎓 Inserting youth training records...")
    
    # Insert youth training data
    training_count = 0
    for scout_id in scout_ids:
        # Each scout gets 1-3 random training records
        num_trainings = random.randint(1, 3)
        selected_trainings = random.sample(youth_training_options, num_trainings)
        
        for training in selected_trainings:
            if training['expires']:
                # Generate expiration date
                base_date = datetime.now()
                years_offset = random.randint(-1, training['years'])  # Some might be expired
                months_offset = random.randint(0, 11)
                exp_date = (base_date + timedelta(days=365*years_offset + 30*months_offset)).strftime('%Y-%m-%d')
            else:
                exp_date = '(does not expire)'
            
            cursor.execute("""
                INSERT OR IGNORE INTO scout_training (scout_id, training_code, training_name, expiration_date)
                VALUES (?, ?, ?, ?)
            """, (scout_id, training['code'], training['name'], exp_date))
            training_count += 1
    
    print(f"✅ Inserted {training_count} youth training records")
    
    # Youth position options
    youth_positions = [
        'Patrol Leader', 'Assistant Patrol Leader', 'Senior Patrol Leader',
        'Assistant Senior Patrol Leader', 'Troop Guide', 'Scribe',
        'Quartermaster', 'Historian', 'Librarian', 'Chaplain Aide',
        'Instructor', 'Den Chief', 'Bugler', 'Order of the Arrow Representative'
    ]
    
    print("👔 Inserting youth position assignments...")
    
    # Insert youth position data
    pos_count = 0
    for i, scout_id in enumerate(scout_ids):
        # Some scouts have leadership positions
        if random.random() < 0.6:  # 60% chance of having a position
            position = random.choice(youth_positions)
            patrol_name = fake_scouts[i]['patrol_name']
            
            # Generate tenure info
            months = random.randint(1, 24)
            days = random.randint(0, 29)
            tenure = f"({months}m {days}d)"
            
            cursor.execute("""
                INSERT INTO scout_positions (scout_id, position_title, patrol_name, tenure_info, is_current)
                VALUES (?, ?, ?, ?, ?)
            """, (scout_id, position, patrol_name, tenure, 1))
            pos_count += 1
    
    print(f"✅ Inserted {pos_count} youth position assignments")
    
    print("👨‍👩‍👧‍👦 Inserting parent/guardian contacts...")
    
    # Generate parent/guardian data
    parent_count = 0
    for i, scout_id in enumerate(scout_ids):
        scout = fake_scouts[i]
        
        # Generate 2-4 parent/guardian contacts per scout
        num_guardians = random.randint(2, 4)
        
        parent_names = [
            ('Michael', 'Thompson'), ('Jennifer', 'Thompson'),
            ('David', 'Garcia'), ('Maria', 'Garcia'),
            ('James', 'Williams'), ('Sarah', 'Williams'),
            ('Robert', 'Brown'), ('Lisa', 'Brown'),
            ('Christopher', 'Davis'), ('Amanda', 'Davis'),
            ('Matthew', 'Miller'), ('Jessica', 'Miller'),
            ('Daniel', 'Wilson'), ('Ashley', 'Wilson'),
            ('Anthony', 'Anderson'), ('Stephanie', 'Anderson')
        ]
        
        for guardian_num in range(1, num_guardians + 1):
            if guardian_num <= len(parent_names):
                first_name, last_name = parent_names[i * 2 + (guardian_num - 1) % 2]
            else:
                first_name, last_name = random.choice(parent_names)
            
            relationship = 'Parent' if guardian_num <= 2 else random.choice(['Guardian', 'Emergency Contact', 'Grandparent'])
            is_primary = 1 if guardian_num == 1 else 0
            
            cursor.execute("""
                INSERT INTO parent_guardians (
                    scout_id, guardian_number, first_name, last_name, relationship,
                    email, phone_cell, phone_home, city, state, zip, is_primary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scout_id, guardian_num, first_name, last_name, relationship,
                f"{first_name.lower()}.{last_name.lower()}@example.com",
                f"555-{random.randint(1000, 9999)}",
                f"217-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                scout['city'], scout['state'], scout['zip'], is_primary
            ))
            parent_count += 1
    
    print(f"✅ Inserted {parent_count} parent/guardian contacts")
    
    print("🏅 Inserting merit badge progress records...")
    
    # Merit badges for youth to work on
    merit_badges_youth = [
        'First Aid', 'Camping', 'Cooking', 'Hiking', 'Swimming', 'Canoeing',
        'Emergency Preparedness', 'Environmental Science', 'Citizenship in the Community',
        'Citizenship in the Nation', 'Citizenship in the World', 'Communication',
        'Personal Fitness', 'Personal Management', 'Family Life'
    ]
    
    # Insert merit badge progress data
    mb_progress_count = 0
    for scout_id in scout_ids:
        # Each scout is working on 2-5 merit badges
        num_mbs = random.randint(2, 5)
        selected_mbs = random.sample(merit_badges_youth, num_mbs)
        
        for mb in selected_mbs:
            status = random.choice(['Not Started', 'In Progress', 'Completed'])
            date_started = None
            date_completed = None
            
            if status != 'Not Started':
                start_date = datetime.now() - timedelta(days=random.randint(30, 365))
                date_started = start_date.strftime('%Y-%m-%d')
                
                if status == 'Completed':
                    complete_date = start_date + timedelta(days=random.randint(30, 180))
                    date_completed = complete_date.strftime('%Y-%m-%d')
            
            # Randomly assign counselors (reference to adult IDs 1-5)
            counselor_id = random.choice([1, 2, 3, 4, 5]) if random.random() < 0.7 else None
            
            cursor.execute("""
                INSERT OR IGNORE INTO scout_merit_badge_progress (
                    scout_id, merit_badge_name, counselor_adult_id, status, 
                    date_started, date_completed
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (scout_id, mb, counselor_id, status, date_started, date_completed))
            mb_progress_count += 1
    
    print(f"✅ Inserted {mb_progress_count} merit badge progress records")
    
    print("📈 Inserting advancement history records...")
    
    # Insert advancement history
    advancement_count = 0
    ranks = ['Scout', 'Tenderfoot', 'Second Class', 'First Class', 'Star', 'Life', 'Eagle']
    
    for i, scout_id in enumerate(scout_ids):
        scout = fake_scouts[i]
        current_rank = scout['rank']
        current_rank_index = ranks.index(current_rank) if current_rank in ranks else 0
        
        # Generate history for all ranks up to current rank
        join_date = datetime.strptime(scout['date_joined'], '%Y-%m-%d')
        
        for rank_index in range(current_rank_index + 1):
            rank = ranks[rank_index]
            # Each rank is earned progressively with some time between
            award_date = join_date + timedelta(days=rank_index * 120 + random.randint(0, 60))
            
            cursor.execute("""
                INSERT INTO scout_advancement_history (
                    scout_id, rank_name, date_awarded
                ) VALUES (?, ?, ?)
            """, (scout_id, rank, award_date.strftime('%Y-%m-%d')))
            advancement_count += 1
    
    print(f"✅ Inserted {advancement_count} advancement history records")

def display_database_summary(db_path: str, include_youth: bool = True):
    """Display summary statistics for the test database."""
    print("\n📊 Database Summary:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Adult statistics
    cursor.execute("SELECT COUNT(*) FROM adults")
    adults_count = cursor.fetchone()[0]
    print(f"   👥 Adults: {adults_count}")
    
    cursor.execute("SELECT COUNT(*) FROM adult_training")
    training_count = cursor.fetchone()[0]
    print(f"   🎓 Adult training records: {training_count}")
    
    cursor.execute("SELECT COUNT(*) FROM adult_merit_badges")
    mb_count = cursor.fetchone()[0]
    print(f"   🏅 Merit badge counselor assignments: {mb_count}")
    
    cursor.execute("SELECT COUNT(*) FROM adult_positions")
    pos_count = cursor.fetchone()[0]
    print(f"   👔 Adult position assignments: {pos_count}")
    
    # Youth statistics if included
    if include_youth:
        cursor.execute("SELECT COUNT(*) FROM scouts")
        scouts_count = cursor.fetchone()[0]
        print(f"   👦 Scouts: {scouts_count}")
        
        cursor.execute("SELECT COUNT(*) FROM scout_training")
        scout_training_count = cursor.fetchone()[0]
        print(f"   🎓 Scout training records: {scout_training_count}")
        
        cursor.execute("SELECT COUNT(*) FROM scout_positions")
        scout_pos_count = cursor.fetchone()[0]
        print(f"   👔 Scout position assignments: {scout_pos_count}")
        
        cursor.execute("SELECT COUNT(*) FROM parent_guardians")
        parent_count = cursor.fetchone()[0]
        print(f"   👨‍👩‍👧‍👦 Parent/guardian contacts: {parent_count}")
        
        cursor.execute("SELECT COUNT(*) FROM scout_merit_badge_progress")
        scout_mb_count = cursor.fetchone()[0]
        print(f"   🏅 Scout merit badge progress records: {scout_mb_count}")
        
        cursor.execute("SELECT COUNT(*) FROM scout_advancement_history")
        advancement_count = cursor.fetchone()[0]
        print(f"   📈 Scout advancement history records: {advancement_count}")
    
    # Show sample validation view data
    print("\n🔍 Sample validation views:")
    
    cursor.execute("SELECT COUNT(*) FROM current_positions")
    current_pos = cursor.fetchone()[0]
    print(f"   📋 Current adult positions: {current_pos}")
    
    cursor.execute("SELECT merit_badge_name, counselor_count FROM merit_badge_counselors ORDER BY counselor_count DESC LIMIT 3")
    top_mbs = cursor.fetchall()
    print("   🥇 Top merit badges by counselor count:")
    for mb, count in top_mbs:
        print(f"      - {mb}: {count} counselors")
    
    if include_youth:
        cursor.execute("SELECT COUNT(*) FROM active_scouts_with_positions")
        active_scouts = cursor.fetchone()[0]
        print(f"   👦 Active scouts with positions: {active_scouts}")
        
        cursor.execute("SELECT patrol_name, scout_count FROM patrol_assignments ORDER BY scout_count DESC LIMIT 3")
        top_patrols = cursor.fetchall()
        print("   🏕️ Top patrols by scout count:")
        for patrol, count in top_patrols:
            print(f"      - {patrol}: {count} scouts")
        
        cursor.execute("SELECT COUNT(*) FROM scouts_needing_counselors")
        needing_counselors = cursor.fetchone()[0]
        print(f"   🎯 Scouts needing counselor assignments: {needing_counselors}")
    
    conn.close()
    
    print("\n💡 Next steps:")
    print("1. Use this database to test roster functionality")
    print("2. Verify data integrity using validation views")
    print("3. Test merit badge counselor assignment features")
    if include_youth:
        print("4. Test youth advancement tracking and parent communication")
        print("5. Test patrol management and leadership position tracking")
    print(f"6. Database file can be found at: {Path(db_path).absolute()}")


def main():
    """Main function to handle command line arguments and run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create test database with fake adult and youth roster data"
    )
    parser.add_argument(
        "--database", "-d",
        default="test_merit_badge_manager.db",
        help="Test database file path (default: test_merit_badge_manager.db)"
    )
    parser.add_argument(
        "--adults-only", "-a",
        action="store_true",
        help="Generate only adult roster data (exclude youth data)"
    )
    
    args = parser.parse_args()
    
    include_youth = not args.adults_only
    success = create_test_database_with_fake_data(args.database, include_youth)
    
    if not success:
        print("❌ Failed to create test database")
        sys.exit(1)
    
    print("\n✅ Test database creation completed successfully!")


if __name__ == "__main__":
    main()