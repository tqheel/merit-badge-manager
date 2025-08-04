"""
Test data for Merit Badge Progress import functionality.
This represents the initial import scenario where no merit badge progress data exists in the database.
Adult and youth rosters are assumed to already be imported.
"""

# Sample raw CSV export from Scoutbook (before cleaning)
SAMPLE_MB_PROGRESS_CSV_RAW = '''Generated: 12/15/2024 14:30:45
Merit Badge In-Progress Report
"Troop 123 BOY SCOUTS",

"In-Progress Merit Badge",
"Member ID","Scout First","Scout Last","MBC","Rank","Location","Merit Badge","Date Completed","Requirements",
"12345678","John","Smith","","Tenderfoot","City, ST 12345","Fire Safety (2025)","","5, 5g, 10, 10a, ",
"87654321","Jane","Doe","Mike Johnson","First Class","Town, ST 54321","Swimming (2024)","","3, 3c, 4, 4a, 5, 5b, 7, 7a, 7b, ",
"11111111","Bob","Wilson","Robert (Bob) Smith","Star","Village, ST 98765","Camping (2025)","","1, 2, 2a, 3, (1 of 4a, 4b, 4c), ",
"22222222","Alice","Brown","","Life","Hometown, ST 13579","Cooking (2024)","","No Requirements Complete, ",
"33333333","Charlie","Davis","Sarah Wilson","Scout","Cityville, ST 24680","First Aid (2025)","08/15/2024","1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ",
'''

# Sample cleaned CSV (after header removal, ready for import)
SAMPLE_MB_PROGRESS_CSV_CLEANED = '''"Member ID","Scout First","Scout Last","MBC","Rank","Location","Merit Badge","Date Completed","Requirements",
"12345678","John","Smith","","Tenderfoot","City, ST 12345","Fire Safety (2025)","","5, 5g, 10, 10a, ",
"87654321","Jane","Doe","Mike Johnson","First Class","Town, ST 54321","Swimming (2024)","","3, 3c, 4, 4a, 5, 5b, 7, 7a, 7b, ",
"11111111","Bob","Wilson","Robert (Bob) Smith","Star","Village, ST 98765","Camping (2025)","","1, 2, 2a, 3, (1 of 4a, 4b, 4c), ",
"22222222","Alice","Brown","","Life","Hometown, ST 13579","Cooking (2024)","","No Requirements Complete, ",
"33333333","Charlie","Davis","Sarah Wilson","Scout","Cityville, ST 24680","First Aid (2025)","08/15/2024","1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ",
'''

# Sample Adult Roster CSV data (for testing MBC matching)
SAMPLE_ADULT_CSV = '''BSA Number,First Name,Last Name,Email,Merit Badge Counselor For
130001,"Michael","Johnson","mjohnson@example.com","Swimming (2024); Lifesaving; Water Sports"
130002,"Robert","Smith","rsmith@example.com","Fire Safety (2025); Emergency Preparedness; Safety"
130003,"Sarah","Wilson","swilson@example.com","First Aid (2025); Medicine; Health Care Professions"
130004,"William","Jones","wjones@example.com","Camping (2025); Backpacking; Hiking"
130005,"Susan","Brown","sbrown@example.com","Cooking (2024); Nutrition; Food Science"
'''

# Sample Youth Roster CSV data (assumes youth are already imported)
SAMPLE_YOUTH_CSV = '''BSA Number,First Name,Last Name,Rank,Patrol Name
12345678,"John","Smith","Tenderfoot","Eagles"
87654321,"Jane","Doe","First Class","Hawks"
11111111,"Bob","Wilson","Star","Wolves"
22222222,"Alice","Brown","Life","Eagles"
33333333,"Charlie","Davis","Scout","Hawks"
99999999,"David","Miller","Second Class","Eagles"
'''

# Expected outcomes after initial import (for test validation)
EXPECTED_IMPORT_RESULTS = {
    'total_records': 5,
    'scouts_with_mbc': 3,  # Jane, Bob, Charlie have assigned MBCs
    'scouts_without_mbc': 2,  # John, Alice have no MBC assigned (normal state)
    'unique_scouts': 5,
    'unique_merit_badges': 5,
    'completed_badges': 1,  # Charlie's First Aid is completed
    'in_progress_badges': 4,
    'unmatched_mbcs': 0,  # Assuming all MBC names match adult roster
    'fuzzy_matches': 1,  # "Robert (Bob) Smith" needs fuzzy matching to "Robert Smith"
}

# Test scenarios for MBC matching
MBC_MATCHING_SCENARIOS = [
    {
        'raw_name': 'Mike Johnson',
        'expected_match': 'Michael Johnson',
        'confidence': 0.8,
        'match_type': 'fuzzy'
    },
    {
        'raw_name': 'Robert (Bob) Smith', 
        'expected_match': 'Robert Smith',
        'confidence': 0.9,
        'match_type': 'nickname_handling'
    },
    {
        'raw_name': 'Sarah Wilson',
        'expected_match': 'Sarah Wilson',
        'confidence': 1.0,
        'match_type': 'exact'
    },
    {
        'raw_name': '',
        'expected_match': None,
        'confidence': 0.0,
        'match_type': 'no_assignment'
    }
]

# Requirements parsing test cases
REQUIREMENTS_PARSING_TESTS = [
    {
        'raw': '5, 5g, 10, 10a, ',
        'parsed': ['5', '5g', '10', '10a'],
        'choice_requirements': []
    },
    {
        'raw': '1, 2, 2a, 3, (1 of 4a, 4b, 4c), ',
        'parsed': ['1', '2', '2a', '3'],
        'choice_requirements': [{'count': 1, 'options': ['4a', '4b', '4c']}]
    },
    {
        'raw': 'No Requirements Complete, ',
        'parsed': [],
        'choice_requirements': []
    },
    {
        'raw': '1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ',
        'parsed': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        'choice_requirements': []
    }
]

# Database state validation - what should exist after fresh import
EXPECTED_DB_STATE = {
    'merit_badge_progress_count': 5,
    'unmatched_mbc_names_count': 0,  # Assuming all match
    'mbc_name_mappings_count': 2,  # Mike->Michael, Robert (Bob)->Robert
    'merit_badge_requirements_count': 17,  # Total parsed requirements across all entries
    'scouts_matched': 5,  # All scouts should match existing youth roster
    'adults_matched': 3,  # 3 MBCs should match existing adult roster
}

# Initial database state (empty merit badge progress tables)
INITIAL_DB_STATE = {
    'merit_badge_progress_count': 0,
    'unmatched_mbc_names_count': 0,
    'mbc_name_mappings_count': 0,
    'merit_badge_requirements_count': 0,
}

# Backward compatibility for existing tests
SAMPLE_MB_PROGRESS_CSV = SAMPLE_MB_PROGRESS_CSV_RAW