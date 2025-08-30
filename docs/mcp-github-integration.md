# MCP Server GitHub Integration

The Merit Badge Manager MCP Server is a **development workflow tool** that provides GitHub integration to automatically publish YAML workitems as GitHub Issues. 

**Note**: This is an auxiliary tool for managing project issues and is **not required** for the core Merit Badge Manager functionality. The main application (Streamlit UI, database management, CSV import, etc.) works independently of this MCP server.

## What This Tool Does

The MCP server enables:
- Publishing YAML feature/bug files as GitHub issues
- Managing workitems in the development workflow
- Integrating with GitHub's issue tracking system

**This is NOT part of the core Merit Badge Manager application** - it's a separate tool for managing the development process itself.

## Setup

### 1. **Set Up Python Virtual Environment**
   ```bash
   # Create virtual environment (if not already created)
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

### 2. **Install Dependencies**
   ```bash
   # Make sure virtual environment is activated (you should see (venv) in your prompt)
   pip install -r requirements.txt
   ```

### 3. **Configure GitHub Access**
   - Copy `.env.template` to `.env`
   - Generate a GitHub Personal Access Token at: https://github.com/settings/tokens
   - Required scopes: `repo` (for creating issues)
   - Add your token to the `.env` file

### 4. **Start the MCP Server**
   ```bash
   # Easy way - uses the startup script that handles venv automatically
   python3 start_server.py
   
   # Manual way - make sure venv is activated first
   source venv/bin/activate  # On macOS/Linux
   cd mcp_server
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

## Important: Always Use Virtual Environment

⚠️ **Always activate the virtual environment before running any Python scripts or commands!**

The specification requires that "the Python Virtual Environment is created and activated before running the application or Python scripts, tests and commands."

Check if you're in the virtual environment:
- Your terminal prompt should show `(venv)` at the beginning
- Run `which python` (macOS/Linux) or `where python` (Windows) to verify you're using the venv Python
- Run `python --version` to ensure you're using Python 3.12.x (not 3.13)

## API Endpoints

### Core Publishing Endpoint

#### `POST /publish-feature`
Publishes a feature YAML file as a GitHub issue and moves it to the published directory.

**Request Body:**
```json
{
  "yml_filename": "01-csv-data-import-module.yml"
}
```

**Response:**
```json
{
  "message": "Feature successfully published to GitHub and moved to published directory",
  "github_issue": {
    "id": 12345,
    "number": 42,
    "url": "https://github.com/tqheel/merit-badge-manager/issues/42",
    "title": "Suggest a new feature or enhancement for the Merit Badge Manager"
  },
  "published_file": "/path/to/workitems/published/features/01-csv-data-import-module.yml"
}
```

### Management Endpoints

#### `GET /features`
Lists all unpublished feature YAML files.

#### `GET /published-features`
Lists all published feature YAML files.

#### `GET /feature/{yml_filename}`
Gets details and GitHub preview for a specific feature file.

#### `GET /health`
Health check endpoint showing configuration status.

## Usage Examples

### Using the Python Script
```bash
# Make sure virtual environment is activated first!
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

python scripts/publish_features.py
```

### Using curl
```bash
# List unpublished features
curl http://127.0.0.1:8000/features

# Publish a specific feature
curl -X POST http://127.0.0.1:8000/publish-feature \
  -H "Content-Type: application/json" \
  -d '{"yml_filename": "01-csv-data-import-module.yml"}'

# Check health
curl http://127.0.0.1:8000/health
```

## Virtual Environment Management

### Creating and Activating Virtual Environment
```bash
# Create (only needed once)
python3 -m venv venv

# Activate (needed every time you start a new terminal session)
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify you're in the virtual environment
which python  # Should show path ending in venv/bin/python
pip list      # Should show installed packages in venv
```

### Deactivating Virtual Environment
```bash
deactivate
```

## File Management

- **Source Directory**: `workitems/features/` - Contains unpublished feature YAML files
- **Published Directory**: `workitems/published/features/` - Contains published feature YAML files

When a feature is successfully published to GitHub, the YAML file is automatically moved from the source directory to the published directory.

## Security Notes

- Never commit your `.env` file to the repository
- GitHub tokens should have minimal required permissions
- The server runs locally and should not be exposed to the internet without proper security measures

## Error Handling

The API provides detailed error messages for common issues:
- Missing GitHub token configuration
- File not found errors
- GitHub API errors
- YAML parsing errors
- File system errors

All errors include appropriate HTTP status codes and descriptive error messages.

## YAML Formatting Requirements

### Critical: Multi-line Content Formatting

When creating YAML feature or bug templates, **always use YAML block literal syntax** for multi-line placeholder content:

#### ✅ **Correct Format**
```yaml
- type: textarea
  id: problem
  attributes:
    label: Problem Statement
    placeholder: |
      Use the pipe (|) character for multi-line content.
      This ensures complete content extraction and prevents
      truncation during YAML parsing.
```

#### ❌ **Incorrect Format**
```yaml
- type: textarea
  id: problem
  attributes:
    label: Problem Statement
    placeholder: Long single-line content may be truncated causing empty GitHub issue sections.
```

### Validation Steps

Before publishing YAML files:

1. **Test locally**: Verify YAML parsing extracts complete content
2. **Check sections**: Ensure all textarea fields have substantial content
3. **Preview**: Use MCP tools to preview GitHub issue content before publishing

### Troubleshooting Empty GitHub Issues

If GitHub issues show empty sections:
- Check YAML file formatting
- Verify multi-line content uses `|` syntax  
- Test content extraction locally
- Republish with corrected formatting
