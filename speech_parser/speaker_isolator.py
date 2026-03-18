def get_speaker(transcript, SPEAKER_INDEX):
    """
    Get the speaker name from the transcript based on the provided speaker index.
    The speaker name is expected to be in a row that ends with a speaker marker like "[13]".
    The function isolates these rows and returns the speaker name corresponding to the given index.
    :param transcript: DataFrame of raw transcript
    :param SPEAKER_INDEX: Index of the speaker
    :return: Transcript row corresponding to the speaker
    """
    if transcript is None:
        raise ValueError("DataFrame is NoneType")
    if not hasattr(transcript, "columns"):
        raise TypeError("transcript must be a pandas DataFrame-like object with a 'line' column.")
    if "line" not in transcript.columns:
        raise KeyError("'line'")
    if isinstance(SPEAKER_INDEX, bool) or not isinstance(SPEAKER_INDEX, int):
        raise TypeError("SPEAKER_INDEX must be an integer.")

    # isolate only rows that end with a speaker marker like "[13]"
    bracket_digit_mask = transcript["line"].str.contains(r"\[\d+\]\s*$", regex=True, na=False)
    speaker_rows = transcript.loc[bracket_digit_mask, "line"]
    total_speakers = len(speaker_rows)

    if total_speakers == 0:
        raise ValueError("No speaker rows found in transcript.")
    if SPEAKER_INDEX < 1 or SPEAKER_INDEX > total_speakers:
        raise IndexError(f"SPEAKER_INDEX must be between 1 and {total_speakers}.")

    return speaker_rows.iloc[SPEAKER_INDEX - 1].strip()
