from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from nltk.tokenize import sent_tokenize

from speech_parser.transcript_parser import parse_transcript_to_json


def _normalize_name(name: object) -> str:
	return str(name or "").strip().casefold()


def create_df_speeches(transcript_path: str | Path) -> pd.DataFrame:
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

	corporate_names = {
		_normalize_name(person.get("Name", ""))
		for person in transcript_data.get("Corporate", [])
		if isinstance(person, dict) and person.get("Name")
	}
	conference_names = {
		_normalize_name(person.get("Name", ""))
		for person in transcript_data.get("Conference", [])
		if isinstance(person, dict) and person.get("Name")
	}

	all_speeches: list[str] = []
	for section_name in ("presentation", "qa"):
		for speaker_entry in transcript_data.get(section_name, []):
			if not isinstance(speaker_entry, dict):
				continue

			speaker_name = _normalize_name(speaker_entry.get("Speaker", ""))
			speech_text = str(speaker_entry.get("Speech", "") or "").strip()
			if speaker_name in corporate_names and speaker_name not in conference_names and speech_text:
				all_speeches.append(speech_text)

	all_sentences: list[str] = []
	for speech in all_speeches:
		all_sentences.extend(sent_tokenize(speech))

	return pd.DataFrame({"sentence": all_sentences})

