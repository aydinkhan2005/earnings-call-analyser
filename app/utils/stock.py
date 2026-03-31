import yfinance as yf
import streamlit as st
@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    try:
        hist = yf.Ticker(ticker).history(start=start_date, end=end_date)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data for {ticker}") from e

    if hist.empty:
        return None

    return hist