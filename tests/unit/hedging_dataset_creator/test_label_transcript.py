import asyncio

import pytest

from hedging_dataset_creator import label_transcript as lt


def test_label_transcript_sentences_rejects_missing_transcript_path(tmp_path):
    missing_path = tmp_path / "does-not-exist.txt"

    with pytest.raises(FileNotFoundError, match="Transcript file does not exist"):
        asyncio.run(lt.label_transcript_sentences(missing_path))


def test_label_transcript_sentences_returns_early_if_processed_csv_exists(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    transcript_path = tmp_path / "data" / "Transcripts" / "AMD" / "2016-Apr-21-AMD.txt"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text("dummy transcript", encoding="utf-8")

    existing_csv = tmp_path / "data" / "hedging_dataset" / "AMD" / "2016-Apr-21-AMD.csv"
    existing_csv.parent.mkdir(parents=True, exist_ok=True)
    existing_csv.write_text("sentence,isHedge\n", encoding="utf-8")

    def should_not_call_parse(*args, **kwargs):
        raise AssertionError("parse_transcript_to_json should not be called when CSV exists")

    def should_not_call_tokenizer(*args, **kwargs):
        raise AssertionError("sentence_tokenizer should not be called when CSV exists")

    async def should_not_call_labeller(*args, **kwargs):
        raise AssertionError("hedging_labeller should not be called when CSV exists")

    monkeypatch.setattr(lt, "parse_transcript_to_json", should_not_call_parse)
    monkeypatch.setattr(lt, "sentence_tokenizer", should_not_call_tokenizer)
    monkeypatch.setattr(lt, "hedging_labeller", should_not_call_labeller)

    result = asyncio.run(lt.label_transcript_sentences(transcript_path))

    assert result is None


