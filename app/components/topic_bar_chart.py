from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
import plotly.express as px

from labellers.sentence_tokenizer import sentence_tokenizer
from components.constants import topic


TOPIC_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "topic_classifier.pkl"


def _topic_label_from_id(topic_id):
    # Support both 0-based and 1-based model outputs.
    try:
        idx = int(topic_id)
    except (TypeError, ValueError):
        return str(topic_id)

    if 0 <= idx < len(topic):
        return topic[idx]
    if 1 <= idx <= len(topic):
        return topic[idx - 1]
    return str(topic_id)


def render_topic_bar_chart(transcript):
    if not isinstance(transcript, dict):
        st.error("Invalid transcript object. Expected a JSON object (dict).")
        return

    if "presentation" not in transcript:
        st.error("Transcript is missing required field: 'presentation'.")
        return

    try:
        sentences_df = sentence_tokenizer(transcript)
    except Exception as exc:
        st.error(f"Failed to tokenize transcript: {exc}")
        return

    if not TOPIC_MODEL_PATH.exists():
        st.error(f"Model pipeline file not found: {TOPIC_MODEL_PATH}")
        return

    try:
        with TOPIC_MODEL_PATH.open("rb") as f:
            topic_pipeline = joblib.load(f)
        sentences = sentences_df["sentence"]
        predictions = topic_pipeline.predict(sentences)
        predictions = [int(float(x)) for x in predictions]
    except Exception as exc:
        st.error(f"Failed to run topic classifier: {exc}")
        return

    topic_preds = pd.DataFrame({
        "sentence": sentences.reset_index(drop=True),
        "topic": predictions,
    })
    topic_freqs = (
        topic_preds["topic"]
        .value_counts()
        .rename_axis("topic")
        .reset_index(name="frequency")
        .sort_values("frequency", ascending=False)
        .reset_index(drop=True)
    )

    topic_freqs = topic_freqs[topic_freqs['frequency'] > 0]

    if topic_freqs.empty:
        st.info("No topic predictions available to chart.")
        return

    top_5_topic_freqs = topic_freqs.head(5).copy()
    top_5_topic_freqs["topic_name"] = top_5_topic_freqs["topic"].map(_topic_label_from_id)

    assert all(0 < p <= len(topic) for p in predictions), \
        f"Prediction indices out of range. Expected 1–{len(topic)}, got: {set(predictions)}"
    fig = px.bar(
        top_5_topic_freqs,
        x="topic_name",
        y="frequency",
        title="Top 5 most mentioned topics",
        labels={"topic_name": "Topic", "frequency": "Frequency"},
        category_orders={"topic_name": top_5_topic_freqs["topic_name"].tolist()},
    )
    st.plotly_chart(fig, use_container_width=True)
