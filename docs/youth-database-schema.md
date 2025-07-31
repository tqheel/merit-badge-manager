# Database Schema for Youth Roster Data

## Overview

This document specifies the SQLite database schema for storing Youth (Scout) roster data imported from CSV files. The schema is designed to normalize the complex youth roster data structure into efficient, queryable tables that support merit badge counselor management and Scout tracking.

## CSV File Analysis

The youth roster CSV contains the following header columns:

### Core Scout Information
- First Name, Last Name, Rank, BSA Number, Date of Birth, Age, Date Joined
- OA Info, Health Form A/B - Health Form C, Swim Class, Swim Class Date
- Positions (Tenure), Unit, Patrol, Training, Expiration Date

### Parent/Guardian Information (Up to 4 contacts)
- Parent/Guardian Name 1-4, Address1-4, City1-4, State1-4, Zip1-4
- Home Phone1-4, Work Phone1-4, Mobile Phone1-4, Email1-4

## Data Type Analysis

Based on sample data values:

### Scout Data
- **Text fields**: Names, ranks, OA status, health forms, swim class, positions, patrol names
- **Numeric fields**: BSA Number (unique identifier), Age
- **Date fields**: Date of Birth, Date Joined, Swim Class Date
- **Structured text fields**: Training (pipe-separated list), Positions (complex tenure info)
- **Rank values**: "Eagle", "Life", "Star", "First Class", "Second Class", "Tenderfoot", "Scout", "NO RANK"
- **OA Status**: "OA - Active", "OA - Inactive", or empty
- **Swim Classification**: "Swimmer", "Beginner", "Nonswimmer", or empty

### Parent/Guardian Data
- **Text fields**: Names, addresses, cities, states, email addresses
- **Numeric fields**: ZIP codes, phone numbers
- **Contact types**: Home, Work, Mobile phones for each guardian

## SQLite Schema

### Scouts Table

```sql
CREATE TABLE scouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    rank TEXT,
    bsa_number INTEGER UNIQUE NOT NULL,
    date_of_birth DATE,
    age INTEGER,
    date_joined DATE,
    oa_info TEXT,
    health_form_status TEXT,
    swim_class TEXT,
    swim_class_date DATE,
    unit TEXT,
    patrol TEXT,
    positions_tenure TEXT, -- Raw positions data for reference
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Scout Training Table

```sql
CREATE TABLE scout_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    training_code TEXT NOT NULL,
    training_name TEXT NOT NULL,
    expiration_date TEXT, -- Some training "does not expire"
    completion_date DATE,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE,
    UNIQUE(scout_id, training_code)
);
```

### Scout Positions Table

```sql
CREATE TABLE scout_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    position_title TEXT NOT NULL,
    patrol_name TEXT,
    tenure_info TEXT, -- e.g., "(5m 1d)", "(1y 4m 29d)"
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT 1,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE
);
```

### Parent Guardians Table

```sql
CREATE TABLE parent_guardians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    guardian_number INTEGER NOT NULL, -- 1, 2, 3, or 4
    name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    home_phone TEXT,
    work_phone TEXT,
    mobile_phone TEXT,
    email TEXT,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE,
    UNIQUE(scout_id, guardian_number)
);
```

### Scout Merit Badge Progress Table (Future Use)

```sql
CREATE TABLE scout_merit_badge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    merit_badge_name TEXT NOT NULL,
    counselor_name TEXT,
    counselor_id INTEGER, -- Foreign key when MBC data is available
    status TEXT DEFAULT 'In Progress', -- 'In Progress', 'Completed', 'Dropped'
    start_date DATE,
    completion_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE
);
```

### Scout Advancement History Table

```sql
CREATE TABLE scout_advancement_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    rank TEXT NOT NULL,
    advancement_date DATE,
    board_of_review_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE
);
```

## Indexes for Performance

```sql
-- Primary lookup indexes
CREATE INDEX idx_scouts_bsa_number ON scouts(bsa_number);
CREATE INDEX idx_scouts_name ON scouts(last_name, first_name);
CREATE INDEX idx_scouts_rank ON scouts(rank);
CREATE INDEX idx_scouts_patrol ON scouts(patrol);
CREATE INDEX idx_scouts_unit ON scouts(unit);
CREATE INDEX idx_scouts_active ON scouts(is_active);

-- Training lookup indexes
CREATE INDEX idx_scout_training_scout_id ON scout_training(scout_id);
CREATE INDEX idx_scout_training_code ON scout_training(training_code);

-- Position indexes
CREATE INDEX idx_scout_positions_scout_id ON scout_positions(scout_id);
CREATE INDEX idx_scout_positions_current ON scout_positions(is_current);
CREATE INDEX idx_scout_positions_patrol ON scout_positions(patrol_name);

-- Parent/Guardian indexes
CREATE INDEX idx_parent_guardians_scout_id ON parent_guardians(scout_id);
CREATE INDEX idx_parent_guardians_email ON parent_guardians(email);
CREATE INDEX idx_parent_guardians_primary ON parent_guardians(is_primary);

-- Merit badge progress indexes
CREATE INDEX idx_scout_mb_progress_scout_id ON scout_merit_badge_progress(scout_id);
CREATE INDEX idx_scout_mb_progress_badge ON scout_merit_badge_progress(merit_badge_name);
CREATE INDEX idx_scout_mb_progress_counselor ON scout_merit_badge_progress(counselor_name);
CREATE INDEX idx_scout_mb_progress_status ON scout_merit_badge_progress(status);

-- Advancement history indexes
CREATE INDEX idx_scout_advancement_scout_id ON scout_advancement_history(scout_id);
CREATE INDEX idx_scout_advancement_rank ON scout_advancement_history(rank);
CREATE INDEX idx_scout_advancement_date ON scout_advancement_history(advancement_date);
```

## Data Import Considerations

### Scout Training Data Processing
- Training field contains pipe-separated training courses with complex formatting
- Each training item includes course code, name, and expiration date
- Example: "S97 ILST-Intro Leadership Skills-Troops (does not expire) | SCO_3008 Overview and Policies (does not expire)"
- Need to parse training items and extract course codes, names, and expiration status
- Youth training is typically position-specific or advancement-related

### Position Data Processing
- Positions field contains complex tenure information with patrol assignments
- Example: "Patrol Leader [ Dragon Fruit] Patrol (5m 1d) | Scouts BSA [ Dragon Fruit] Patrol (2y 5m 6d) | Scribe (11m 3d)"
- Format: position title, optional patrol name in brackets, tenure duration in parentheses
- Multiple positions may be held simultaneously (current and historical)
- Common positions: Patrol Leader, Assistant Patrol Leader, Senior Patrol Leader, Scribe, Historian, Librarian, etc.

### Parent/Guardian Data Processing
- Up to 4 parent/guardian contacts per Scout
- Each contact has complete address and multiple phone number fields
- Some fields may be empty or incomplete
- First guardian is typically considered primary contact
- Phone numbers may have various formats: (919) 123-4567, 919-123-4567, etc.
- Email addresses should be validated and cleaned

### Rank Progression Tracking
- Current rank is stored in main scouts table
- Advancement history table can track rank progression over time
- Rank hierarchy: Scout → Tenderfoot → Second Class → First Class → Star → Life → Eagle
- "NO RANK" indicates new Scouts who haven't completed Scout rank requirements

### Age and Activity Status
- Age is calculated field based on date of birth
- Scouts aged out (18+) may be marked as inactive
- "2025 Inactive and Aged Out" patrol indicates aged-out Scouts
- Active status should be determined by age, patrol assignment, and activity

### Data Quality Notes
- Some patrol names are generic: "Anonymous Message", "2025 Inactive and Aged Out"
- BSA Numbers are unique identifiers for matching between systems
- Empty fields should be handled as NULL values
- Some addresses may be incomplete or have formatting issues
- Phone numbers may be missing area codes or have invalid formats
- OA (Order of the Arrow) status tracks honor society membership

## Normalized Data Benefits

1. **Scout Management**: Centralized Scout information with proper data types and constraints
2. **Parent Communication**: Structured contact information for multiple guardians per Scout
3. **Position Tracking**: Historical record of leadership positions and patrol assignments
4. **Training Management**: Separate table for tracking Scout training completions and requirements
5. **Merit Badge Integration**: Ready for integration with merit badge counselor assignment system
6. **Advancement Tracking**: Support for tracking rank progression over time
7. **Data Integrity**: Foreign key constraints ensure referential integrity
8. **Query Performance**: Indexes optimize common lookup patterns for reports and assignments

## Integration with Merit Badge System

This youth schema is designed to integrate seamlessly with the adult roster and merit badge counselor management system:

- Scout-to-counselor assignments through merit badge progress table
- Fuzzy name matching between Scout data and merit badge in-progress reports
- Parent contact information for communication about merit badge assignments
- Training status to determine Scout readiness for specific merit badges
- Rank tracking to ensure merit badge requirements align with advancement goals

## Views for Common Queries

### Active Scouts View
```sql
CREATE VIEW active_scouts AS
SELECT 
    s.*,
    pg.name as primary_guardian_name,
    pg.email as primary_guardian_email,
    pg.mobile_phone as primary_guardian_phone
FROM scouts s
LEFT JOIN parent_guardians pg ON s.id = pg.scout_id AND pg.is_primary = 1
WHERE s.is_active = 1 AND s.age < 18;
```

### Scout Current Positions View
```sql
CREATE VIEW scout_current_positions AS
SELECT 
    s.first_name,
    s.last_name,
    s.bsa_number,
    sp.position_title,
    sp.patrol_name,
    sp.tenure_info
FROM scouts s
JOIN scout_positions sp ON s.id = sp.scout_id
WHERE sp.is_current = 1;
```

### Merit Badge Assignment Candidates View
```sql
CREATE VIEW mb_assignment_candidates AS
SELECT 
    s.id as scout_id,
    s.first_name,
    s.last_name,
    s.rank,
    s.patrol,
    pg.name as parent_name,
    pg.email as parent_email
FROM scouts s
LEFT JOIN parent_guardians pg ON s.id = pg.scout_id AND pg.is_primary = 1
WHERE s.is_active = 1 AND s.age BETWEEN 11 AND 17;
```
