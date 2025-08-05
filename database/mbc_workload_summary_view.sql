-- MBC Workload View
-- Shows ALL qualified MBCs and how many scouts are currently assigned to them
-- Includes MBCs with zero assignments for workload balancing purposes
CREATE VIEW IF NOT EXISTS mbc_workload_summary AS
SELECT 
    -- MBC Information
    a.first_name || ' ' || a.last_name as mbc_name,
    a.id as mbc_adult_id,
    a.first_name,
    a.last_name,
    a.email,
    a.bsa_number as mbc_bsa_number,
    
    -- Assignment Counts (will be 0 for MBCs with no assignments)
    COUNT(CASE WHEN mbp.id IS NOT NULL THEN 1 END) as total_assignments,
    COUNT(CASE WHEN mbp.id IS NOT NULL AND (mbp.date_completed IS NULL OR mbp.date_completed = '') THEN 1 END) as active_assignments,
    COUNT(CASE WHEN mbp.id IS NOT NULL AND mbp.date_completed IS NOT NULL AND mbp.date_completed != '' THEN 1 END) as completed_assignments,
    
    -- Progress Status Breakdown (will be 0 for MBCs with no assignments)
    COUNT(CASE WHEN mbp.id IS NOT NULL AND mbp.requirements_raw = 'No Requirements Complete, ' THEN 1 END) as scouts_not_started,
    COUNT(CASE WHEN mbp.id IS NOT NULL AND mbp.requirements_raw IS NOT NULL 
                AND mbp.requirements_raw != '' 
                AND mbp.requirements_raw != 'No Requirements Complete, ' THEN 1 END) as scouts_in_progress,
    
    -- Unique Statistics (will be 0 for MBCs with no assignments)
    COUNT(DISTINCT CASE WHEN mbp.scout_id IS NOT NULL THEN mbp.scout_id END) as unique_scouts_assigned,
    COUNT(DISTINCT CASE WHEN mbp.merit_badge_name IS NOT NULL THEN mbp.merit_badge_name END) as unique_merit_badges,
    
    -- Recent Activity (will be NULL for MBCs with no assignments)
    MAX(mbp.last_updated) as last_assignment_update,
    MIN(mbp.import_date) as first_assignment_date,
    
    -- Merit Badge List (for detailed view)
    -- For MBCs with assignments: shows assigned merit badges
    -- For MBCs with no assignments: shows qualified merit badges
    CASE 
        WHEN COUNT(mbp.id) > 0 THEN GROUP_CONCAT(DISTINCT mbp.merit_badge_name)
        ELSE (SELECT GROUP_CONCAT(amb.merit_badge_name) 
              FROM adult_merit_badges amb 
              WHERE amb.adult_id = a.id)
    END as merit_badges_counseling

FROM adults a
-- Left join to assignments (some MBCs may have zero assignments)
LEFT JOIN merit_badge_progress mbp ON a.id = mbp.mbc_adult_id

-- Only include adults who are qualified MBCs (have at least one merit badge qualification)
WHERE EXISTS (SELECT 1 FROM adult_merit_badges amb WHERE amb.adult_id = a.id)

GROUP BY a.id, a.first_name, a.last_name, a.email, a.bsa_number

ORDER BY total_assignments ASC, mbc_name;
