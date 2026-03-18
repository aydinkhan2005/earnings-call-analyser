import pytest
import pandas as pd
from pathlib import Path

from speech_parser.speech_isolator import get_speech


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def sample_transcript() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "line": [
                "Operator    [13]",           # speaker row 1
                "Katy Huberty with Morgan Stanley. ",      # between 1 and 2
                "Katy Huberty,  Morgan Stanley - Analyst    [14]",             # speaker row 2
                "Yes, thank you. First for Luca. \
                This is the worst gross margin guide in a year and a half or so, and over the \
                last couple of quarters, you have talked about number of tailwinds including component cost, \
                the lower accounting deferrals that went into effect in September. \
                You just mentioned the services margins are above corporate average. \
                So the question is, are some of those tailwinds winding down? \
                Or is a significant guide down in gross margin for the June quarter entirely related to volume \
                and the 5 SE? And then I have a follow-up for Tim. ",        # between 2 and 3
                "Luca Maestri,  Apple Inc. - CFO    [15]",           # speaker row 3
                "Final note",          # between 3 and 4
                "Katy Huberty,  Morgan Stanley - Analyst    [16]",             # speaker row 4
            ]
        }
    )


def test_none_dataframe():
    with pytest.raises(ValueError, match='DataFrame is NoneType'):
        get_speech(None, 1, 2)


@pytest.mark.parametrize(
    "speaker_1, speaker_2",
    [
        ("a", 2),
        (1, "b"),
        (1.5, 2),
        (1, None),
        (True, 2),
        (1, False),
        (True, False),
    ],
)
def test_non_integer_speaker_params_raise_type_error(sample_transcript, speaker_1, speaker_2):
    with pytest.raises(TypeError, match='SPEAKER_1 and SPEAKER_2 must be integers.'):
        get_speech(sample_transcript, speaker_1, speaker_2)


@pytest.mark.parametrize("speaker_1, speaker_2", [(1, 3), (2, 4), (2, 2)])
def test_non_adjacent_speaker_params_raise_value_error(sample_transcript, speaker_1, speaker_2):
    with pytest.raises(ValueError, match='SPEAKER_1 and SPEAKER_2 must be adjacent speaker numbers.'):
        get_speech(sample_transcript, speaker_1, speaker_2)


@pytest.mark.parametrize("speaker_1, speaker_2", [(0, 1), (1, 0), (1, 9), (9, 1)])
def test_out_of_range_speaker_params_raise_index_error(sample_transcript, speaker_1, speaker_2):
    with pytest.raises(IndexError, match=r'SPEAKER_1 and SPEAKER_2 must be between 1 and \d+\.'):
        get_speech(sample_transcript, speaker_1, speaker_2)


def test_returns_only_non_whitespace_rows_with_letters():
    transcript = pd.DataFrame(
        {
            "line": [
                "--------------------------------------------------------------------------------",
                "Operator    [1]                                                                 ",
                "--------------------------------------------------------------------------------",
                "                                                                                ",
                "Good day, everyone, and welcome to the Apple, \
                Incorporated second-quarter FY16 earnings release conference call. \
                Today's call is being recorded. At this time, for opening remarks and introductions, \
                I would like to turn the call over Nancy Paxton, Senior Director of Investor Relations. \
                Please go ahead, ma'am. ",
                "                                                                                ",
                "--------------------------------------------------------------------------------",
                "Nancy Paxton,  Apple Inc. - Senior Director of IR    [2]                        ",
                "--------------------------------------------------------------------------------",
            ]
        }
    )

    result = get_speech(transcript, 1, 2)

    assert result == [
        "Good day, everyone, and welcome to the Apple, \
                Incorporated second-quarter FY16 earnings release conference call. \
                Today's call is being recorded. At this time, for opening remarks and introductions, \
                I would like to turn the call over Nancy Paxton, Senior Director of Investor Relations. \
                Please go ahead, ma'am.",
    ]
    assert all(s.strip() != "" for s in result)
    assert all(any(c.isalpha() for c in s) for s in result)


def test_reversed_adjacent_inputs_return_same_result(sample_transcript):
    forward = get_speech(sample_transcript, 1, 2)
    reversed_ = get_speech(sample_transcript, 2, 1)
    assert forward == reversed_


def test_missing_line_column_raises_key_error():
    transcript = pd.DataFrame({"text": ["some content [1]", "hello", "more content [2]"]})
    with pytest.raises(KeyError):
        get_speech(transcript, 1, 2)


def test_less_than_two_speaker_rows_returns_empty_list():
    transcript = pd.DataFrame(
        {
            "line": [
                "Opening remarks",
                "Operator [1]",
                "Closing remarks",
            ]
        }
    )

    result = get_speech(transcript, 1, 2)

    assert result == []


def test_adjacent_speaker_rows_with_no_valid_content_returns_empty_list():
    transcript = pd.DataFrame(
        {
            "line": [
                "Operator [1]",
                "   ",
                "--------------------",
                "Nancy Paxton, Apple Inc. - Senior Director of IR [2]",
            ]
        }
    )

    result = get_speech(transcript, 1, 2)

    assert result == []


def test_null_lines_between_speakers_are_ignored():
    transcript = pd.DataFrame(
        {
            "line": [
                "Operator [1]",
                None,
                pd.NA,
                "   ",
                "Actual spoken content.",
                "Nancy Paxton, Apple Inc. - Senior Director of IR [2]",
            ]
        }
    )

    result = get_speech(transcript, 1, 2)

    assert result == ["Actual spoken content."]


def test_content_line_with_bracket_number_is_not_treated_as_speaker_row():
    transcript = pd.DataFrame(
        {
            "line": [
                "Operator [1]",
                "We saw growth of [2] percentage points in services.",
                "Tim Cook, Apple Inc. - CEO [2]",
            ]
        }
    )

    result = get_speech(transcript, 1, 2)

    assert result == ["We saw growth of [2] percentage points in services."]


@pytest.mark.parametrize(
    "file_path, speaker_1, speaker_2, expected_lines",
    [
        (
            "data/Transcripts/AAPL/2016-Apr-26-AAPL.txt",
            45,
            46,
            ['Yes, thanks for fitting me in. I wanted to start with a general, more general question. I guess, Tim, this one is aimed at you. As you think about where you thought things were going to head last quarter, when you reported to us, and how it\'s changed this quarter, obviously it\'s kind of a disappointing demand environment. Can you just help us understand what maybe the top two or three things are that have changed? And so as we walk away from this, we understand what the differences are, and what the direction of change is? Then I have a follow-up.'],
        ),
        (
            "data/Transcripts/AMZN/2017-Feb-02-AMZN.txt",
            1,
            2,
            ['Good day, everyone, and welcome to the Amazon.com Q4 2016 financial results teleconference.', '(Operator Instructions)', 'Today\'s call is being recorded. For opening remarks, I will be turning the call over to the Director of Investor Relations, Darin Manney. Please go ahead.'],
        ),
        (
            "data/Transcripts/AMD/2020-Jul-28-AMD.txt",
            6,
            7,
            ['(Operator Instructions) Our first question today is coming from Mark Lipacis from Jefferies.'],
        ),
        (
            "data/Transcripts/AMD/2020-Jul-28-AMD.txt",
            69,
            70,
            ['Thank you, everybody, for joining the call today. We appreciate it, and we look forward to seeing many of you virtually throughout the quarter.', 'Operator, if you can close the call, please.'],
        )
    ],
)
def test_correct_rows_returned_from_real_transcript(file_path, speaker_1, speaker_2, expected_lines):
    text = (ROOT / file_path).read_text(encoding="utf-8", errors="replace")
    transcript = pd.DataFrame({"line": text.splitlines()})

    result = get_speech(transcript, speaker_1, speaker_2)

    assert result == expected_lines

