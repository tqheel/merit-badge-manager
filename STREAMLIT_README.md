# Running the Streamlit Web UI

The Merit Badge Manager includes a web-based user interface built with Streamlit that provides:

- **Settings Management**: Configure and persist .env file settings
- **CSV Import & Validation**: Upload and validate roster CSV files with error reporting
- **Database Views**: Display and explore the various database views with data

## Quick Start

1. **Set up the environment** (if not already done):
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Streamlit application**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open your browser** to the URL shown (typically http://localhost:8501)

## Using the Web UI

### 1. Settings Page
- Configure all environment variables from the `.env.template`
- Set GitHub token, repository, CSV file names, and validation options
- Click "Save Settings" to persist configuration to `.env` file

### 2. CSV Import & Validation Page
- View expected file locations for roster and merit badge progress CSV files
- Validate CSV files before import to catch errors early
- Import data into the database with one-click operation
- Reset database if needed

### 3. Database Views Page
- Browse all available database views organized by category:
  - **Adult Views**: Adults missing data, training expiration, merit badge counselors, current positions
  - **Youth Views**: Scouts missing data, active scouts with positions, merit badge progress, advancement by rank, etc.
- View data in easy-to-read tables with record counts

## Features

- **Automatic Validation**: Ensures settings are configured before allowing imports
- **Error Reporting**: Clear error messages for validation and import issues
- **User-Friendly Interface**: Clean, organized layout with helpful warnings and success messages
- **Real-time Updates**: Changes are immediately reflected in the interface

## Notes

- The application requires Python 3.12 and the dependencies listed in `requirements.txt`
- CSV files should be placed in the `data/` directory with names matching your configuration
- The SQLite database (`database/merit_badge_manager.db`) is automatically created during first import