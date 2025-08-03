# Merit Badge Manager - UI Testing with Playwright

This directory contains Playwright-based UI tests for the Merit Badge Manager web interface. These tests provide comprehensive coverage of all user-facing functionality through automated browser testing.

## Overview

The UI test suite validates:
- **Basic UI Functionality**: Page loading, navigation, responsive design
- **CSV Import & Validation**: File upload, validation feedback, import process
- **Database Management**: Database creation, backup, restore, reset operations
- **Database Views**: Data display, view selection, filtering
- **Environment Configuration**: Settings management, form validation
- **Integration Workflows**: Complete user journeys from setup to data analysis

## Test Structure

```
ui-tests/
├── __init__.py                     # Package initialization
├── conftest.py                     # Pytest fixtures and configuration
├── test_basic_ui.py               # Basic UI and navigation tests
├── test_csv_import.py             # CSV import and validation tests
├── test_database_management.py    # Database management tests
├── test_database_views.py         # Database views and data display tests
├── test_environment_config.py     # Environment configuration tests
└── test_integration_workflows.py  # End-to-end integration tests
```

## Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install pytest-playwright playwright
   ```

2. **Install Browsers**:
   ```bash
   playwright install
   ```
   Note: If browser installation fails in CI environments, tests will be skipped with appropriate warnings.

3. **Ensure Virtual Environment**:
   ```bash
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided test runner script:

```bash
# Run all UI tests
python run_ui_tests.py

# Run specific test suite
python run_ui_tests.py --suite basic      # Basic UI tests only
python run_ui_tests.py --suite csv        # CSV import tests only
python run_ui_tests.py --suite database   # Database management tests only
python run_ui_tests.py --suite views      # Database views tests only
python run_ui_tests.py --suite config     # Environment config tests only
python run_ui_tests.py --suite integration # Integration workflow tests only

# Run with different browser
python run_ui_tests.py --browser firefox
python run_ui_tests.py --browser webkit

# Run in headed mode (show browser window)
python run_ui_tests.py --headed

# Include slow tests (more comprehensive but longer running)
python run_ui_tests.py --slow
```

### Using Pytest Directly

```bash
# Run all UI tests
pytest ui-tests/ -v

# Run specific test file
pytest ui-tests/test_basic_ui.py -v

# Run with specific browser
pytest ui-tests/ --browser chromium -v

# Run in headed mode
pytest ui-tests/ --headed -v

# Exclude slow tests
pytest ui-tests/ -m "not slow" -v

# Run only UI tests (exclude other test suites)
pytest -m ui -v
```

## Test Categories

### Test Markers

Tests are marked with the following pytest markers:

- `@pytest.mark.ui`: All UI tests
- `@pytest.mark.slow`: Tests that take longer to run (> 10 seconds)

### Test Suites

1. **Basic UI Tests** (`test_basic_ui.py`)
   - Application loading and initialization
   - Sidebar navigation
   - Page transitions
   - Responsive design
   - Error message display

2. **CSV Import Tests** (`test_csv_import.py`)
   - File upload functionality
   - CSV validation and error reporting
   - Import process workflow
   - Progress indicators
   - File type restrictions

3. **Database Management Tests** (`test_database_management.py`)
   - Database creation and initialization
   - Backup and restore operations
   - Database reset functionality
   - Status display and feedback
   - Error handling

4. **Database Views Tests** (`test_database_views.py`)
   - View category selection
   - Data display and formatting
   - Adult vs. Youth view separation
   - Empty view handling
   - View refresh functionality

5. **Environment Configuration Tests** (`test_environment_config.py`)
   - Configuration form display
   - Environment variable management
   - Form validation
   - Settings persistence
   - Reset functionality

6. **Integration Workflow Tests** (`test_integration_workflows.py`)
   - Complete user workflows
   - Error recovery scenarios
   - Multi-step processes
   - Performance validation
   - Accessibility testing

## Test Data and Fixtures

### Fixtures Provided

- `streamlit_app`: Starts the Streamlit application for testing
- `clean_database`: Ensures clean database state for each test
- `sample_csv_files`: Provides sample CSV files for testing import functionality

### Sample Data

The test suite includes sample CSV data representing:
- Adult roster with positions and training dates
- Youth roster with ranks and parent contacts
- Combined roster files (typical user upload format)
- Invalid CSV files for error testing

## Configuration

### Playwright Configuration

The `playwright.config.py` file provides:
- Browser launch arguments optimized for CI environments
- Viewport settings for consistent testing
- Timeout configurations
- Security settings for HTTPS handling

### Pytest Configuration

The `pytest.ini` file is updated to include:
- UI test discovery in the `ui-tests` directory
- Test markers for categorization
- Logging configuration

## CI/CD Integration

### GitHub Actions

The UI tests are designed to work in CI environments:

```yaml
- name: Install UI Test Dependencies
  run: |
    pip install pytest-playwright playwright
    playwright install chromium

- name: Run UI Tests
  run: |
    python run_ui_tests.py --suite basic
```

### Browser Availability

Tests gracefully handle browser installation failures:
- Automatic fallback when browsers are not available
- Clear error messages in CI logs
- Conditional test skipping

## Debugging

### Running Tests in Debug Mode

```bash
# Run with browser visible for debugging
python run_ui_tests.py --headed

# Run single test for focused debugging
pytest ui-tests/test_basic_ui.py::test_streamlit_app_loads --headed -v

# Increase timeout for slow environments
pytest ui-tests/ --timeout 30000 -v
```

### Common Issues

1. **Browser Not Found**: Install browsers with `playwright install`
2. **Port Conflicts**: Ensure port 8501 is available for Streamlit
3. **Slow Tests**: Use `--timeout` to increase timeout values
4. **Memory Issues**: Run tests individually or in smaller suites

## Coverage

The UI test suite provides coverage for:

- ✅ **Page Loading**: All main application pages
- ✅ **Navigation**: Sidebar and page transitions
- ✅ **File Operations**: CSV upload and processing
- ✅ **Database Operations**: CRUD operations through UI
- ✅ **Data Validation**: Form validation and error handling
- ✅ **Data Display**: Tables, charts, and view rendering
- ✅ **User Workflows**: Complete user journeys
- ✅ **Error Scenarios**: Error handling and recovery
- ✅ **Responsive Design**: Multiple screen sizes
- ✅ **Accessibility**: Basic accessibility features

## Contributing

When adding new UI functionality:

1. **Add corresponding UI tests** in the appropriate test file
2. **Use descriptive test names** that explain what is being tested
3. **Include both positive and negative test cases**
4. **Add appropriate test markers** (`@pytest.mark.ui`, `@pytest.mark.slow`)
5. **Update this README** with new test categories or features
6. **Test in multiple browsers** when possible

## Performance

### Test Execution Times

- **Basic UI Tests**: ~2-3 minutes
- **CSV Import Tests**: ~3-5 minutes (includes file processing)
- **Database Management Tests**: ~4-6 minutes (includes database operations)
- **Database Views Tests**: ~3-4 minutes
- **Environment Config Tests**: ~2-3 minutes
- **Integration Workflow Tests**: ~8-12 minutes (marked as slow)

### Optimization

- Tests use `clean_database` fixture to avoid state contamination
- Sample data is generated in memory when possible
- Browser instances are reused within test sessions
- Timeouts are optimized for each test type

## Troubleshooting

### Common Error Messages

1. **"Browser not found"**: Run `playwright install chromium`
2. **"Streamlit server failed to start"**: Check port 8501 availability
3. **"Element not found"**: Verify Streamlit app is fully loaded
4. **"Timeout waiting for selector"**: Increase timeout or check element selectors

### Getting Help

- Check the test logs for detailed error messages
- Run tests in headed mode to see what's happening in the browser
- Use `pytest --tb=long` for detailed tracebacks
- Verify that the Streamlit app starts correctly with `streamlit run web-ui/main.py`