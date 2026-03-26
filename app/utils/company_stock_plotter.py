import pandas as pd
import yfinance as yf
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

def plot_stock_data(ticker: str, year: int, quarter: str):
    """
    Get stock data for a specific quarter and year.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        year: Year (e.g., 2023)
        quarter: Quarter (1-4)
    """
    # Define quarter date ranges
    quarter_dates = {
        'Q1': (f"{year}-01-01", f"{year}-03-31"),
        'Q2': (f"{year}-04-01", f"{year}-06-30"),
        'Q3': (f"{year}-07-01", f"{year}-09-30"),
        'Q4': (f"{year}-10-01", f"{year}-12-31"),
    }

    start_date, end_date = quarter_dates[quarter]

    stock = yf.Ticker(ticker)
    # Historical OHLCV price data for the quarter (unchanged source data)
    hist = stock.history(start=start_date, end=end_date)

    if hist.empty:
        st.warning(f"No stock data available for {ticker} in {quarter} {year}.")
        return

    x_vals = hist.index
    y_vals = hist["Close"]

    # Build an initial y-range with light padding to avoid a flat-looking start.
    y0 = float(y_vals.iloc[0])
    y_padding = max(abs(y0) * 0.01, 0.5)

    fig = go.Figure(
        data=[
            go.Scatter(x=[x_vals[0]], y=[y_vals.iloc[0]], mode="lines", name="Close", line=dict(width=2)),
        ],
        layout=go.Layout(
            title=f"{ticker} Close Price",
            xaxis=dict(title="Date", range=[x_vals[0], x_vals[0]], autorange=False),
            yaxis=dict(title="Close", range=[y0 - y_padding, y0 + y_padding], autorange=False),
        )
    )

    # Interpolate before the frames loop
    num_interp = 5
    x_numeric = np.linspace(0, len(hist) - 1, len(hist))
    x_smooth = np.linspace(0, len(hist) - 1, len(hist) * num_interp)
    y_smooth = np.interp(x_smooth, x_numeric, y_vals.values)
    x_smooth_dates = pd.date_range(hist.index[0], hist.index[-1], periods=len(y_smooth))
    y_min_full = float(y_smooth.min())
    y_max_full = float(y_smooth.max())
    pad = max((y_max_full - y_min_full) * 0.05, 0.5)
    # Then just replace len(hist) with len(y_smooth), and x_vals/y_vals with the smooth versions
    frames = []
    for i in range(1, len(y_smooth) + 1):
        current_y = y_smooth[:i]
        frames.append(go.Frame(
            data=[go.Scatter(x=x_smooth_dates[:i], y=current_y, mode="lines", line=dict(width=2))],
            layout=go.Layout(
                xaxis=dict(range=[x_smooth_dates[0], x_smooth_dates[-1]], autorange=False),
                yaxis=dict(range=[y_min_full - pad, y_max_full + pad], autorange=False)
            ),
            name=str(i)
        ))

    fig.frames = frames

    # Autoplay the animation in Streamlit without a manual Play button.
    animation_args = {"frame": {"duration": 10, "redraw": True},  "transition": {"duration": 0}, "fromcurrent": True}
    fig.update_layout(autosize=True)

    html = pio.to_html(
        fig,
        include_plotlyjs="cdn",
        full_html=False,
        auto_play=True,
        animation_opts=animation_args
    )

    # Inject CSS + wrapper
    fade_html = f"""
    <style>
    .fade-in {{
        opacity: 0;
        transform: translateY(12px);  
        animation: fadeIn 1.2s ease-out forwards;
    }}

    @keyframes fadeIn {{
        to {{
            opacity: 1;
            transform: translateY(0); 
        }}
    }}
    </style>

    <div class="fade-in">
        {html}
    </div>
    """

    components.html(fade_html, height=500)
