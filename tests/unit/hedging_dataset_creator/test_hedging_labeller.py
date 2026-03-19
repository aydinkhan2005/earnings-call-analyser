from types import SimpleNamespace

import pandas as pd
import pytest

from hedging_dataset_creator import hedging_labeller as hl


@pytest.mark.parametrize("bad_input", [None, [], {"sentence": ["text"]}, "text"])
# hedging_labeller should raise a TypeError if a DataFrame is not passed as the parameter
def test_hedging_labeller_rejects_non_dataframe_input(bad_input):
    with pytest.raises(TypeError, match="sentences_df must be a pandas DataFrame"):
        hl.hedging_labeller(bad_input)

# hedging_labeller should ensure that the input DataFrame passed in has a column called "sentence"
def test_hedging_labeller_requires_sentence_column():
    with pytest.raises(ValueError, match="sentences_df must include a 'sentence' column"):
        hl.hedging_labeller(pd.DataFrame({"text": ["hello"]}))


@pytest.mark.parametrize("save_every", [0, -1, 1.5, "2", None])
# user can only pass in a positive number for how often results should be saved
def test_hedging_labeller_requires_positive_integer_save_every(save_every):
    with pytest.raises(ValueError, match="save_every must be a positive integer"):
        hl.hedging_labeller(pd.DataFrame({"sentence": ["hello"]}), save_every=save_every)

# function should output a DataFrame with columns ["sentence", "isHedge"] and output CSV file should exist
def test_hedging_labeller_accepts_valid_input_with_mocked_client(monkeypatch, tmp_path):
    class DummyClient:
        def __init__(self, labels):
            self.labels = labels
            self.idx = 0
            self.messages = self

        def create(self, **kwargs):
            label = self.labels[self.idx]
            self.idx += 1
            return SimpleNamespace(content=[SimpleNamespace(text=label)])

    monkeypatch.setattr(hl.anthropic, "Anthropic", lambda api_key=None: DummyClient(["1", "0"]))

    output_csv = tmp_path / "labelled.csv"
    result = hl.hedging_labeller(
        pd.DataFrame({"sentence": ["We may see stronger demand.", None]}),
        output_csv_path=output_csv,
        save_every=1,
    )
    # DataFrame has the necessary columns
    assert list(result.columns) == ["sentence", "isHedge"]
    # Output CSV file should exist
    assert output_csv.exists()
    written = pd.read_csv(output_csv, keep_default_na=False)
    # NoneType sentences should be rewritten as empty strings
    assert written["sentence"].tolist() == ["We may see stronger demand.", ""]
