import asyncio
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

    # Tokenize sentences from JSON
    sentences_df = st.sentence_tokenizer(json_path)

    # Label sentences using a DummyClient via monkeypatch
    class DummyMessages:
        async def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(text="1")])

    class DummyClient:
        def __init__(self):
            self.messages = DummyMessages()

    monkeypatch.setattr(hl.anthropic, "AsyncAnthropic", lambda api_key=None: DummyClient())

    result = asyncio.run(hl.hedging_labeller(sentences_df, semaphore=asyncio.Semaphore(10)))

    assert "sentence" in result.columns
    assert "isHedge" in result.columns
