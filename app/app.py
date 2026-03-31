import pandas as pd
import plotly.express as px
import streamlit as st
import os
from components.stock_chart import render_stock_chart
from utils.sidebar_displayer.main_sidebar_displayer import render_sidebar
PLACEHOLDER = "-- select an option --"
# --- Trigger call() only when all three are selected ---
def call(ticker, year, quarter):
    # Your function logic here
    st.write(f"Called with: {ticker}, {year}, {quarter}")
def take_input():
    path = "data/Transcripts/"
    TICKERS = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and 'AAPL' not in f]
    ticker = st.selectbox(
        "Ticker",
        options=["-- select an option --"] + TICKERS,
        index=0
    )
    year = st.selectbox(
        "Year",
        options=["-- select an option --", 2016, 2017, 2018, 2019, 2020],
        index=0
    )
    quarter_labels = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}

    quarter = st.slider('Quarter', 1, 4)
    return ticker, quarter, year

st.title('Earnings Call Analyser')
# render sidebar and take user input
with st.sidebar:
    render_sidebar()
    ticker, quarter, year = take_input()

# if user is prompting to see info about a particular company, show it
if ticker != PLACEHOLDER and year != PLACEHOLDER and quarter != PLACEHOLDER:
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    with row1_col1:
        render_stock_chart(ticker, quarter, year)
    with row2_col2:
        # Sample data
        df = pd.DataFrame({
            "Category": ["A", "B", "C"],
            "Values": [10, 20, 15]
        })

        # Create bar chart
        fig = px.bar(df, y="Category", x="Values", title='Top 5 Topics')

        # Render in Streamlit
        st.plotly_chart(fig)
    with row1_col2:
        st.subheader('Hedging Rate Breakdown')
        c1, c2 = st.columns(2)
        with c1:
            st.metric('Q&A', '86%')
        with c2:
            st.metric('Opening', '60%')
        st.metric('Most Common Topic', 'Hardware')
        message = st.text_area("Ask AI Follow-Up Questions", height=100)
    with row2_col1:
        st.subheader('Per-Quarter Breakdown')