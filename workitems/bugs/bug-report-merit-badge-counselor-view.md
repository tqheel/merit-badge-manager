# Bug Report: Merit Badge Counselor View Shows No Records

## Issue Summary
After importing data, the Merit Badge Counselor view (`merit_badge_counselors`) does not display any records. This issue prevents users from viewing available counselors for merit badges, which is critical for Scout-to-counselor assignment workflows.
## Steps to Reproduce
1. Generate test data for the adult roster file and place it in the `./data` directory
2. Set the required file names in the `.env` settings to point to the test data files
3. Start the Streamlit application by running `streamlit run streamlit_app.py`
4. Navigate to the "Database Management" section in the UI
5. Use the "Create/Reset Database" function to initialize the SQLite database schema
6. Use the "Import Roster Data" function to upload and import the adult roster CSV file
7. After import completion, navigate to the "Merit Badge Counselors" view or query section
8. Query the `merit_badge_counselors` view using the following SQL command:

   ```sql
   SELECT merit_badge_name, counselor_count, counselors FROM merit_badge_counselors;
   ```

9. Observe that the query returns no records despite adults having merit badge qualifications in the CSV file.

## Expected Behavior
The `merit_badge_counselors` view should display merit badge names, the count of counselors available for each badge, and the names of the counselors.

## Actual Behavior
The query returns an empty result set, indicating that no data is available in the `merit_badge_counselors` view.

## Root Cause Analysis
**CONFIRMED:** The issue is caused by incorrect column name mapping in the import script.

### Column Name Mismatch
- **CSV Column Name:** `Merit Badges` (confirmed in `adult_roster.csv`)
- **Import Script Expects:** `Merit Badge Counselor For`, `merit_badge_counselor_for`, or `Merit_Badge_Counselor_For`
- **Result:** The import script cannot find the merit badge data column, so no merit badge counselor data is imported into the `adult_merit_badges` table.

### Data Format Issues
- **CSV Format:** Merit badges are pipe-separated (`|`) in the CSV file
- **Import Script Expects:** Semicolon-separated (`;`) values
- **Example CSV Data:** `Bird Study | Citizenship in Society | Cit. in Comm. | Cit. in Nation | Cit. in World | Communication | Cooking`

### Database Verification
- `adult_merit_badges` table: **0 records** (confirmed via SQL query)
- `merit_badge_counselors` view: **empty** (depends on `adult_merit_badges` table)

## Solution
Fixed the import script (`scripts/import_roster.py`) to:

1. **Correct Column Name Mapping:**
   - Added `'Merit Badges'` as the primary column name to check
   - Kept fallback options for backward compatibility

2. **Handle Pipe-Separated Data:**
   - Updated both the preview check and the import method to detect and handle pipe-separated (`|`) data
   - Maintained backward compatibility with semicolon-separated (`;`) data

3. **Code Changes:**
   ```python
   # Before (lines 389-393):
   merit_badges_raw = (row.get('Merit Badge Counselor For', '') or 
                      row.get('merit_badge_counselor_for', '') or 
                      row.get('Merit_Badge_Counselor_For', ''))
   
   # After:
   merit_badges_raw = (row.get('Merit Badges', '') or 
                      row.get('Merit Badge Counselor For', '') or 
                      row.get('merit_badge_counselor_for', '') or 
                      row.get('Merit_Badge_Counselor_For', ''))
   ```

## Test Results Expected
After applying the fix and re-importing data:
- `adult_merit_badges` table should contain records for each adult's merit badge qualifications
- `merit_badge_counselors` view should display aggregated counselor data
- Example expected output:
  ```
  merit_badge_name        | counselor_count | counselors
  ---------------------- | --------------- | ------------------
  Camping                | 8               | Ryan Verdery, Todd Qualls, ...
  Cooking                | 6               | Laura Kehn, Ryan Verdery, ...
  First Aid              | 4               | Ryan Verdery, Tom Hansen, ...
  ```

## Suggested Debugging Steps
1. Verify that the `adult_merit_badges` table contains data:

   ```sql
   SELECT * FROM adult_merit_badges;
   ```

2. Check the `adults` table for valid entries:

   ```sql
   SELECT * FROM adults;
   ```

3. Review the `merit_badge_counselors` view definition:

   ```sql
   SELECT sql FROM sqlite_master WHERE type = 'view' AND name = 'merit_badge_counselors';
   ```

4. Ensure that the `adult_merit_badges` table has valid `adult_id` references to the `adults` table.

## Additional Information
- The issue may be related to the `_import_merit_badge_counselor_data` method in `import_roster.py`.
- The `merit_badge_counselors` view is defined to aggregate data from the `adult_merit_badges` and `adults` tables.

## Environment
- **Application Version:** Merit Badge Manager v1.0
- **Database:** SQLite
- **Operating System:** macOS
- **Python Version:** 3.12

## Related Files
- `scripts/import_roster.py`
- `db-scripts/create_adult_roster_schema.sql`
- `db-scripts/setup_database.py`

## GitHub Issue
Please create a GitHub issue using this bug report and label it as `bug`. Include the issue number in the commit message when fixing this bug.
