import streamlit as st
def render_sidebar():
    if "ticker" not in st.session_state:
        st.session_state.ticker = None
    if "quarter" not in st.session_state:
        st.session_state.quarter = None
    if "year" not in st.session_state:
        st.session_state.year = None

    st.markdown("""
        <style>
            [data-testid="stSidebarCollapseButton"] { display: none; }
            [data-testid="stSidebarResizeHandle"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        ticker = st.session_state.ticker
        quarter = None
        year= None

        st.title("NVIDIA Corporation")
        st.subheader(
            f"{'N/A' if ticker in st.session_state else ticker} — {'N/A' if quarter in st.session_state else quarter} · Nov 20, "
            f"{'N/A' if year in st.session_state else year}"
        )

        st.metric("Hedging Score", "38%")
        st.metric("Total Sentences", "284")
        st.metric("Hedged", "108")
        st.metric("CEO Hedging", "41%")
        st.metric("CFO Hedging", "52%")
        st.metric("Q&A Hedging", "61%")
        ticker = st.selectbox(
            "Company",
            options=[None, 'AMD', 'AMZN', 'ASML', 'CSCO', 'GOOGL', 'INTC', 'MSFT', 'MU', 'NVDA'],
            format_func=lambda x: "-- Select an option --" if x is None else x,
            index=0
        )
        quarter = st.selectbox(
            "Quarter",
            [None, "Q1", "Q2", "Q3", "Q4"],
            format_func=lambda x: "-- Select an option --" if x is None else x,
            index=0
        )
        year = st.selectbox(
            "Year",
            [None, '2016', '2017', '2018', '2019', '2020'],
            format_func=lambda x: "-- Select an option --" if x is None else x,
            index=0
        )

        st.session_state.ticker = ticker
        st.session_state.quarter = quarter
        st.session_state.year = year


    st.title("Earnings Call Analyzer")