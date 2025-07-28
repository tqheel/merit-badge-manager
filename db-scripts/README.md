# Database Scripts

This directory contains scripts for creating and managing the Merit Badge Manager database schema.

## Files

### `create_adult_roster_schema.sql`
Complete SQL script that creates the adult roster database schema including:
- **Tables**: adults, adult_training, adult_merit_badges, adult_positions
- **Indexes**: Performance optimized indexes for common queries
- **Views**: Data validation and reporting views
- **Triggers**: Automatic timestamp updates

### `setup_database.py`
Python script that executes the SQL schema and provides database setup utilities.

## Usage

### Quick Setup (Recommended)
```bash
# Activate virtual environment
source venv/bin/activate

# Create database with default name
python db-scripts/setup_database.py

# Create database with custom name and verify
python db-scripts/setup_database.py -d my_database.db --verify
```

### Manual SQL Execution
```bash
# Using sqlite3 command line
sqlite3 merit_badge_manager.db < db-scripts/create_adult_roster_schema.sql
```

### Command Line Options
```bash
python db-scripts/setup_database.py --help

Options:
  --database, -d    Database file path (default: merit_badge_manager.db)
  --verify, -v      Verify schema after creation
  --force, -f       Force recreation even if database exists
```

## Database Schema Overview

### Core Tables

1. **adults** - Primary table for adult member information
   - Basic info: names, contact, BSA numbers
   - Demographics: age category, join date
   - Status: OA info, health forms, swim class

2. **adult_training** - Training certifications
   - Training codes and names
   - Expiration dates (some never expire)
   - One-to-many relationship with adults

3. **adult_merit_badges** - Merit badge counselor certifications
   - Merit badge names
   - One-to-many relationship with adults

4. **adult_positions** - Position history and tenure
   - Position titles and tenure information
   - Start/end dates and current status
   - One-to-many relationship with adults

### Validation Views

- **adults_missing_data** - Identifies adults with missing required information
- **training_expiration_summary** - Shows training status (current, expired, expiring soon)
- **merit_badge_counselors** - Lists counselors available for each merit badge
- **current_positions** - Shows current position assignments

### Performance Features

- **Indexes** on frequently queried fields (BSA numbers, names, training codes)
- **Foreign key constraints** for data integrity
- **Unique constraints** to prevent duplicate assignments
- **Automatic timestamps** for audit trails

## Data Import Considerations

The schema is designed to handle complex CSV data parsing:

- **Pipe-separated fields**: Training lists, merit badges, positions
- **Complex tenure data**: Position titles with duration information
- **Date parsing**: Various date formats from CSV exports
- **Data quality**: Handles missing values and placeholder data

## Next Steps After Schema Creation

1. **Import CSV Data**: Use the roster parser to populate tables
2. **Data Validation**: Run validation views to check data quality
3. **Performance Testing**: Verify query performance with real data
4. **Backup Strategy**: Implement regular database backups

## Schema Version

- **Version**: 1.0.0
- **Created**: 2025-07-28
- **Reference**: docs/create-db-schema-for-adult-roster.md
- **Compatible with**: SQLite 3.x

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure write permissions in the directory
2. **Foreign key errors**: Check that foreign key constraints are enabled
3. **Import failures**: Verify CSV data format matches expected schema

### Verification Commands

```sql
-- Check foreign key constraints
PRAGMA foreign_keys;

-- List all tables
SELECT name FROM sqlite_master WHERE type='table';

-- Check table structure
PRAGMA table_info(adults);

-- Test data integrity
SELECT * FROM adults_missing_data;
```
