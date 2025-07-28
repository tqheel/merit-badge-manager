
# Merit Badge Counselor Management Application — Specification

## 1. Overview

This document specifies the requirements and architecture for the Scouting America Merit Badge Counselor Management Application, designed to streamline the assignment and reporting of Merit Badge Counselors (MBCs) for Scouts in any Scouting America Troop.

**Coding Standards and Best Practices**
- All code and documentation must follow the standards outlined in `.github/copilot-instructions.md`.
- All changes must include descriptive commit messages referencing the relevant GitHub issue number.
- Code must be modular, reusable, and use descriptive variable and function names.
- All new features and bug fixes must include corresponding tests.
- Documentation must be updated to reflect any changes in functionality.
- All new dependencies must be added to `requirements.txt` and installed in the active Python virtual environment.
- Database schema changes must be managed with change scripts and applied to the SQLite database.

## 2. Purpose
- Provide an efficient, local system for managing MBC assignments and workloads.
- Enable data-driven decision-making and reporting outside of Scoutbook.
- Simplify the process of preparing assignments for manual entry into Scoutbook.

## 3. Goals
- Track MBC assignments and workloads.
- Enable efficient assignment of MBCs to Scouts.
- Generate actionable reports.
- Streamline pre-Scoutbook assignment workflows.

## 4. Data Sources
### 4.1 Merit Badge In-Progress Report (CSV)
- Contains: Scouts currently working on merit badges and their assigned counselors.
- Fields: Scout info (with Member ID), merit badge, assigned MBC name (text).
- Challenges:
  - MBC names may not exactly match roster names.
  - No Member ID for MBCs; requires fuzzy matching to roster.

### 4.2 Troop Roster File (CSV)
- Contains: Adult and youth members in separate sections, different columns.
- Structure:
  - Index column (to be removed)
  - "ADULT MEMBERS" and "YOUTH MEMBERS" headers
  - Empty rows separate sections
- Processing:
  - Remove index column and section headers
  - Handle empty rows
  - Parse different columns for adults/youth

## 5. Technical Architecture
### 5.1 Core Technologies
- Python 3.12
- Virtual Environment for dependency management (must be created and activated before running scripts, tests, or commands)
- SQLite database
- Microsoft Excel libraries for export
- No authentication (local app)
- MCP server for Copilot integration of queries concerning Troop dataand for the creation of GitHub Issues using the appropriate YAML template as defined in the .github/ISSUE_TEMPLATE directory.
- GitHub Issues for work item management (issues must use the appropriate template)
- Automated test case generation for all GitHub issues

### 5.2 Key Components
- Data import and cleaning modules
- Fuzzy name matching algorithm
- Database schema for scouts, adults, and merit badge assignments
- Reporting and export functionality
- MCP server for Copilot integration

## 6. Future Enhancements
### 6.1 Web Application
- Browser-based UI for data viewing/editing
- Assignment interface
- Task list for Scoutbook entry
- MBC workload dashboard

### 6.2 Automation
- Playwright-based automation for downloading CSVs from Scoutbook
- Automated report generation
- Google account authentication for Scoutbook access

**Note:** No API access to Scoutbook; web scraping/automation will be required for future data sync.

## 7. Security and Privacy
- Never include passwords, API keys, or sensitive information in the codebase except in secure configuration files that are not committed to the repository.
- Never hard-code values that should be configurable.
- Never use global variables unless absolutely necessary.
- Never commit code that does not pass automated tests.
- Never include any PII or any other Troop data in the codebase, test cases, documentation, comments, or GitHub issues.
