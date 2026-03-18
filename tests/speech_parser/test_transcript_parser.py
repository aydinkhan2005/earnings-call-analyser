import pytest
import pandas as pd
import json
from pathlib import Path

from speech_parser import transcript_parser as tp


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def minimal_valid_transcript_text() -> str:
    return "\n".join(
        [
            "Q2 2016 Apple Inc Earnings Call",
            "Corporate Participants",
            " * Tim Cook",
            " Apple Inc. - CEO",
            "Conference Call Participiants",
            " * Rod Hall",
            " JPMorgan - Analyst",
            "Operator [1]",
            "Welcome everyone.",
            "Tim Cook, Apple Inc. - CEO [2]",
        ]
    )


def test_normalize_company_name_rejects_non_string():
    with pytest.raises(TypeError):
        tp._normalize_company_name(123)


@pytest.mark.parametrize("bad_text", ["", "Q5 2016 Apple Inc Earnings Call", "hello world"])
def test_extract_header_metadata_rejects_missing_header_pattern(bad_text):
    with pytest.raises(ValueError, match="Could not locate header metadata"):
        tp._extract_header_metadata(bad_text)


def test_extract_header_metadata_rejects_non_string():
    with pytest.raises(TypeError):
        tp._extract_header_metadata(2024)


def test_extract_conference_participants_rejects_missing_line_column():
    with pytest.raises(KeyError):
        tp._extract_conference_participants(pd.DataFrame({"text": [" * Tim Cook"]}))


def test_extract_conference_participants_handles_empty_dataframe():
    assert tp._extract_conference_participants(pd.DataFrame(columns=["line"])) == []


def test_extract_corporate_participants_rejects_missing_line_column():
    with pytest.raises(KeyError):
        tp._extract_corporate_participants(pd.DataFrame({"text": ["Corporate Participants"]}))


def test_extract_corporate_participants_handles_empty_dataframe():
    assert tp._extract_corporate_participants(pd.DataFrame(columns=["line"])) == []


def test_extract_speaker_tuples_rejects_non_dataframe_input():
    with pytest.raises(TypeError):
        tp._extract_speaker_tuples([])


def test_extract_speaker_tuples_rejects_missing_line_column():
    with pytest.raises(KeyError):
        tp._extract_speaker_tuples(pd.DataFrame({"text": ["Operator [1]"]}))


def test_presentation_cutoff_handles_non_positive_total_speakers():
    assert tp._presentation_cutoff([1, 2], 0) == 0
    assert tp._presentation_cutoff([1, 2], -2) == 0


def test_presentation_cutoff_rejects_invalid_total_speakers_type():
    with pytest.raises(TypeError):
        tp._presentation_cutoff([1, 2], "2")


def test_presentation_cutoff_rejects_incompatible_marker_values():
    with pytest.raises(TypeError):
        tp._presentation_cutoff([1, "2"], 2)


def test_parse_transcript_to_json_rejects_bool_transcript_path():
    with pytest.raises(TypeError, match="transcript_path must be a string or pathlib.Path"):
        tp.parse_transcript_to_json(True)


def test_parse_transcript_to_json_rejects_non_path_type():
    with pytest.raises(TypeError, match="transcript_path must be a string or pathlib.Path"):
        tp.parse_transcript_to_json(123)


def test_parse_transcript_to_json_rejects_non_txt_extension(tmp_path):
    bad_path = tmp_path / "transcript.csv"
    with pytest.raises(ValueError, match="must point to a .txt file"):
        tp.parse_transcript_to_json(bad_path)


def test_parse_transcript_to_json_rejects_missing_file(tmp_path):
    missing_txt = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        tp.parse_transcript_to_json(missing_txt)


def test_parse_transcript_to_json_rejects_directory_path(tmp_path):
    txt_dir = tmp_path / "fake.txt"
    txt_dir.mkdir()
    with pytest.raises(ValueError, match="is not a file"):
        tp.parse_transcript_to_json(txt_dir)


def test_parse_transcript_to_json_rejects_whitespace_only_file(tmp_path):
    transcript_path = tmp_path / "empty.txt"
    transcript_path.write_text("   \n\t\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty after stripping whitespace"):
        tp.parse_transcript_to_json(transcript_path)


def test_parse_transcript_to_json_rejects_invalid_output_dir_type(tmp_path, minimal_valid_transcript_text):
    transcript_path = tmp_path / "valid.txt"
    transcript_path.write_text(minimal_valid_transcript_text, encoding="utf-8")

    with pytest.raises(TypeError, match="output_dir must be a string or pathlib.Path"):
        tp.parse_transcript_to_json(transcript_path, output_dir=False)


def test_parse_transcript_to_json_rejects_missing_header_metadata(tmp_path):
    transcript_path = tmp_path / "bad_header.txt"
    transcript_path.write_text("not a valid earnings header\nOperator [1]\nTim Cook, Apple Inc. - CEO [2]", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not locate header metadata"):
        tp.parse_transcript_to_json(transcript_path)


def test_parse_transcript_to_json_wraps_speech_isolation_errors(tmp_path, minimal_valid_transcript_text, monkeypatch):
    transcript_path = tmp_path / "valid.txt"
    transcript_path.write_text(minimal_valid_transcript_text, encoding="utf-8")

    def _boom(*args, **kwargs):
        raise ValueError("bad speaker boundary")

    monkeypatch.setattr(tp, "get_speech", _boom)

    with pytest.raises(ValueError, match=r"Could not isolate speech for speaker boundary 1 -> 2"):
        tp.parse_transcript_to_json(transcript_path)


def test_parse_transcript_to_json_writes_non_empty_corporate_and_analysts(tmp_path):
    transcript_path = ROOT / "data/Transcripts/AAPL/2016-Apr-26-AAPL.txt"

    output_path = tp.parse_transcript_to_json(transcript_path, output_dir=tmp_path)

    with output_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["Corporate"]) > 0
    assert len(data["Analysts"]) > 0


def test_extract_corporate_participants_correctness_case_1_placeholder():
    transcript_path = ROOT / "data/Transcripts/NVDA/2016-Aug-11-NVDA.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_corporate = [
        ("Arnab Chanda", "NVIDIA Corporation", "VP of IR"),
        ("Jen-Hsun Huang", "NVIDIA Corporation", "President & CEO"),
        ("Colette Kress", "NVIDIA Corporation", "EVP & CFO")
    ]

    assert tp._extract_corporate_participants(transcript_df) == expected_corporate

def test_extract_corporate_participants_correctness_case_2_placeholder():
    transcript_path = ROOT / "data/Transcripts/AAPL/2016-Apr-26-AAPL.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_corporate = [
        ("Luca Maestri", "Apple Inc.", 'CFO'),
        ("Tim Cook", "Apple Inc.", 'CEO'),
        ("Nancy Paxton", 'Apple Inc.', 'Senior Director of IR')
    ]

    assert tp._extract_corporate_participants(transcript_df) == expected_corporate


def test_extract_conference_participants_correctness_case_1_placeholder():
    transcript_path = ROOT / "data/Transcripts/NVDA/2016-Aug-11-NVDA.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_conference = [
        ("Vijay Rakesh", "Mizuho Securities", "Analyst"),
        ("Steve  Smigie", "Raymond James", "Analyst"),
        ("Harlan Sur", "JPMorgan", "Analyst"),
        ("Blayne Curtis", "Barclays Capital", "Analyst"),
        ("C.J. Muse", "Evercore ISI", "Analyst"),
        ("Steven Chin", "UBS", "Analyst"),
        ("Craig Ellis", "B. Riley & Co.", "Analyst"),
        ("Vivek Arya", "BofA Merrill Lynch", "Analyst"),
        ("Mitch Steves", "RBC Capital Markets", "Analyst"),
        ("Kevin Cassidy", "Stifel Nicolaus", "Analyst"),
        ("Matt Ramsay", "Canaccord Genuity", "Analyst"),
        ("Joe Moore", "Morgan Stanley", "Analyst"),
        ("Rajvindra Gill", "Needham & Company", "Analyst"),
        ("Ambrish Srivastava", "BMO Capital Markets", "Analyst"),
        ("Mark Lipacis", "Jefferies LLC", "Analyst"),
        ("Ross Seymore", "Deutsche Bank", "Analyst"),
        ("Romit Shah", "Nomura Securities Co., Ltd.", "Analyst"),
        ("Brian Alger", "Raymond James", "Analyst"),
        ("Toshi Otani", "TransLink Capital", "Analyst"),
        ("Ian Ing", "MKM Partners", "Analyst"),
    ]

    assert tp._extract_conference_participants(transcript_df) == expected_conference


def test_extract_conference_participants_correctness_case_2_placeholder():
    transcript_path = ROOT / "data/Transcripts/AAPL/2016-Apr-26-AAPL.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_conference = [
        ("Katy Huberty", "Morgan Stanley", "Analyst"),
        ("Gene Munster", "Piper Jaffray & Co.", "Analyst"),
        ("Rod Hall", "JPMorgan", "Analyst"),
        ("Shannon Cross", "Cross Research", "Analyst"),
        ("Toni Sacconaghi", "Bernstein", "Analyst"),
        ("Simona Jankowski", "Goldman Sachs", "Analyst"),
        ("Steve Milunovich", "UBS", "Analyst"),
    ]

    assert tp._extract_conference_participants(transcript_df) == expected_conference


