import pandas as pd
import pytest

from speech_parser.speaker_isolator import get_speaker


@pytest.fixture
def sample_transcript() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "line": [
                "Opening line",
                "Operator [1]",
                "Content between speakers",
                "Tim Cook, Apple Inc. - CEO [2]",
            ]
        }
    )


def test_get_speaker_returns_first_speaker_line(sample_transcript):
    assert get_speaker(sample_transcript, 1) == "Operator [1]"


def test_none_transcript_raises_value_error():
    with pytest.raises(ValueError, match="DataFrame is NoneType"):
        get_speaker(None, 1)


@pytest.mark.parametrize("speaker_index", ["1", 1.5, None, True, False])
def test_invalid_speaker_index_type_raises_type_error(sample_transcript, speaker_index):
    with pytest.raises(TypeError, match="SPEAKER_INDEX must be an integer."):
        get_speaker(sample_transcript, speaker_index)


def test_missing_line_column_raises_key_error():
    transcript = pd.DataFrame({"text": ["Operator [1]", "Tim [2]"]})
    with pytest.raises(KeyError):
        get_speaker(transcript, 1)


@pytest.mark.parametrize("speaker_index", [0, 3, -1])
def test_out_of_range_speaker_index_raises_index_error(sample_transcript, speaker_index):
    with pytest.raises(IndexError, match=r"SPEAKER_INDEX must be between 1 and \d+\."):
        get_speaker(sample_transcript, speaker_index)


def test_no_speaker_rows_found_raises_value_error():
    transcript = pd.DataFrame({"line": ["Hello", "World"]})
    with pytest.raises(ValueError, match="No speaker rows found in transcript."):
        get_speaker(transcript, 1)


def test_content_line_with_bracket_number_is_not_treated_as_speaker():
    transcript = pd.DataFrame(
        {
            "line": [
                "Operator [1]",
                "We saw growth of [2] percentage points in services.",
                "Tim Cook, Apple Inc. - CEO [2]",
            ]
        }
    )

    assert get_speaker(transcript, 2) == "Tim Cook, Apple Inc. - CEO [2]"

