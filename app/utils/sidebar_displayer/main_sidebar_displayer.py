import streamlit as st
def render_sidebar():

    st.markdown("""
        <style>
            [data-testid="stSidebarCollapseButton"] { display: none; }
            [data-testid="stSidebarResizeHandle"] { display: none; }
        </style>
    """, unsafe_allow_html=True)
    st.title('Nvidia Corporation')
    st.subheader('Corporate Executive Panel')
    st.markdown(
        """
        <div style='display:flex; justify-content:space-between; width:100%;'>
            <span style='font-size:18px; '>John Doe</span>
            <span style='font-size:18px; color:gray;'>CEO</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.markdown(
        """
        <div style='display:flex; justify-content:space-between; width:100%;'>
            <span style='font-size:18px'>Jane Doe</span>
            <span style='font-size:18px; color:gray'>CFO</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")