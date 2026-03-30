import streamlit as st
from datetime import datetime
from pathlib import Path

from utils.company_stock_plotter import plot_stock_data
from utils.sidebar_displayer.main_sidebar_displayer import render_sidebar

render_sidebar()
ticker = st.session_state.ticker
quarter = st.session_state.quarter
year = st.session_state.year
if ticker is not None and quarter is not None and year is not None:
    transcript_dir = Path(__file__).resolve().parents[1] / "data" / "Transcripts" / ticker

    if not transcript_dir.exists():
        st.error(f"Transcript directory not found: {transcript_dir}")
    else:
        parsed_transcripts = []
        for transcript_path in transcript_dir.glob("*.txt"):
            parts = transcript_path.stem.split("-")
            if len(parts) < 4:
                continue
            try:
                transcript_date = datetime.strptime("-".join(parts[:3]), "%Y-%b-%d")
            except ValueError:
                continue
            parsed_transcripts.append((transcript_date, transcript_path))

        parsed_transcripts.sort(key=lambda item: item[0])
        transcripts_in_year = [item for item in parsed_transcripts if item[0].year == int(year)]
        n = int(quarter[1])

        if not transcripts_in_year:
            st.error(f"No transcripts found for {ticker} in {year}.")
        elif n > len(transcripts_in_year):
            st.error(
                f"{quarter} is unavailable for {ticker} in {year}: only {len(transcripts_in_year)} transcript(s) found."
            )
        else:
            # N-th transcript in selected year (1-indexed)
            target_idx = n - 1
            target_transcript = transcripts_in_year[target_idx]

            # Build window from full chronological list so Q1-Q3 can pull prior-year context.
            absolute_target_idx = parsed_transcripts.index(target_transcript)
            selected_window = parsed_transcripts[max(0, absolute_target_idx - 3): absolute_target_idx + 1]
            start_date = selected_window[0][0].strftime("%Y-%m-%d")
            end_date = selected_window[-1][0].strftime("%Y-%m-%d")

            plot_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)
