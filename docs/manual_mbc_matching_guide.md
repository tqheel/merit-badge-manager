# Manual MBC Matching Guide

The Manual MBC Matching feature allows users to resolve unmatched Merit Badge Counselor names from imported Merit Badge In-Progress Reports. When MBC names in the imported data don't automatically match to adult roster entries, they can be manually resolved through an intuitive web interface.

## Overview

During Merit Badge progress import, some MBC names cannot be automatically matched due to:
- Name variations (e.g., "John Smith" vs "J. Smith" vs "John Smyth")
- Nicknames or shortened names
- Typos in the source data
- Missing adults in the roster

These unmatched names are stored in the `unmatched_mbc_names` table and can be resolved through the Manual MBC Matching interface.

## Features

### Statistics Dashboard
- **Total Unmatched**: Number of unmatched MBC names requiring resolution
- **Manually Matched**: Number of names successfully matched to adults
- **Unresolved**: Number of names still needing attention
- **Total Assignments**: Total merit badge assignments affected
- **Skipped**: Names temporarily skipped for later review
- **Marked Invalid**: Names marked as invalid or not real MBCs
- **New Adult Needed**: Names requiring new adult roster entries
- **Progress**: Overall completion percentage

### Fuzzy Matching Engine
The system uses advanced fuzzy matching algorithms to find potential adult matches:
- **Exact matching**: Direct name matches
- **Partial matching**: Handles abbreviated names
- **Token-based matching**: Reorders names (e.g., "Smith, John" → "John Smith")
- **String similarity**: Handles minor typos and variations

### Confidence Indicators
Visual confidence scoring helps users make informed decisions:
- 🟢 **High Confidence (90%+)**: Very likely matches
- 🟡 **Good Confidence (80-89%)**: Probable matches
- 🟠 **Medium Confidence (60-79%)**: Possible matches
- 🔴 **Low Confidence (<60%)**: Unlikely matches

## Using the Interface

### Navigation
1. Start the web interface: `streamlit run web-ui/main.py`
2. Navigate to **Manual MBC Matching** in the sidebar
3. Review the statistics dashboard for overall progress

### Manual Matching Workflow

#### For Each Unmatched Name:

1. **Review Name Details**
   - Unmatched MBC name as it appears in the source data
   - Number of assignments affected
   - Merit badges involved
   - Affected scouts

2. **Evaluate Potential Matches**
   - System shows potential adult matches with confidence scores
   - Adult information includes name, BSA number, email, and merit badges
   - Confidence emoji and percentage help assess match quality

3. **Take Action**
   - **Match**: Confirm a match between unmatched name and adult
   - **Skip**: Temporarily skip for later review
   - **Mark Invalid**: Mark as invalid MBC name (typo, non-existent, etc.)
   - **Create New**: Flag that a new adult roster entry is needed
   - **Undo**: Reverse a previous decision

### User Tracking and Audit Trail
- All decisions are tracked with user name and timestamp
- Complete audit trail maintained in `mbc_manual_matches` table
- User activity summary shows individual contributions
- Undo functionality allows reversal of decisions

## Database Schema

### New Tables

#### `mbc_manual_matches`
Tracks all manual matching decisions:
```sql
CREATE TABLE mbc_manual_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unmatched_mbc_name TEXT NOT NULL,
    matched_adult_id INTEGER,
    match_action TEXT NOT NULL, -- 'matched', 'skipped', 'marked_invalid', 'create_new', 'undone'
    confidence_score REAL,
    user_name TEXT NOT NULL,
    notes TEXT,
    original_match_id INTEGER, -- For undo operations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Updated Views

#### `unmatched_mbc_assignments`
Enhanced to show manual match status:
- Manual match status (Manually Matched, Skipped, Marked Invalid, etc.)
- User who made the decision
- Date of manual match

#### `mbc_manual_matches_summary`
User activity summary:
- Total decisions per user
- Breakdown by action type
- Activity timeframes
- Unique names processed

## Integration with Existing Workflow

### Data Flow
1. Merit Badge progress imported from Scoutbook
2. Automatic fuzzy matching attempts to resolve MBC names
3. Unmatched names stored in `unmatched_mbc_names` table
4. Manual resolution through web interface
5. Resolved matches update `merit_badge_progress` records
6. MBC workload views show resolved assignments

### Updated Database Views
- `mbc_workload_summary`: Shows counselor names from adult roster
- `scout_mbc_assignments`: Includes manually matched counselors
- `merit_badge_status_view`: Reflects manual matching decisions

## Best Practices

### Matching Guidelines
1. **High Confidence Matches**: Accept matches with 90%+ confidence
2. **Good Confidence Matches**: Review carefully, likely accurate
3. **Medium Confidence Matches**: Check additional context (merit badges, contact info)
4. **Low Confidence Matches**: Use with caution, consider creating new adult

### Quality Assurance
1. Review merit badge qualifications when matching
2. Cross-reference with contact information if available
3. Use notes field to document reasoning for complex decisions
4. Regular review of skipped items

### User Management
1. Use consistent user names for tracking
2. Train multiple users for distributed workload
3. Review user activity summaries for quality control
4. Document institutional knowledge in notes

## Troubleshooting

### Common Issues
- **No potential matches found**: Consider typos in source data or missing adults
- **Multiple high-confidence matches**: Review additional context (contact info, merit badges)
- **Performance with large datasets**: Use filters to focus on specific subsets

### Database Maintenance
- Regular cleanup of resolved matches
- Monitor user activity for quality patterns
- Backup before major matching sessions

## Technical Details

### Dependencies
- `fuzzywuzzy`: Fuzzy string matching
- `python-levenshtein`: Enhanced string distance calculations
- `streamlit`: Web interface framework
- `sqlite3`: Database operations

### Performance Considerations
- Fuzzy matching limited to reasonable confidence thresholds (40%+)
- Pagination for large datasets (5 items per page)
- Indexed database queries for optimal performance
- Optimized views for real-time statistics

### API Integration
The manual matching functionality is designed to integrate with:
- Existing MBC name matcher (`mbc_name_matcher.py`)
- Merit badge progress import (`import_mb_progress.py`)
- Adult roster management systems
- Reporting and analytics tools