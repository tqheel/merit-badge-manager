# Scout Merit Badge Modal Feature

## Overview

The Scout Merit Badge Modal feature provides Scoutmasters with an intuitive interface to view and manage a Scout's merit badge progress and counselor assignments. This feature was implemented to address Issue #43.

## Accessing the Feature

1. Navigate to **Database Views** in the sidebar
2. Select **Youth Views** from the view category options
3. Choose **Active Scouts With Positions** from the dropdown
4. Click on any Scout's name (👤 Scout Name button) to open their merit badge modal

## What the Modal Shows

### Scout Information
- Scout's name and BSA number
- Count of merit badges currently in progress

### Merit Badges In Progress
The modal displays **only merit badges that are currently in progress** (not completed badges), showing:

- 🏅 Merit badge name
- Date started
- Progress notes/requirements completed
- Counselor assignment status

### For Each Merit Badge

**If Counselor is Assigned:**
- 👤 Counselor name
- ✉️ Counselor email address 
- Counselor's current workload metrics

**If No Counselor is Assigned:**
- ⚠️ Warning that no counselor is assigned
- 🔗 "Assign Counselor" button to start the assignment workflow

## Counselor Assignment Workflow

When clicking "🔗 Assign Counselor" for an unassigned merit badge:

1. **Counselor Selection Interface** appears showing:
   - Available counselors qualified for that specific merit badge
   - Each counselor's current workload (active assignments, total scouts, etc.)
   - Counselors sorted by workload (least busy first)

2. **Assignment Process:**
   - Click "Select" next to the desired counselor
   - Confirm the assignment when prompted
   - Assignment is saved immediately and modal updates in real-time

3. **Navigation:**
   - Use "← Back to Merit Badges" to return without assigning
   - Use "Cancel" to cancel a pending assignment

## Key Features

### Real-Time Updates
- Assignments are reflected immediately without closing the modal
- No page refresh required

### Intelligent Filtering
- Shows only "in progress" merit badges (filters out completed badges)
- Uses youth roster data (`scout_merit_badge_progress` table)

### Workload-Based Selection
- Available counselors are sorted by current workload
- Helps balance counselor assignments across the troop

### User-Friendly Interface
- Clear visual indicators for assignment status
- Proper error handling and user feedback
- Accessible navigation and controls

## Technical Details

### Database Integration
- Uses `scout_merit_badge_progress` table for merit badge tracking
- Uses `adult_merit_badges` table to find qualified counselors
- Integrates with `mbc_workload_summary` view for counselor metrics

### Data Filtering
- Filters on `status != 'Completed'` and `date_completed IS NULL`
- LEFT JOIN to include badges without assigned counselors
- Sorts counselors by `active_assignments ASC` (least busy first)

## Error Handling

The system gracefully handles various scenarios:
- Scouts with no merit badges in progress: Shows appropriate message
- Merit badges with no available counselors: Explains situation and suggests contacting Scoutmaster
- Database connection issues: Displays user-friendly error messages

## Benefits for Scoutmasters

1. **Quick Overview**: See all in-progress merit badges at a glance
2. **Efficient Assignment**: Assign counselors based on current workload
3. **Better Workload Management**: Prevent counselor overload
4. **Real-Time Updates**: Changes are immediately visible
5. **Streamlined Workflow**: Complete assignments without leaving the interface

## Testing

The feature includes comprehensive Playwright tests covering:
- Modal opening and closing
- Data filtering (in-progress vs completed badges)  
- Counselor assignment workflow
- Edge cases (no badges, no counselors)
- UI accessibility and navigation

---

*This feature addresses Issue #43: Scout youth roster record detail for merit badges*