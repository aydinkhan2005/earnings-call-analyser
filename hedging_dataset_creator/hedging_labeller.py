from __future__ import annotations

import os
from pathlib import Path

import anthropic
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv

def get_hedging_on_sentence(sentence):
    prompt = f"""You are a financial language expert specialising in earnings call analysis.

    Label the following sentence as hedging (1) or not hedging (0).

    Hedging language includes any of the following:
    - Modal verbs expressing uncertainty: may, might, could, would, should
    - Epistemic verbs: believe, think, expect, anticipate, feel, assume
    - Approximators: approximately, around, roughly, about
    - Probability expressions: likely, unlikely, possibly, probably, perhaps
    - Conditional framing: assuming, subject to, if, provided that
    - Opportunity hedges: potential, opportunity, possibility
    - Attribution hedges: based on current trends, according to our estimates
    - Distancing language: it appears, it seems, there is reason to believe
    - Negative hedges: cannot guarantee, no assurance, cannot predict

    Important:
    - Not every modal verb is hedging. "We will pay the dividend"
    is NOT hedging. "We believe we will pay the dividend" IS hedging.
    Direct factual statements about past results are NOT hedging.

    Sentences reporting figures or statistics using words like "estimated," "approximately," or "around" ARE hedging -- the speaker is deliberately qualifying the precision of the claim.

    Sentence: "{sentence}"

    You must reply with ONLY a single character: 0 or 1. Any other response is invalid."""

    return prompt


def hedging_labeller(
    sentences_df,
    model="claude-haiku-4-5-20251001",
    output_csv_path="labelled_sentences.csv",
    save_every=50,
):
    load_dotenv()
    if not isinstance(sentences_df, pd.DataFrame):
        raise TypeError("sentences_df must be a pandas DataFrame")
    if "sentence" not in sentences_df.columns:
        raise ValueError("sentences_df must include a 'sentence' column")
    if not isinstance(save_every, int) or save_every <= 0:
        raise ValueError("save_every must be a positive integer")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    sentences_with_labels = sentences_df.copy()
    labels = []
    # current list of sentence-hedge label pairs
    checkpoint_buffer = []
    output_path = Path(output_csv_path)
    is_first_write = True
    sentence_values = sentences_with_labels["sentence"].tolist()

    for idx, sentence in enumerate(
        tqdm(
            sentence_values,
            total=len(sentence_values),
            desc="Labelling hedging sentences",
            unit="sentence",
        ),
        start=1,
    ):
        if not pd.isna(sentence):
            sentence_text = str(sentence)
            response = client.messages.create(
                model=model,
                max_tokens=5,
                messages=[{"role": "user", "content": get_hedging_on_sentence(sentence_text)}],
            )
            label_text = response.content[0].text.strip()
        else:
            label_text = np.nan
            sentence_text = ""

        labels.append(label_text)

        checkpoint_buffer.append({"sentence": sentence_text, "isHedge": label_text})
        if idx % save_every == 0:
            pd.DataFrame(checkpoint_buffer).to_csv(
                output_path,
                mode="w" if is_first_write else "a",
                header=is_first_write,
                index=False,
            )
            checkpoint_buffer.clear()
            is_first_write = False

    if checkpoint_buffer:
        pd.DataFrame(checkpoint_buffer).to_csv(
            output_path,
            mode="w" if is_first_write else "a",
            header=is_first_write,
            index=False,
        )

    sentences_with_labels["isHedge"] = labels
    return sentences_with_labels

