from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from nltk.tokenize import sent_tokenize

from speech_parser.transcript_parser import parse_transcript_to_json


def _normalize_name(name: object) -> str:
	return str(name or "").strip().casefold()


def sentence_tokenizer(transcript_path: str | Path) -> pd.DataFrame:
	"""Create a sentence-level DataFrame using only Corporate speakers.

	The function parses the transcript into JSON (via parse_transcript_to_json),
	loads the generated JSON, extracts speech text from `presentation` and `qa`
	where the speaker belongs to `Corporate` (and not `Conference`), tokenizes
	speech into sentences, and returns a DataFrame with one column: `sentence`.
	"""
	if isinstance(transcript_path, bool) or not isinstance(transcript_path, (str, Path)):
		raise TypeError("transcript_path must be a string or pathlib.Path.")

	json_output_path = parse_transcript_to_json(transcript_path)

	try:
		with Path(json_output_path).open("r", encoding="utf-8") as file_obj:
			transcript_data = json.load(file_obj)
	except OSError as exc:
		raise OSError(f"Failed to read processed JSON file: {json_output_path}") from exc
	except json.JSONDecodeError as exc:
		raise ValueError(f"Invalid JSON in processed file: {json_output_path}") from exc

	corporate_tuples = [
		(
			_normalize_name(person.get("Name", "")),
			_normalize_name(person.get("Company", "")),
			_normalize_name(person.get("Role", "")),
		)
		for person in transcript_data.get("Corporate", [])
		if isinstance(person, dict)
	]
	conference_tuples = [
		(
			_normalize_name(person.get("Name", "")),
			_normalize_name(person.get("Company", "")),
			_normalize_name(person.get("Role", "")),
		)
		for person in transcript_data.get("Conference", [])
		if isinstance(person, dict)
	]

	all_speeches: list[str] = []
	for section_name in ("presentation", "qa"):
		for speaker_entry in transcript_data.get(section_name, []):
			if not isinstance(speaker_entry, dict):
				continue

			speaker_tuple = (
				_normalize_name(speaker_entry.get("Speaker", "")),
				_normalize_name(speaker_entry.get("Company", "")),
				_normalize_name(speaker_entry.get("Role", "")),
			)
			speech_test = str(speaker_entry.get("Speech", "") or "").strip()
			if speaker_tuple in corporate_tuples and speaker_tuple not in conference_tuples:
				all_speeches.append(speech_test)

	all_sentences: list[str] = []
	for speech in all_speeches:
		all_sentences.extend(sent_tokenize(speech))

	return pd.DataFrame({"sentence": all_sentences})

