-- Current Positions of Responsibility (POR) View
-- Shows scouts currently holding positions of responsibility within the troop
-- Created: 2025-09-03
-- Purpose: Identify scouts in leadership positions for advancement tracking and recognition

CREATE VIEW IF NOT EXISTS current_por_scouts AS
SELECT 
    s.bsa_number,
    s.first_name,
    s.last_name,
    s.patrol_name,
    s.rank,
    sp.position_title,
    sp.tenure_info,
    sp.start_date,
    sp.end_date,
    'Current' as position_status
FROM scouts s
INNER JOIN scout_positions sp ON s.id = sp.scout_id
WHERE sp.is_current = 1
    AND sp.position_title IS NOT NULL
    AND sp.position_title != ''
    AND sp.position_title != 'No Position'
ORDER BY 
    sp.position_title,
    s.last_name,
    s.first_name;

-- Query to get POR summary by position
-- SELECT position_title, COUNT(*) as scout_count 
-- FROM current_por_scouts 
-- GROUP BY position_title 
-- ORDER BY scout_count DESC, position_title;
