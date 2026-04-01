from __future__ import annotations

from typing import Any

import pandas as pd
from nltk.tokenize import sent_tokenize


def _normalize_name(name: object) -> str:
	return str(name or "").strip().casefold()


def sentence_tokenizer(data: dict[str, Any]) -> pd.DataFrame:
	"""Create a sentence-level DataFrame using only Corporate speakers.

	The function consumes parsed transcript JSON data, extracts speech text from
	`presentation` and `qa` where the speaker belongs to `Corporate` (and not
	`Conference`), tokenizes speech into sentences, and returns columns
	`sentence`, `section`, and `Role`.
	"""
	if isinstance(data, bool) or not isinstance(data, dict):
		raise TypeError("data must be a JSON object (dict).")

	transcript_data = data

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

	all_rows: list[dict[str, Any]] = []
	for section_name in ("presentation", "qa"):
		section_value = 1 if section_name == "presentation" else 0
		for speaker_entry in transcript_data.get(section_name, []):
			if not isinstance(speaker_entry, dict):
				continue

			speaker_tuple = (
				_normalize_name(speaker_entry.get("Speaker", "")),
				_normalize_name(speaker_entry.get("Company", "")),
				_normalize_name(speaker_entry.get("Role", "")),
			)
			speaker_role = str(speaker_entry.get("Role", "") or "").strip()
			speech_text = str(speaker_entry.get("Speech", "") or "").strip()
			if speaker_tuple in corporate_tuples and speaker_tuple not in conference_tuples:
				for sentence in sent_tokenize(speech_text):
					all_rows.append(
						{"sentence": sentence, "section": section_value, "Role": speaker_role}
					)

	return pd.DataFrame(all_rows, columns=["sentence", "section", "Role"])
