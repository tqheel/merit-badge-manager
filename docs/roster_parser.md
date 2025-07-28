# Roster Parser Documentation

## Overview

The Merit Badge Counselor Management Application requires robust data parsing capabilities to handle the Troop Roster CSV data source from Scoutbook. This document outlines the parsing requirements, challenges, and implementation approach for cleaning and structuring roster CSV data.

## Data Source

### Troop Roster File (CSV)

**Purpose:** Contains adult and youth member information in a structured format.

**File Structure:**
- Index column (must be removed during processing)
- "ADULT MEMBERS" section header
- Adult member data rows
- Empty separator rows
- "YOUTH MEMBERS" section header  
- Youth member data rows
- Different column structures for adults vs. youth

**Parsing Requirements:**
- Remove index columns (keeping only Member ID and BSA Number columns)
- Remove section headers ("ADULT MEMBERS", "YOUTH MEMBERS")
- Handle empty rows between sections
- Parse different column structures for adults and youth members
- Maintain data integrity during section separation

## Output Files

The parser generates two cleaned CSV files for database import:

### 1. adult_roster.csv
- Contains cleaned adult member data from the roster file
- Includes BSA Number, and other adult-specific fields such as Merit Badges offered
- Removes index columns and section headers

### 2. scout_roster.csv
- Contains cleaned youth member data from the roster file
- Includes BSA Number, and other scout-specific fields
- Removes index columns and section headers

## Technical Implementation

### Processing Steps

1. **File Validation**
   - Verify CSV format and structure
   - Check for required headers and sections
   - Handle encoding issues

2. **Data Cleaning**
   - Remove index columns (preserve BSA Number that will be the primary key when we create the database)
   - Remove section header rows
   - Filter out empty rows
   - Standardize data formats

3. **Section Parsing**
   - Identify adult vs. youth member sections
   - Apply appropriate column mapping for each section
   - Preserve Member IDs and BSA Numbers for database linking
   - Generate separate output files for each data type


## Dependencies

- Python CSV parsing libraries
- Data validation utilities

## Error Handling

- Graceful handling of malformed CSV files
- Detailed logging of parsing issues
- Recovery mechanisms for partial data corruption
- User-friendly error messages with suggested fixes
