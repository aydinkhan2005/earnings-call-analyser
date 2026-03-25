import pytest
import json
from pathlib import Path

from speech_parser import transcript_parser as tp


ROOT = Path(__file__).resolve().parents[3]


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

def test_parse_transcript_to_json_rejects_bool_transcript_path():
    with pytest.raises(TypeError, match="transcript_path must be a string or pathlib.Path"):
        tp.parse_transcript_to_data(True)


def test_parse_transcript_to_json_rejects_non_path_type():
    with pytest.raises(TypeError, match="transcript_path must be a string or pathlib.Path"):
        tp.parse_transcript_to_data(123)


def test_parse_transcript_to_json_rejects_non_txt_extension(tmp_path):
    bad_path = tmp_path / "transcript.csv"
    with pytest.raises(ValueError, match="must point to a .txt file"):
        tp.parse_transcript_to_data(bad_path)


def test_parse_transcript_to_json_rejects_missing_file(tmp_path):
    missing_txt = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        tp.parse_transcript_to_data(missing_txt)


def test_parse_transcript_to_json_rejects_directory_path(tmp_path):
    txt_dir = tmp_path / "fake.txt"
    txt_dir.mkdir()
    with pytest.raises(ValueError, match="is not a file"):
        tp.parse_transcript_to_data(txt_dir)


def test_parse_transcript_to_json_rejects_whitespace_only_file(tmp_path):
    transcript_path = tmp_path / "empty.txt"
    transcript_path.write_text("   \n\t\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty after stripping whitespace"):
        tp.parse_transcript_to_data(transcript_path)


def test_parse_transcript_to_json_rejects_unexpected_output_dir_keyword(tmp_path, minimal_valid_transcript_text):
    transcript_path = tmp_path / "valid.txt"
    transcript_path.write_text(minimal_valid_transcript_text, encoding="utf-8")

    with pytest.raises(TypeError, match="unexpected keyword argument 'output_dir'"):
        tp.parse_transcript_to_data(transcript_path, output_dir=False)


def test_parse_transcript_to_json_rejects_missing_header_metadata(tmp_path):
    transcript_path = tmp_path / "bad_header.txt"
    transcript_path.write_text("not a valid earnings header\nOperator [1]\nTim Cook, Apple Inc. - CEO [2]", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not locate header metadata"):
        tp.parse_transcript_to_data(transcript_path)


def test_parse_transcript_to_json_wraps_speech_isolation_errors(tmp_path, minimal_valid_transcript_text, monkeypatch):
    transcript_path = tmp_path / "valid.txt"
    transcript_path.write_text(minimal_valid_transcript_text, encoding="utf-8")

    def _boom(*args, **kwargs):
        raise ValueError("bad speaker boundary")

    monkeypatch.setattr(tp, "get_speech", _boom)

    with pytest.raises(ValueError, match=r"Could not isolate speech for speaker boundary 1 -> 2"):
        tp.parse_transcript_to_data(transcript_path)


def test_parse_transcript_to_json_writes_non_empty_corporate_and_conference():
    transcript_path = ROOT / "data/Transcripts/AAPL/2016-Apr-26-AAPL.txt"

    data = tp.parse_transcript_to_data(transcript_path)

    assert len(data["Corporate"]) > 0
    assert len(data["Conference"]) > 0

def test_parse_transcript_to_json_end_to_end_matches_expected_json():
    transcript_path = ROOT / "data/Transcripts/INTC/2017-Jan-26-INTC.txt"
    expected_json_path = ROOT / "tests/integration/speech_parser/EXPECTED_OUTPUT.json"

    if not expected_json_path.exists():
        pytest.skip(f"Expected JSON fixture not found: {expected_json_path}")

    actual_data = tp.parse_transcript_to_data(transcript_path)

    with expected_json_path.open("r", encoding="utf-8") as f:
        expected_data = json.load(f)

    assert actual_data == expected_data