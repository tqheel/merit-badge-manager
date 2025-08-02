# Database Schema for Adult Roster Data

## Overview

This document specifies the SQLite database schema for storing Adult roster data imported from CSV files. The schema is based on analysis of the adult roster CSV file structure and data types.

## CSV File Analysis

The adult roster CSV contains the following header columns:
- First Name, Last Name, Email, City, State, Zip
- Age, Date Joined, BSA Number, Unit Number
- Training, Expiration Date
- OA Info, Health Form A/B - Health Form C, Swim Class, Swim Class Date
- Positions (Tenure), Merit Badges

## Data Type Analysis

Based on sample data values:
- **Text fields**: Names, email addresses, cities, states, training details, positions, merit badges
- **Numeric fields**: BSA Number, Zip codes
- **Date fields**: Date Joined, Expiration Date, Swim Class Date
- **Structured text fields**: Training (pipe-separated list), Expiration Date (pipe-separated list), Positions (complex tenure info), Merit Badges (pipe-separated list)
- **Age categories**: "21 or more", "18 to 20", "18 or less" (categorical data)
- **Status fields**: OA Info, Health Form status, Swim Class

## SQLite Schema

### Adults Table

```sql
CREATE TABLE adults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    age_category TEXT,
    date_joined DATE,
    bsa_number INTEGER UNIQUE NOT NULL,
    unit_number TEXT,
    oa_info TEXT,
    health_form_status TEXT,
    swim_class TEXT,
    swim_class_date DATE,
    positions_tenure TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Adult Training Table

```sql
CREATE TABLE adult_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adult_id INTEGER NOT NULL,
    training_code TEXT NOT NULL,
    training_name TEXT NOT NULL,
    expiration_date TEXT, -- Some training "does not expire"
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE,
    UNIQUE(adult_id, training_code)
);
```

### Adult Merit Badge Qualifications Table

The `adult_merit_badges` table stores which merit badges each adult member is qualified to counsel for. This represents the merit badges that counselors **offer** or are **qualified** to help scouts with, not merit badges assigned to the adults themselves.

**Key Points:**
- Adults select which merit badges they are qualified to counsel for
- This data comes from the "Merit Badge Counselor For" column in the adult roster CSV  
- Scouts choose merit badges and are assigned to these qualified counselors by the Scoutmaster
- The actual scout-to-counselor assignments are tracked separately in the youth database

```sql
CREATE TABLE adult_merit_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adult_id INTEGER NOT NULL,
    merit_badge_name TEXT NOT NULL, -- Merit badge the adult is qualified to counsel for
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE,
    UNIQUE(adult_id, merit_badge_name)
);
```

### Adult Positions Table

```sql
CREATE TABLE adult_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adult_id INTEGER NOT NULL,
    position_title TEXT NOT NULL,
    tenure_info TEXT, -- e.g., "(4m 16d)", "(7y 1m 26d)"
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT 1,
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE
);
```

## Indexes for Performance

```sql
-- Primary lookup indexes
CREATE INDEX idx_adults_bsa_number ON adults(bsa_number);
CREATE INDEX idx_adults_name ON adults(last_name, first_name);
CREATE INDEX idx_adults_email ON adults(email);
CREATE INDEX idx_adults_unit ON adults(unit_number);

-- Training lookup indexes
CREATE INDEX idx_adult_training_adult_id ON adult_training(adult_id);
CREATE INDEX idx_adult_training_code ON adult_training(training_code);

-- Merit badge counselor indexes
CREATE INDEX idx_adult_merit_badges_adult_id ON adult_merit_badges(adult_id);
CREATE INDEX idx_adult_merit_badges_name ON adult_merit_badges(merit_badge_name);

-- Position indexes
CREATE INDEX idx_adult_positions_adult_id ON adult_positions(adult_id);
CREATE INDEX idx_adult_positions_current ON adult_positions(is_current);
```

## Data Import Considerations

### Training Data Processing
- Training field contains pipe-separated training courses with complex formatting
- Each training item includes course code, name, and expiration date
- Example: "C40 Cubmaster and Assist Pos Specific Tng Classroom | Y01 Safeguarding Youth Training Certification"
- Expiration dates are in separate pipe-separated field: "(does not expire) | 06/21/2026"
- Need to parse and match training items with their expiration dates by position

### Merit Badge Counselor Qualification Data Processing
- Merit badge field contains pipe-separated list of badge names that the adult is qualified to counsel for
- Example: "Bird Study | Citizenship in Society | Cit. in Comm. | Cit. in Nation"  
- These represent qualifications/offerings by the counselor, not assignments to the counselor
- Adults select which merit badges they are qualified to help scouts with based on their expertise
- Some adults have no merit badge counselor qualifications (empty field)
- The actual assignment of counselors to scouts happens separately via the Scoutmaster

### Position Data Processing
- Positions field contains complex tenure information
- Example: "Assistant Scoutmaster (4m 16d) | Committee Member (7y 5m 26d)"
- Tenure format: position title followed by duration in parentheses
- Duration format: years (y), months (m), days (d)
- Multiple positions may be held simultaneously

### Age Category Mapping
- "21 or more" -> Adult
- "18 to 20" -> Young Adult
- "18 or less" -> Youth (unusual for adult roster)

### Data Quality Notes
- Some email addresses may be placeholder values: "changeyouremail@scoutbook.com"
- BSA Numbers are unique identifiers for matching between systems
- Empty fields should be handled as NULL values
- Some ZIP codes may be missing or incomplete
- OA Info includes status: "OA - Active", "OA - Inactive", or empty
- Swim Class values: "Swimmer", "Nonswimmer", or empty

## Normalized Data Benefits

1. **Training Management**: Separate table allows for easier reporting on training completions and expirations
2. **Merit Badge Counselor Tracking**: Enables queries for available counselors by merit badge
3. **Position History**: Supports tracking of leadership role changes over time
4. **Data Integrity**: Foreign key constraints ensure referential integrity
5. **Query Performance**: Indexes optimize common lookup patterns
