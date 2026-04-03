import streamlit as st
import os
from utils.fetch_transcript import fetch_transcript
from components.ai_powered_summary import summarise_with_ai
from components.topic_bar_chart import render_topic_bar_chart
from components.sidebar import render_sidebar_styles
from components.hedging_breakdown import render_hedging_breakdown
from components.stock_chart import render_stock_chart
from components.sidebar import render_sidebar
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
PLACEHOLDER = "-- select an option --"
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: Linen;  /* or any color you want */
    }

    /* Optional: sidebar background */
    [data-testid="stSidebar"] {
        background-color: grey;
    }
    </style>
    """,
    unsafe_allow_html=True
)
def take_input():
    path = "data/Transcripts/"
    TICKERS = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and 'AAPL' not in f]
    st.markdown(
        """
        <style>
        div[data-testid="stSelectbox"] > div > div {
            background-color: Ivory;
            color: grey;
            font-size:16px; font-weight: 200;font-family:'IBM Plex Mono',monospace;margin-bottom:1.5rem;
            border-color: black !important;
            border-width: 1px !important;
        }
        /* Dropdown container */
        div[data-testid="stSelectbox"] ul {
            background-color: red !important;
            border: 2px solid red;
        }
        
        /* Individual options */
        div[data-testid="stSelectbox"] ul li {
            color: black;
            background-color: red !important;
        }
        
        /* Hovered option */
        div[data-testid="stSelectbox"] ul li:hover {
            background-color: red;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    ticker = st.selectbox(
        "TICKER",
        options=["-- select an option --"] + TICKERS,
        index=0
    )
    year = st.selectbox(
        "YEAR",
        options=["-- select an option --", 2016, 2017, 2018, 2019, 2020],
        index=0
    )

    quarter = st.slider('QUARTER', 1, 4)
    return ticker, quarter, year
st.set_page_config(layout='wide')
st.markdown(
    """
    <style>
    div[data-testid="stMetricValue"] {
        color: black;
        letter-spacing: .14em
        font-weight: 600;
    }
    label[data-testid="stMetricLabel"] p {
        color: grey;
        font-size:.85rem;
        letter-spacing:.14em;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.metric(label="EARNINGS CALL ANALYSIS", value='SENTIMENT OVERVIEW')
st.markdown(
    """
    <style>
    hr {
        border-color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.divider()
# render sidebar and take user input
with st.sidebar:
    render_sidebar_styles()
    sidebar_placeholder = st.empty()
    st.divider()
    ticker, quarter, year = take_input()

if ticker != PLACEHOLDER and year != PLACEHOLDER and quarter != PLACEHOLDER:
    transcript = fetch_transcript(ticker, quarter, year)
    with sidebar_placeholder.container():
        render_sidebar(transcript)

    row1_col1, divider, row1_col2 = st.columns([5, 0.2, 5])
    row2_col1, row2_col2 = st.columns(2)
    with row1_col1:
        render_stock_chart(ticker, quarter, year)
    with divider:
        st.markdown(
            """
            <div style="
                border-left: 2px solid black;
                height: 450px;
                margin: auto;
            "></div>
            """,
            unsafe_allow_html=True
        )
    with row2_col2:
        render_topic_bar_chart(transcript)
    with row1_col2:
        render_hedging_breakdown(transcript)
    with row2_col1:
        summarise_with_ai()