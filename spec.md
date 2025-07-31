
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
- YAML files for GitHub issues must use block literal syntax (`|`) for multi-line content to prevent truncation.

## 2. Purpose
- Provide an efficient, local system for managing MBC assignments and workloads.
- Enable comprehensive Scout tracking with merit badge progress management.
- Support Scout-to-counselor assignment workflows with parent communication.
- Enable data-driven decision-making and reporting outside of Scoutbook.
- Simplify the process of preparing assignments for manual entry into Scoutbook.

## 3. Goals
- Track MBC assignments and workloads.
- Manage comprehensive Scout roster with advancement tracking.
- Support Scout merit badge progress with counselor assignments.
- Enable efficient assignment of MBCs to Scouts.
- Provide parent/guardian communication integration.
- Generate actionable reports for both adult and youth data.
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
  - Extract Scout training data (pipe-separated with complex formatting)
  - Process Scout position tenure information with patrol assignments
  - Handle parent/guardian data (up to 4 contacts per Scout)
  - Manage rank progression and advancement tracking

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
- Data import and cleaning modules for both adult and youth rosters
- Fuzzy name matching algorithm for Scout-to-counselor assignments
- Comprehensive database schema for scouts, adults, and merit badge assignments
- Database testing infrastructure with fake data generation for integrated systems
- Scout advancement tracking and rank progression management
- Parent/guardian communication system with contact management
- Reporting and export functionality for operational insights
- MCP server for Copilot integration

### 5.3 Database Management
- SQLite database with comprehensive adult and youth roster schemas
- Automated schema creation and validation for both systems
- Test database generation with realistic fake data for adult-youth integration
- Comprehensive test suite for database functionality and cross-system interactions
- Performance optimization with 36 indexes and 12 validation views
- Scout-to-counselor assignment system with merit badge progress tracking
- Parent/guardian contact management with communication features

## 6. Future Enhancements
### 6.1 Web Application
- Browser-based UI for data viewing/editing of both adult and youth rosters
- Assignment interface for Scout-to-counselor matching
- Task list for Scoutbook entry with integrated assignment tracking
- MBC workload dashboard with Scout progress visualization
- Parent communication portal for merit badge updates
- Scout advancement tracking and rank progression interface

### 6.2 Automation
- Playwright-based automation for downloading CSVs from Scoutbook (both adult and youth rosters)
- Automated report generation for merit badge assignments and Scout progress
- Google account authentication for Scoutbook access
- Automated parent notifications for merit badge milestones

**Note:** No API access to Scoutbook; web scraping/automation will be required for future data sync.

## 7. Security and Privacy
- Never include passwords, API keys, or sensitive information in the codebase except in secure configuration files that are not committed to the repository.
- Never hard-code values that should be configurable.
- Never use global variables unless absolutely necessary.
- Never commit code that does not pass automated tests.
- Never include any PII or any other Troop data in the codebase, test cases, documentation, comments, or GitHub issues.
