from types import SimpleNamespace

import pandas as pd
import pytest

from hedging_dataset_creator import hedging_labeller as hl


@pytest.mark.parametrize("bad_input", [None, [], {"sentence": ["text"]}, "text"])
def test_hedging_labeller_rejects_non_dataframe_input(bad_input):
    with pytest.raises(TypeError, match="sentences_df must be a pandas DataFrame"):
        hl.hedging_labeller(bad_input)


def test_hedging_labeller_requires_sentence_column():
    with pytest.raises(ValueError, match="sentences_df must include a 'sentence' column"):
        hl.hedging_labeller(pd.DataFrame({"text": ["hello"]}))


@pytest.mark.parametrize("save_every", [0, -1, 1.5, "2", None])
def test_hedging_labeller_requires_positive_integer_save_every(save_every):
    with pytest.raises(ValueError, match="save_every must be a positive integer"):
        hl.hedging_labeller(pd.DataFrame({"sentence": ["hello"]}), save_every=save_every)


def test_hedging_labeller_raises_for_unexpected_model_label(monkeypatch, tmp_path):
    class DummyClient:
        def __init__(self):
            self.messages = self

        def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(text="unexpected")])

    monkeypatch.setattr(hl.anthropic, "Anthropic", lambda api_key=None: DummyClient())

    with pytest.raises(ValueError, match="Unexpected label returned by model"):
        hl.hedging_labeller(
            pd.DataFrame({"sentence": ["We may see stronger demand."]}),
            output_csv_path=tmp_path / "out.csv",
            save_every=1,
        )


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

    assert list(result.columns) == ["sentence", "isHedge"]
    assert result["isHedge"].tolist() == [1, 0]
    assert output_csv.exists()
