# Bug Report: Scout Position Data Not Parsed During Roster Import

## Issue Summary
Scout position data from the "Positions (Tenure)" column in roster CSV files is not being parsed and imported into the `scout_positions` table during the roster import process.

## Current Behavior
- Roster import successfully creates the database schema including `scout_positions` table
- Basic scout data (name, rank, patrol, etc.) is imported correctly
- Position data exists in CSV but is not parsed into individual position records
- `scout_positions` table remains empty after import
- Views like `current_por_scouts` show no results despite having scouts with leadership positions

## Expected Behavior
- Position data from "Positions (Tenure)" CSV column should be parsed
- Individual position records should be created in `scout_positions` table
- Current positions should have `is_current = 1` flag set
- Position titles and tenure information should be extracted and stored properly
- Views like `current_por_scouts` should display actual scout leadership positions

## Example Position Data from CSV
```
"Webmaster (5m 9d)"
"Patrol Leader [ Anonymous Message] Patrol (5m 9d)"
"Assistant Patrol Leader [ Anonymous Message] Patrol (5m 9d)"
"Scouts BSA [ 2025 Inactive and Aged Out] Patrol (5m 24d)"
```

## Impact
- Cannot track current scout leadership positions
- POR (Position of Responsibility) reporting views are empty
- Unable to identify scouts holding leadership roles for advancement requirements
- Missing critical data for troop management and leadership development

## Steps to Reproduce
1. Run roster import: `python3 database-access/import_roster.py`
2. Check scout_positions table: `SELECT COUNT(*) FROM scout_positions WHERE is_current = 1`
3. Result: 0 records (should show current leadership positions)
4. Query POR view: `SELECT * FROM current_por_scouts`
5. Result: No records returned

## Technical Details
- **Database**: SQLite (`database/merit_badge_manager.db`)
- **Import Script**: `database-access/import_roster.py`
- **Parser Module**: `database-access/roster_parser.py`
- **CSV Column**: "Positions (Tenure)"
- **Target Table**: `scout_positions`
- **Key Fields**: `position_title`, `tenure_info`, `is_current`

## Affected Components
- `database-access/roster_parser.py` - Position parsing logic needed
- `database-access/import_roster.py` - Position import functionality needed
- `database/current_por_scouts_view.sql` - View depends on position data
- Any reports or UI components that display scout leadership positions

## Priority
**High** - This affects core scout leadership tracking functionality and advancement requirements monitoring.

## Acceptance Criteria
- [ ] Parse "Positions (Tenure)" column from scout roster CSV
- [ ] Extract individual position titles (e.g., "Webmaster", "Patrol Leader")
- [ ] Extract tenure information (e.g., "5m 9d")
- [ ] Create records in `scout_positions` table with `is_current = 1`
- [ ] Handle multiple positions per scout (pipe-separated)
- [ ] Filter out non-leadership positions (e.g., basic patrol membership)
- [ ] Validate that `current_por_scouts` view returns expected results
- [ ] Add unit tests for position parsing functionality

## Related Files
- `/database/current_por_scouts_view.sql` - POR view (working correctly)
- `/database-access/roster_parser.py` - Needs position parsing logic
- `/database-access/import_roster.py` - Needs position import integration
- `/tests/test_import_roster.py` - Needs position parsing tests
