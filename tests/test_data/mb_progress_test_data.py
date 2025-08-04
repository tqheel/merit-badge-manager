"""
Test data for Merit Badge Progress import functionality.
"""

# Sample Merit Badge In-Progress Report CSV content
SAMPLE_MB_PROGRESS_CSV = '''Generated: 12/15/2024 14:30:45
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

# Sample Adult Roster CSV data (for testing MBC matching)
SAMPLE_ADULT_CSV = '''BSA Number,First Name,Last Name,Email,Merit Badge Counselor For
130001,"Michael","Johnson","mjohnson@example.com","Swimming (2024); Lifesaving; Water Sports"
130002,"Robert","Smith","rsmith@example.com","Fire Safety (2025); Emergency Preparedness; Safety"
130003,"Sarah","Wilson","swilson@example.com","First Aid (2025); Medicine; Health Care Professions"
130004,"William","Jones","wjones@example.com","Camping (2025); Backpacking; Hiking"
130005,"Susan","Brown","sbrown@example.com","Cooking (2024); Nutrition; Food Science"
'''

# Sample Youth Roster CSV data (for testing Scout matching)
SAMPLE_YOUTH_CSV = '''BSA Number,First Name,Last Name,Rank,Patrol Name
12345678,"John","Smith","Tenderfoot","Eagles"
87654321,"Jane","Doe","First Class","Hawks"
11111111,"Bob","Wilson","Star","Wolves"
22222222,"Alice","Brown","Life","Eagles"
99999999,"David","Miller","Scout","Hawks"
'''