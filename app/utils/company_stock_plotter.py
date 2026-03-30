import pandas as pd
import yfinance as yf
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
def fetch_stock_history(ticker, start_date, end_date):
    """
    Fetches historical close price data for a given ticker and date range.

    Args:
        ticker (str): ticker symbol of company
        start_date (datetime): start date
        end_date (datetime): end date

    Returns:
        pd.DataFrame if successful, None if fetch fails
    """
    try:
        stock_data = yf.Ticker(ticker)
        hist = stock_data.history(start=start_date, end=end_date)
    except Exception as e:
        st.error(f"Failed to fetch data for {ticker}: {e}")
        return None

    if hist.empty:
        st.warning(f"No stock data available for {ticker} between {start_date} and {end_date}.")
        return None

    return hist


def build_stock_figure(hist, ticker):
    """
    Builds a Plotly line figure of closing prices.

    Args:
        hist (pd.DataFrame): historical OHLCV data
        ticker (str): ticker symbol, used for the plot title

    Returns:
        go.Figure
    """
    return go.Figure(
        data=[
            go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close", line=dict(width=2)),
        ],
        layout=go.Layout(
            title=f"{ticker} Close Price",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Close Price (USD)"),
        )
    )

def plot_stock_data(ticker, start_date, end_date):
    """
    Plots a line graph of a company's stock value from start_date to end_date.

    Args:
        ticker (str): ticker symbol of company
        start_date (datetime): start date given by user
        end_date (datetime): end date given by user

    Returns:
        None
    """
    hist = fetch_stock_history(ticker, start_date, end_date)
    if hist is None:
        return

    fig = build_stock_figure(hist, ticker)
    fig.update_layout(autosize=True)

    st.plotly_chart(fig, use_container_width=True)
