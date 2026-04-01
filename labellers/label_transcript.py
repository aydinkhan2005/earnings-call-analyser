from __future__ import annotations

import asyncio
from pathlib import Path

import pandas as pd

from labellers.hedging_labeller import sentence_labeller
from labellers.sentence_tokenizer import sentence_tokenizer
from speech_parser.transcript_parser import parse_transcript_to_data


async def label_transcript(
    transcript_path: str | Path,
    get_prompt,
    labelName: str,
    output_folder: str = "hedging_dataset",
):
    """
    Generic function to label transcript sentences.

    Args:
        transcript_path: Path to the transcript text file
        get_prompt: Function that takes sentences and returns a prompt string
        labelName: Name of the label column to add (e.g., "isHedge", "topic")
        output_folder: Folder name in data/ where CSV will be saved (default: "hedging_dataset")

    Returns:
        DataFrame with labelled sentences or None if already processed
    """
    if isinstance(transcript_path, bool) or not isinstance(transcript_path, (str, Path)):
        raise TypeError("transcript_path must be a string or pathlib.Path")

    transcript_file = Path(transcript_path)
    if not transcript_file.exists():
        raise FileNotFoundError(f"Transcript file does not exist: {transcript_file}")
    if not transcript_file.is_file():
        raise ValueError(f"transcript_path is not a file: {transcript_file}")

    file_name = transcript_file.stem
    company = transcript_file.parent.name

    csv_path = Path("data") / output_folder / company / f"{file_name}.csv"
    if csv_path.exists():
        return

    transcript_data = parse_transcript_to_data(str(transcript_file))

    sentences_df = pd.DataFrame(sentence_tokenizer(transcript_data))

    classified_sentences = await sentence_labeller(
        sentences_df,
        get_prompt,
        labelName,
        semaphore=asyncio.Semaphore(10),
    )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    classified_sentences.to_csv(csv_path, index=False)
    return classified_sentences


async def label_transcript_with_hedging(transcript_path: str | Path):
    """Label transcript sentences for hedging language."""
    from labellers.hedging_labeller import get_hedging_on_sentence

    return await label_transcript(
        transcript_path,
        get_hedging_on_sentence,
        "isHedge",
        output_folder="hedging_dataset",
    )


async def label_transcript_with_topics(transcript_path: str | Path):
    """Label transcript sentences by topic."""
    from sentence_topic_classifier.topic_classifier import get_topic_on_sentences

    return await label_transcript(
        transcript_path,
        get_topic_on_sentences,
        "topic",
        output_folder="topic_dataset",
    )
