# Merit Badge Manager

A comprehensive application for managing Merit Badge Counselor (MBC) assignments and workloads for Scouting America Troops. This system streamlines the assignment and reporting of Merit Badge Counselors, enabling data-driven decision-making outside of Scoutbook.

## Quick Start

### Prerequisites
- **Python 3.12** (required - the project is designed for Python 3.12.x)
- Git

### 1. Environment Setup

**⚠️ Important: This project requires Python 3.12 and uses a virtual environment as required by the project specification.**

#### On macOS/Linux:
```bash
# Clone and navigate to the project
git clone https://github.com/tqheel/merit-badge-manager.git
cd merit-badge-manager

# Run the setup script
./setup.sh

# The setup script will:
# - Create a Python virtual environment
# - Activate the virtual environment  
# - Install all required dependencies
```

#### On Windows:
```cmd
# Clone and navigate to the project
git clone https://github.com/tqheel/merit-badge-manager.git
cd merit-badge-manager

# Run the setup script
setup.bat

# The setup script will:
# - Create a Python virtual environment
# - Activate the virtual environment
# - Install all required dependencies
```

#### Manual Setup:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the environment template
cp .env.template .env

# Edit .env file and add your GitHub token
# Generate token at: https://github.com/settings/tokens
# Required scopes: repo (for creating issues)
```

### 3. Start the Web UI (Recommended)

The Merit Badge Manager now features a comprehensive web interface for all operations:

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Start the Streamlit web application
streamlit run web-ui/main.py
```

The web interface provides:
- Environment configuration management
- CSV data import and validation
- Database setup and management
- Data viewing and reporting
- All functionality through a user-friendly interface

**Web Interface URL:** http://localhost:8501

### 4. Alternative: Start the MCP Server

For GitHub integration and API access:

```bash
# Easy way (handles virtual environment automatically)
python start_server.py

# Manual way (make sure venv is activated first)
source venv/bin/activate  # On macOS/Linux
cd mcp-server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The server will be available at:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs

## Features

### Web Interface (Primary)
- **Complete Web UI**: Streamlit-based interface for all operations
- **Environment Management**: Configure settings through web interface
- **CSV Import & Validation**: Upload and validate data files with real-time feedback
- **Database Operations**: Create, backup, and restore databases via UI
- **Data Visualization**: View and export database reports and analytics
- **No Command Line Required**: All functionality accessible through web browser

### Core Functionality
- **Merit Badge In-Progress Report Import**: Comprehensive CSV import system for Scoutbook Merit Badge In-Progress Reports with intelligent header cleaning, requirement parsing, and progress tracking
- **Advanced MBC Name Matching**: 4-tier fuzzy matching system (exact, nickname, string similarity, phonetic) with configurable confidence thresholds and manual review capabilities
- **CSV Data Import**: Process Merit Badge In-Progress Reports and Troop Roster Files with validation and error handling
- **Database Management**: SQLite database with proper schema and relationships, including 51 optimized indexes and 6 specialized views
- **Adult Roster Management**: Complete adult member database with training, merit badges, and positions
- **Youth Roster Management**: Comprehensive Scout tracking with merit badge progress, advancement history, and parent contacts
- **Scout-to-Counselor Integration**: Seamless assignment system connecting Scouts with adult merit badge counselors through BSA number matching
- **Reporting & Export**: Generate actionable reports and Excel exports with comprehensive import statistics
- **MBC Assignment Engine**: Intelligent assignment recommendations with data quality validation

### GitHub Integration
- **Feature Publishing**: Convert YAML feature requests to GitHub Issues
- **Workflow Management**: Automatic file management when features are published  
- **API Integration**: Full GitHub API integration for issue creation
- **YAML Format Validation**: Proper multi-line content formatting for complete issue publishing

### Database & Testing
- **Schema Management**: Automated database schema creation and validation for both adult and youth rosters
- **Test Data Generation**: Realistic fake data for development and testing with integrated adult-youth relationships
- **Comprehensive Test Suite**: Full test coverage for database functionality including cross-system integration

### Future Enhancements
- Web application interface
- Scoutbook automation with Playwright
- Automated report generation

## Project Structure

The project is organized into four distinct layers for clear separation of concerns:

```
merit-badge-manager/
├── data/                           # Data files (CSV imports)
├── database/                       # Database layer - SQL schemas and setup scripts
│   ├── create_adult_roster_schema.sql  # Adult database schema
│   ├── youth_database_schema.sql       # Youth database schema
│   ├── merit_badge_progress_schema.sql # Merit Badge progress tracking schema
│   ├── setup_database.py          # Automated database creation
│   └── README.md                   # Database documentation
├── database-access/                # Database access layer - Data processing and imports
│   ├── csv_validator.py           # CSV validation logic
│   ├── roster_parser.py           # CSV parsing functionality
│   ├── import_roster.py           # Data import and processing
│   ├── import_mb_progress.py      # Merit Badge In-Progress Report import system
│   ├── mb_progress_parser.py      # Merit Badge progress CSV parser with header cleaning
│   └── mbc_name_matcher.py        # Advanced fuzzy MBC name matching engine
├── web-ui/                         # Web UI layer - Streamlit application
│   └── main.py                     # Main Streamlit web interface
├── mcp-server/                     # MCP server layer - FastAPI server with GitHub integration
│   └── main.py                     # FastAPI server implementation
├── docs/                           # Documentation
│   ├── youth-database-schema.md    # Youth roster schema documentation
│   └── merit_badge_import_guide.md # Merit Badge In-Progress Report import documentation
├── logs/                           # Application logs
├── scripts/                        # Utility scripts
│   ├── create_test_database.py    # Test database with fake data generator
│   └── publish_features.py        # Feature publishing script
├── tests/                          # Unit and integration tests
│   ├── test_database_schema.py    # Adult database schema and functionality tests
│   ├── test_youth_database_schema.py   # Youth database schema and integration tests
│   ├── test_mb_progress_import.py # Merit Badge progress import system tests
│   ├── test_mb_progress_parser.py # Merit Badge CSV parser tests
│   ├── test_mb_progress_views.py  # Merit Badge database views tests
│   ├── test_mbc_name_matcher.py   # MBC fuzzy name matching tests
│   ├── test_mcp_server.py         # MCP server tests
│   └── test_*.py                  # Additional test files
├── ui-tests/                       # UI tests with Playwright
│   ├── test_basic_ui.py           # Basic UI and navigation tests
│   ├── test_csv_import.py         # CSV import functionality tests
│   ├── test_database_management.py # Database management tests
│   ├── test_database_views.py     # Database views tests
│   ├── test_environment_config.py # Environment configuration tests
│   ├── test_integration_workflows.py # End-to-end workflow tests
│   ├── conftest.py                # Pytest fixtures for UI testing
│   └── README.md                  # UI testing documentation
├── workitems/                      # Work item management
│   ├── features/                   # Unpublished feature requests
│   └── published/                  # Published feature requests
│       └── features/
├── requirements.txt                # Python dependencies
├── spec.md                        # Project specification
├── .env.template                  # Environment variables template
├── setup.sh                      # Setup script (macOS/Linux)
├── setup.bat                     # Setup script (Windows)
├── start_server.py               # Server startup script
├── run_ui_tests.py               # UI test runner script
└── playwright.config.py          # Playwright configuration
```

## Virtual Environment Management

### Why Virtual Environment is Required

The project specification mandates: *"Ensure the Python Virtual Environment is created and activated before running the application or Python scripts, tests and commands."*

### Daily Usage

**Every time you start a new terminal session:**

```bash
# Navigate to project directory
cd merit-badge-manager

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Verify activation (should show (venv) in prompt)
which python  # Should show path ending in venv/bin/python
python --version  # Should show Python 3.12.x (not 3.13)
```

### Installing New Dependencies

```bash
# Make sure venv is activated first!
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### YAML Feature/Bug Template Guidelines

When creating feature or bug YAML files, follow these formatting requirements:

#### ✅ **Correct Multi-line Formatting**
```yaml
- type: textarea
  id: problem
  attributes:
    label: Problem Statement
    placeholder: |
      Multi-line content should use YAML block literal syntax
      with the pipe (|) character to preserve formatting
      and prevent content truncation during parsing.
```

#### ❌ **Incorrect Single-line Formatting**  
```yaml
- type: textarea
  id: problem
  attributes:
    label: Problem Statement
    placeholder: Very long single-line content that may be truncated during YAML parsing and cause empty sections in GitHub issues.
```

**Important**: Always use the `|` block literal syntax for multi-line placeholder content to ensure complete GitHub issue publishing.

## Merit Badge In-Progress Report Import

The system includes comprehensive support for importing Merit Badge In-Progress Reports from Scoutbook with advanced data processing and matching capabilities.

### Quick Import Examples

**Web Interface (Recommended):**
1. Start the web interface: `streamlit run web-ui/main.py`
2. Navigate to "CSV Import & Validation" 
3. Upload your Merit Badge In-Progress Report CSV file
4. Review validation results and matching statistics
5. Import data with automatic MBC name matching

**Command Line Usage:**
```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Import Merit Badge In-Progress Report with auto-matching
python database-access/import_mb_progress.py data/mb_report.csv --auto-match-threshold 0.9

# Test MBC name matching against adult roster
python database-access/mbc_name_matcher.py --database merit_badge_manager.db "Mike Johnson"

# Parse CSV file and view structure (validation only)
python database-access/mb_progress_parser.py data/mb_report.csv --verbose
```

### Import Features
- **Intelligent CSV Processing**: Removes Scoutbook metadata, extracts merit badge years, parses complex requirements
- **4-Tier MBC Matching**: Exact (100%), nickname-aware (95%), fuzzy string, and phonetic matching (80%)
- **Scout Integration**: Links progress to youth roster via BSA number matching
- **Comprehensive Validation**: Detailed error reporting and data quality checks
- **Import Statistics**: Complete reporting of matching success rates and data insights

### Database Views for Merit Badge Management
```bash
# Connect to database to view imported data
sqlite3 merit_badge_manager.db

# View comprehensive merit badge status
sqlite> SELECT * FROM merit_badge_status_view LIMIT 5;

# Find scouts needing counselor assignments  
sqlite> SELECT * FROM scouts_available_for_mbc_assignment LIMIT 5;

# Review unmatched MBC names for manual resolution
sqlite> SELECT * FROM unmatched_mbc_assignments LIMIT 5;

sqlite> .quit
```

For detailed documentation, see: **[Merit Badge Import Guide](docs/merit_badge_import_guide.md)**

## API Usage

### Publishing Feature Requests

```bash
# List unpublished features
curl http://127.0.0.1:8000/features

# Publish a feature to GitHub
curl -X POST http://127.0.0.1:8000/publish-feature \
  -H "Content-Type: application/json" \
  -d '{"yml_filename": "01-csv-data-import-module.yml"}'

# Check server health
curl http://127.0.0.1:8000/health
```

### Using the Publishing Script

```bash
# Make sure virtual environment is activated!
source venv/bin/activate

# Run the publishing script
python scripts/publish_features.py
```

## Development Guidelines

### Coding Standards
- Follow standards outlined in `.github/copilot-instructions.md`
- Include issue numbers in all commit messages
- Use descriptive variable and function names
- Write modular, reusable code
- Include tests for new features and bug fixes
- Update documentation for functionality changes

### Security Requirements
- Never include passwords, API keys, or sensitive information in code
- Never hard-code configurable values
- Never use global variables unless absolutely necessary
- Never commit code that doesn't pass automated tests
- Never include PII or Troop data in code, tests, documentation, or issues

### Database Management
- Generate change scripts for schema changes
- Apply changes to SQLite database
- Update compatible dependencies (non-breaking changes)

## Contributing

1. Create feature requests using the GitHub issue templates
2. Label sub-issues of feature requests as `user story`
3. Generate test cases for every GitHub issue
4. Ensure virtual environment is activated before development
5. Follow the coding standards and security requirements

## Support

- **Documentation**: See `/docs` directory for detailed documentation
- **Issues**: Use GitHub issue templates for bug reports and feature requests
- **Specification**: See `spec.md` for detailed requirements and architecture

---

**Remember**: Always activate the virtual environment before running any Python commands! 🐍

## Database Management

### Web Interface Approach (Recommended)

The primary way to manage the database is through the Streamlit web interface:

```bash
# Start the web interface
source venv/bin/activate
streamlit run web-ui/main.py
```

The web interface provides:
- **Database Creation**: Create production databases with both adult and youth schemas
- **Data Import**: Upload and import CSV files with validation
- **Backup & Restore**: Database backup and restoration functionality  
- **Schema Verification**: Automatic schema validation and integrity checks
- **Test Data**: Generate test databases with realistic fake data
- **Configuration Management**: Manage .env settings through the UI

### Command Line Approach (Advanced Users)

For advanced users and automation, command line tools are still available:

### Creating the Production Database

The application uses SQLite for data storage with comprehensive schemas for both adult and youth roster management.

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Create production database with both adult and youth schemas (default)
python database/setup_database.py

# Create database with custom name and verify schema
python database/setup_database.py -d my_database.db --verify

# Create adult-only database (legacy mode)
python database/setup_database.py --adults-only

# Force recreation of existing database
python database/setup_database.py --force
```

### Creating a Test Database with Fake Data

For development and testing purposes, you can create a test database populated with realistic fake data for both adult and youth rosters:

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Create test database with fake adult and youth roster data
python scripts/create_test_database.py

# Create test database with custom name
python scripts/create_test_database.py --database my_test_database.db
```

The test database includes:
- **5 adult members** with complete profiles
- **14 training records** (YPT, Position Specific, IOLS, etc.)
- **21 merit badge counselor assignments** across various merit badges
- **6 adult position records** with tenure information
- **15 youth members (Scouts)** with complete demographics and advancement
- **45 Scout training records** with appropriate expiration tracking
- **18 Scout position assignments** including patrol leadership roles
- **45 parent/guardian contacts** (up to 4 per Scout)
- **25 merit badge progress records** with Scout-to-counselor assignments
- **30 advancement history entries** tracking rank progression

### Testing the Database

Run the comprehensive test suite to verify database functionality for both adult and youth systems, plus Merit Badge progress import:

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Run all database tests (adult, youth, and merit badge progress)
python -m pytest tests/test_database_schema.py tests/test_youth_database_schema.py tests/test_mb_progress*.py -v

# Run specific adult database tests
python -m pytest tests/test_database_schema.py::TestDatabaseSchema::test_database_creation -v
python -m pytest tests/test_database_schema.py::TestDatabaseSchema::test_schema_validation -v
python -m pytest tests/test_database_schema.py::TestDatabaseSchema::test_fake_data_generation -v

# Run specific youth database tests
python -m pytest tests/test_youth_database_schema.py::TestYouthDatabaseSchema::test_youth_schema_creation -v
python -m pytest tests/test_youth_database_schema.py::TestYouthDatabaseSchema::test_scout_counselor_integration -v
python -m pytest tests/test_youth_database_schema.py::TestYouthDatabaseSchema::test_validation_views -v

# Run Merit Badge progress import tests
python -m pytest tests/test_mb_progress_import.py -v
python -m pytest tests/test_mb_progress_parser.py -v
python -m pytest tests/test_mb_progress_views.py -v
python -m pytest tests/test_mbc_name_matcher.py -v
```

### UI Testing with Playwright

The project includes comprehensive UI tests for the Streamlit web interface using Playwright:

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Install Playwright browsers (one-time setup)
playwright install

# Run all UI tests using the test runner
python run_ui_tests.py

# Run specific UI test suites
python run_ui_tests.py --suite basic      # Basic UI and navigation tests
python run_ui_tests.py --suite csv        # CSV import functionality tests
python run_ui_tests.py --suite database   # Database management tests
python run_ui_tests.py --suite views      # Database views tests
python run_ui_tests.py --suite config     # Environment configuration tests
python run_ui_tests.py --suite integration # End-to-end workflow tests

# Run with different browsers
python run_ui_tests.py --browser firefox
python run_ui_tests.py --browser webkit

# Run in headed mode (show browser window)
python run_ui_tests.py --headed

# Include slow tests for comprehensive coverage
python run_ui_tests.py --slow

# Run UI tests directly with pytest
pytest ui-tests/ -v                       # All UI tests
pytest ui-tests/test_basic_ui.py -v       # Basic UI tests only
pytest -m ui -v                          # All tests marked as UI tests
pytest -m "ui and not slow" -v           # UI tests excluding slow ones
```

#### UI Test Coverage

The UI test suite validates:
- **Page Loading & Navigation**: All main application pages and sidebar navigation
- **CSV Import & Validation**: File upload, validation feedback, and import workflows
- **Database Management**: Database creation, backup, restore, and reset operations
- **Database Views**: Data display, view selection, and filtering functionality
- **Environment Configuration**: Settings management and form validation
- **Error Handling**: Error messages and recovery scenarios
- **Responsive Design**: Multiple screen sizes and accessibility features
- **Integration Workflows**: Complete user journeys from setup to data analysis

#### CI/CD Integration

UI tests are designed for automated testing in CI environments:

```bash
# Run UI tests in CI mode (headless, fast)
python run_ui_tests.py --suite basic --browser chromium

# Validate UI test setup without running browser-dependent tests
pytest ui-tests/test_ui_setup_validation.py -v
```

See `ui-tests/README.md` for detailed UI testing documentation.

### Database Schema Overview

The database includes comprehensive schemas for both adult and youth roster management, plus specialized Merit Badge progress tracking:

**Adult Tables:**
- `adults` - Primary member information (names, contact, BSA numbers, demographics)
- `adult_training` - Training certifications with expiration tracking
- `adult_merit_badges` - Merit badge counselor qualifications (which badges adults can counsel for)
- `adult_positions` - Position history with tenure information

**Youth Tables:**
- `scouts` - Core Scout information (rank, BSA number, patrol assignments, activity status)
- `scout_training` - Scout training certifications with expiration tracking
- `scout_positions` - Leadership positions and patrol assignments with tenure information
- `parent_guardians` - Parent/guardian contact information (up to 4 per Scout)
- `scout_merit_badge_progress` - Merit badge work tracking with counselor assignments
- `scout_advancement_history` - Historical record of rank progression

**Merit Badge Progress Tables:**
- `merit_badge_progress` - Detailed Merit Badge In-Progress Report data with requirement tracking
- `unmatched_mbc_names` - MBC names requiring manual review and resolution
- `mbc_name_mappings` - Manual mappings for fuzzy name matching improvements
- `merit_badge_requirements` - Individual requirement completion tracking with choice groups

**Integration Features:**
- **Scout-to-Counselor Assignments**: Connects Scouts with adult merit badge counselors
- **Merit Badge Progress Integration**: Links imported Scoutbook data with youth and adult rosters via BSA numbers
- **Cross-System BSA Number Matching**: Enables data reconciliation between systems
- **Shared Validation Patterns**: Consistent data quality across adult and youth systems

**Performance Features:**
- **51 optimized indexes** for common query patterns across all systems  
- **19 validation and reporting views** for data quality checks and operational reporting
- Foreign key constraints with cascade delete for data integrity
- Automatic timestamp triggers for audit trails

### Database Views

The database includes several validation and reporting views for operational insights and data quality checks:

**Adult Roster Views:**
- **Adults Missing Data View** (`adults_missing_data`) - Identifies adults with missing required information
- **Training Expiration Summary View** (`training_expiration_summary`) - Shows training status (current, expired, expiring soon)
- **Merit Badge Counselors View** (`merit_badge_counselors`) - Lists counselors available for each merit badge
- **Current Positions View** (`current_positions`) - Shows current position assignments and tenure information  
- **Registered Volunteers View** (`registered_volunteers`) - Shows all adults with BSA numbers and their active roles

**Merit Badge Progress Views:**
- **Merit Badge Status View** (`merit_badge_status_view`) - Comprehensive merit badge progress with Scout and counselor details
- **Scouts Available for MBC Assignment** (`scouts_available_for_mbc_assignment`) - Scouts with merit badge work but no assigned counselor
- **Unmatched MBC Assignments** (`unmatched_mbc_assignments`) - Progress records with unresolved counselor names
- **MBC Assignment Summary** (`mbc_assignment_summary`) - Statistical summary of counselor assignment success rates
- **Merit Badge Progress Summary** (`merit_badge_progress_summary`) - Overview of merit badge work across all Scouts
- **Data Quality Dashboard** (`data_quality_dashboard`) - Comprehensive data quality metrics and validation results

### Validating Database Content

After creating a database, you can validate its content for both adult and youth data:

```bash
# Connect to database and run validation queries
sqlite3 merit_badge_test_database.db

# Sample validation commands for adult data:
sqlite> SELECT COUNT(*) as adult_count FROM adults;
sqlite> SELECT * FROM current_positions;
sqlite> SELECT merit_badge_name, counselor_count FROM merit_badge_counselors LIMIT 5;
sqlite> SELECT * FROM registered_volunteers WHERE position_status = 'No Current Position';
sqlite> SELECT COUNT(*) as total_registered, 
       COUNT(CASE WHEN position_status = 'Has Position' THEN 1 END) as with_positions,
       COUNT(CASE WHEN position_status = 'No Current Position' THEN 1 END) as without_positions
       FROM registered_volunteers;

# Sample validation commands for youth data:
sqlite> SELECT COUNT(*) as scout_count FROM scouts;
sqlite> SELECT * FROM active_scouts_with_positions LIMIT 5;
sqlite> SELECT * FROM scouts_needing_counselors LIMIT 5;
sqlite> SELECT patrol_name, scout_count FROM patrol_assignments;

# Integration validation:
sqlite> SELECT s.first_name, s.last_name, smbp.merit_badge_name, a.first_name as counselor_first, a.last_name as counselor_last 
        FROM scout_merit_badge_progress smbp
        JOIN scouts s ON smbp.scout_id = s.id
        JOIN adults a ON smbp.counselor_adult_id = a.id
        LIMIT 5;
sqlite> .quit
```

### Database Files

- **Production Database**: `merit_badge_manager.db` (main application database with both adult and youth schemas)
- **Test Database**: `test_merit_badge_manager.db` (created by test script with sample data)
- **Adult Schema File**: `database/create_adult_roster_schema.sql` (adult database schema)
- **Youth Schema File**: `database/youth_database_schema.sql` (youth database schema)
- **Setup Script**: `database/setup_database.py` (automated database creation)

See `database/README.md` and `docs/youth-database-schema.md` for detailed database documentation.
