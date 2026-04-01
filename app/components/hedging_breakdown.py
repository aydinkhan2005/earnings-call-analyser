import joblib
import streamlit as st
from pathlib import Path

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
    try:
        with PIPELINE_PATH.open("rb") as f:
            pipeline = joblib.load(f)
        predictions = pipeline.predict(sentences["sentence"])
    except Exception as exc:
        st.error(f"Failed to run hedging classifier: {exc}")
        return pd.DataFrame(columns=["sentence", "isHedge"])

    sentences_with_preds = sentences.copy()
    sentences_with_preds["isHedge"] = predictions

    presentation_mask = sentences_with_preds["section"] == 1
    presentation_rows = sentences_with_preds.loc[presentation_mask, "isHedge"]

    qa_mask = sentences_with_preds["section"] == 0
    qa_rows = sentences_with_preds.loc[qa_mask, "isHedge"]

    st.subheader("Hedging Rate Breakdown")
    col11, col12 = st.columns(2)

    if len(presentation_rows) > 0:
        hedge_rate = 100 * float((presentation_rows == 1).mean())
        col11.metric("Presentation", f"{hedge_rate:.1f}%")
    else:
        col11.metric("Presentation", "N/A")

    if len(qa_rows) > 0:
        qa_hedge_rate = 100 * float((qa_rows == 1).mean())
        col12.metric("Q&A", f"{qa_hedge_rate:.1f}%")
    else:
        col12.metric("Q&A", "N/A")


    st.subheader("Hedging Rate By Role")
    valid_role_rows = sentences_with_preds[sentences_with_preds["Role"].astype(str).str.strip() != ""]
    if len(valid_role_rows) == 0:
        st.info("No role data available for hedging-rate breakdown.")
    else:
        role_rates = (
            valid_role_rows.assign(Role=valid_role_rows["Role"].astype(str).str.strip())
            .groupby("Role")["isHedge"]
            .apply(lambda s: 100 * float((s == 1).mean()))
            .sort_values(ascending=False)
        )
        role_items = list(role_rates.items())

        for i in range(0, len(role_items), 2):
            col21, col22 = st.columns(2)

            role_1, role_1_rate = role_items[i]
            col21.metric(role_1, f"{role_1_rate:.1f}%")

            if i + 1 < len(role_items):
                role_2, role_2_rate = role_items[i + 1]
                col22.metric(role_2, f"{role_2_rate:.1f}%")
            else:
                col22.metric("", "")

    st.text_area("Ask AI Follow-Up Questions", height=100)
    return sentences_with_preds
