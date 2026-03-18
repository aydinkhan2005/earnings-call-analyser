def get_speech(transcript, SPEAKER_1: int, SPEAKER_2: int) -> list:
    """Return transcript rows strictly between two speaker rows from rows_with_bracket_digit.

    SPEAKER_1 and SPEAKER_2 are 1-indexed row positions in rows_with_bracket_digit.
    """
    if transcript is None:
        raise ValueError("DataFrame is NoneType")
    if (
        isinstance(SPEAKER_1, bool)
        or isinstance(SPEAKER_2, bool)
        or not isinstance(SPEAKER_1, int)
        or not isinstance(SPEAKER_2, int)
    ):
        raise TypeError('SPEAKER_1 and SPEAKER_2 must be integers.')

    # isolate only rows that end with a speaker marker like "[13]"
    bracket_digit_mask = transcript["line"].str.contains(r"\[\d+\]\s*$", regex=True, na=False)
    speaker_rows = transcript.loc[bracket_digit_mask].copy()
    total_speakers = len(speaker_rows)

    if total_speakers < 2:
        return []

    if SPEAKER_1 < 1 or SPEAKER_2 < 1 or SPEAKER_1 > total_speakers or SPEAKER_2 > total_speakers:
        raise IndexError(f'SPEAKER_1 and SPEAKER_2 must be between 1 and {total_speakers}.')

    if abs(SPEAKER_1 - SPEAKER_2) != 1:
        raise ValueError('SPEAKER_1 and SPEAKER_2 must be adjacent speaker numbers.')

    sectioned_speaker_rows = speaker_rows.reset_index(names='transcript_row_index')
    sectioned_speaker_rows['transcript_row_index'] = sectioned_speaker_rows['transcript_row_index'] + 1

    start_pos, end_pos = sorted((SPEAKER_1 - 1, SPEAKER_2 - 1))
    row_index1 = sectioned_speaker_rows.loc[start_pos, 'transcript_row_index']
    row_index2 = sectioned_speaker_rows.loc[end_pos, 'transcript_row_index']

    between_rows = transcript.iloc[row_index1 : row_index2 - 1, :].copy()
    stripped_lines = between_rows['line'].fillna('').str.strip()
    valid_text_mask = (
        stripped_lines.ne('')
        & stripped_lines.str.contains(r'[A-Za-z]', regex=True, na=False)
    )
    return stripped_lines.loc[valid_text_mask].tolist()
