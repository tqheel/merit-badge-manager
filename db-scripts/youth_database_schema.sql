-- Merit Badge Manager - Youth Roster Database Schema
-- Created: 2025-07-31
-- Purpose: Create SQLite database schema for youth roster data import
-- Reference: GitHub Issue #12 - Youth roster database schema

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- =============================================================================
-- DROP EXISTING TABLES (if they exist) - for clean rebuild
-- =============================================================================

-- Drop tables in reverse dependency order to avoid foreign key constraint issues
DROP TABLE IF EXISTS scout_advancement_history;
DROP TABLE IF EXISTS scout_merit_badge_progress;
DROP TABLE IF EXISTS parent_guardians;
DROP TABLE IF EXISTS scout_positions;
DROP TABLE IF EXISTS scout_training;
DROP TABLE IF EXISTS scouts;

-- =============================================================================
-- CREATE TABLES
-- =============================================================================

-- Scouts Table (Primary table for youth member information)
CREATE TABLE scouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    bsa_number INTEGER UNIQUE NOT NULL,
    unit_number TEXT,
    rank TEXT, -- Scout, Tenderfoot, Second Class, First Class, Star, Life, Eagle
    date_joined DATE,
    date_of_birth DATE,
    age INTEGER,
    patrol_name TEXT,
    activity_status TEXT, -- Active, Inactive, Aged Out
    oa_info TEXT, -- Order of the Arrow membership info
    email TEXT,
    phone TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    positions_tenure TEXT, -- Raw tenure data for reference
    training_raw TEXT, -- Raw training data for reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scout Training Table (Training certifications and expiration dates)
CREATE TABLE scout_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    training_code TEXT NOT NULL,
    training_name TEXT NOT NULL,
    expiration_date TEXT, -- Some training "does not expire"
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE,
    UNIQUE(scout_id, training_code)
);

-- Scout Positions Table (Position history with tenure information and patrol assignments)
CREATE TABLE scout_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    position_title TEXT NOT NULL,
    patrol_name TEXT, -- Patrol assignment for this position
    tenure_info TEXT, -- e.g., "(5m 1d)", "(2y 5m 6d)"
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT 1,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE
);

-- Parent Guardians Table (Up to 4 parent/guardian contacts per Scout)
CREATE TABLE parent_guardians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    guardian_number INTEGER NOT NULL CHECK (guardian_number BETWEEN 1 AND 4),
    first_name TEXT,
    last_name TEXT,
    relationship TEXT, -- Parent, Guardian, Emergency Contact, etc.
    email TEXT,
    phone_home TEXT,
    phone_work TEXT,
    phone_cell TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    is_primary BOOLEAN DEFAULT 0,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE,
    UNIQUE(scout_id, guardian_number)
);

-- Scout Merit Badge Progress Table (Merit badge tracking and counselor assignments)
CREATE TABLE scout_merit_badge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    merit_badge_name TEXT NOT NULL,
    counselor_adult_id INTEGER, -- Reference to adults table for counselor assignment
    status TEXT DEFAULT 'Not Started', -- Not Started, In Progress, Completed, Approved
    date_started DATE,
    date_completed DATE,
    requirements_completed TEXT, -- JSON or pipe-separated list of completed requirements
    notes TEXT,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE,
    -- Note: counselor_adult_id references adults table but no FK constraint since it's in separate schema
    UNIQUE(scout_id, merit_badge_name)
);

-- Scout Advancement History Table (Rank progression tracking over time)
CREATE TABLE scout_advancement_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scout_id INTEGER NOT NULL,
    rank_name TEXT NOT NULL,
    date_awarded DATE NOT NULL,
    board_of_review_date DATE,
    scoutmaster_conference_date DATE,
    notes TEXT,
    FOREIGN KEY (scout_id) REFERENCES scouts(id) ON DELETE CASCADE
);

-- =============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

-- Primary lookup indexes for scouts table
CREATE INDEX idx_scouts_bsa_number ON scouts(bsa_number);
CREATE INDEX idx_scouts_name ON scouts(last_name, first_name);
CREATE INDEX idx_scouts_unit ON scouts(unit_number);
CREATE INDEX idx_scouts_rank ON scouts(rank);
CREATE INDEX idx_scouts_patrol ON scouts(patrol_name);
CREATE INDEX idx_scouts_activity_status ON scouts(activity_status);
CREATE INDEX idx_scouts_age ON scouts(age);

-- Training lookup indexes
CREATE INDEX idx_scout_training_scout_id ON scout_training(scout_id);
CREATE INDEX idx_scout_training_code ON scout_training(training_code);
CREATE INDEX idx_scout_training_expiration ON scout_training(expiration_date);

-- Position indexes
CREATE INDEX idx_scout_positions_scout_id ON scout_positions(scout_id);
CREATE INDEX idx_scout_positions_current ON scout_positions(is_current);
CREATE INDEX idx_scout_positions_title ON scout_positions(position_title);
CREATE INDEX idx_scout_positions_patrol ON scout_positions(patrol_name);

-- Parent/Guardian indexes
CREATE INDEX idx_parent_guardians_scout_id ON parent_guardians(scout_id);
CREATE INDEX idx_parent_guardians_primary ON parent_guardians(is_primary);
CREATE INDEX idx_parent_guardians_name ON parent_guardians(last_name, first_name);

-- Merit badge progress indexes
CREATE INDEX idx_scout_mb_progress_scout_id ON scout_merit_badge_progress(scout_id);
CREATE INDEX idx_scout_mb_progress_badge ON scout_merit_badge_progress(merit_badge_name);
CREATE INDEX idx_scout_mb_progress_counselor ON scout_merit_badge_progress(counselor_adult_id);
CREATE INDEX idx_scout_mb_progress_status ON scout_merit_badge_progress(status);

-- Advancement history indexes
CREATE INDEX idx_scout_advancement_scout_id ON scout_advancement_history(scout_id);
CREATE INDEX idx_scout_advancement_rank ON scout_advancement_history(rank_name);
CREATE INDEX idx_scout_advancement_date ON scout_advancement_history(date_awarded);

-- =============================================================================
-- CREATE TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- =============================================================================

-- Trigger to update the updated_at timestamp when scouts table is modified
CREATE TRIGGER update_scouts_timestamp 
    AFTER UPDATE ON scouts
    FOR EACH ROW
BEGIN
    UPDATE scouts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- =============================================================================
-- VALIDATION VIEWS (for data quality checks)
-- =============================================================================

-- View to identify scouts with missing required information
CREATE VIEW scouts_missing_data AS
SELECT 
    id,
    first_name,
    last_name,
    bsa_number,
    CASE WHEN rank IS NULL OR rank = '' THEN 'Missing Rank' END AS rank_issue,
    CASE WHEN unit_number IS NULL OR unit_number = '' THEN 'Missing Unit Number' END AS unit_issue,
    CASE WHEN date_joined IS NULL THEN 'Missing Join Date' END AS join_date_issue,
    CASE WHEN date_of_birth IS NULL THEN 'Missing Birth Date' END AS birth_date_issue,
    CASE WHEN patrol_name IS NULL OR patrol_name = '' THEN 'Missing Patrol' END AS patrol_issue
FROM scouts
WHERE 
    rank IS NULL OR rank = ''
    OR unit_number IS NULL OR unit_number = ''
    OR date_joined IS NULL
    OR date_of_birth IS NULL
    OR patrol_name IS NULL OR patrol_name = '';

-- View to show active scouts with current positions
CREATE VIEW active_scouts_with_positions AS
SELECT 
    s.first_name,
    s.last_name,
    s.bsa_number,
    s.rank,
    s.patrol_name,
    s.unit_number,
    s.activity_status,
    sp.position_title,
    sp.tenure_info
FROM scouts s
LEFT JOIN scout_positions sp ON s.id = sp.scout_id AND sp.is_current = 1
WHERE s.activity_status = 'Active'
ORDER BY s.last_name, s.first_name;

-- View to show merit badge progress summary
CREATE VIEW merit_badge_progress_summary AS
SELECT 
    mb.merit_badge_name,
    COUNT(*) as scout_count,
    COUNT(CASE WHEN mb.status = 'Completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN mb.status = 'In Progress' THEN 1 END) as in_progress_count,
    COUNT(CASE WHEN mb.status = 'Not Started' THEN 1 END) as not_started_count
FROM scout_merit_badge_progress mb
GROUP BY mb.merit_badge_name
ORDER BY scout_count DESC, mb.merit_badge_name;

-- View to show scouts needing merit badge counselors
CREATE VIEW scouts_needing_counselors AS
SELECT 
    s.first_name,
    s.last_name,
    s.bsa_number,
    s.rank,
    mb.merit_badge_name,
    mb.status,
    mb.date_started
FROM scouts s
JOIN scout_merit_badge_progress mb ON s.id = mb.scout_id
WHERE mb.counselor_adult_id IS NULL 
    AND mb.status IN ('Not Started', 'In Progress')
    AND s.activity_status = 'Active'
ORDER BY s.last_name, s.first_name, mb.merit_badge_name;

-- View to show advancement progress by rank
CREATE VIEW advancement_progress_by_rank AS
SELECT 
    rank,
    COUNT(*) as scout_count,
    COUNT(CASE WHEN activity_status = 'Active' THEN 1 END) as active_count,
    AVG(age) as average_age
FROM scouts
WHERE rank IS NOT NULL
GROUP BY rank
ORDER BY 
    CASE rank
        WHEN 'Scout' THEN 1
        WHEN 'Tenderfoot' THEN 2
        WHEN 'Second Class' THEN 3
        WHEN 'First Class' THEN 4
        WHEN 'Star' THEN 5
        WHEN 'Life' THEN 6
        WHEN 'Eagle' THEN 7
        ELSE 8
    END;

-- View to show primary parent contacts
CREATE VIEW primary_parent_contacts AS
SELECT 
    s.first_name as scout_first_name,
    s.last_name as scout_last_name,
    s.bsa_number,
    pg.first_name as parent_first_name,
    pg.last_name as parent_last_name,
    pg.relationship,
    pg.email,
    pg.phone_cell,
    pg.phone_home
FROM scouts s
JOIN parent_guardians pg ON s.id = pg.scout_id
WHERE pg.is_primary = 1
ORDER BY s.last_name, s.first_name;

-- View to show training expiration summary for scouts
CREATE VIEW scout_training_expiration_summary AS
SELECT 
    s.first_name,
    s.last_name,
    s.bsa_number,
    st.training_code,
    st.training_name,
    st.expiration_date,
    CASE 
        WHEN st.expiration_date = '(does not expire)' THEN 'Never Expires'
        WHEN st.expiration_date IS NULL THEN 'Unknown'
        WHEN DATE(SUBSTR(st.expiration_date, -10)) < DATE('now') THEN 'Expired'
        WHEN DATE(SUBSTR(st.expiration_date, -10)) <= DATE('now', '+30 days') THEN 'Expiring Soon'
        ELSE 'Current'
    END AS status
FROM scouts s
JOIN scout_training st ON s.id = st.scout_id
ORDER BY s.last_name, s.first_name, st.training_code;

-- View to show patrol assignments
CREATE VIEW patrol_assignments AS
SELECT 
    patrol_name,
    COUNT(*) as scout_count,
    GROUP_CONCAT(first_name || ' ' || last_name, ', ') as scouts,
    COUNT(CASE WHEN activity_status = 'Active' THEN 1 END) as active_scouts
FROM scouts
WHERE patrol_name IS NOT NULL AND patrol_name != ''
GROUP BY patrol_name
ORDER BY active_scouts DESC, patrol_name;

-- =============================================================================
-- SAMPLE DATA VALIDATION QUERIES (commented for reference)
-- =============================================================================

/*
-- Check for duplicate BSA numbers
SELECT bsa_number, COUNT(*) as count 
FROM scouts 
GROUP BY bsa_number 
HAVING COUNT(*) > 1;

-- Check for scouts without any training
SELECT s.first_name, s.last_name, s.bsa_number
FROM scouts s
LEFT JOIN scout_training st ON s.id = st.scout_id
WHERE st.scout_id IS NULL AND s.activity_status = 'Active';

-- Check for scouts without parent/guardian contacts
SELECT s.first_name, s.last_name, s.bsa_number
FROM scouts s
LEFT JOIN parent_guardians pg ON s.id = pg.scout_id
WHERE pg.scout_id IS NULL;

-- Check for active scouts without current positions
SELECT s.first_name, s.last_name, s.bsa_number, s.patrol_name
FROM scouts s
LEFT JOIN scout_positions sp ON s.id = sp.scout_id AND sp.is_current = 1
WHERE sp.scout_id IS NULL AND s.activity_status = 'Active';

-- Check advancement progression anomalies
SELECT s.first_name, s.last_name, s.bsa_number, s.rank, s.age
FROM scouts s
WHERE s.activity_status = 'Active'
    AND ((s.rank = 'Eagle' AND s.age < 14) 
         OR (s.rank = 'Scout' AND s.age > 16));
*/

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
-- VALUES ('1.0.0', 'Initial youth roster schema creation');

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

SELECT 'Youth roster database schema created successfully!' as message;
SELECT 'Tables created: scouts, scout_training, scout_positions, parent_guardians, scout_merit_badge_progress, scout_advancement_history' as tables_info;
SELECT 'Indexes created for optimal query performance' as indexes_info;
SELECT 'Views created for data validation and reporting' as views_info;