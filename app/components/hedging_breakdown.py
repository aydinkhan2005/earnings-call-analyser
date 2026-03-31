import streamlit as st
from pathlib import Path
import pickle

import pandas as pd

from hedging_dataset_creator.sentence_tokenizer import sentence_tokenizer


PIPELINE_PATH = Path(__file__).resolve().parents[2] / "models" / "tfidf_lr.pkl"


def render_hedging_breakdown(transcript):
    """
    Gives a hedging rate breakdown on a transcript using a Logistic Regression
    classifier.
    :param transcript: Dict/JSON transcript in memory
    :return:
    """
    if not isinstance(transcript, dict):
        st.error("Invalid transcript object. Expected a JSON object (dict).")
        return pd.DataFrame(columns=["sentence", "isHedge"])

    if "presentation" not in transcript:
        st.error("Transcript is missing required field: 'presentation'.")
        return pd.DataFrame(columns=["sentence", "isHedge"])

    sentences = sentence_tokenizer(transcript)
    if "sentence" not in sentences.columns:
        st.error("Tokenizer output is missing required column: 'sentence'.")
        return pd.DataFrame(columns=["sentence", "isHedge"])

    if not PIPELINE_PATH.exists():
        st.error(f"Model pipeline file not found: {PIPELINE_PATH}")
        return pd.DataFrame(columns=["sentence", "isHedge"])
    data = PIPELINE_PATH.read_bytes()
    try:
        with PIPELINE_PATH.open("rb") as f:
            pipeline = pickle.load(f)
        predictions = pipeline.predict(sentences["sentence"])
    except Exception as exc:
        st.error(f"Failed to run hedging classifier: {exc}")
        return pd.DataFrame(columns=["sentence", "isHedge"])

    sentences_with_preds = sentences.copy()
    sentences_with_preds["isHedge"] = predictions

    st.subheader("Hedging Rate Breakdown")
    if len(sentences_with_preds) > 0:
        hedge_rate = 100 * float((sentences_with_preds["isHedge"] == 1).mean())
        st.metric("Overall", f"{hedge_rate:.1f}%")
    else:
        st.metric("Overall", "N/A")

    st.text_area("Ask AI Follow-Up Questions", height=100)
    return sentences_with_preds
