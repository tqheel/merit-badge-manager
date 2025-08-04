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
