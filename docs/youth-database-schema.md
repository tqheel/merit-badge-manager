# Youth Roster Database Schema Documentation

## Overview

This document describes the youth roster database schema implementation for the Merit Badge Manager system, as specified in GitHub Issue #12. The schema provides comprehensive support for Scout tracking, merit badge progress management, and integration with the adult roster system for counselor assignments.

## Database Schema Components

### Core Tables

#### 1. `scouts` - Core Scout Information
The primary table storing essential Scout member data:

- **Primary Key**: `id` (auto-increment)
- **Unique Identifier**: `bsa_number` (for cross-system matching)
- **Demographics**: `first_name`, `last_name`, `date_of_birth`, `age`
- **Scouting Info**: `rank`, `patrol_name`, `unit_number`, `date_joined`
- **Status**: `activity_status` (Active, Inactive, Aged Out)
- **Contact**: `email`, `phone`, address fields
- **OA Membership**: `oa_info` (Order of the Arrow status)
- **Raw Data**: `positions_tenure`, `training_raw` (for import reference)

#### 2. `scout_training` - Training Records
Tracks Scout training certifications with expiration dates:

- **Foreign Key**: `scout_id` → `scouts.id`
- **Training Info**: `training_code`, `training_name`
- **Expiration**: `expiration_date` (supports "does not expire")
- **Constraint**: Unique per scout and training code

#### 3. `scout_positions` - Leadership Positions
Manages Scout leadership positions and patrol assignments:

- **Foreign Key**: `scout_id` → `scouts.id`
- **Position Info**: `position_title`, `patrol_name`
- **Tenure**: `tenure_info` (complex format: "5m 1d", "2y 5m 6d")
- **Status**: `is_current` flag for active positions
- **Dates**: `start_date`, `end_date` (optional)

#### 4. `parent_guardians` - Parent/Guardian Contacts
Stores up to 4 parent/guardian contacts per Scout:

- **Foreign Key**: `scout_id` → `scouts.id`
- **Identifier**: `guardian_number` (1-4)
- **Contact Info**: `first_name`, `last_name`, `relationship`
- **Communication**: `email`, multiple phone fields
- **Address**: Complete address information
- **Primary**: `is_primary` flag for main contact
- **Constraint**: Unique per scout and guardian number

#### 5. `scout_merit_badge_progress` - Merit Badge Tracking
Tracks Scout merit badge work and counselor assignments:

- **Foreign Key**: `scout_id` → `scouts.id`
- **Merit Badge**: `merit_badge_name`
- **Counselor**: `counselor_adult_id` (references adult roster)
- **Status**: `status` (Not Started, In Progress, Completed, Approved)
- **Tracking**: `date_started`, `date_completed`
- **Requirements**: `requirements_completed` (flexible format)
- **Notes**: Additional information
- **Constraint**: Unique per scout and merit badge

#### 6. `scout_advancement_history` - Rank Progression
Historical record of Scout advancement:

- **Foreign Key**: `scout_id` → `scouts.id`
- **Advancement**: `rank_name`, `date_awarded`
- **Process**: `board_of_review_date`, `scoutmaster_conference_date`
- **Notes**: Additional information

### Performance Optimization

#### Comprehensive Indexing Strategy
- **Scout Lookups**: BSA number, name, unit, rank, patrol, activity status, age
- **Training Queries**: Scout ID, training code, expiration date
- **Position Searches**: Scout ID, current positions, position title, patrol
- **Parent Contacts**: Scout ID, primary contacts, name
- **Merit Badge Progress**: Scout ID, badge name, counselor, status
- **Advancement**: Scout ID, rank, date

#### Foreign Key Constraints
- All child tables reference `scouts.id` with CASCADE DELETE
- Maintains data integrity and automatic cleanup

### Integration Features

#### Scout-to-Counselor Assignment System
The `scout_merit_badge_progress` table provides the integration point between Scout data and adult merit badge counselors:

```sql
-- Example: Assign counselor to scout for specific merit badge
INSERT INTO scout_merit_badge_progress (
    scout_id, merit_badge_name, counselor_adult_id, 
    status, date_started
) VALUES (1, 'First Aid', 3, 'In Progress', '2024-01-01');
```

#### Cross-System BSA Number Matching
Both adults and scouts use `bsa_number` as unique identifiers for:
- Data import reconciliation
- Cross-system queries and reporting
- Fuzzy name matching support

## Data Validation Views

### Scout Management Views

#### `scouts_missing_data`
Identifies scouts with incomplete required information:
- Missing rank, unit, join date, birth date, or patrol assignment

#### `active_scouts_with_positions`
Shows active scouts and their current leadership positions:
- Filtered to active scouts only
- Includes current position and patrol information

#### `advancement_progress_by_rank`
Summarizes advancement statistics by rank:
- Scout count per rank
- Active vs. total counts
- Average age by rank

#### `patrol_assignments`
Displays patrol membership and assignments:
- Scout count per patrol
- Active vs. total membership
- Scout names by patrol

### Merit Badge Management Views

#### `merit_badge_progress_summary`
Aggregates merit badge work across all scouts:
- Total scouts working on each badge
- Progress status breakdown (completed, in progress, not started)

#### `scouts_needing_counselors`
Critical view for counselor assignment management:
- Shows scouts without assigned counselors
- Filtered to active scouts with merit badge work
- Includes status and start date for prioritization

### Communication and Contact Views

#### `primary_parent_contacts`
Provides primary parent/guardian contact information:
- One contact per scout (primary flag = 1)
- Essential for communication about merit badge assignments
- Includes email and phone information

#### `scout_training_expiration_summary`
Tracks Scout training status:
- Expiration status (current, expired, expiring soon)
- Essential for determining Scout readiness for positions

## Data Processing Considerations

### Complex Data Import Requirements

#### Scout Training Data Processing
Training data arrives in pipe-separated format with complex structures:
```
"TLT - Troop Leadership Training (does not expire) | YPT_YOUTH - Youth Protection Training (expires 2025-01-15)"
```

Processing requirements:
- Parse pipe-separated values
- Extract training codes and names
- Handle various expiration formats
- Support "does not expire" values

#### Position Data Processing
Position data includes complex tenure and patrol information:
```
"Patrol Leader [Eagle Patrol] (5m 1d) | Senior Patrol Leader (2y 5m 6d) | Scribe [Dragon Fruit Patrol] (11m 3d)"
```

Processing requirements:
- Parse multiple concurrent/historical positions
- Extract patrol names from brackets
- Parse tenure duration formats
- Determine current vs. historical positions

#### Parent/Guardian Data Processing
Each Scout can have up to 4 parent/guardian contacts:
- Complete contact information per guardian
- Primary contact designation
- Relationship categorization
- Phone number normalization

### Data Quality Validation

#### BSA Number Uniqueness
- Enforced at database level
- Critical for cross-system matching
- Import validation required

#### Rank Hierarchy Validation
Proper advancement sequence validation:
Scout → Tenderfoot → Second Class → First Class → Star → Life → Eagle

#### Age-Based Activity Status
- 18+ typically aged out
- Activity status should align with age
- Exception handling for older active scouts

## Integration Points

### Merit Badge Counselor System Integration

#### Counselor Assignment Workflow
1. Scout registers interest in merit badge
2. Query available counselors from adult roster
3. Assign counselor via `scout_merit_badge_progress` table
4. Track progress and requirements completion
5. Update status upon completion

#### Query Examples
```sql
-- Find available counselors for a specific merit badge
SELECT a.first_name, a.last_name, a.email, a.phone
FROM adults a
JOIN adult_merit_badges amb ON a.id = amb.adult_id
WHERE amb.merit_badge_name = 'First Aid'
  AND a.health_form_status = 'Current';

-- Show scout assignments for a counselor
SELECT s.first_name, s.last_name, smbp.merit_badge_name, smbp.status
FROM scout_merit_badge_progress smbp
JOIN scouts s ON smbp.scout_id = s.id
WHERE smbp.counselor_adult_id = 3;
```

### Parent Communication Integration
The parent/guardian system enables:
- Merit badge assignment notifications
- Progress updates to families
- Contact information for counselor communication
- Emergency contact availability

### Patrol Management Integration
Patrol assignments support:
- Leadership position tracking within patrols
- Patrol-based merit badge projects
- Advancement coordination by patrol
- Activity planning and communication

## Usage Examples

### Common Query Patterns

#### Active Scouts by Rank
```sql
SELECT rank, COUNT(*) as count
FROM scouts 
WHERE activity_status = 'Active'
GROUP BY rank
ORDER BY CASE rank
  WHEN 'Scout' THEN 1
  WHEN 'Tenderfoot' THEN 2
  WHEN 'Second Class' THEN 3
  WHEN 'First Class' THEN 4
  WHEN 'Star' THEN 5
  WHEN 'Life' THEN 6
  WHEN 'Eagle' THEN 7
END;
```

#### Merit Badge Counselor Assignments
```sql
SELECT 
  s.first_name || ' ' || s.last_name as scout_name,
  smbp.merit_badge_name,
  a.first_name || ' ' || a.last_name as counselor_name,
  smbp.status,
  smbp.date_started
FROM scout_merit_badge_progress smbp
JOIN scouts s ON smbp.scout_id = s.id
LEFT JOIN adults a ON smbp.counselor_adult_id = a.id
WHERE s.activity_status = 'Active'
ORDER BY s.last_name, s.first_name;
```

#### Patrol Leadership
```sql
SELECT 
  sp.patrol_name,
  sp.position_title,
  s.first_name || ' ' || s.last_name as scout_name,
  sp.tenure_info
FROM scout_positions sp
JOIN scouts s ON sp.scout_id = s.id
WHERE sp.is_current = 1
  AND s.activity_status = 'Active'
ORDER BY sp.patrol_name, sp.position_title;
```

## Testing and Validation

### Test Database Generation
The system includes comprehensive test data generation:
- Realistic Scout demographics and advancement
- Varied patrol assignments and positions
- Parent/guardian contact information
- Merit badge progress with counselor assignments
- Training records with appropriate expiration dates

### Test Coverage Areas
1. **Schema Validation**: Table structure, constraints, indexes
2. **Data Integrity**: Foreign keys, unique constraints, cascading deletes
3. **View Functionality**: All validation views with sample data
4. **Integration Testing**: Adult-youth system interactions
5. **Performance Testing**: Index usage and query optimization

## Deployment and Maintenance

### Schema Setup
```bash
# Create database with both adult and youth schemas
python db-scripts/setup_database.py --database production.db --verify

# Create test database with sample data
python scripts/create_test_database.py --database test.db
```

### Backup and Migration
- Regular database backups recommended
- Schema version tracking via metadata table
- Migration scripts for future schema updates

### Monitoring and Performance
- Regular index usage analysis
- Query performance monitoring
- View optimization based on usage patterns

This youth roster database schema provides a comprehensive foundation for Scout tracking, merit badge management, and counselor assignment coordination while maintaining integration with the existing adult roster system.

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
