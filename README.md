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
- **Reporting & Export**: Generate actionable reports and Excel exports
- **MBC Assignment Engine**: Intelligent assignment recommendations

### GitHub Integration
- **Feature Publishing**: Convert YAML feature requests to GitHub Issues
- **Workflow Management**: Automatic file management when features are published
- **API Integration**: Full GitHub API integration for issue creation

### Future Enhancements
- Web application interface
- Scoutbook automation with Playwright
- Automated report generation

## Project Structure

```
merit-badge-manager/
├── data/                          # Data files (CSV imports)
├── docs/                          # Documentation
├── logs/                          # Application logs
├── mcp_server/                    # MCP server implementation
│   └── main.py                    # FastAPI server with GitHub integration
├── scripts/                       # Utility scripts
│   └── publish_features.py       # Feature publishing script
├── tests/                         # Test files
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
