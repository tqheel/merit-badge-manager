import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# Add the new layer directories to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database-access"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "database"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Import database utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from database_utils import get_database_path, database_exists

st.header("🎯 Manual MBC Matching")
st.markdown("Manually resolve unmatched Merit Badge Counselor names from imported data.")

# Check if database exists
if not database_exists():
    st.warning("⚠️ Database not found. Please import data first!")
    st.stop()

# Import the manual matcher
try:
    from manual_mbc_matcher import ManualMBCMatcher
    matcher = ManualMBCMatcher(str(get_database_path()))
except ImportError as e:
    st.error(f"Error importing manual matcher: {e}")
    st.stop()

# Get statistics
with st.spinner("Loading matching statistics..."):
    stats = matcher.get_matching_statistics()

if not stats:
    st.error("Error loading matching statistics.")
    st.stop()

# Display statistics dashboard
st.subheader("📊 Matching Progress")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Unmatched", stats.get('total_unmatched', 0))
with col2:
    st.metric("Manually Matched", stats.get('manually_matched', 0))
with col3:
    st.metric("Unresolved", stats.get('unresolved', 0))
with col4:
    st.metric("Total Assignments", stats.get('total_assignments', 0))

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("Skipped", stats.get('skipped', 0))
with col6:
    st.metric("Marked Invalid", stats.get('marked_invalid', 0))
with col7:
    st.metric("New Adult Needed", stats.get('create_new', 0))
with col8:
    progress = 0
    if stats.get('total_unmatched', 0) > 0:
        resolved_count = stats.get('total_unmatched', 0) - stats.get('unresolved', 0)
        progress = (resolved_count / stats.get('total_unmatched', 0)) * 100
    st.metric("Progress", f"{progress:.1f}%")

# Get unmatched names
unmatched_names = matcher.get_unmatched_mbc_names()

if not unmatched_names:
    st.success("🎉 All MBC names have been resolved!")
    st.balloons()
    st.stop()

st.markdown("---")

# Manual matching interface
st.subheader("🔍 Manual Matching Interface")

# User identification
col_user, col_filter = st.columns([1, 2])
with col_user:
    user_name = st.text_input("Your Name", value="Anonymous", help="Used for audit trail")
with col_filter:
    # Filter options
    filter_option = st.selectbox(
        "Filter by:",
        ["All Unmatched", "High Assignment Count", "Recently Added"],
        help="Filter unmatched names to focus on specific criteria"
    )

# Apply filter
if filter_option == "High Assignment Count":
    unmatched_names = [name for name in unmatched_names if name['assignment_count'] >= 3]
elif filter_option == "Recently Added":
    # For this demo, we'll show all since we don't have dates
    pass

# Pagination
items_per_page = 5
total_items = len(unmatched_names)
total_pages = (total_items + items_per_page - 1) // items_per_page

if total_pages > 1:
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    with col_page:
        current_page = st.selectbox("Page", range(1, total_pages + 1), key="page_selector")

    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_items = unmatched_names[start_idx:end_idx]
else:
    page_items = unmatched_names
    current_page = 1

# Process each unmatched name
for idx, unmatched_item in enumerate(page_items):
    mbc_name_raw = unmatched_item['mbc_name_raw']
    assignment_count = unmatched_item['assignment_count']

    st.markdown(f"### {idx + 1}. `{mbc_name_raw}`")

    col_info, col_matches = st.columns([1, 2])

    with col_info:
        st.markdown("**Unmatched Name Details:**")
        st.write(f"**Name:** {mbc_name_raw}")
        st.write(f"**Assignment Count:** {assignment_count}")
        st.write(f"**Merit Badges:** {unmatched_item.get('merit_badges', 'N/A')}")

        # Show affected scouts (without truncation)
        scouts = unmatched_item.get('scouts', '')
        st.write(f"**Affected Scouts:** {scouts}")

    with col_matches:
        st.markdown("**Potential Adult Matches:**")

        with st.spinner(f"Finding matches for '{mbc_name_raw}'..."):
            potential_matches = matcher.get_potential_adult_matches(mbc_name_raw, limit=8)

        if potential_matches:
            # Display potential matches with confidence indicators
            for match_idx, match in enumerate(potential_matches):
                confidence = match['confidence_score']
                emoji = matcher.get_confidence_emoji(confidence)

                # Create a container for each match
                match_container = st.container()
                with match_container:
                    match_col1, match_col2, match_col3 = st.columns([3, 1, 1])

                    with match_col1:
                        st.write(f"{emoji} **{match['full_name']}**")
                        st.write(f"BSA #: {match.get('bsa_number', 'N/A')} | Email: {match.get('email', 'N/A')}")
                        if match.get('merit_badges'):
                            # Display merit badges using text area for full content
                            st.text_area(
                                "Merit Badges",
                                value=match['merit_badges'],
                                height=50,
                                key=f"match_mb_{mbc_name_raw}_{match['id']}",
                                disabled=True,
                                label_visibility="collapsed"
                            )

                    with match_col2:
                        st.write(f"**{confidence:.1%}**")
                        st.caption("Confidence")

                    with match_col3:
                        if st.button(f"Match", key=f"match_{mbc_name_raw}_{match['id']}"):
                            # Record the match
                            success = matcher.record_manual_match(
                                unmatched_mbc_name=mbc_name_raw,
                                match_action='matched',
                                matched_adult_id=match['id'],
                                confidence_score=confidence,
                                user_name=user_name,
                                notes=f"Manually matched to {match['full_name']} with {confidence:.1%} confidence"
                            )

                            if success:
                                st.success(f"✅ Matched '{mbc_name_raw}' to {match['full_name']}")
                                st.rerun()
                            else:
                                st.error("❌ Error recording match")

                    st.markdown("---")

        else:
            st.warning("No potential matches found with sufficient confidence.")

    # Action buttons for each unmatched name
    st.markdown("**Actions:**")
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    with action_col1:
        if st.button(f"Skip", key=f"skip_{mbc_name_raw}"):
            success = matcher.record_manual_match(
                unmatched_mbc_name=mbc_name_raw,
                match_action='skipped',
                user_name=user_name,
                notes="Skipped for now"
            )
            if success:
                st.info(f"⏭️ Skipped '{mbc_name_raw}'")
                st.rerun()

    with action_col2:
        if st.button(f"Mark Invalid", key=f"invalid_{mbc_name_raw}"):
            success = matcher.record_manual_match(
                unmatched_mbc_name=mbc_name_raw,
                match_action='marked_invalid',
                user_name=user_name,
                notes="Marked as invalid MBC name"
            )
            if success:
                st.warning(f"❌ Marked '{mbc_name_raw}' as invalid")
                st.rerun()

    with action_col3:
        if st.button(f"Create New", key=f"create_{mbc_name_raw}"):
            success = matcher.record_manual_match(
                unmatched_mbc_name=mbc_name_raw,
                match_action='create_new',
                user_name=user_name,
                notes="New adult record needed"
            )
            if success:
                st.info(f"➕ Marked '{mbc_name_raw}' for new adult creation")
                st.rerun()

    with action_col4:
        if st.button(f"Undo", key=f"undo_{mbc_name_raw}"):
            success = matcher.undo_manual_match(mbc_name_raw, user_name)
            if success:
                st.info(f"↩️ Undid previous decision for '{mbc_name_raw}'")
                st.rerun()

    st.markdown("---")

# Pagination info
if total_pages > 1:
    st.info(f"Showing {len(page_items)} of {total_items} unmatched names (Page {current_page} of {total_pages})")

# User activity summary
if stats.get('user_activity'):
    st.subheader("👥 User Activity Summary")
    user_activity_df = pd.DataFrame(stats['user_activity'])
    st.dataframe(user_activity_df, use_container_width=True)
