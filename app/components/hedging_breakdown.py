import joblib
import streamlit as st
from pathlib import Path

import pandas as pd

from labellers.sentence_tokenizer import sentence_tokenizer


PIPELINE_PATH = Path(__file__).resolve().parents[2] / "models" / "tfidf_lr.pkl"


def _render_colored_metric(col, label: str, rate_value: float | str):
    """Render a metric with color-coded percentage based on hedge rate."""
    if isinstance(rate_value, str) and rate_value == "N/A":
        col.metric(label, rate_value)
        return

    rate_num = float(rate_value.rstrip("%"))
    if rate_num > 50:
        color = "red"
    elif rate_num > 25:
        color = "orange"
    else:
        color = "white"

    col.markdown(
        f"""
        <div>
            <div style='font-size: 14px; color: white;'>{label}</div>
            <div style='font-size: 32px; color: {color}; font-weight: bold;'>{rate_value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
        _render_colored_metric(col11, "Presentation", f"{hedge_rate:.1f}%")
    else:
        _render_colored_metric(col11, "Presentation", "N/A")

    if len(qa_rows) > 0:
        qa_hedge_rate = 100 * float((qa_rows == 1).mean())
        _render_colored_metric(col12, "Q&A", f"{qa_hedge_rate:.1f}%")
    else:
        _render_colored_metric(col12, "Q&A", "N/A")
    st.write("")
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
            _render_colored_metric(col21, role_1, f"{role_1_rate:.1f}%")

            if i + 1 < len(role_items):
                role_2, role_2_rate = role_items[i + 1]
                _render_colored_metric(col22, role_2, f"{role_2_rate:.1f}%")
            else:
                col22.metric("", "")

    return sentences_with_preds
