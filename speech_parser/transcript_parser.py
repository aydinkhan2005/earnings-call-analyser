from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from speech_parser.speaker_isolator import get_speaker
from speech_parser.speech_isolator import get_speech

_HEADER_PATTERN = re.compile(r"(Q[1-4])\s+(\d{4})\s+(.+?)\s+Earnings Call", re.IGNORECASE)
_PARTICIPANT_NAME_PATTERN = re.compile(r"^\s*\*\s*(.+?)\s*$")
_PARTICIPANT_ROLE_PATTERN = re.compile(r"^\s*(?P<company>.+?)\s*-\s*(?P<role>.+?)\s*$")
_CORPORATE_HEADER = "Corporate Participants"
_CONFERENCE_HEADER = "Conference Call Participiants"
_SPEAKER_PATTERN = re.compile(
    r"^\s*(?P<name>.+?),\s*(?P<company>.+?)\s*-\s*(?P<role>.+?)\s*\[(?P<marker>\d+)]\s*$"
)
_OPERATOR_PATTERN = re.compile(r"^\s*(?P<name>[^,\-\[]+?)\s*\[(?P<marker>\d+)]\s*$")


def _normalize_company_name(value: str) -> str:
    return re.sub(r"\.", "", value or "").strip().casefold()


def _extract_header_metadata(text: str) -> tuple[str, str, str]:
    match = _HEADER_PATTERN.search(text)
    if not match:
        raise ValueError("Could not locate header metadata like 'Q2 2016 Apple Inc Earnings Call'.")

    quarter, year, company = match.groups()
    return company.strip(), year.strip(), quarter[-1]


def _extract_conference_participants(transcript_df: pd.DataFrame) -> list[tuple[str, str, str]]:
    if transcript_df.empty:
        return []

    line_series = transcript_df["line"].fillna("").astype(str)
    stripped_lines = line_series.str.lstrip()
    conference_header_mask = stripped_lines.str.startswith(_CONFERENCE_HEADER, na=False)
    if not conference_header_mask.any():
        return []

    conference_start = conference_header_mask[conference_header_mask].index[0]

    # Bound conference participants to the participant block before presentation/QA starts.
    section_end = len(line_series)
    for idx in range(conference_start + 1, len(line_series)):
        heading = stripped_lines.iloc[idx]
        if heading.startswith("Presentation") or heading.startswith("Questions and Answers"):
            section_end = idx
            break

    section_lines = line_series.iloc[conference_start + 1 : section_end].reset_index(drop=True)
    name_line_mask = section_lines.str.match(_PARTICIPANT_NAME_PATTERN.pattern, na=False)

    participant_names = (
        section_lines.loc[name_line_mask]
        .str.replace(r"^\s*\*\s*", "", regex=True)
        .str.strip()
        .reset_index(drop=True)
    )

    participant_roles = section_lines.loc[
        name_line_mask.shift(1, fill_value=False),
    ].reset_index(drop=True)

    participant_tuples: list[tuple[str, str, str]] = []
    for name, role_line in zip(participant_names, participant_roles):
        role_match = _PARTICIPANT_ROLE_PATTERN.match(str(role_line or ""))
        if role_match:
            participant_tuples.append(
                (
                    name.strip(),
                    role_match.group("company").strip(),
                    role_match.group("role").strip(),
                )
            )

    return participant_tuples


def _extract_corporate_participants(transcript_df: pd.DataFrame) -> list[tuple[str, str, str]]:
    """Extract corporate participants from the bounded corporate-participants section only."""
    if transcript_df.empty:
        return []
    line_series = transcript_df["line"].fillna("").astype(str)
    stripped_lines = line_series.str.lstrip()

    corporate_header_mask = stripped_lines.str.startswith(_CORPORATE_HEADER, na=False)
    conference_header_mask = stripped_lines.str.startswith(_CONFERENCE_HEADER, na=False)
    if not corporate_header_mask.any() or not conference_header_mask.any():
        return []

    corporate_start = corporate_header_mask[corporate_header_mask].index[0]
    conference_idx_candidates = conference_header_mask[conference_header_mask].index
    conference_after = conference_idx_candidates[conference_idx_candidates > corporate_start]
    if len(conference_after) == 0:
        return []

    conference_start = conference_after[0]
    section_lines = line_series.iloc[corporate_start + 1 : conference_start].reset_index(drop=True)

    name_mask = section_lines.str.startswith(" *", na=False)
    corporate_names = (
        section_lines.loc[name_mask]
        .str.replace(r"^\s*\*\s*", "", regex=True)
        .str.strip()
        .reset_index(drop=True)
    )
    corporate_role_lines = section_lines.shift(-1).loc[name_mask].reset_index(drop=True)

    corporate_tuples: list[tuple[str, str, str]] = []
    for name, role_line in zip(corporate_names, corporate_role_lines):
        role_match = _PARTICIPANT_ROLE_PATTERN.match(str(role_line or ""))
        if role_match:
            corporate_tuples.append(
                (
                    name.strip(),
                    role_match.group("company").strip(),
                    role_match.group("role").strip(),
                )
            )
    return corporate_tuples


def _extract_speaker_tuples(transcript_df: pd.DataFrame) -> tuple[list[tuple[str, str, str]], list[int]]:
    speaker_tuples: list[tuple[str, str, str]] = []
    speaker_markers: list[int] = []
    speaker_idx = 1

    while True:
        try:
            speaker_line = get_speaker(transcript_df, SPEAKER_INDEX=speaker_idx)
        except IndexError:
            break
        except ValueError:
            break

        stripped_line = speaker_line.strip()

        speaker_match = _SPEAKER_PATTERN.match(stripped_line)
        if speaker_match:
            speaker_tuples.append(
                (
                    speaker_match.group("name").strip(),
                    speaker_match.group("company").strip(),
                    speaker_match.group("role").strip(),
                )
            )
            speaker_markers.append(int(speaker_match.group("marker")))
            speaker_idx += 1
            continue

        operator_match = _OPERATOR_PATTERN.match(stripped_line)
        if operator_match:
            speaker_tuples.append((operator_match.group("name").strip(), "", ""))
            speaker_markers.append(int(operator_match.group("marker")))

        speaker_idx += 1

    return speaker_tuples, speaker_markers


def _presentation_cutoff(marker_numbers: list[int], total_speakers: int) -> int:
    if total_speakers <= 0:
        return 0

    if not marker_numbers:
        return total_speakers

    for i in range(len(marker_numbers) - 1):
        if marker_numbers[i + 1] < marker_numbers[i]:
            return i + 1

    return total_speakers


def parse_transcript_to_json(transcript_path: str | Path, output_dir: str | Path | None = None) -> Path:
    """Parse an earnings transcript text file and write a structured JSON file.

    Args:
        transcript_path: Path to transcript .txt, e.g. data/Transcripts/AAPL/2016-Apr-26-AAPL.txt.
        output_dir: Optional output directory. If omitted, writes JSON to data/processed/.

    Returns:
        Path to the written JSON file.
    """
    if isinstance(transcript_path, bool) or not isinstance(transcript_path, (str, Path)):
        raise TypeError("transcript_path must be a string or pathlib.Path.")
    transcript_path = Path(transcript_path)
    if transcript_path.suffix.lower() != ".txt":
        raise ValueError("transcript_path must point to a .txt file.")
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript file does not exist: {transcript_path}")
    if not transcript_path.is_file():
        raise ValueError(f"transcript_path is not a file: {transcript_path}")

    try:
        text = transcript_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise OSError(f"Failed to read transcript file: {transcript_path}") from exc

    if not text.strip():
        raise ValueError("Transcript file is empty after stripping whitespace.")

    transcript_df = pd.DataFrame({"line": text.splitlines()})
    if "line" not in transcript_df.columns:
        raise KeyError("Transcript DataFrame does not contain 'line' column.")

    company, year, quarter = _extract_header_metadata(text)

    participant_tuples = _extract_conference_participants(transcript_df)
    corporate_tuples = _extract_corporate_participants(transcript_df)

    if corporate_tuples:
        corporate = [
            {"Name": name, "Company": comp, "Role": role}
            for name, comp, role in corporate_tuples
        ]
        corporate_set = set(corporate_tuples)
        analysts = [
            {"Name": name, "Company": comp, "Role": role}
            for name, comp, role in participant_tuples
            if (name, comp, role) not in corporate_set
        ]
    else:
        company_key = _normalize_company_name(company)
        corporate = [
            {"Name": name, "Company": comp, "Role": role}
            for name, comp, role in participant_tuples
            if _normalize_company_name(comp) == company_key
        ]
        analysts = [
            {"Name": name, "Company": comp, "Role": role}
            for name, comp, role in participant_tuples
            if _normalize_company_name(comp) != company_key
        ]

    speaker_tuples, speaker_row_numbers = _extract_speaker_tuples(transcript_df)
    if len(speaker_tuples) < 2:
        raise ValueError("Transcript must contain at least two speaker rows to build speech segments.")

    cutoff = _presentation_cutoff(speaker_row_numbers, len(speaker_tuples))

    presentation: list[dict[str, Any]] = []
    qa: list[dict[str, Any]] = []

    for i in range(1, len(speaker_tuples)):
        speaker_name, speaker_company, speaker_role = speaker_tuples[i - 1]
        try:
            speech_rows = get_speech(transcript_df, SPEAKER_1=i, SPEAKER_2=i + 1)
        except (IndexError, TypeError, ValueError) as exc:
            raise ValueError(f"Could not isolate speech for speaker boundary {i} -> {i + 1}.") from exc

        entry = {
            "Speaker": speaker_name,
            "Company": speaker_company,
            "Role": speaker_role,
            "Speech": " ".join(speech_rows).strip(),
        }

        if (i - 1) < cutoff:
            presentation.append(entry)
        else:
            qa.append(entry)

    output_base_dir: Path
    if output_dir is None:
        output_base_dir = Path("data") / "processed"
    else:
        if isinstance(output_dir, bool) or not isinstance(output_dir, (str, Path)):
            raise TypeError("output_dir must be a string or pathlib.Path when provided.")
        output_base_dir = Path(output_dir)

    output_base_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_base_dir / f"{transcript_path.stem}.json"

    data = {
        "Company": company,
        "Year": year,
        "Quarter": quarter,
        "Corporate": corporate,
        "Analysts": analysts,
        "presentation": presentation,
        "qa": qa,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return output_path

