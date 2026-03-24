import datetime
from pathlib import Path
import streamlit as st

def recieve_input(ticker, quarter, year):
    transcript_dir = Path(__file__).resolve().parents[2] / "data" / "Transcripts" / ticker
    if not transcript_dir.exists():
        st.error(f"Transcript directory not found: {transcript_dir}")
        st.stop()

    dated_files = []
    for path in transcript_dir.glob("*.txt"):
        parts = path.stem.split("-")
        if len(parts) < 4:
            continue
        try:
            file_date = datetime.datetime.strptime("-".join(parts[:3]), "%Y-%b-%d")
        except ValueError:
            continue
        if file_date.year == year:
            dated_files.append((file_date, path))

    dated_files.sort(key=lambda item: item[0])
    transcript_files = [path for _, path in dated_files]

    quarter_to_index = {"Q1": 0, "Q2": 1, "Q3": 2, "Q4": 3}
    file_index = quarter_to_index[quarter]
    if len(transcript_files) <= file_index:
        st.error(f"Expected at least {file_index + 1} transcript files for year {year} in {transcript_dir}")
        st.stop()

    transcript_path = transcript_files[file_index]
    return transcript_path