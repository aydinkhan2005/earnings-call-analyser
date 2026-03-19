from pathlib import Path
from types import SimpleNamespace

from speech_parser import transcript_parser as tp
from hedging_dataset_creator import sentence_tokenizer as st
from hedging_dataset_creator import hedging_labeller as hl


ROOT = Path(__file__).resolve().parents[3]

TRANSCRIPT_PATH = "2017-Apr-19-ASML.txt"


def test_hedging_dataset_creation_pipeline(monkeypatch, tmp_path):
    # Parse transcript to JSON
    json_path = tp.parse_transcript_to_json(
        ROOT / "data" / "Transcripts" / "ASML" / TRANSCRIPT_PATH,
        output_dir=tmp_path,
    )
    assert json_path.name == "2017-Apr-19-ASML.json"

    # Tokenize sentences from JSON, monkeypatching the internal parser call
    monkeypatch.setattr(st, "parse_transcript_to_json", lambda _: json_path)
    sentences_df = st.sentence_tokenizer(json_path)

    # Label sentences using a DummyClient via monkeypatch
    class DummyClient:
        def __init__(self):
            self.messages = self

        def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(text="1")])

    monkeypatch.setattr(hl.anthropic, "Anthropic", lambda api_key=None: DummyClient())

    output_csv = Path(__file__).resolve().parent / "test_labelled_sentences.csv"
    result = hl.hedging_labeller(sentences_df, output_csv_path=output_csv)

    assert "sentence" in result.columns
    assert "isHedge" in result.columns
    assert output_csv.exists()
