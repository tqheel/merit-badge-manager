# Merit Badge In-Progress Import Documentation

## Overview

The Merit Badge In-Progress import functionality enables importing Merit Badge progress data from Scoutbook's "Merit Badge In-Progress Report" CSV export. This system handles the complex data parsing, MBC name matching, and requirement tracking needed to manage Scout merit badge assignments efficiently.

## Features

### CSV Parsing and Cleaning
- **Metadata Removal**: Automatically removes Scoutbook export headers, timestamps, and troop information
- **Year Extraction**: Extracts merit badge requirement years from badge names (e.g., "Fire Safety (2025)" → "2025")
- **Requirements Parsing**: Handles complex requirement strings including choice requirements like "(1 of 4a, 4b, 4c)"
- **Data Validation**: Validates CSV structure and required fields before import

### MBC Name Fuzzy Matching
- **Exact Matching**: 100% confidence for identical names
- **Nickname Matching**: 95% confidence for known patterns (Mike → Michael, Bob → Robert, etc.)
- **Fuzzy String Matching**: Variable confidence based on string similarity using Levenshtein distance
- **Soundex Phonetic Matching**: 80% confidence for names that sound similar
- **Automatic Storage**: Unmatched names stored for manual review with potential matches

### Database Integration
- **Scout Matching**: Links merit badge progress to youth roster by BSA number
- **Comprehensive Views**: 6 new database views for reporting and management
- **Requirements Tracking**: Individual requirements stored with choice group handling
- **Data Quality**: Built-in validation and missing data identification

## Database Schema

### Core Tables

#### `merit_badge_progress`
Primary table for tracking Scout merit badge work:
- **scout_bsa_number**: Scout's BSA membership number
- **scout_first_name**, **scout_last_name**: Scout identification
- **merit_badge_name**: Full merit badge name with year
- **merit_badge_year**: Extracted requirement year
- **mbc_name_raw**: Original MBC name from report
- **mbc_adult_id**: Matched adult roster ID
- **mbc_match_confidence**: Fuzzy match confidence (0.0-1.0)
- **requirements_raw**: Original requirements string
- **requirements_parsed**: JSON array of parsed requirements

#### `unmatched_mbc_names`
Tracks counselor names needing manual resolution:
- **mbc_name_raw**: Original name from report
- **occurrence_count**: Number of times this name appears
- **potential_matches**: JSON array of possible matches
- **is_resolved**: Manual resolution status

#### `mbc_name_mappings`
Stores successful name matches:
- **raw_name**: Original MBC name
- **adult_id**: Matched adult roster ID
- **confidence_score**: Match confidence
- **mapping_type**: Match method (exact, fuzzy, manual)

#### `merit_badge_requirements`
Individual requirement tracking:
- **progress_id**: Reference to merit badge progress
- **requirement_number**: Requirement identifier
- **requirement_type**: individual, choice, or group
- **choice_group**: Choice requirement details

### Database Views

#### `merit_badge_status_view`
Comprehensive status overview:
```sql
SELECT scout_first_name, scout_last_name, merit_badge_name, 
       assignment_status, requirements_completed_count
FROM merit_badge_status_view;
```

#### `scouts_available_for_mbc_assignment`
Scouts needing counselor assignments:
```sql
SELECT scout_first_name, scout_last_name, merit_badge_name, days_since_started
FROM scouts_available_for_mbc_assignment
ORDER BY days_since_started DESC;
```

#### `unmatched_mbc_assignments`
MBC names requiring manual review:
```sql
SELECT mbc_name_raw, assignment_count, merit_badges
FROM unmatched_mbc_assignments
ORDER BY assignment_count DESC;
```

## Usage Instructions

### Command Line Tools

#### 1. Parse CSV File Only
```bash
python database-access/mb_progress_parser.py data/merit_badge_report.csv --verbose
```

#### 2. Test MBC Name Matching
```bash
python database-access/mbc_name_matcher.py --database merit_badge_manager.db "Mike Johnson"
```

#### 3. Full Import Process
```bash
python database-access/import_mb_progress.py data/merit_badge_report.csv --auto-match-threshold 0.9
```

### Python API Usage

#### Basic Import
```python
from database_access.import_mb_progress import MeritBadgeProgressImporter

importer = MeritBadgeProgressImporter("merit_badge_manager.db")
success = importer.import_csv("merit_badge_report.csv")

if success:
    stats = importer.get_import_summary()
    print(f"Imported {stats['imported_records']} records")
    print(f"MBC exact matches: {stats['mbc_exact_matches']}")
    print(f"MBC fuzzy matches: {stats['mbc_fuzzy_matches']}")
```

#### Custom MBC Matching
```python
from database_access.mbc_name_matcher import MBCNameMatcher

matcher = MBCNameMatcher("merit_badge_manager.db")
matches = matcher.find_matches("Mike Johnson", min_confidence=0.7)

for match in matches:
    print(f"{match['name']} (confidence: {match['confidence']:.2f})")
```

#### Requirements Parsing
```python
from database_access.mb_progress_parser import MeritBadgeProgressParser

parser = MeritBadgeProgressParser("input.csv", "output_dir")
output_file = parser.parse_csv()

summary = parser.get_parsing_summary()
print(f"Processed {summary['data_rows_processed']} rows")
```

## Data Quality and Validation

### Import Statistics
The system provides comprehensive statistics for each import:
- **Total Records**: Number of Scout progress entries processed
- **MBC Matching**: Breakdown of exact, fuzzy, and unmatched counselor names
- **Scout Matching**: Success rate for BSA number matches to youth roster
- **Requirements Parsing**: Number of successfully parsed requirement strings
- **Error Tracking**: Detailed error messages for failed operations

### Data Validation Views
Query validation views to assess data quality:

```sql
-- Missing data identification
SELECT * FROM mb_progress_missing_data;

-- Merit badge summary statistics
SELECT * FROM mb_progress_summary;

-- Requirements completion analysis
SELECT * FROM mb_requirements_summary;
```

### Error Handling
The system gracefully handles common issues:
- **Invalid CSV Format**: Clear error messages for malformed files
- **Missing Required Fields**: Skips records with validation failures
- **Database Errors**: Rollback capability with error reporting
- **Duplicate Entries**: Uses UPSERT operations to update existing records

## Configuration Options

### Auto-Match Threshold
Controls automatic MBC name matching confidence level:
- **0.9 (default)**: High confidence required for automatic matching
- **0.8**: Medium confidence, more automatic matches
- **1.0**: Only exact matches processed automatically

### CSV Processing Options
- **Header Validation**: Ensures required columns are present
- **Encoding Support**: UTF-8 encoding with error replacement
- **Empty Field Handling**: Graceful handling of missing data

### Database Configuration
- **Transaction Management**: Atomic imports with rollback capability
- **Index Optimization**: 51 indexes for optimal query performance
- **View Refreshing**: Automatic view updates after import

## Troubleshooting

### Common Issues

#### 1. CSV Format Problems
**Symptom**: "Could not find valid header row" error
**Solution**: Verify CSV file contains proper Scoutbook export format with expected headers

#### 2. Database Lock Errors
**Symptom**: "database is locked" error during import
**Solution**: Ensure no other applications are accessing the database file

#### 3. Low MBC Match Rates
**Symptom**: Many unmatched MBC names
**Solution**: Review nickname mappings and consider lowering auto-match threshold

#### 4. Missing Scout Matches
**Symptom**: Scouts not linked to youth roster
**Solution**: Verify BSA numbers match between Merit Badge report and youth roster

### Performance Considerations

#### Large File Processing
For CSV files with >1000 records:
- Increase database timeout settings
- Consider processing in batches
- Monitor memory usage during requirements parsing

#### Fuzzy Matching Optimization
- Higher confidence thresholds reduce processing time
- Pre-populate MBC name mappings for common counselors
- Use manual matching for frequently occurring unmatched names

## Integration Examples

### Weekly Import Workflow
```bash
#!/bin/bash
# Weekly Merit Badge Progress Import

# 1. Backup existing database
cp merit_badge_manager.db merit_badge_manager_backup.db

# 2. Import new progress data
python database-access/import_mb_progress.py data/weekly_mb_report.csv

# 3. Generate management reports
sqlite3 merit_badge_manager.db < scripts/generate_weekly_reports.sql

# 4. Email reports to leadership
python scripts/email_reports.py
```

### MBC Assignment Review Process
```sql
-- 1. Review unmatched MBC names
SELECT mbc_name_raw, assignment_count 
FROM unmatched_mbc_assignments 
ORDER BY assignment_count DESC;

-- 2. Find available counselors for assignments
SELECT mb.merit_badge_name, 
       COUNT(DISTINCT sa.scout_bsa_number) as scouts_waiting,
       COUNT(DISTINCT amb.adult_id) as available_counselors
FROM scouts_available_for_mbc_assignment sa
JOIN merit_badge_progress mb ON sa.merit_badge_name = mb.merit_badge_name  
LEFT JOIN adult_merit_badges amb ON mb.merit_badge_name LIKE '%' || amb.merit_badge_name || '%'
GROUP BY mb.merit_badge_name;

-- 3. Generate assignment recommendations
SELECT sa.scout_first_name, sa.scout_last_name, sa.merit_badge_name,
       a.first_name || ' ' || a.last_name as recommended_counselor,
       a.email as counselor_email
FROM scouts_available_for_mbc_assignment sa
JOIN adult_merit_badges amb ON sa.merit_badge_name LIKE '%' || amb.merit_badge_name || '%'
JOIN adults a ON amb.adult_id = a.id
WHERE a.health_form_status = 'Current'
ORDER BY sa.days_since_started DESC;
```

This comprehensive system provides all the tools needed to efficiently manage Merit Badge progress tracking and counselor assignments while maintaining data quality and providing actionable insights for Troop leadership.