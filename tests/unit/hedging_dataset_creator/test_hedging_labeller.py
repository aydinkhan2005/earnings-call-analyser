import asyncio
from types import SimpleNamespace

import pandas as pd
import pytest

from hedging_dataset_creator import hedging_labeller as hl


@pytest.mark.parametrize("bad_input", [None, [], {"sentence": ["text"]}, "text"])
# hedging_labeller should raise a TypeError if a DataFrame is not passed as the parameter
def test_hedging_labeller_rejects_non_dataframe_input(bad_input):
    with pytest.raises(TypeError, match="sentences_df must be a pandas DataFrame"):
        asyncio.run(hl.hedging_labeller(bad_input))

# hedging_labeller should ensure that the input DataFrame passed in has a column called "sentence"
def test_hedging_labeller_requires_sentence_column():
    with pytest.raises(ValueError, match="sentences_df must include a 'sentence' column"):
        asyncio.run(hl.hedging_labeller(pd.DataFrame({"text": ["hello"]})))

# function should output a DataFrame with columns ["sentence", "isHedge"] and output CSV file should exist
def test_hedging_labeller_accepts_valid_input_with_mocked_client(monkeypatch, tmp_path):
    class DummyMessages:
        def __init__(self, labels):
            self.labels = labels
            self.idx = 0

        async def create(self, **kwargs):
            label = self.labels[self.idx]
            self.idx += 1
            return SimpleNamespace(content=[SimpleNamespace(text=label)])

    class DummyClient:
        def __init__(self, labels):
            self.messages = DummyMessages(labels)

    monkeypatch.setattr(hl.anthropic, "AsyncAnthropic", lambda api_key=None: DummyClient(["1", "0"]))

    result = asyncio.run(
        hl.hedging_labeller(
            pd.DataFrame({"sentence": ["We may see stronger demand.", None]}),
            semaphore=asyncio.Semaphore(10),
        )
    )
    # DataFrame has the necessary columns
    assert list(result.columns) == ["sentence", "isHedge"]
