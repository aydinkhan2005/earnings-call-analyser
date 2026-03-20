from __future__ import annotations

import asyncio
from pathlib import Path

import pandas as pd

from hedging_dataset_creator.hedging_labeller import hedging_labeller
from hedging_dataset_creator.sentence_tokenizer import sentence_tokenizer
from speech_parser.transcript_parser import parse_transcript_to_json


async def label_transcript_sentences(transcript_path: str | Path):
    if isinstance(transcript_path, bool) or not isinstance(transcript_path, (str, Path)):
        raise TypeError("transcript_path must be a string or pathlib.Path")

    transcript_file = Path(transcript_path)
    if not transcript_file.exists():
        raise FileNotFoundError(f"Transcript file does not exist: {transcript_file}")
    if not transcript_file.is_file():
        raise ValueError(f"transcript_path is not a file: {transcript_file}")

    file_name = transcript_file.stem
    company = transcript_file.parent.name

    csv_path = Path("data") / "hedging_dataset" / company / f"{file_name}.csv"
    if csv_path.exists():
        return

    parse_transcript_to_json(str(transcript_file))

    processed_json_path = Path("data") / "processed" / f"{file_name}.json"
    sentences_df = pd.DataFrame(sentence_tokenizer(processed_json_path))

    classified_sentences = await hedging_labeller(
        sentences_df,
        semaphore=asyncio.Semaphore(10),
    )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    classified_sentences.to_csv(csv_path, index=False)
    return classified_sentences

