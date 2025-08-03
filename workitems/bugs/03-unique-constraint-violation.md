# Unique Constraint Violation During Data Import

## Labels
- bug
- data-integrity
- database
- validation

## Assignees
- Copilot

## Priority
High

## Branch
copilot/fix-16

## Steps to Reproduce
1. Import the CSV file `RosterReport_Troop0212B_Roster_by_Unit_Patrol_DOB_Scouts_and_Adults_20250727.csv` using the Streamlit UI.
2. Observe the validation report indicating skipped rows due to duplicate BSA numbers.
3. Check the database logs for UNIQUE constraint violation errors.

## Expected Behavior
- Duplicate rows should be skipped without causing database errors.
- Validation report should clearly indicate skipped rows and reasons.

## Actual Behavior
- UNIQUE constraint violation errors occur during data import.
- Validation report indicates skipped rows but does not prevent database errors.

## Possible Solutions
- Enhance the `import_roster.py` script to handle duplicates before database insertion.
- Add logic to validate and skip duplicate entries during the import process.
- Update the database schema to include CASCADE DELETE constraints where necessary.

## Additional Notes
- Ensure backward compatibility with adult roster system.
- Test both adult and youth database schemas for cross-system compatibility.
- Validate Scout-to-counselor assignment functionality after fixing the issue.
- Include automated tests for duplicate handling and constraint validation.
- When in "Development" environment, the UI should provide the detailed error message in a modal window.
