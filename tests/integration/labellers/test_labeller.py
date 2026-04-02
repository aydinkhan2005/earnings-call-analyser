import asyncio
import re
from pathlib import Path
from types import SimpleNamespace

from speech_parser import transcript_parser as tp
from labellers import sentence_tokenizer as st
from labellers import sentence_classifier as hl
from labellers import topic_classifier as tc


ROOT = Path(__file__).resolve().parents[3]

TRANSCRIPT_PATH = "2017-Apr-19-ASML.txt"


def test_hedging_dataset_creation_pipeline(monkeypatch):
    # Parse transcript to in-memory JSON data
    data = tp.parse_transcript_to_data(
        ROOT / "data" / "Transcripts" / "ASML" / TRANSCRIPT_PATH,
    )
    assert isinstance(data, dict)

    # Tokenize sentences from parsed data
    sentences_df = st.sentence_tokenizer(data)

    # Label sentences using a DummyClient via monkeypatch
    class DummyMessages:
        async def create(self, **kwargs):
            prompt = kwargs["messages"][0]["content"]

            # Keep only the final sentence block so numbered examples don't inflate counts.
            if "SENTENCES TO LABEL:" in prompt:
                section = prompt.split("SENTENCES TO LABEL:", 1)[1]
            elif "Sentences:" in prompt:
                section = prompt.split("Sentences:", 1)[1].split("Return ONLY", 1)[0]
            else:
                section = prompt

            count = len(re.findall(r"(?m)^\s*\d+\.\s+.+$", section))
            labels = ",".join(["1"] * count)
            return SimpleNamespace(content=[SimpleNamespace(text=labels)])

    class DummyClient:
        def __init__(self):
            self.messages = DummyMessages()

    monkeypatch.setattr(hl.anthropic, "AsyncAnthropic", lambda api_key=None: DummyClient())

    # Test hedging labeller
    result_hedging = asyncio.run(hl.sentence_labeller(sentences_df, hl.get_hedging_on_sentence, "isHedge", semaphore=asyncio.Semaphore(10)))

    assert "sentence" in result_hedging.columns
    assert "isHedge" in result_hedging.columns

    # Test topic labeller
    result_topic = asyncio.run(hl.sentence_labeller(sentences_df, tc.get_topic_on_sentences, "topic", semaphore=asyncio.Semaphore(10)))

    assert "sentence" in result_topic.columns
    assert "topic" in result_topic.columns
