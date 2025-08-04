-- Merit Badge Manager - Merit Badge Progress Database Schema
-- Created: 2024-08-04
-- Purpose: Create SQLite database schema for Merit Badge In-Progress Report import
-- Reference: GitHub Issue #30 - MB In Progress import and db schema

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- =============================================================================
-- DROP EXISTING TABLES (if they exist) - for clean rebuild
-- =============================================================================

-- Drop tables in reverse dependency order to avoid foreign key constraint issues
DROP TABLE IF EXISTS merit_badge_requirements;
DROP TABLE IF EXISTS mbc_manual_matches;
DROP TABLE IF EXISTS mbc_name_mappings;
DROP TABLE IF EXISTS unmatched_mbc_names;
DROP TABLE IF EXISTS merit_badge_progress;

-- =============================================================================
-- CREATE TABLES
-- =============================================================================

-- Merit Badge Progress Table (Core table for tracking scout merit badge progress)
CREATE TABLE merit_badge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_bsa_number TEXT NOT NULL,
    scout_first_name TEXT NOT NULL,
    scout_last_name TEXT NOT NULL,
    scout_rank TEXT,
    scout_location TEXT,
    merit_badge_name TEXT NOT NULL,
    merit_badge_year TEXT, -- Extracted from merit badge name (e.g., "Fire Safety (2025)" -> "2025")
    mbc_name_raw TEXT, -- Raw MBC name from report (may be empty)
    mbc_adult_id INTEGER, -- Matched adult roster ID
    mbc_match_confidence REAL, -- Fuzzy match confidence score (0.0 to 1.0)
    date_completed TEXT,
    requirements_raw TEXT, -- Raw requirements string from report
    requirements_parsed TEXT, -- JSON array of parsed requirements
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to scouts table when available (soft reference)
    scout_id INTEGER,
    
    -- Note: No FK constraint to adults table since it's in separate schema
    -- Foreign key relationships handled at application level
    
    -- Unique constraint per scout per merit badge
    UNIQUE(scout_bsa_number, merit_badge_name)
);

-- Unmatched MBC Names Table (Track counselor names that need manual resolution)
CREATE TABLE unmatched_mbc_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mbc_name_raw TEXT UNIQUE NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    potential_matches TEXT, -- JSON array of potential adult roster matches
    manual_match_adult_id INTEGER, -- Manually assigned match
    is_resolved BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
    -- Note: No FK constraint to adults table since it's in separate schema
);

-- MBC Name Mapping Table (Store fuzzy match results and manual overrides)
CREATE TABLE mbc_name_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name TEXT NOT NULL,
    adult_id INTEGER NOT NULL,
    confidence_score REAL NOT NULL,
    mapping_type TEXT NOT NULL, -- 'exact', 'fuzzy', 'manual'
    created_by TEXT, -- 'system' or user identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Note: No FK constraint to adults table since it's in separate schema
    UNIQUE(raw_name, adult_id)
);

-- MBC Manual Matches Table (Track manual matching decisions with audit trail)
CREATE TABLE mbc_manual_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unmatched_mbc_name TEXT NOT NULL,
    matched_adult_id INTEGER, -- NULL if marked as invalid/skip
    match_action TEXT NOT NULL, -- 'matched', 'skipped', 'marked_invalid', 'create_new', 'undone'
    confidence_score REAL, -- User-assigned or calculated confidence
    user_name TEXT NOT NULL, -- User who made the decision
    notes TEXT, -- Optional notes about the decision
    original_match_id INTEGER, -- Reference to previous match if undoing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Note: No FK constraint to adults or unmatched_mbc_names since they're across schemas
    -- application-level referential integrity is maintained
    
    -- Unique constraint to prevent duplicate active decisions
    UNIQUE(unmatched_mbc_name, match_action) 
    -- This allows multiple entries for the same name if actions differ (e.g., match then undo)
);

-- Merit Badge Requirements Tracking Table (Parse complex requirements)
CREATE TABLE merit_badge_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    progress_id INTEGER NOT NULL,
    requirement_number TEXT NOT NULL,
    requirement_type TEXT, -- 'individual', 'choice', 'group'
    is_completed BOOLEAN DEFAULT 1,
    choice_group TEXT, -- For "(1 of 7a, 7b, 7c)" requirements
    notes TEXT,
    
    FOREIGN KEY (progress_id) REFERENCES merit_badge_progress(id) ON DELETE CASCADE,
    UNIQUE(progress_id, requirement_number)
);

-- =============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

-- Primary lookup indexes for merit_badge_progress table
CREATE INDEX idx_mb_progress_scout_bsa ON merit_badge_progress(scout_bsa_number);
CREATE INDEX idx_mb_progress_scout_name ON merit_badge_progress(scout_last_name, scout_first_name);
CREATE INDEX idx_mb_progress_badge ON merit_badge_progress(merit_badge_name);
CREATE INDEX idx_mb_progress_mbc_raw ON merit_badge_progress(mbc_name_raw);
CREATE INDEX idx_mb_progress_mbc_id ON merit_badge_progress(mbc_adult_id);
CREATE INDEX idx_mb_progress_scout_id ON merit_badge_progress(scout_id);
CREATE INDEX idx_mb_progress_import_date ON merit_badge_progress(import_date);

-- MBC matching indexes
CREATE INDEX idx_unmatched_mbc_name ON unmatched_mbc_names(mbc_name_raw);
CREATE INDEX idx_unmatched_mbc_resolved ON unmatched_mbc_names(is_resolved);
CREATE INDEX idx_mbc_mappings_raw_name ON mbc_name_mappings(raw_name);
CREATE INDEX idx_mbc_mappings_adult_id ON mbc_name_mappings(adult_id);
CREATE INDEX idx_mbc_mappings_confidence ON mbc_name_mappings(confidence_score);

-- Manual matches indexes
CREATE INDEX idx_manual_matches_name ON mbc_manual_matches(unmatched_mbc_name);
CREATE INDEX idx_manual_matches_adult_id ON mbc_manual_matches(matched_adult_id);
CREATE INDEX idx_manual_matches_action ON mbc_manual_matches(match_action);
CREATE INDEX idx_manual_matches_user ON mbc_manual_matches(user_name);
CREATE INDEX idx_manual_matches_created ON mbc_manual_matches(created_at);

-- Requirements indexes
CREATE INDEX idx_mb_requirements_progress_id ON merit_badge_requirements(progress_id);
CREATE INDEX idx_mb_requirements_number ON merit_badge_requirements(requirement_number);
CREATE INDEX idx_mb_requirements_type ON merit_badge_requirements(requirement_type);

-- =============================================================================
-- CREATE TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- =============================================================================

-- Trigger to update the last_updated timestamp when merit_badge_progress table is modified
CREATE TRIGGER update_mb_progress_timestamp 
    AFTER UPDATE ON merit_badge_progress
    FOR EACH ROW
BEGIN
    UPDATE merit_badge_progress SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to update the updated_at timestamp when unmatched_mbc_names table is modified
CREATE TRIGGER update_unmatched_mbc_timestamp 
    AFTER UPDATE ON unmatched_mbc_names
    FOR EACH ROW
BEGIN
    UPDATE unmatched_mbc_names SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- =============================================================================
-- DATA INTEGRATION VIEWS
-- =============================================================================

-- Drop existing views if they exist to ensure clean recreation
DROP VIEW IF EXISTS merit_badge_status_view;
DROP VIEW IF EXISTS unmatched_mbc_assignments;
DROP VIEW IF EXISTS scouts_available_for_mbc_assignment;
DROP VIEW IF EXISTS mbc_manual_matches_summary;

-- Comprehensive Merit Badge Status View
-- Note: This view uses LEFT JOINs since foreign key constraints cross schema boundaries
CREATE VIEW merit_badge_status_view AS
SELECT 
    mbp.id,
    mbp.scout_bsa_number,
    mbp.scout_first_name,
    mbp.scout_last_name,
    mbp.scout_rank,
    mbp.merit_badge_name,
    mbp.merit_badge_year,
    mbp.mbc_name_raw,
    -- MBC information would be joined from adults table in application logic
    mbp.mbc_match_confidence,
    CASE 
        WHEN mbp.mbc_adult_id IS NOT NULL THEN 'Matched'
        WHEN mbp.mbc_name_raw != '' AND mbp.mbc_name_raw IS NOT NULL THEN 'Unmatched'
        ELSE 'No Assignment'
    END AS assignment_status,
    mbp.requirements_raw,
    COUNT(mbr.id) AS requirements_completed_count,
    mbp.date_completed,
    mbp.scout_location,
    mbp.import_date,
    mbp.last_updated
FROM merit_badge_progress mbp
LEFT JOIN merit_badge_requirements mbr ON mbp.id = mbr.progress_id
GROUP BY mbp.id;

-- Unmatched MBC Assignments View
CREATE VIEW unmatched_mbc_assignments AS
SELECT 
    mbp.mbc_name_raw,
    COUNT(*) AS assignment_count,
    GROUP_CONCAT(DISTINCT mbp.merit_badge_name) AS merit_badges,
    GROUP_CONCAT(DISTINCT mbp.scout_first_name || ' ' || mbp.scout_last_name) AS scouts,
    umn.potential_matches,
    umn.manual_match_adult_id,
    umn.is_resolved,
    umn.notes,
    umn.created_at,
    umn.updated_at,
    -- Manual match status information
    CASE 
        WHEN mmm.match_action = 'matched' THEN 'Manually Matched'
        WHEN mmm.match_action = 'skipped' THEN 'Skipped'
        WHEN mmm.match_action = 'marked_invalid' THEN 'Marked Invalid'
        WHEN mmm.match_action = 'create_new' THEN 'New Adult Needed'
        ELSE 'Unresolved'
    END as manual_match_status,
    mmm.user_name as matched_by,
    mmm.created_at as manual_match_date
FROM merit_badge_progress mbp
LEFT JOIN unmatched_mbc_names umn ON mbp.mbc_name_raw = umn.mbc_name_raw
LEFT JOIN (
    -- Get the most recent manual match decision for each name
    SELECT unmatched_mbc_name, match_action, user_name, created_at, matched_adult_id,
           ROW_NUMBER() OVER (PARTITION BY unmatched_mbc_name ORDER BY created_at DESC) as rn
    FROM mbc_manual_matches
    WHERE match_action != 'undone'
) mmm ON mbp.mbc_name_raw = mmm.unmatched_mbc_name AND mmm.rn = 1
WHERE mbp.mbc_name_raw != '' 
  AND mbp.mbc_name_raw IS NOT NULL
  AND mbp.mbc_adult_id IS NULL
GROUP BY mbp.mbc_name_raw
ORDER BY assignment_count DESC;

-- Scouts Available for MBC Assignment View
CREATE VIEW scouts_available_for_mbc_assignment AS
SELECT 
    mbp.scout_bsa_number,
    mbp.scout_first_name,
    mbp.scout_last_name,
    mbp.scout_rank,
    mbp.merit_badge_name,
    mbp.merit_badge_year,
    mbp.scout_location,
    -- Available counselors would be calculated in application logic from adults table
    mbp.import_date,
    JULIANDAY('now') - JULIANDAY(mbp.import_date) AS days_since_started,
    mbp.requirements_raw,
    COUNT(mbr.id) AS requirements_completed_count
FROM merit_badge_progress mbp
LEFT JOIN merit_badge_requirements mbr ON mbp.id = mbr.progress_id
WHERE (mbp.mbc_name_raw = '' OR mbp.mbc_name_raw IS NULL)
  OR mbp.mbc_adult_id IS NULL
GROUP BY mbp.id
ORDER BY mbp.scout_last_name, mbp.scout_first_name, mbp.merit_badge_name;

-- MBC Manual Matches Summary View
-- Shows statistics about manual matching decisions and user activity
CREATE VIEW mbc_manual_matches_summary AS
SELECT 
    -- Overall statistics
    COUNT(*) as total_manual_decisions,
    COUNT(CASE WHEN match_action = 'matched' THEN 1 END) as matched_count,
    COUNT(CASE WHEN match_action = 'skipped' THEN 1 END) as skipped_count,
    COUNT(CASE WHEN match_action = 'marked_invalid' THEN 1 END) as invalid_count,
    COUNT(CASE WHEN match_action = 'create_new' THEN 1 END) as create_new_count,
    COUNT(CASE WHEN match_action = 'undone' THEN 1 END) as undone_count,
    
    -- User activity
    user_name,
    MIN(created_at) as first_decision,
    MAX(created_at) as last_decision,
    
    -- Unique names processed
    COUNT(DISTINCT unmatched_mbc_name) as unique_names_processed
    
FROM mbc_manual_matches
GROUP BY user_name
ORDER BY total_manual_decisions DESC, user_name;

-- =============================================================================
-- VALIDATION VIEWS (for data quality checks)
-- =============================================================================

-- Drop existing validation views if they exist
DROP VIEW IF EXISTS mb_progress_missing_data;
DROP VIEW IF EXISTS mb_progress_summary;
DROP VIEW IF EXISTS mb_requirements_summary;

-- View to identify merit badge progress entries with missing required information
CREATE VIEW mb_progress_missing_data AS
SELECT 
    id,
    scout_bsa_number,
    scout_first_name,
    scout_last_name,
    merit_badge_name,
    CASE WHEN scout_rank IS NULL OR scout_rank = '' THEN 'Missing Scout Rank' END AS rank_issue,
    CASE WHEN merit_badge_year IS NULL OR merit_badge_year = '' THEN 'Missing Merit Badge Year' END AS year_issue,
    CASE WHEN scout_location IS NULL OR scout_location = '' THEN 'Missing Scout Location' END AS location_issue,
    CASE WHEN requirements_raw IS NULL OR requirements_raw = '' THEN 'Missing Requirements Data' END AS requirements_issue
FROM merit_badge_progress
WHERE 
    scout_rank IS NULL OR scout_rank = ''
    OR merit_badge_year IS NULL OR merit_badge_year = ''
    OR scout_location IS NULL OR scout_location = ''
    OR requirements_raw IS NULL OR requirements_raw = '';

-- Merit Badge Progress Summary View
CREATE VIEW mb_progress_summary AS
SELECT 
    merit_badge_name,
    COUNT(*) AS total_scouts,
    COUNT(CASE WHEN mbc_adult_id IS NOT NULL THEN 1 END) AS assigned_counselors,
    COUNT(CASE WHEN mbc_name_raw != '' AND mbc_name_raw IS NOT NULL AND mbc_adult_id IS NULL THEN 1 END) AS unmatched_counselors,
    COUNT(CASE WHEN (mbc_name_raw = '' OR mbc_name_raw IS NULL) AND mbc_adult_id IS NULL THEN 1 END) AS no_counselor_assigned,
    COUNT(CASE WHEN date_completed IS NOT NULL AND date_completed != '' THEN 1 END) AS completed_count,
    merit_badge_year
FROM merit_badge_progress
GROUP BY merit_badge_name, merit_badge_year
ORDER BY total_scouts DESC, merit_badge_name;

-- Merit Badge Requirements Summary View
CREATE VIEW mb_requirements_summary AS
SELECT 
    mbp.merit_badge_name,
    COUNT(DISTINCT mbp.id) AS scouts_working,
    AVG(CAST(req_counts.requirement_count AS REAL)) AS avg_requirements_completed,
    MAX(req_counts.requirement_count) AS max_requirements_completed,
    MIN(req_counts.requirement_count) AS min_requirements_completed
FROM merit_badge_progress mbp
LEFT JOIN (
    SELECT 
        progress_id,
        COUNT(*) AS requirement_count
    FROM merit_badge_requirements
    GROUP BY progress_id
) req_counts ON mbp.id = req_counts.progress_id
GROUP BY mbp.merit_badge_name
ORDER BY scouts_working DESC, mbp.merit_badge_name;

-- =============================================================================
-- SCOUT-MBC ASSIGNMENT AND WORKLOAD VIEWS
-- =============================================================================

-- Scout-to-MBC Assignment View
-- Shows each scout and their assigned MBC for merit badge progress tracking
CREATE VIEW IF NOT EXISTS scout_mbc_assignments AS
SELECT 
    -- Scout Information
    COALESCE(s.first_name, mbp.scout_first_name) as scout_first_name,
    COALESCE(s.last_name, mbp.scout_last_name) as scout_last_name,
    COALESCE(s.bsa_number, CAST(mbp.scout_bsa_number AS INTEGER)) as scout_bsa_number,
    COALESCE(s.rank, mbp.scout_rank) as scout_rank,
    s.patrol_name,
    
    -- Merit Badge Information
    mbp.merit_badge_name,
    mbp.merit_badge_year,
    mbp.date_completed,
    
    -- MBC Assignment Information
    CASE 
        WHEN mbp.mbc_adult_id IS NOT NULL THEN 
            a.first_name || ' ' || a.last_name
        ELSE 
            'No MBC Assigned'
    END as mbc_name,
    mbp.mbc_name_raw as original_mbc_name,
    mbp.mbc_match_confidence,
    
    -- Status Information
    CASE 
        WHEN mbp.date_completed IS NOT NULL AND mbp.date_completed != '' THEN 'Completed'
        WHEN mbp.mbc_adult_id IS NOT NULL THEN 'In Progress - MBC Assigned'
        ELSE 'In Progress - Needs MBC'
    END as assignment_status,
    
    -- Progress Information
    CASE 
        WHEN mbp.requirements_raw = 'No Requirements Complete, ' THEN 'Not Started'
        WHEN mbp.requirements_raw IS NULL OR mbp.requirements_raw = '' THEN 'Unknown'
        ELSE 'Requirements in Progress'
    END as progress_status,
    
    -- IDs for joining
    mbp.id as merit_badge_progress_id,
    s.id as scout_id,
    mbp.mbc_adult_id,
    mbp.import_date,
    mbp.last_updated

FROM merit_badge_progress mbp
LEFT JOIN scouts s ON mbp.scout_id = s.id
LEFT JOIN adults a ON mbp.mbc_adult_id = a.id

ORDER BY 
    scout_last_name, 
    scout_first_name, 
    merit_badge_name;

-- MBC Workload View
-- Shows each MBC and how many scouts are currently assigned to them
CREATE VIEW IF NOT EXISTS mbc_workload_summary AS
SELECT 
    -- MBC Information
    a.first_name || ' ' || a.last_name as mbc_name,
    a.first_name,
    a.last_name,
    a.email,
    a.bsa_number as mbc_bsa_number,
    
    -- Assignment Counts
    COUNT(mbp.id) as total_assignments,
    COUNT(CASE WHEN mbp.date_completed IS NULL OR mbp.date_completed = '' THEN 1 END) as active_assignments,
    COUNT(CASE WHEN mbp.date_completed IS NOT NULL AND mbp.date_completed != '' THEN 1 END) as completed_assignments,
    
    -- Progress Status Breakdown
    COUNT(CASE WHEN mbp.requirements_raw = 'No Requirements Complete, ' THEN 1 END) as scouts_not_started,
    COUNT(CASE WHEN mbp.requirements_raw IS NOT NULL 
                AND mbp.requirements_raw != '' 
                AND mbp.requirements_raw != 'No Requirements Complete, ' THEN 1 END) as scouts_in_progress,
    
    -- Unique Statistics
    COUNT(DISTINCT mbp.scout_id) as unique_scouts_assigned,
    COUNT(DISTINCT mbp.merit_badge_name) as unique_merit_badges,
    
    -- Recent Activity
    MAX(mbp.last_updated) as last_assignment_update,
    MIN(mbp.import_date) as first_assignment_date,
    
    -- Merit Badge List (for detailed view)
    GROUP_CONCAT(DISTINCT mbp.merit_badge_name) as merit_badges_counseling

FROM adults a
INNER JOIN merit_badge_progress mbp ON a.id = mbp.mbc_adult_id

GROUP BY a.id, a.first_name, a.last_name, a.email, a.bsa_number

ORDER BY total_assignments DESC, mbc_name;

-- =============================================================================
-- SCHEMA INFORMATION
-- =============================================================================

-- Insert schema metadata (if metadata table exists)
-- CREATE TABLE IF NOT EXISTS schema_versions (
--     version TEXT PRIMARY KEY,
--     applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     description TEXT
-- );
-- 
-- INSERT OR REPLACE INTO schema_versions (version, description) 
-- VALUES ('1.1.0', 'Merit Badge Progress schema creation');

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

SELECT 'Merit Badge Progress database schema created successfully!' as message;
SELECT 'Tables created: merit_badge_progress, unmatched_mbc_names, mbc_name_mappings, merit_badge_requirements' as tables_info;
SELECT 'Indexes created for optimal query performance' as indexes_info;
SELECT 'Views created for data integration and reporting' as views_info;