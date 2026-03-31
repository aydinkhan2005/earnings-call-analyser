from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Make repository-root packages (e.g., speech_parser) importable from app/utils.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from speech_parser.transcript_parser import parse_transcript_to_data


def fetch_transcript(ticker: str, quarter: int, year: int):
    """Return parsed transcript data for the requested ticker/year/quarter.

    This function searches `data/Transcripts/{ticker}` for transcript files whose
    names start with `{year}-`, sorts matching files by their embedded date
    (`YYYY-MMM-DD-{ticker}.txt`), selects the K-th file where `K = quarter`
    (1-indexed), and passes that file path into `parse_transcript_to_data()`.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL").
        quarter: Quarter index (1-indexed within the selected year).
        year: Calendar year to filter transcript files.

    Returns:
        Parsed JSON-like transcript object from `parse_transcript_to_data()`, or
        `None` when the selected year does not have enough transcript files.

    Raises:
        TypeError: If any input type is invalid.
    """
    if not isinstance(ticker, str) or isinstance(ticker, bool):
        raise TypeError("ticker must be a string")
    if not isinstance(quarter, int) or isinstance(quarter, bool):
        raise TypeError("quarter must be an integer")
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError("year must be an integer")

    transcripts_dir = Path(__file__).resolve().parents[2] / "data" / "Transcripts" / ticker
    if not transcripts_dir.exists() or not transcripts_dir.is_dir():
        st.error(f"{year} does not contain the transcript for quarter {quarter}")
        return None

    pattern = re.compile(rf"^(?P<date>{year}-[A-Za-z]{{3}}-\d{{2}})-{re.escape(ticker)}\.txt$")
    dated_files: list[tuple[datetime, Path]] = []

    for file_path in transcripts_dir.glob(f"{year}-*.txt"):
        match = pattern.match(file_path.name)
        if not match:
            continue
        try:
            file_dt = datetime.strptime(match.group("date"), "%Y-%b-%d")
        except ValueError:
            continue
        dated_files.append((file_dt, file_path))

    dated_files.sort(key=lambda item: item[0])

    if quarter < 1 or len(dated_files) < quarter:
        st.error(f"{year} does not contain the transcript for quarter {quarter}")
        return None

    transcript_path = dated_files[quarter - 1][1]
    return parse_transcript_to_data(transcript_path)


