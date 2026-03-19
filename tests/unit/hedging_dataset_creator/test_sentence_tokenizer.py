import json

import pandas as pd
import pytest

from hedging_dataset_creator import sentence_tokenizer as st


def test_normalize_name_handles_empty_and_whitespace():
    assert st._normalize_name(None) == ""
    assert st._normalize_name("  Tim Cook  ") == "tim cook"


@pytest.mark.parametrize("bad_path", [True, None, 123, 1.25, []])
def test_sentence_tokenizer_rejects_invalid_transcript_path_type(bad_path):
    with pytest.raises(TypeError, match="transcript_path must be a string or pathlib.Path"):
        st.sentence_tokenizer(bad_path)


def test_sentence_tokenizer_wraps_json_read_errors(monkeypatch):
    monkeypatch.setattr(st, "parse_transcript_to_json", lambda _: "/definitely/missing.json")

    with pytest.raises(OSError, match="Failed to read processed JSON file"):
        st.sentence_tokenizer("dummy.txt")


def test_sentence_tokenizer_rejects_invalid_json(monkeypatch, tmp_path):
    invalid_json = tmp_path / "bad.json"
    invalid_json.write_text("{not valid json", encoding="utf-8")

    monkeypatch.setattr(st, "parse_transcript_to_json", lambda _: invalid_json)

    with pytest.raises(ValueError, match="Invalid JSON in processed file"):
        st.sentence_tokenizer("dummy.txt")


def test_sentence_tokenizer_accepts_valid_input(monkeypatch, tmp_path):
    transcript_json = {
        "Corporate": [
            {"Name": "Alice", "Company": "Contoso Inc.", "Role": "CFO"},
            {"Name": "Bob", "Company": "Contoso Inc.", "Role": "CEO"},
        ],
        "Conference": [
            {"Name": "Nina", "Company": "Big Bank", "Role": "Analyst"},
            {"Name": "Alice", "Company": "JP Morgan", "Role": "Analyst"},
            {"Name": "Aydin", "Company": "Goldman Sachs", "Role": "Analyst"}
        ],
        "presentation": [
            {
                "Speaker": "Alice",
                "Company": "Contoso Inc.",
                "Role": "CFO",
                "Speech": "We might beat guidance. Revenue is stable.",
            },
            {
                "Speaker": "Operator",
                "Company": "",
                "Role": "",
                "Speech": "Next question.",
            },
        ],
        "qa": [
            {
                "Speaker": "Bob",
                "Company": "Contoso Inc.",
                "Role": "CEO",
                "Speech": "We expect growth around 5%. This is a 2% increase over the previous quarter.",
            },
            {
                "Speaker": "Nina",
                "Company": "Big Bank",
                "Role": "Analyst",
                "Speech": "Can you expand on margins?",
            },
            {
                "Speaker": "Aydin",
                "Company": "Goldman Sachs",
                "Role": "Analyst",
                "Speech": "Should be excluded.",
            },
            {
                "Speaker": "Alice",
                "Company": "Contoso Inc.",
                "Role": "CFO",
                "Speech": "Revenue was at an all time high.",
            },
            {
                "Speaker": "Alice",
                "Company": "JP Morgan",
                "Role": "Analyst",
                "Speech": "Thanks.",
            },
        ],
    }
    processed_path = tmp_path / "processed.json"
    processed_path.write_text(json.dumps(transcript_json), encoding="utf-8")

    monkeypatch.setattr(st, "parse_transcript_to_json", lambda _: processed_path)
    monkeypatch.setattr(st, "sent_tokenize", lambda text: [s.strip() for s in text.split(".") if s.strip()])

    result = st.sentence_tokenizer("dummy.txt")

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["sentence"]
    assert result["sentence"].tolist() == [
        "We might beat guidance",
        "Revenue is stable",
        "We expect growth around 5%",
        "This is a 2% increase over the previous quarter",
        "Revenue was at an all time high"
    ]
