# Merit Badge In-Progress Report - CSV Layout and Database Schema

## Overview

This document describes the layout of the "Merit Badge In-Progress Report" CSV file from Scoutbook and the proposed database schema for storing and managing merit badge progress data with counselor assignments. This report provides critical data needed to determine Merit Badge Counselor (MBC) assignments to Scouts for each merit badge they have chosen to work on.

**Report Generated**: Generic date format from Scoutbook  
**Source**: Scoutbook Merit Badge In-Progress Report  
**Processing**: Raw CSV requires header cleaning before import

## CSV File Structure

### Raw Export Format
The CSV file exported from Scoutbook contains metadata and header rows that must be cleaned before import:

```csv
Generated: MM/DD/YYYY HH:MM:SS
Merit Badge In-Progress Report
"Troop XXXX UNIT_TYPE",

"In-Progress Merit Badge",
"Member ID","Scout First","Scout Last","MBC","Rank","Location","Merit Badge","Date Completed","Requirements",
```

### Header Cleaning Requirements
Similar to adult and youth roster imports, the Merit Badge In-Progress Report requires preprocessing:

1. **Remove metadata rows**: Generation timestamp and report title
2. **Remove troop identification**: Troop name and unit type information  
3. **Remove section headers**: "In-Progress Merit Badge" delimiter
4. **Remove empty rows**: Blank lines between sections
5. **Preserve data headers**: Column names row for import validation
6. **Output cleaned file**: Save processed CSV to `output/` directory before database import

### Cleaned CSV Format
After preprocessing, the file should contain only the data header and records:

```csv
"Member ID","Scout First","Scout Last","MBC","Rank","Location","Merit Badge","Date Completed","Requirements",
"12345678","John","Smith","","Tenderfoot","City, ST 12345","Fire Safety (2025)","","5, 5g, 10, 10a, ",
"87654321","Jane","Doe","Mike Johnson","First Class","Town, ST 54321","Swimming (2024)","","3, 3c, 4, 4,, 5, 5b, 7, 7a, 7b, ",
```

### Data Columns

| Column | Field Name | Type | Description | Example Values |
|--------|------------|------|-------------|----------------|
| 1 | Member ID | TEXT | Scout's BSA membership number (unique identifier) | "12345678", "87654321" |
| 2 | Scout First | TEXT | Scout's first name | "John", "Jane" |
| 3 | Scout Last | TEXT | Scout's last name | "Smith", "Doe" |
| 4 | MBC | TEXT | Merit Badge Counselor name (often empty) | "Mike Johnson", "" |
| 5 | Rank | TEXT | Scout's current rank | "Tenderfoot", "First Class", "Life", "Eagle" |
| 6 | Location | TEXT | Scout's address/location | "City, ST 12345", "Town, ST 54321" |
| 7 | Merit Badge | TEXT | Merit badge name with year | "Fire Safety (2025)", "Swimming (2024)" |
| 8 | Date Completed | TEXT | Completion date (usually empty for in-progress) | "", "08/15/2024" |
| 9 | Requirements | TEXT | Completed requirements list | "5, 5g, 10, 10a, ", "No Requirements Complete, " |

### Data Characteristics

#### Scout Information
- **Member ID**: BSA membership number, used for cross-system matching with youth roster
- **Names**: Standard first/last name format, some include nicknames in parentheses
- **Rank**: Current Scout rank at time of report generation
- **Location**: City, state, and ZIP code where Scout resides

#### Merit Badge Counselor (MBC) Data
- **Optional Assignments**: Many merit badge entries have empty MBC field ("") - this is normal as Scouts often start merit badges before requesting counselor assignment
- **Name Format Variations**: When present, MBC names may include:
  - Full name: "Robert (Bob) Smith"
  - Nickname format: "Michael (Mike) Johnson"
  - Standard format: "Sarah Wilson"
- **No BSA Number**: MBC entries only contain names, no BSA membership numbers
- **Inconsistent Naming**: MBC names may not exactly match adult roster names

#### Merit Badge Information
- **Badge Names**: Include year in parentheses indicating merit badge requirements version
- **Progress Status**: All entries represent "in-progress" merit badges
- **Requirements Format**: Complex comma-separated list with various formats:
  - Simple requirements: "5, 5g, 10, 10a, "
  - Choice requirements: "(1 of 7a, 7b, 7c)"
  - Multiple choice: "(2 of 5a, 5b)"
  - No progress: "No Requirements Complete, "

## Data Quality Challenges

### MBC Assignment Issues

1. **Normal Unassigned State**: Approximately 60-70% of merit badge entries have no assigned counselor - this is expected as Scouts often begin working on merit badges before requesting counselor assignment
2. **Name Matching Problems**: When MBC names are present, they may not exactly match adult roster entries due to:
   - Nickname variations
   - Middle name inclusion/exclusion
   - Name format differences
   - Typos or data entry errors
3. **No BSA Numbers**: MBC entries lack BSA membership numbers for direct matching

### Requirements Format Complexity
- Variable requirement numbering systems
- Complex choice requirements with parenthetical notation
- Inconsistent spacing and punctuation
- Some requirements marked as duplicates (e.g., "4, 4,,")

## Proposed Database Schema

### Core Merit Badge Progress Table

```sql
CREATE TABLE merit_badge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_bsa_number TEXT NOT NULL,
    scout_first_name TEXT NOT NULL,
    scout_last_name TEXT NOT NULL,
    scout_rank TEXT,
    scout_location TEXT,
    merit_badge_name TEXT NOT NULL,
    merit_badge_year TEXT, -- Extracted from merit badge name
    mbc_name_raw TEXT, -- Raw MBC name from report
    mbc_adult_id INTEGER, -- Matched adult roster ID
    mbc_match_confidence REAL, -- Fuzzy match confidence score
    date_completed TEXT,
    requirements_raw TEXT, -- Raw requirements string
    requirements_parsed TEXT, -- JSON array of parsed requirements
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to scouts table when available
    scout_id INTEGER,
    
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE SET NULL,
    FOREIGN KEY (mbc_adult_id) REFERENCES adults(id) ON DELETE SET NULL,
    
    -- Unique constraint per scout per merit badge
    UNIQUE(scout_bsa_number, merit_badge_name)
);
```

### MBC Matching and Assignment Tables

#### Unmatched MBC Names Table
```sql
CREATE TABLE unmatched_mbc_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mbc_name_raw TEXT UNIQUE NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    potential_matches TEXT, -- JSON array of potential adult roster matches
    manual_match_adult_id INTEGER, -- Manually assigned match
    is_resolved BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (manual_match_adult_id) REFERENCES adults(id) ON DELETE SET NULL
);
```

#### MBC Name Mapping Table
```sql
CREATE TABLE mbc_name_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name TEXT NOT NULL,
    adult_id INTEGER NOT NULL,
    confidence_score REAL NOT NULL,
    mapping_type TEXT NOT NULL, -- 'exact', 'fuzzy', 'manual'
    created_by TEXT, -- 'system' or user identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE,
    UNIQUE(raw_name, adult_id)
);
```

### Merit Badge Requirements Tracking

#### Parsed Requirements Table
```sql
CREATE TABLE merit_badge_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    progress_id INTEGER NOT NULL,
    requirement_number TEXT NOT NULL,
    requirement_type TEXT, -- 'individual', 'choice', 'group'
    is_completed BOOLEAN DEFAULT 1,
    choice_group TEXT, -- For "(1 of 7a, 7b, 7c)" requirements
    notes TEXT,
    
    FOREIGN KEY (progress_id) REFERENCES merit_badge_progress(id) ON DELETE CASCADE,
    UNIQUE(progress_id, requirement_number)
);
```

### Performance Indexes

```sql
-- Primary lookup indexes
CREATE INDEX idx_mb_progress_scout_bsa ON merit_badge_progress(scout_bsa_number);
CREATE INDEX idx_mb_progress_scout_name ON merit_badge_progress(scout_last_name, scout_first_name);
CREATE INDEX idx_mb_progress_badge ON merit_badge_progress(merit_badge_name);
CREATE INDEX idx_mb_progress_mbc_raw ON merit_badge_progress(mbc_name_raw);
CREATE INDEX idx_mb_progress_mbc_id ON merit_badge_progress(mbc_adult_id);
CREATE INDEX idx_mb_progress_scout_id ON merit_badge_progress(scout_id);

-- MBC matching indexes
CREATE INDEX idx_unmatched_mbc_name ON unmatched_mbc_names(mbc_name_raw);
CREATE INDEX idx_unmatched_mbc_resolved ON unmatched_mbc_names(is_resolved);
CREATE INDEX idx_mbc_mappings_raw_name ON mbc_name_mappings(raw_name);
CREATE INDEX idx_mbc_mappings_adult_id ON mbc_name_mappings(adult_id);

-- Requirements indexes
CREATE INDEX idx_mb_requirements_progress_id ON merit_badge_requirements(progress_id);
CREATE INDEX idx_mb_requirements_number ON merit_badge_requirements(requirement_number);
```

## Data Integration Views

### Comprehensive Merit Badge Status View
```sql
CREATE VIEW merit_badge_status_view AS
SELECT 
    mbp.id,
    mbp.scout_bsa_number,
    mbp.scout_first_name,
    mbp.scout_last_name,
    mbp.scout_rank,
    mbp.merit_badge_name,
    mbp.merit_badge_year,
    mbp.mbc_name_raw,
    a.first_name || ' ' || a.last_name AS mbc_matched_name,
    a.email AS mbc_email,
    a.phone AS mbc_phone,
    mbp.mbc_match_confidence,
    CASE 
        WHEN mbp.mbc_adult_id IS NOT NULL THEN 'Matched'
        WHEN mbp.mbc_name_raw != '' THEN 'Unmatched'
        ELSE 'No Assignment'
    END AS assignment_status,
    mbp.requirements_raw,
    COUNT(mbr.id) AS requirements_completed_count,
    mbp.date_completed,
    s.first_name || ' ' || s.last_name AS scout_full_name,
    pg.email AS parent_email,
    pg.mobile_phone AS parent_phone
FROM merit_badge_progress mbp
LEFT JOIN adults a ON mbp.mbc_adult_id = a.id
LEFT JOIN scouts s ON mbp.scout_id = s.id
LEFT JOIN parent_guardians pg ON s.id = pg.scout_id AND pg.is_primary = 1
LEFT JOIN merit_badge_requirements mbr ON mbp.id = mbr.progress_id
GROUP BY mbp.id;
```

### Unmatched MBC Assignments View
```sql
CREATE VIEW unmatched_mbc_assignments AS
SELECT 
    mbp.mbc_name_raw,
    COUNT(*) AS assignment_count,
    GROUP_CONCAT(DISTINCT mbp.merit_badge_name) AS merit_badges,
    GROUP_CONCAT(DISTINCT mbp.scout_first_name || ' ' || mbp.scout_last_name) AS scouts,
    umn.potential_matches,
    umn.manual_match_adult_id,
    umn.is_resolved,
    umn.notes
FROM merit_badge_progress mbp
LEFT JOIN unmatched_mbc_names umn ON mbp.mbc_name_raw = umn.mbc_name_raw
WHERE mbp.mbc_name_raw != '' 
  AND mbp.mbc_adult_id IS NULL
GROUP BY mbp.mbc_name_raw
ORDER BY assignment_count DESC;
```

### Scouts Needing MBC Assignment View
```sql
CREATE VIEW scouts_available_for_mbc_assignment AS
SELECT 
    mbp.scout_bsa_number,
    mbp.scout_first_name,
    mbp.scout_last_name,
    mbp.scout_rank,
    mbp.merit_badge_name,
    mbp.merit_badge_year,
    s.patrol,
    pg.email AS parent_email,
    pg.mobile_phone AS parent_phone,
    -- Count of available counselors for this merit badge
    (SELECT COUNT(*) 
     FROM adult_merit_badges amb 
     JOIN adults a ON amb.adult_id = a.id 
     WHERE amb.merit_badge_name LIKE '%' || SUBSTR(mbp.merit_badge_name, 1, INSTR(mbp.merit_badge_name, ' (') - 1) || '%'
       AND a.health_form_status = 'Current') AS available_counselors,
    mbp.import_date,
    JULIANDAY('now') - JULIANDAY(mbp.import_date) AS days_since_started
FROM merit_badge_progress mbp
LEFT JOIN scouts s ON mbp.scout_id = s.id
LEFT JOIN parent_guardians pg ON s.id = pg.scout_id AND pg.is_primary = 1
WHERE mbp.mbc_name_raw = ''
  OR mbp.mbc_adult_id IS NULL
ORDER BY mbp.scout_last_name, mbp.scout_first_name, mbp.merit_badge_name;
```

## Fuzzy Matching Strategy

### MBC Name Matching Algorithm

The system will implement a multi-stage fuzzy matching process to link MBC names from the merit badge report to adult roster entries:

#### Stage 1: Exact Matching
- Direct name comparison (first + last)
- Handle common nickname patterns
- Account for middle name variations

#### Stage 2: Fuzzy String Matching
- Levenshtein distance calculation
- Soundex algorithm for phonetic matching
- Confidence scoring (0.0 to 1.0)

#### Stage 3: Manual Review Interface
- UI view for unmatched MBC names
- Side-by-side comparison with potential matches
- Manual assignment capability
- Bulk approval for high-confidence matches

### Implementation Example

```sql
-- Sample fuzzy matching logic (pseudocode)
WITH potential_matches AS (
    SELECT 
        umn.mbc_name_raw,
        a.id AS adult_id,
        a.first_name || ' ' || a.last_name AS adult_name,
        -- Fuzzy matching score calculation
        CASE 
            WHEN LOWER(umn.mbc_name_raw) = LOWER(a.first_name || ' ' || a.last_name) THEN 1.0
            WHEN SOUNDEX(umn.mbc_name_raw) = SOUNDEX(a.first_name || ' ' || a.last_name) THEN 0.8
            ELSE levenshtein_ratio(umn.mbc_name_raw, a.first_name || ' ' || a.last_name)
        END AS confidence_score
    FROM unmatched_mbc_names umn
    CROSS JOIN adults a
    WHERE umn.is_resolved = 0
)
SELECT *
FROM potential_matches
WHERE confidence_score >= 0.7
ORDER BY mbc_name_raw, confidence_score DESC;
```

## Data Import Process

### CSV Import Steps

1. **Clean CSV File**
   - Remove metadata header rows (generation timestamp, report title)
   - Remove troop identification information
   - Remove section headers and empty rows
   - Save cleaned file to `output/` directory
   - Validate column structure matches expected format

2. **Parse Cleaned CSV File**
   - Load cleaned CSV from `output/` directory
   - Validate data header row
   - Handle quoted fields and embedded commas

3. **Data Cleaning**
   - Normalize Scout names and BSA numbers
   - Extract merit badge year from badge name
   - Clean requirements text formatting

4. **Scout Matching**
   - Match Scout BSA numbers to youth roster
   - Flag unmatched Scout entries for review

5. **MBC Processing**
   - Identify unique MBC names
   - Attempt automatic matching with adult roster
   - Store unmatched names for manual review

6. **Requirements Parsing**
   - Parse complex requirement strings
   - Store both raw and parsed formats
   - Handle choice requirements and groupings

7. **Data Validation**
   - Check for duplicate entries
   - Validate data integrity
   - Generate import summary report

### Error Handling

- **Missing Scout Matches**: Flag for manual review
- **Invalid Requirements**: Store raw format, log parsing errors
- **Duplicate Entries**: Update existing records with newest data
- **Invalid MBC Names**: Add to unmatched table for manual review (when MBC name is present but cannot be matched)

## Reporting and Management

### Key Reports

1. **MBC Assignment Status Report**
   - Total merit badges by assignment status
   - MBC workload distribution
   - Merit badge completion tracking

2. **Unmatched MBC Report**
   - MBC names requiring manual matching (for entries with assigned counselors)
   - Potential matches with confidence scores
   - Assignment priority by Scout count

3. **Merit Badge Progress Summary**
   - Progress by merit badge type
   - Completion rates by Scout rank
   - Popular merit badges by enrollment

4. **Scout Merit Badge Tracking Report**
   - Scouts working on merit badges (with and without assigned counselors)
   - Merit badge start dates and progress
   - Counselor assignment opportunities

5. **Parent Communication Report**
   - Merit badge assignments with counselor contact information
   - Progress updates for family communication
   - Contact information for MBC coordination

### User Interface Requirements

1. **MBC Matching Interface**
   - Drag-and-drop name matching
   - Confidence score visualization
   - Bulk approval capabilities
   - Manual override options

2. **Assignment Management**
   - Scout-to-counselor assignment workflow for Scouts ready for counselor assignment
   - Merit badge availability checking
   - Parent notification integration
   - Progress tracking dashboard

3. **Data Quality Dashboard**
   - Import validation results
   - Matching statistics
   - Error resolution tracking
   - System health metrics

## Acceptance Criteria

### Database Schema Implementation
- [ ] Create `merit_badge_progress` table with all specified fields and constraints
- [ ] Create `unmatched_mbc_names` table for tracking unresolved counselor name matches
- [ ] Create `mbc_name_mappings` table for storing fuzzy match results and manual overrides
- [ ] Create `merit_badge_requirements` table for parsed requirements tracking
- [ ] Implement all specified database indexes for performance optimization
- [ ] Create foreign key relationships with proper CASCADE DELETE constraints
- [ ] Add unique constraints for scout/merit badge combinations

### CSV Import System
- [ ] Parse Merit Badge In-Progress Report CSV format with proper header handling
- [ ] Clean CSV file by removing metadata, troop identification, and section headers
- [ ] Save cleaned CSV to `output/` directory before database import
- [ ] Extract merit badge year from badge name (e.g., "Fire Safety (2025)" → "2025")
- [ ] Parse complex requirements strings including choice requirements
- [ ] Match Scout BSA numbers to existing youth roster entries
- [ ] Store both raw and parsed requirements data for validation
- [ ] Handle duplicate entries by updating existing records with newest data
- [ ] Generate detailed import summary reports with statistics

### MBC Name Matching System
- [ ] Implement exact name matching algorithm with nickname handling
- [ ] Implement fuzzy string matching using Levenshtein distance algorithm
- [ ] Implement Soundex algorithm for phonetic name matching
- [ ] Generate confidence scores (0.0 to 1.0) for all potential matches
- [ ] Store unmatched MBC names with occurrence counts for manual review
- [ ] Support manual override and bulk approval of high-confidence matches
- [ ] Track mapping types (exact, fuzzy, manual) for audit purposes

### Data Integration Views
- [ ] Create `merit_badge_status_view` showing comprehensive merit badge status
- [ ] Create `unmatched_mbc_assignments` view for manual resolution interface
- [ ] Create `scouts_available_for_mbc_assignment` view with time tracking
- [ ] Include parent contact information in all relevant assignment views
- [ ] Show available counselor counts per merit badge for assignment planning
- [ ] Support filtering by Scout rank, merit badge type, and assignment status

### Error Handling and Data Validation
- [ ] Flag unmatched Scout BSA numbers for manual review with detailed reports
- [ ] Store raw requirements format when parsing fails with error logging
- [ ] Validate CSV column structure and data types during import
- [ ] Generate validation reports for data quality assessment
- [ ] Handle edge cases in requirements parsing (duplicates, special formats)
- [ ] Provide clear error messages for import failures

### Reporting and Management Features
- [ ] Generate MBC Assignment Status Report with workload distribution
- [ ] Generate Unmatched MBC Report with potential matches and confidence scores
- [ ] Generate Merit Badge Progress Summary by type, rank, and completion status
- [ ] Generate Scout Merit Badge Tracking Report with assignment opportunities
- [ ] Generate Parent Communication Report with counselor contact information
- [ ] Export reports to Excel format for external use

### User Interface Requirements
- [ ] Create MBC name matching interface with drag-and-drop functionality
- [ ] Display confidence score visualization for fuzzy matches
- [ ] Implement bulk approval capabilities for high-confidence matches
- [ ] Provide manual override options with notes and audit tracking
- [ ] Create assignment management workflow for Scout-to-counselor matching
- [ ] Show merit badge availability and counselor qualification status

### Testing and Quality Assurance
- [ ] Create comprehensive test database with sample merit badge progress data
- [ ] Write unit tests for CSV parsing with various input formats
- [ ] Write unit tests for fuzzy matching algorithms with known test cases
- [ ] Test database views and reporting queries with realistic data volumes
- [ ] Performance test import process with large CSV files
- [ ] Validate data integrity after import operations

### Documentation and Training
- [ ] Document complete import process with step-by-step procedures
- [ ] Document error resolution procedures for common issues
- [ ] Create user guide for MBC name matching interface
- [ ] Document database schema with relationship diagrams
- [ ] Create troubleshooting guide for import and matching issues

This schema provides a robust foundation for managing merit badge progress data while gracefully handling the inherent challenges of MBC name matching and assignment coordination between Scoutbook reports and local roster management systems. The system recognizes that unassigned counselors are a normal part of the merit badge process, as Scouts often begin working on merit badges independently before requesting counselor assignment.
