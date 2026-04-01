import streamlit as st
def render_sidebar_styles():
    st.markdown("""
        <h1 style='font-size: 48px; font-weight: 700; display: flex; align-items: center; gap: 12px;'>
            <span style='
                display: inline-block;
                width: 12px;
                height: 48px;
                background-color: orange;
                border-radius: 2px;
            '></span>
            EARNINGSSENSE
        </h1>
    """, unsafe_allow_html=True)
    st.markdown("""
        <style>
            [data-testid="stSidebarCollapseButton"] { display: none; }
            [data-testid="stSidebarResizeHandle"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar(transcript):
    company = transcript['Company']
    st.title(company)
    st.markdown(f'<div style="font-size: 18px">{transcript['Year']} — Q{transcript['Quarter']}</div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("CORPORATE EXECUTIVE PANEL")
    corporate_participants = transcript.get("Corporate", [])
    if not corporate_participants:
        st.caption("No corporate participants found.")
        return

    for participant in corporate_participants:
        name = str(participant.get("Name", "") or "")
        role = str(participant.get("Role", "") or "").strip() or "Unknown role"

        st.markdown(
            f"""
            <div style='display:flex; justify-content:space-between; width:100%;'>
                <span style='font-size:18px; '>{name}</span>
                <span style='font-size:18px; color:gray;'>{role}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")
