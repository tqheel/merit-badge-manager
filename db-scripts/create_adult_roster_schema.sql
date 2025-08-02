-- Merit Badge Manager - Adult Roster Database Schema
-- Created: 2025-07-28
-- Purpose: Create SQLite database schema for adult roster data import
-- Reference: docs/create-db-schema-for-adult-roster.md

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- =============================================================================
-- DROP EXISTING TABLES (if they exist) - for clean rebuild
-- =============================================================================

-- Drop tables in reverse dependency order to avoid foreign key constraint issues
DROP TABLE IF EXISTS adult_positions;
DROP TABLE IF EXISTS adult_merit_badges;
DROP TABLE IF EXISTS adult_training;
DROP TABLE IF EXISTS adults;

-- =============================================================================
-- CREATE TABLES
-- =============================================================================

-- Adults Table (Primary table for adult member information)
CREATE TABLE adults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    age_category TEXT,
    date_joined DATE,
    bsa_number INTEGER UNIQUE NOT NULL,
    unit_number TEXT,
    oa_info TEXT,
    health_form_status TEXT,
    swim_class TEXT,
    swim_class_date DATE,
    positions_tenure TEXT, -- Raw tenure data for reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adult Training Table (Training certifications and expiration dates)
CREATE TABLE adult_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adult_id INTEGER NOT NULL,
    training_code TEXT NOT NULL,
    training_name TEXT NOT NULL,
    expiration_date TEXT, -- Some training "does not expire"
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE,
    UNIQUE(adult_id, training_code)
);

-- Adult Counselor Qualifications Table (Merit badges that adults are qualified to counsel for)
-- Note: This represents merit badges that counselors OFFER/are qualified for, 
-- NOT merit badges assigned TO adults. Scout-to-counselor assignments are tracked separately.
CREATE TABLE adult_merit_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adult_id INTEGER NOT NULL,
    merit_badge_name TEXT NOT NULL, -- Merit badge the adult is qualified to counsel for
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE,
    UNIQUE(adult_id, merit_badge_name)
);

-- Adult Positions Table (Position history with tenure information)
CREATE TABLE adult_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adult_id INTEGER NOT NULL,
    position_title TEXT NOT NULL,
    tenure_info TEXT, -- e.g., "(4m 16d)", "(7y 1m 26d)"
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT 1,
    FOREIGN KEY (adult_id) REFERENCES adults(id) ON DELETE CASCADE
);

-- =============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

-- Primary lookup indexes for adults table
CREATE INDEX idx_adults_bsa_number ON adults(bsa_number);
CREATE INDEX idx_adults_name ON adults(last_name, first_name);
CREATE INDEX idx_adults_email ON adults(email);
CREATE INDEX idx_adults_unit ON adults(unit_number);

-- Training lookup indexes
CREATE INDEX idx_adult_training_adult_id ON adult_training(adult_id);
CREATE INDEX idx_adult_training_code ON adult_training(training_code);
CREATE INDEX idx_adult_training_expiration ON adult_training(expiration_date);

-- Counselor qualification indexes
CREATE INDEX idx_adult_merit_badges_adult_id ON adult_merit_badges(adult_id);
CREATE INDEX idx_adult_merit_badges_name ON adult_merit_badges(merit_badge_name);

-- Position indexes
CREATE INDEX idx_adult_positions_adult_id ON adult_positions(adult_id);
CREATE INDEX idx_adult_positions_current ON adult_positions(is_current);
CREATE INDEX idx_adult_positions_title ON adult_positions(position_title);

-- =============================================================================
-- CREATE TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- =============================================================================

-- Trigger to update the updated_at timestamp when adults table is modified
CREATE TRIGGER update_adults_timestamp 
    AFTER UPDATE ON adults
    FOR EACH ROW
BEGIN
    UPDATE adults SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- =============================================================================
-- VALIDATION VIEWS (for data quality checks)
-- =============================================================================

-- Drop existing views if they exist to ensure clean recreation
DROP VIEW IF EXISTS adults_missing_data;
DROP VIEW IF EXISTS training_expiration_summary;
DROP VIEW IF EXISTS merit_badge_counselors;
DROP VIEW IF EXISTS current_positions;

-- View to identify adults with missing required information
CREATE VIEW adults_missing_data AS
SELECT 
    id,
    first_name,
    last_name,
    bsa_number,
    CASE WHEN email IS NULL OR email = '' THEN 'Missing Email' END AS email_issue,
    CASE WHEN email = 'changeyouremail@scoutbook.com' THEN 'Placeholder Email' END AS email_placeholder,
    CASE WHEN date_joined IS NULL THEN 'Missing Join Date' END AS join_date_issue,
    CASE WHEN unit_number IS NULL OR unit_number = '' THEN 'Missing Unit Number' END AS unit_issue
FROM adults
WHERE 
    email IS NULL OR email = '' OR email = 'changeyouremail@scoutbook.com'
    OR date_joined IS NULL
    OR unit_number IS NULL OR unit_number = '';

-- View to show training expiration summary
CREATE VIEW training_expiration_summary AS
SELECT 
    a.first_name,
    a.last_name,
    a.bsa_number,
    t.training_code,
    t.training_name,
    t.expiration_date,
    CASE 
        WHEN t.expiration_date = '(does not expire)' THEN 'Never Expires'
        WHEN t.expiration_date IS NULL THEN 'Unknown'
        WHEN DATE(SUBSTR(t.expiration_date, -10)) < DATE('now') THEN 'Expired'
        WHEN DATE(SUBSTR(t.expiration_date, -10)) <= DATE('now', '+30 days') THEN 'Expiring Soon'
        ELSE 'Current'
    END AS status
FROM adults a
JOIN adult_training t ON a.id = t.adult_id
ORDER BY a.last_name, a.first_name, t.training_code;

-- View to show available merit badge counselors by qualification
-- Shows which merit badges have qualified counselors available to offer them
CREATE VIEW merit_badge_counselors AS
SELECT 
    mb.merit_badge_name,
    COUNT(*) as counselor_count,
    GROUP_CONCAT(a.first_name || ' ' || a.last_name, ', ') as counselors
FROM adult_merit_badges mb
JOIN adults a ON mb.adult_id = a.id
GROUP BY mb.merit_badge_name
ORDER BY mb.merit_badge_name;

-- View to show current positions
CREATE VIEW current_positions AS
SELECT 
    a.first_name,
    a.last_name,
    a.bsa_number,
    p.position_title,
    p.tenure_info,
    p.start_date,
    p.end_date
FROM adults a
JOIN adult_positions p ON a.id = p.adult_id
WHERE p.is_current = 1
ORDER BY a.last_name, a.first_name;

-- =============================================================================
-- SAMPLE DATA VALIDATION QUERIES (commented for reference)
-- =============================================================================

/*
-- Check for duplicate BSA numbers
SELECT bsa_number, COUNT(*) as count 
FROM adults 
GROUP BY bsa_number 
HAVING COUNT(*) > 1;

-- Check for adults without any training
SELECT a.first_name, a.last_name, a.bsa_number
FROM adults a
LEFT JOIN adult_training t ON a.id = t.adult_id
WHERE t.adult_id IS NULL;

-- Check for adults without any merit badge counselor qualifications
SELECT a.first_name, a.last_name, a.bsa_number
FROM adults a
LEFT JOIN adult_merit_badges mb ON a.id = mb.adult_id
WHERE mb.adult_id IS NULL;

-- Check for expired training
SELECT * FROM training_expiration_summary 
WHERE status = 'Expired' OR status = 'Expiring Soon';
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
-- VALUES ('1.0.0', 'Initial adult roster schema creation');

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

SELECT 'Adult roster database schema created successfully!' as message;
SELECT 'Tables created: adults, adult_training, adult_merit_badges (counselor qualifications), adult_positions' as tables_info;
SELECT 'Indexes created for optimal query performance' as indexes_info;
SELECT 'Views created for data validation and reporting' as views_info;
