# MBC Workload Summary Enhancements Feature Request

## Current State

The Merit Badge Manager already includes a basic MBC Workload Summary view accessible through the Streamlit web interface. 

![Current MBC Workload Summary](https://github.com/user-attachments/assets/6a6653b8-4a24-461c-8b74-4863351b616b)

### Current Functionality

The existing `mbc_workload_summary` database view provides:
- MBC name and contact information
- Total assignments count  
- Active assignments count
- Completed assignments count
- Basic tabular display in Streamlit web interface

### Limitations

The current implementation lacks:
- Filtering and search capabilities
- Export functionality (Excel, PDF, CSV)
- Drill-down to detailed scout assignments
- Visual indicators for workload imbalances
- Sorting options beyond basic table sorting
- Quick action capabilities for counselor management

## Proposed Enhancements

The feature request `mbc-workload-summary-enhancements.yml` addresses these limitations by proposing:

1. **Enhanced Filtering & Search**
   - Filter by workload thresholds
   - Filter by assignment status
   - Search by counselor name/contact
   - Filter by merit badge categories

2. **Advanced Display Options**
   - Visual workload indicators
   - Progress bars for completion rates
   - Color-coded alerts for attention needed

3. **Export Capabilities**  
   - Excel exports with formatting
   - PDF reports with charts
   - CSV exports for external analysis

4. **Interactive Features**
   - Click-through to detailed scout assignments
   - Direct email links for counselor contact
   - Quick assignment actions

## Technical Implementation

The enhancement will build upon:
- Existing `mbc_workload_summary` SQL view
- Current Streamlit web interface framework
- Adult roster and merit badge progress database schemas
- Project coding standards and security guidelines

## Testing

The feature request includes comprehensive test coverage validation:
- YAML format validation
- GitHub issue template compatibility
- Project standards compliance
- Content quality assurance

See `tests/test_mbc_workload_feature_request.py` for validation details.