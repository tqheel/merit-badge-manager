# CSV Import and Validation

This directory contains tools for importing and validating Scout roster CSV files from Scoutbook.

## Overview

The import system provides:
- **Configuration-based file naming** via `.env` file
- **Schema validation** against database structure
- **Detailed error reporting** with actionable recommendations
- **Database recreation** with clean import
- **Test data** for validation scenarios

## Configuration

Copy `.env.template` to `.env` and configure the following settings:

```bash
# CSV Import Configuration
ROSTER_CSV_FILE=roster_report.csv
MB_PROGRESS_CSV_FILE=merit_badge_progress.csv

# Import Validation Settings
VALIDATE_BEFORE_IMPORT=true
GENERATE_VALIDATION_REPORTS=true
VALIDATION_REPORTS_DIR=logs
```

## Usage

### Basic Import

1. Place your roster CSV file in the `data/` directory
2. Update the `ROSTER_CSV_FILE` setting in `.env`
3. Run the import script:

```bash
python scripts/import_roster.py
```

### Validation Only

To validate CSV files without importing:

```bash
python scripts/import_roster.py --validate-only
```

### Force Import (Skip Validation)

To skip validation and force import:

```bash
python scripts/import_roster.py --force
```

## Validation Features

### Adult Roster Validation
- **Required fields:** First Name, Last Name, BSA Number
- **Format validation:** Email, BSA numbers, dates
- **Duplicate detection:** BSA numbers must be unique
- **Optional fields:** All other adult roster columns

### Youth Roster Validation
- **Required fields:** First Name, Last Name, BSA Number
- **Format validation:** Email, phone, BSA numbers, dates
- **Data validation:** Age ranges, rank values, activity status
- **Duplicate detection:** BSA numbers must be unique

### Error Reporting

The system provides:
- **Terminal summary** with immediate feedback
- **Detailed reports** saved to logs directory
- **Actionable recommendations** for fixing issues
- **User prompts** for viewing detailed reports

## File Structure

```
data/                    # Place CSV files here
├── roster_report.csv    # Main roster file (configurable name)
└── merit_badge_progress.csv  # MB progress (future)

output/                  # Processed CSV files
├── adult_roster.csv     # Parsed adult data
└── scout_roster.csv     # Parsed youth data

logs/                    # Validation reports
└── validation_report_*.txt  # Timestamped reports

tests/test_data/validation/  # Test data files
├── roster_report_valid.csv       # Valid test data
├── roster_report_invalid.csv     # Invalid test data
├── adult_roster_valid.csv        # Valid adult data
├── adult_roster_invalid.csv      # Invalid adult data
├── youth_roster_valid.csv        # Valid youth data
└── youth_roster_invalid.csv      # Invalid youth data
```

## Expected CSV Format

### Combined Roster File (from Scoutbook)
The system expects a combined CSV file with sections for adults and youth:

```
"ADULT MEMBERS"
"First Name","Last Name","Email","BSA Number",...
"John","Smith","john@email.com","12345678",...

"YOUTH MEMBERS"  
"First Name","Last Name","BSA Number","Rank",...
"Tommy","Scout","99887766","Scout",...
```

### Individual Files (after parsing)

**Adult Roster:** `first_name`, `last_name`, `email`, `bsa_number`, `city`, `state`, etc.

**Youth Roster:** `first_name`, `last_name`, `bsa_number`, `rank`, `age`, `patrol_name`, etc.

## Validation Rules

### BSA Numbers
- Must be numeric
- 6-12 digits long
- Must be unique within each roster
- Required for all records

### Email Addresses
- Standard email format validation
- Optional for both adults and youth

### Dates
- Supports multiple formats: YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY
- Validates actual date values
- Optional for most date fields

### Youth-Specific Rules
- **Ranks:** Scout, Tenderfoot, Second Class, First Class, Star, Life, Eagle
- **Activity Status:** Active, Inactive, Aged Out
- **Age:** Reasonable range 6-21 years (warning if outside)

## Testing

Run validation tests:
```bash
python -m pytest tests/test_csv_validation.py -v
```

Run import tests:
```bash
python -m pytest tests/test_import_roster.py -v
```

## Troubleshooting

### Common Issues

1. **File not found:** Check file path and name in `.env`
2. **Header mismatch:** Ensure CSV headers match expected format
3. **Encoding errors:** Save CSV files as UTF-8
4. **Empty required fields:** Check for missing names or BSA numbers

### Getting Help

1. Run with `--validate-only` to see specific errors
2. Check generated validation reports in logs directory
3. Review test data files for examples
4. Ensure CSV file format matches Scoutbook export format

## Future Enhancements

- Merit badge progress validation (when schema is defined)
- Custom validation rules configuration
- CSV format auto-detection
- Data transformation options