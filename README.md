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

### 3. Start the MCP Server

```bash
# Easy way (handles virtual environment automatically)
python start_server.py

# Manual way (make sure venv is activated first)
source venv/bin/activate  # On macOS/Linux
cd mcp_server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The server will be available at:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs

## Features

### Core Functionality
- **CSV Data Import**: Process Merit Badge In-Progress Reports and Troop Roster Files
- **Fuzzy Name Matching**: Intelligent matching of MBC names across data sources
- **Database Management**: SQLite database with proper schema and relationships
- **Adult Roster Management**: Complete adult member database with training, merit badges, and positions
- **Youth Roster Management**: Comprehensive Scout tracking with merit badge progress, advancement history, and parent contacts
- **Scout-to-Counselor Integration**: Seamless assignment system connecting Scouts with adult merit badge counselors
- **Reporting & Export**: Generate actionable reports and Excel exports
- **MBC Assignment Engine**: Intelligent assignment recommendations

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

```
merit-badge-manager/
├── data/                          # Data files (CSV imports)
├── db-scripts/                    # Database setup and schema scripts
│   ├── create_adult_roster_schema.sql  # Adult database schema
│   ├── youth_database_schema.sql       # Youth database schema
│   └── setup_database.py         # Automated database creation
├── docs/                          # Documentation
│   └── youth-database-schema.md   # Youth roster schema documentation
├── logs/                          # Application logs
├── mcp_server/                    # MCP server implementation
│   └── main.py                    # FastAPI server with GitHub integration
├── scripts/                       # Utility scripts
│   ├── create_test_database.py   # Test database with fake data generator
│   └── publish_features.py       # Feature publishing script
├── tests/                         # Test files
│   ├── test_database_schema.py   # Adult database schema and functionality tests
│   ├── test_youth_database_schema.py   # Youth database schema and integration tests
│   ├── test_mcp_server.py        # MCP server tests
│   └── test_roster_parser.py     # Roster parsing tests
├── workitems/                     # Work item management
│   ├── features/                  # Unpublished feature requests
│   └── published/                 # Published feature requests
│       └── features/
├── requirements.txt               # Python dependencies
├── spec.md                       # Project specification
├── .env.template                 # Environment variables template
├── setup.sh                     # Setup script (macOS/Linux)
├── setup.bat                    # Setup script (Windows)
└── start_server.py              # Server startup script
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

### Creating the Production Database

The application uses SQLite for data storage with comprehensive schemas for both adult and youth roster management.

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Create production database with both adult and youth schemas (default)
python db-scripts/setup_database.py

# Create database with custom name and verify schema
python db-scripts/setup_database.py -d my_database.db --verify

# Create adult-only database (legacy mode)
python db-scripts/setup_database.py --adults-only

# Force recreation of existing database
python db-scripts/setup_database.py --force
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

Run the comprehensive test suite to verify database functionality for both adult and youth systems:

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Run all database tests (adult and youth)
python -m pytest tests/test_database_schema.py tests/test_youth_database_schema.py -v

# Run specific adult database tests
python -m pytest tests/test_database_schema.py::TestDatabaseSchema::test_database_creation -v
python -m pytest tests/test_database_schema.py::TestDatabaseSchema::test_schema_validation -v
python -m pytest tests/test_database_schema.py::TestDatabaseSchema::test_fake_data_generation -v

# Run specific youth database tests
python -m pytest tests/test_youth_database_schema.py::TestYouthDatabaseSchema::test_youth_schema_creation -v
python -m pytest tests/test_youth_database_schema.py::TestYouthDatabaseSchema::test_scout_counselor_integration -v
python -m pytest tests/test_youth_database_schema.py::TestYouthDatabaseSchema::test_validation_views -v
```

### Database Schema Overview

The database includes comprehensive schemas for both adult and youth roster management:

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

**Integration Features:**
- **Scout-to-Counselor Assignments**: Connects Scouts with adult merit badge counselors
- **Cross-System BSA Number Matching**: Enables data reconciliation between systems
- **Shared Validation Patterns**: Consistent data quality across adult and youth systems

**Performance Features:**
- **36 optimized indexes** for common query patterns across both systems  
- **13 validation views** for data quality checks and operational reporting
- Foreign key constraints with cascade delete for data integrity
- Automatic timestamp triggers for audit trails

### Database Views

The database includes several validation and reporting views for operational insights and data quality checks:

**Adults Missing Data View** (`adults_missing_data`)
- Identifies adults with missing required information
- Helps ensure data completeness for roster management

**Training Expiration Summary View** (`training_expiration_summary`)  
- Shows training status (current, expired, expiring soon)
- Critical for compliance tracking and certification management

**Merit Badge Counselors View** (`merit_badge_counselors`)
- Lists counselors available for each merit badge
- Enables efficient Scout-to-counselor assignment workflows

**Current Positions View** (`current_positions`)
- Shows current position assignments and tenure information  
- Provides leadership structure overview

**Registered Volunteers View** (`registered_volunteers`)
- Shows all adults with BSA numbers (registered volunteers) and their active roles
- Comprehensive view of all registered adults, including those without current positions
- Enables quick identification of volunteer capacity and leadership gaps

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
- **Adult Schema File**: `db-scripts/create_adult_roster_schema.sql` (adult database schema)
- **Youth Schema File**: `db-scripts/youth_database_schema.sql` (youth database schema)
- **Setup Script**: `db-scripts/setup_database.py` (automated database creation)

See `db-scripts/README.md` and `docs/youth-database-schema.md` for detailed database documentation.
