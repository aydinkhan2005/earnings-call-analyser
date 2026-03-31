import streamlit as st
import plotly.graph_objects as go
import re
from datetime import datetime
from pathlib import Path

from utils.stock import get_stock_data

def _build_stock_figure(hist, ticker):
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

def render_stock_chart(ticker, quarter, year):
    if not isinstance(ticker, str) or isinstance(ticker, bool):
        raise TypeError("ticker must be a string")
    if not isinstance(quarter, int) or isinstance(quarter, bool):
        raise TypeError("quarter must be an integer")
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError("year must be an integer")
    if quarter < 1:
        raise TypeError("quarter must be >= 1")

    transcripts_dir = Path(__file__).resolve().parents[2] / "data" / "Transcripts" / ticker
    if not transcripts_dir.exists() or not transcripts_dir.is_dir():
        st.error(f"Transcript directory not found for ticker {ticker}")
        return

    pattern = re.compile(rf"^(\d{{4}}-[A-Za-z]{{3}}-\d{{2}})-{re.escape(ticker)}\.txt$")
    all_datetimes = []
    for transcript_file in transcripts_dir.glob("*.txt"):
        match = pattern.match(transcript_file.name)
        if not match:
            continue
        try:
            all_datetimes.append(datetime.strptime(match.group(1), "%Y-%b-%d"))
        except ValueError:
            continue

    if not all_datetimes:
        st.error(f"No transcript files were found for ticker {ticker}")
        return

    all_datetimes.sort()
    year_datetimes = [dt for dt in all_datetimes if dt.year == year]

    if len(year_datetimes) < quarter:
        st.error(f"{year} does not contain the transcript for quarter {quarter}")
        return

    end_date = year_datetimes[quarter - 1]
    end_idx = all_datetimes.index(end_date)
    start_idx = max(0, end_idx - 3)
    start_date = all_datetimes[start_idx]

    if start_date == end_date:
        st.error("Sorry. Transcript data is not available that goes back this far")
        return

    try:
        hist = get_stock_data(ticker, start_date, end_date)
    except RuntimeError as e:
        st.error(str(e))
        return

    if hist is None:
        st.warning(f"No stock data available for {ticker}.")
        return

    fig = _build_stock_figure(hist, ticker)
    fig.update_layout(autosize=True)
    st.plotly_chart(fig, use_container_width=True)