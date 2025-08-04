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
