# Bug Report: Playwright UI Test Failures

**Issue Date:** August 3, 2025  
**Severity:** High  
**Priority:** High  
**Category:** Testing Infrastructure  
**Environment:** macOS, Python 3.12.10, Chromium Browser  

## Summary

Multiple Playwright UI tests are failing with two primary categories of errors:
1. **Timeout errors** when attempting to click navigation elements (25+ tests)
2. **Strict mode violations** due to duplicate UI elements (2 tests)

**Test Results:** 25 failed, 16 passed, 19 deselected (Total runtime: 11 minutes 49 seconds)

## Error Categories

### 1. Navigation Timeout Errors (Primary Issue)
**Error Pattern:**
```
playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("label:has-text(\"[PAGE_NAME]\")").first
```

**Affected Test Files:**
- `test_csv_import.py` - All 4 tests failing
- `test_database_management.py` - All 4 tests failing  
- `test_database_views.py` - All 4 tests failing
- `test_environment_config.py` - All 12 tests failing

**Failed Navigation Labels:**
- "CSV Import & Validation"
- "Database Management" 
- "Environment Configuration"

### 2. Strict Mode Violations (Secondary Issue)
**Error Pattern:**
```
Error: strict mode violation: locator("[SELECTOR]") resolved to 2 elements
```

**Affected Tests:**
- `test_basic_ui.py::test_streamlit_app_loads` - Multiple `<h1>` elements found
- `test_integration_workflows.py::test_accessibility_workflow` - Multiple "Merit Badge Manager" text elements

**Duplicate Elements:**
1. Two `<h1>` elements:
   - `<h1>Navigation</h1>`
   - `<h1 id="merit-badge-manager">…</h1>`
2. Two "Merit Badge Manager" text elements:
   - Main heading with emoji: "🏕️ Merit Badge Manager"
   - Subtitle text: "Merit Badge Manager - Streamlit Web UI"

## Root Cause Analysis

### Navigation Timeout Issues
The primary cause appears to be that the **sidebar navigation elements are not being rendered** or are **not accessible** in the test environment. Possible causes:

1. **Streamlit App Structure Change**: The navigation may have changed from radio buttons to another UI pattern
2. **CSS/JavaScript Loading Issues**: Streamlit components may not be fully initialized
3. **Test Environment Configuration**: The Streamlit app may not be running in the expected mode for testing
4. **Timing Issues**: The app may need more time to render navigation elements

### Strict Mode Violations
The UI contains duplicate elements that violate Playwright's strict mode requirements:

1. **Multiple H1 elements**: Navigation header conflicts with main title
2. **Duplicate text content**: Main title and subtitle both contain "Merit Badge Manager"

## Impact Assessment

**High Impact Issues:**
- **83% test failure rate** (25/30 navigation-dependent tests failing)
- **Complete inability to test** core functionality (CSV import, database management, environment config)
- **Test suite reliability compromised** - 11+ minute runtime with mostly failures

**Medium Impact Issues:**
- **Accessibility testing blocked** due to element ambiguity
- **Integration workflow testing impaired**

## Technical Details

### Test Environment
- **Python:** 3.12.10
- **Pytest:** 8.4.1
- **Playwright:** 1.54.0
- **pytest-playwright:** 0.7.0
- **Browser:** Chromium
- **Timeout Settings:** 30 seconds for navigation, 5 seconds for assertions

### Working Tests (16 passed)
- Basic page load validation
- Sidebar presence detection
- Basic UI element visibility
- Test setup and configuration validation

## Recommended Solutions

### Priority 1: Fix Navigation Timeout Issues

1. **Investigate Streamlit App Structure**
   ```python
   # Verify current navigation implementation in web-ui/main.py
   # Check if sidebar radio buttons are still used for navigation
   ```

2. **Update Test Selectors**
   - Inspect actual DOM structure in running Streamlit app
   - Update locator patterns to match current implementation
   - Consider using more robust selectors (data-testid attributes)

3. **Improve Test Stability**
   - Add explicit wait conditions for Streamlit initialization
   - Implement retry mechanisms for navigation
   - Increase timeout for navigation elements if needed

### Priority 2: Resolve Strict Mode Violations

1. **Fix Duplicate H1 Elements**
   ```python
   # Update test selectors to be more specific:
   # Instead of: page.locator("h1")
   # Use: page.locator("h1#merit-badge-manager")
   ```

2. **Fix Duplicate Text Content**
   ```python
   # Instead of: page.locator("text=Merit Badge Manager")
   # Use: page.locator("h1:has-text('Merit Badge Manager')")
   ```

### Priority 3: Enhance Test Infrastructure

1. **Add Debug Logging**
   - Capture screenshots on test failures
   - Log DOM structure when navigation fails
   - Add performance timing measurements

2. **Implement Test Reliability Measures**
   - Add retry logic for flaky navigation
   - Implement graceful degradation for missing elements
   - Add health checks before running test suites

## Next Steps

1. **Immediate Actions** (Today):
   - Investigate current Streamlit app navigation structure
   - Update failing test selectors based on actual DOM
   - Fix strict mode violations in basic UI tests

2. **Short-term Actions** (This Week):
   - Implement robust navigation helper functions
   - Add comprehensive error handling and debugging
   - Create test stability improvements

3. **Long-term Actions** (Next Sprint):
   - Add visual regression testing
   - Implement cross-browser testing
   - Create performance benchmarks for UI tests

## Reproduction Instructions

### Prerequisites
1. **Python 3.12+** installed
2. **Git** access to the repository
3. **macOS/Linux/Windows** environment

### Step 1: Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/tqheel/merit-badge-manager.git
cd merit-badge-manager

# Create and activate Python virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with the following minimum configuration:
# (Update file paths to match your system)
ENVIRONMENT=development
ROSTER_CSV_FILE=test_roster_report.csv
MB_PROGRESS_CSV_FILE=test_merit_badge_progress.csv
VALIDATE_BEFORE_IMPORT=true
GENERATE_VALIDATION_REPORTS=true
VALIDATION_REPORTS_DIR=logs
```

### Step 3: Generate Test Data
Create test CSV files in the `data/` directory:

**File: `data/test_roster_report.csv`**
```csv
" ",ADULT MEMBERS
" ","First Name","Last Name","Email","City","State","Zip","Age","Date Joined","BSA Number","Unit Number","Training","Expiration Date","OA Info","Health Form A/B - Health Form C","Swim Class","Swim Class Date","Positions (Tenure)","Merit Badges"
"1","John","Doe","john.doe@example.com","Anytown","NC","27519","21 or more","01/01/2020","12345678","Troop 212 B","Y01 Safeguarding Youth Training Certification","01/01/2026","","","Swimmer","01/01/2024","Scoutmaster (3y 6m)","Camping | Cooking | First Aid"
"2","Jane","Smith","jane.smith@example.com","Anytown","NC","27519","21 or more","01/01/2019","12345679","Troop 212 B","Y01 Safeguarding Youth Training Certification","01/01/2026","","","Nonswimmer","","Assistant Scoutmaster (4y 6m)","Hiking | Nature | Orienteering"

" ",YOUTH MEMBERS
" ","First Name","Last Name","Date Joined","BSA Number","Unit Number","Rank","Eagle Scout Date","OA Info","Health Form A/B - Health Form C","Swim Class","Swim Class Date","Positions (Tenure)","Patrol","Address","City","State","Zip","Phone","Date of Birth","Parents/Guardians","Email","Emergency Contact Name","Emergency Contact Phone"
"1","Alex","Johnson","01/01/2021","87654321","Troop 212 B","Star","","","","Swimmer","01/01/2024","Senior Patrol Leader (6m)","Eagles","123 Main St","Anytown","NC","27519","(555) 123-4567","01/01/2008","John Johnson | Jane Johnson","alex.johnson@example.com","John Johnson","(555) 123-4567"
"2","Sam","Wilson","01/01/2020","87654322","Troop 212 B","Life","","OA - Active","","Nonswimmer","","Patrol Leader (1y)","Hawks","456 Oak Ave","Anytown","NC","27519","(555) 234-5678","01/01/2007","Mike Wilson | Lisa Wilson","sam.wilson@example.com","Mike Wilson","(555) 234-5678"
```

**File: `data/test_merit_badge_progress.csv`**
```csv
Generated: 08/03/2025 15:00:00
Merit Badge In-Progress Report
"Troop 0212 BOYS",

"In-Progress Merit Badge",
"Member ID","Scout First","Scout Last","MBC","Rank","Location","Merit Badge","Date Completed","Requirements",
"87654321","Alex","Johnson","John Doe","Star","Troop","Camping","","1,2,3,4"
"87654322","Sam","Wilson","Jane Smith","Life","Troop","Cooking","","1,2,3"
```

### Step 4: Create Database
```bash
# Create the database schema
python database/setup_database.py

# Generate test database with fake data
python scripts/create_test_database.py
```

### Step 5: Install Playwright
```bash
# Install Playwright browsers
python -m playwright install chromium
```

### Step 6: Start the Web Application
```bash
# Start the Streamlit web application (in a separate terminal)
python -m streamlit run web-ui/main.py --server.port=8501

# Or use the start script
python start_server.py
```

### Step 7: Run the UI Tests
```bash
# Run all UI tests
python run_ui_tests.py

# Or run with pytest directly
python -m pytest ui-tests/ -v --tb=short --browser=chromium -m "not slow"

# Run specific test files
python -m pytest ui-tests/test_basic_ui.py -v --browser=chromium
python -m pytest ui-tests/test_environment_config.py -v --browser=chromium
```

### Expected Failure Reproduction
The tests should fail with the following patterns:

1. **Navigation timeout errors** in most tests:
   ```
   TimeoutError: Locator.click: Timeout 30000ms exceeded.
   Call log:
     - waiting for locator("label:has-text(\"Environment Configuration\")").first
   ```

2. **Strict mode violations** in basic UI tests:
   ```
   Error: strict mode violation: locator("h1") resolved to 2 elements
   ```

### Verification Steps
1. **Confirm Streamlit app is running**: Navigate to `http://localhost:8501` in browser
2. **Check navigation elements**: Verify sidebar contains radio buttons for page navigation
3. **Inspect DOM structure**: Use browser dev tools to examine actual element selectors
4. **Test data presence**: Ensure CSV files are in `data/` directory and database is created

### Additional Debug Information
```bash
# Check test data files
ls -la data/

# Verify environment configuration
cat .env

# Check database exists
ls -la *.db

# Check database backups (stored in backups/ directory)
ls -la backups/

# View test logs
ls -la logs/

# Run tests with additional debugging
python -m pytest ui-tests/ -v --tb=long --capture=no
```

## Dependencies

- **Streamlit app must be running** on expected port during tests
- **Navigation UI structure** needs to be documented and stable
- **Test data** requirements for database-dependent tests
- **Environment configuration** template needs to be accessible
- **Python virtual environment** must be created and activated
- **CSV test data files** must be present in `data/` directory
- **Database schema** must be initialized before running tests
- **Playwright browsers** must be installed (`chromium` required)

## Risk Assessment

**High Risk:**
- Current test failures may mask real UI bugs
- Lack of reliable UI testing impedes development confidence
- Manual testing burden increases significantly

**Mitigation:**
- Prioritize fixing navigation timeout issues
- Implement monitoring for test health
- Consider alternative testing approaches if Playwright issues persist

---

**Reported by:** GitHub Copilot  
**Assigned to:** Development Team  
**Labels:** `bug`, `testing`, `ui`, `high-priority`, `playwright`
