import streamlit as st
import sys
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict

# Add the new layer directories to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

def get_database_connection():
    """Get SQLite database connection."""
    db_path = "merit_badge_manager.db"
    if not Path(db_path).exists():
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def get_available_views() -> List[str]:
    """Get list of available database views."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
        views = [row[0] for row in cursor.fetchall()]
        conn.close()
        return views
    except Exception as e:
        st.error(f"Error fetching views: {e}")
        if conn:
            conn.close()
        return []

def get_scout_assignments_for_mbc(mbc_adult_id: int) -> List[Dict]:
    """Get all scout assignments for a specific MBC."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        query = """
        SELECT 
            scout_first_name,
            scout_last_name,
            scout_bsa_number,
            scout_rank,
            merit_badge_name,
            merit_badge_year,
            date_completed,
            requirements_raw,
            CASE 
                WHEN date_completed IS NOT NULL AND date_completed != '' THEN 'Completed'
                ELSE 'In Progress'
            END as status
        FROM merit_badge_progress 
        WHERE mbc_adult_id = ?
        ORDER BY scout_last_name, scout_first_name, merit_badge_name
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (mbc_adult_id,))
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        assignments = []
        for row in rows:
            assignments.append(dict(zip(columns, row)))
        
        return assignments
        
    except Exception as e:
        st.error(f"Error fetching scout assignments: {e}")
        return []
    finally:
        conn.close()

def get_scout_mbcs_with_workload(scout_id: int) -> List[Dict]:
    """Get all MBCs for a specific Scout along with their workload data."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        query = """
        SELECT DISTINCT
            -- MBC Information
            a.id as mbc_adult_id,
            a.first_name || ' ' || a.last_name as mbc_name,
            a.email as mbc_email,
            a.bsa_number as mbc_bsa_number,
            
            -- Merit Badge Information for this Scout
            mbp.merit_badge_name,
            mbp.merit_badge_year,
            mbp.date_completed,
            CASE 
                WHEN mbp.date_completed IS NOT NULL AND mbp.date_completed != '' THEN 'Completed'
                ELSE 'In Progress'
            END as status,
            mbp.requirements_raw,
            
            -- MBC Workload Data (from mbc_workload_summary view)
            mws.total_assignments,
            mws.active_assignments,
            mws.completed_assignments,
            mws.unique_scouts_assigned,
            mws.unique_merit_badges,
            mws.merit_badges_counseling
            
        FROM merit_badge_progress mbp
        INNER JOIN adults a ON mbp.mbc_adult_id = a.id
        INNER JOIN mbc_workload_summary mws ON a.id = mws.mbc_adult_id
        WHERE mbp.scout_id = ?
        ORDER BY mbc_name, mbp.merit_badge_name
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (scout_id,))
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        mbcs = []
        for row in rows:
            mbcs.append(dict(zip(columns, row)))
        
        return mbcs
        
    except Exception as e:
        st.error(f"Error fetching scout MBC assignments: {e}")
        return []
    finally:
        conn.close()

def display_mbc_modal(mbc_name: str, mbc_adult_id: int):
    """Display modal dialog with scout assignments for selected MBC."""
    st.markdown("---")
    st.subheader(f"🎯 Scout Assignments for {mbc_name}")
    
    # Get scout assignments
    assignments = get_scout_assignments_for_mbc(mbc_adult_id)
    
    if not assignments:
        st.info(f"No scout assignments found for {mbc_name}.")
        if st.button("Close", key="close_modal_empty"):
            st.session_state.selected_mbc = None
            st.rerun()
        return
    
    # Group assignments by scout
    scouts_dict = {}
    for assignment in assignments:
        scout_key = f"{assignment['scout_first_name']} {assignment['scout_last_name']}"
        if scout_key not in scouts_dict:
            scouts_dict[scout_key] = {
                'scout_info': {
                    'name': scout_key,
                    'bsa_number': assignment['scout_bsa_number'],
                    'rank': assignment['scout_rank']
                },
                'merit_badges': []
            }
        
        scouts_dict[scout_key]['merit_badges'].append({
            'name': assignment['merit_badge_name'],
            'year': assignment['merit_badge_year'],
            'status': assignment['status'],
            'requirements': assignment['requirements_raw'] or 'No requirements recorded'
        })
    
    # Display scout assignments
    st.write(f"**Total Scouts:** {len(scouts_dict)}")
    st.write(f"**Total Merit Badge Assignments:** {len(assignments)}")
    
    # Create responsive layout
    for scout_name, scout_data in scouts_dict.items():
        with st.expander(f"📍 {scout_name} - {scout_data['scout_info']['rank']} (BSA #{scout_data['scout_info']['bsa_number']})", expanded=True):
            
            # Merit badges for this scout
            st.write("**Merit Badges:**")
            
            for mb in scout_data['merit_badges']:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status_emoji = "✅" if mb['status'] == 'Completed' else "🔄"
                    st.write(f"{status_emoji} **{mb['name']}** ({mb['year']})")
                    
                with col2:
                    if mb['status'] == 'Completed':
                        st.success("Completed")
                    else:
                        st.info("In Progress")
                
                with col3:
                    # Display requirements with proper wrapping
                    requirements_text = mb['requirements'] if mb['requirements'] else 'No requirements recorded'
                    st.text_area(
                        "Requirements",
                        value=requirements_text,
                        height=60,
                        key=f"mbc_req_{scout_name}_{mb['name']}",
                        disabled=True,
                        label_visibility="collapsed"
                    )
    
    # Close button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✖️ Close", key="close_modal", use_container_width=True):
            st.session_state.selected_mbc = None
            st.rerun()

def display_scout_mbc_modal(scout_name: str, scout_id: int, scout_bsa_number: int):
    """Display modal dialog with MBC assignments for selected Scout."""
    st.markdown("---")
    st.subheader(f"🎯 MBC Assignments for {scout_name}")
    
    # Get Scout's MBC assignments with workload data
    mbcs = get_scout_mbcs_with_workload(scout_id)
    
    if not mbcs:
        st.info(f"No MBC assignments found for {scout_name} (BSA #{scout_bsa_number}).")
        if st.button("Close", key="close_scout_modal_empty"):
            st.session_state.selected_scout = None
            st.rerun()
        return
    
    # Group MBCs by MBC name to show all merit badges they're working on with this Scout
    mbcs_dict = {}
    for mbc_assignment in mbcs:
        mbc_key = mbc_assignment['mbc_name']
        if mbc_key not in mbcs_dict:
            mbcs_dict[mbc_key] = {
                'mbc_info': {
                    'name': mbc_assignment['mbc_name'],
                    'email': mbc_assignment['mbc_email'],
                    'bsa_number': mbc_assignment['mbc_bsa_number'],
                    'adult_id': mbc_assignment['mbc_adult_id']
                },
                'workload': {
                    'total_assignments': mbc_assignment['total_assignments'],
                    'active_assignments': mbc_assignment['active_assignments'],
                    'completed_assignments': mbc_assignment['completed_assignments'],
                    'unique_scouts_assigned': mbc_assignment['unique_scouts_assigned'],
                    'unique_merit_badges': mbc_assignment['unique_merit_badges'],
                    'merit_badges_counseling': mbc_assignment['merit_badges_counseling']
                },
                'merit_badges': []
            }
        
        mbcs_dict[mbc_key]['merit_badges'].append({
            'name': mbc_assignment['merit_badge_name'],
            'year': mbc_assignment['merit_badge_year'],
            'status': mbc_assignment['status'],
            'requirements': mbc_assignment['requirements_raw'] or 'No requirements recorded'
        })
    
    # Display Scout and MBC assignments summary
    st.write(f"**Scout:** {scout_name} (BSA #{scout_bsa_number})")
    st.write(f"**Total MBCs:** {len(mbcs_dict)}")
    st.write(f"**Total Merit Badge Assignments:** {len(mbcs)}")
    
    st.markdown("---")
    
    # Display each MBC and their assignments
    for mbc_name, mbc_data in mbcs_dict.items():
        with st.expander(f"👤 {mbc_name} - {mbc_data['mbc_info']['email']}", expanded=True):
            
            # MBC Workload Information
            st.subheader("📊 MBC Current Workload")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Scouts", mbc_data['workload']['unique_scouts_assigned'])
            with col2:
                st.metric("Active Assignments", mbc_data['workload']['active_assignments'])
            with col3:
                st.metric("Completed Assignments", mbc_data['workload']['completed_assignments'])
            with col4:
                st.metric("Merit Badges", mbc_data['workload']['unique_merit_badges'])
            
            # All Merit Badges this MBC counsels
            st.write("**All Merit Badges Counseled:**")
            mb_badges = mbc_data['workload']['merit_badges_counseling']
            # Use text area for better display of long text
            st.text_area(
                "Merit Badges",
                value=mb_badges,
                height=80,
                key=f"mb_counseled_{mbc_data['mbc_info']['adult_id']}",
                disabled=True,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Merit badges for this Scout with this MBC
            st.subheader(f"🏅 Merit Badges with {scout_name}")
            
            for mb in mbc_data['merit_badges']:
                mb_col1, mb_col2, mb_col3 = st.columns([3, 1, 2])
                
                with mb_col1:
                    status_emoji = "✅" if mb['status'] == 'Completed' else "🔄"
                    st.write(f"{status_emoji} **{mb['name']}** ({mb['year']})")
                    
                with mb_col2:
                    if mb['status'] == 'Completed':
                        st.success("Completed")
                    else:
                        st.info("In Progress")
                
                with mb_col3:
                    # Display requirements with proper wrapping
                    requirements_text = mb['requirements'] if mb['requirements'] else 'No requirements recorded'
                    st.text_area(
                        "Requirements",
                        value=requirements_text,
                        height=60,
                        key=f"req_{mbc_data['mbc_info']['adult_id']}_{mb['name']}",
                        disabled=True,
                        label_visibility="collapsed"
                    )
    
    # Close button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✖️ Close", key="close_scout_modal", use_container_width=True):
            st.session_state.selected_scout = None
            st.rerun()

def refresh_mbc_workload_view():
    """Refresh the mbc_workload_summary view to ensure it has the latest structure."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Drop the existing view
        cursor.execute("DROP VIEW IF EXISTS mbc_workload_summary")
        
        # Read the updated view definition from the SQL file
        view_sql_path = Path(__file__).parent.parent.parent / "database" / "mbc_workload_summary_view.sql"
        if view_sql_path.exists():
            with open(view_sql_path, 'r') as f:
                view_sql = f.read()
            
            # Execute the new view creation
            cursor.execute(view_sql)
            conn.commit()
            return True
        else:
            st.error("View SQL file not found")
            return False
            
    except Exception as e:
        st.error(f"Error refreshing view: {e}")
        return False
    finally:
        conn.close()

def display_view_data(view_name: str):
    """Display data from a database view."""
    conn = get_database_connection()
    if not conn:
        st.warning("Database not found. Please import data first.")
        return
    
    try:
        # Special handling for MBC Workload Summary - refresh view if needed
        if view_name == 'mbc_workload_summary':
            # Try to query for mbc_adult_id column to see if view is updated
            try:
                pd.read_sql_query("SELECT mbc_adult_id FROM mbc_workload_summary LIMIT 1", conn)
            except Exception:
                # Column doesn't exist, refresh the view
                conn.close()
                if refresh_mbc_workload_view():
                    st.success("Updated MBC Workload Summary view structure")
                    conn = get_database_connection()
                else:
                    st.error("Failed to update view structure")
                    return
        
        df = pd.read_sql_query(f"SELECT * FROM {view_name}", conn)
        
        # Special handling for MBC Workload Summary
        if view_name == 'mbc_workload_summary':
            display_mbc_workload_with_modal(df)
        # Special handling for Scout views with clickable names
        elif view_name == 'active_scouts_with_positions':
            display_scouts_roster_with_modal(df)
        else:
            # Configure dataframe for text wrapping
            display_dataframe_with_text_wrapping(df)
        
        # Display record count
        st.info(f"Total records: {len(df)}")
        
    except Exception as e:
        st.error(f"Error loading view {view_name}: {e}")
    finally:
        conn.close()

def display_dataframe_with_text_wrapping(df: pd.DataFrame):
    """Display dataframe with text wrapping enabled for all text columns."""
    if df.empty:
        st.info("No data to display")
        return
    
    # Create column configuration for text wrapping
    column_config = {}
    
    for col in df.columns:
        # Check if this column contains long text content
        max_text_length = 0
        if not df[col].empty:
            max_text_length = df[col].astype(str).str.len().max()
        
        # Determine appropriate width based on content and column name
        if col.lower() in ['counselors', 'merit_badges_counseling', 'requirements', 'requirements_raw'] or max_text_length > 100:
            # Use large width for columns known to contain long concatenated text
            width = "large"
        elif max_text_length > 50:
            # Use medium width for moderately long text
            width = "medium"
        else:
            # Use small width for short text
            width = "small"
        
        # Configure column with appropriate text wrapping
        column_config[col] = st.column_config.TextColumn(
            col,
            help=f"Content for {col}",
            width=width,
            max_chars=None,  # No character limit to prevent truncation
        )
    
    # Display the dataframe with text wrapping configuration
    st.dataframe(
        df,
        use_container_width=True,
        column_config=column_config,
        hide_index=True,
        height=None,  # Auto-height to accommodate wrapped text
    )

def display_mbc_workload_with_modal(df: pd.DataFrame):
    """Display MBC workload summary with clickable MBC names that open modal dialogs."""
    
    # Initialize session state for selected MBC
    if 'selected_mbc' not in st.session_state:
        st.session_state.selected_mbc = None
    
    # Check if modal should be displayed
    if st.session_state.selected_mbc:
        mbc_info = st.session_state.selected_mbc
        display_mbc_modal(mbc_info['name'], mbc_info['adult_id'])
        return
    
    # Display MBC workload summary table with clickable names
    st.write("**Click on an MBC name to view their scout assignments**")
    
    # Create a custom display of the dataframe with clickable MBC names
    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 2])
            
            with col1:
                # Make MBC name clickable
                if st.button(
                    f"👤 {row['mbc_name']}", 
                    key=f"mbc_{row['mbc_adult_id']}",
                    help=f"Click to view scout assignments for {row['mbc_name']}"
                ):
                    st.session_state.selected_mbc = {
                        'name': row['mbc_name'],
                        'adult_id': row['mbc_adult_id'],
                        'email': row['email']
                    }
                    st.rerun()
                
                st.caption(f"✉️ {row['email']}")
            
            with col2:
                st.metric("Total", row['total_assignments'])
            
            with col3:
                st.metric("Active", row['active_assignments'])
            
            with col4:
                st.metric("Completed", row['completed_assignments'])
            
            with col5:
                st.metric("Scouts", row['unique_scouts_assigned'])
            
            with col6:
                # Display merit badges with wrapping
                merit_badges = str(row['merit_badges_counseling'])
                # Use text area for better wrapping of long text
                st.text_area(
                    "Merit Badges", 
                    value=merit_badges,
                    height=60,
                    key=f"mb_text_{row['mbc_adult_id']}",
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        st.markdown("---")

def display_scouts_roster_with_modal(df: pd.DataFrame):
    """Display Scouts roster with clickable Scout names that open modal dialogs."""
    
    # Initialize session state for selected Scout
    if 'selected_scout' not in st.session_state:
        st.session_state.selected_scout = None
    
    # Check if modal should be displayed
    if st.session_state.selected_scout:
        scout_info = st.session_state.selected_scout
        display_scout_mbc_modal(scout_info['name'], scout_info['id'], scout_info['bsa_number'])
        return
    
    # Display Scout roster table with clickable names
    st.write("**Click on a Scout name to view their MBC assignments and workload**")
    
    # First, we need to get scout IDs from the scouts table since the view might not have them
    conn = get_database_connection()
    if not conn:
        st.error("Database connection error")
        return
    
    try:
        # Get scout IDs by joining with scouts table
        scout_id_query = """
        SELECT s.id, s.first_name, s.last_name, s.bsa_number
        FROM scouts s
        """
        cursor = conn.cursor()
        cursor.execute(scout_id_query)
        scout_ids = {(row[1], row[2], row[3]): row[0] for row in cursor.fetchall()}
        
    except Exception as e:
        st.error(f"Error getting scout IDs: {e}")
        return
    finally:
        conn.close()
    
    # Create a custom display of the dataframe with clickable Scout names
    for index, row in df.iterrows():
        scout_key = (row['first_name'], row['last_name'], row['bsa_number'])
        scout_id = scout_ids.get(scout_key)
        
        if not scout_id:
            continue  # Skip if we can't find the scout ID
            
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 2, 2, 2])
            
            with col1:
                # Make Scout name clickable
                scout_name = f"{row['first_name']} {row['last_name']}"
                if st.button(
                    f"👤 {scout_name}", 
                    key=f"scout_{scout_id}",
                    help=f"Click to view MBC assignments for {scout_name}"
                ):
                    st.session_state.selected_scout = {
                        'name': scout_name,
                        'id': scout_id,
                        'bsa_number': row['bsa_number']
                    }
                    st.rerun()
                
                st.caption(f"BSA #{row['bsa_number']}")
            
            with col2:
                st.write(f"**{row['rank']}**")
            
            with col3:
                st.write(f"{row['patrol_name'] or 'No Patrol'}")
            
            with col4:
                st.write(f"Unit {row['unit_number']}")
            
            with col5:
                status_color = "🟢" if row['activity_status'] == 'Active' else "🔴"
                st.write(f"{status_color} {row['activity_status']}")
            
            with col6:
                position = row['position_title'] or 'No Position'
                st.caption(f"Position: {position}")
        
        st.markdown("---")

st.header("📊 Database Views")

# Check if database exists
if not Path("merit_badge_manager.db").exists():
    st.warning("⚠️ Database not found. Please import data first!")
    st.stop()

# Get available views
views = get_available_views()

if not views:
    st.warning("No database views found.")
    st.stop()

# Group views by type
adult_views = [v for v in views if 'adult' in v or v in ['training_expiration_summary', 'merit_badge_counselors', 'current_positions', 'registered_volunteers', 'mbc_workload_summary']]
youth_views = [v for v in views if 'scout' in v or v in ['advancement_progress_by_rank', 'primary_parent_contacts', 'patrol_assignments']]
other_views = [v for v in views if v not in adult_views and v not in youth_views]

# Sidebar for view selection
st.sidebar.subheader("Select a View")

view_type = st.sidebar.radio("View Category:", ["Adult Views", "Youth Views", "Other Views"] if other_views else ["Adult Views", "Youth Views"])

if view_type == "Adult Views" and adult_views:
    selected_view = st.sidebar.selectbox("Adult Views:", adult_views)
elif view_type == "Youth Views" and youth_views:
    selected_view = st.sidebar.selectbox("Youth Views:", youth_views)
elif view_type == "Other Views" and other_views:
    selected_view = st.sidebar.selectbox("Other Views:", other_views)
else:
    selected_view = None

# Display selected view
if selected_view:
    st.subheader(f"📋 {selected_view.replace('_', ' ').title()}")

    # Add view description
    view_descriptions = {
        'adults_missing_data': 'Adults with missing required information',
        'training_expiration_summary': 'Training status and expiration dates',
        'merit_badge_counselors': 'Merit badge counselor assignments',
        'current_positions': 'Current adult positions',
        'registered_volunteers': 'All adults with BSA numbers (registered volunteers) and their active roles',
        'scouts_missing_data': 'Scouts with missing required information',
        'active_scouts_with_positions': 'Scout roster with ranks and positions',
        'merit_badge_progress_summary': 'Merit badge progress overview',
        'scouts_needing_counselors': 'Scouts who need counselor assignments',
        'advancement_progress_by_rank': 'Advancement statistics by rank',
        'primary_parent_contacts': 'Primary parent/guardian contacts',
        'scout_training_expiration_summary': 'Scout training status',
        'patrol_assignments': 'Patrol membership',
        'scout_mbc_assignments': 'Scout-to-MBC assignment tracking with status details',
        'mbc_workload_summary': 'MBC workload statistics and assignment counts'
    }

    if selected_view in view_descriptions:
        st.info(view_descriptions[selected_view])

    # Display the view data
    display_view_data(selected_view)
else:
    st.info("Select a view from the sidebar to display data.")
