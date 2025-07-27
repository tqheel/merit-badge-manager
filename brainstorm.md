# Scouting America Merit Badge Counselor Management Application

## Project Overview

### Purpose
As the Scoutmaster for Troop 212, I need a streamlined system to manage Merit Badge Counselor (MBC) assignments for Scouts in my unit. While [Scoutbook](https://scoutbook.scouting.org/) is the official tool for these assignments, it is cumbersome and slow. This application will provide an efficient reporting system to assess MBC workloads and make appropriate assignments outside of Scoutbook.

### Goals
- Track Merit Badge Counselor assignments and workloads
- Enable efficient assignment of MBCs to Scouts requesting merit badge work
- Generate reports for better decision-making
- Streamline the assignment process before manual entry into Scoutbook

## Data Sources

### Merit Badge In-Progress Report (CSV)
Contains records of Scouts currently working on merit badges and their assigned counselors.

**Data Structure:**
- Scout information with Member ID (matches BSA Number in roster)
- Merit badge being worked on
- Assigned MBC name (first and last name as text string)

**Data Challenges:**
- MBC names in this file may not exactly match the concatenated first/last names in the troop roster
- No Member ID provided for MBCs in this file
- Requires fuzzy matching logic to correlate MBCs between files

### Troop Roster File (CSV)
Contains separate sections for adult and youth members, each with different column structures.

**File Structure:**
- First column: Index column (to be removed during processing)
- Adult section: Begins with "ADULT MEMBERS" header
- Empty rows separate adult and youth sections
- Youth section: Begins with "YOUTH MEMBERS" header

**Data Processing Requirements:**
- Remove index column before processing
- Remove both "ADULT MEMBERS" and "YOUTH MEMBERS" header rows
- Handle empty rows between sections
- Parse different column structures for adults vs. youth

## Technical Architecture

### Core Technologies
- **Runtime:** Python 3.12
- **Dependency Management:** Virtual Environment
- **Database:** SQLite
- **Export:** Microsoft Excel libraries
- **Authentication:** None required (local application)
- **Integration:** MCP server to expose database and reports to Copilot for chat queries
- **GitHub for Work Item Management:** Generate issues using the appropriate GitHub Issues template.
- **Automated Test Case Generation:** Automatically generate test cases for all GitHub issues.

### Key Components
- Data import and cleaning modules
- Fuzzy name matching algorithm
- Database schema for scouts, adults, and merit badge assignments
- Reporting and export functionality
- MCP server for Copilot integration

## Future Enhancements

### Web Application
- Browser-based UI for viewing and editing data
- Assignment interface for making merit badge assignments
- Task list generation for manual entry into Scoutbook
- Dashboard for MBC workload visualization

### Automation
- Playwright-based automation for downloading CSV files from Scoutbook
- Automated report generation using saved Scoutbook reports
- Integration with Google account authentication for Scoutbook access

**Note:** API access to Scoutbook data is not available; web scraping/automation will be required for future data synchronization.