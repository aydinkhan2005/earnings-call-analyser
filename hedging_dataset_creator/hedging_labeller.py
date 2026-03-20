from __future__ import annotations

import os
import logging

import anthropic
import asyncio
import numpy as np
import pandas as pd
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
import textwrap

def get_hedging_on_sentence(sentences):
    if not isinstance(sentences, list):
        raise TypeError("sentences must be a list of strings")

    formatted_sentences = "\n".join(
        f"{idx}. {str(sentence)}" for idx, sentence in enumerate(sentences, start=1)
    )
    formatted_sentences = textwrap.indent(formatted_sentences, '    ')
    prompt = f"""You are a financial language expert specialising in earnings call analysis.

    Label the following sentences as hedging (1) or not hedging (0).

    Hedging language includes any of the following:
    - Modal verbs expressing uncertainty: may, might, could, would, should
    - Epistemic verbs: believe, think, expect, anticipate, feel, assume
    - Approximators: approximately, around, roughly, about
    - Probability expressions: likely, unlikely, possibly, probably, perhaps
    - Conditional framing: assuming, subject to, if, provided that
    - Opportunity hedges: potential, opportunity, possibility
    - Attribution hedges: based on current trends, according to our estimates
    - Distancing language: it appears, it seems, there is reason to believe
    - Negative hedges: cannot guarantee, no assurance, cannot predict
    
    Important:
    - Not every modal verb is hedging. "We will pay the dividend"
    is NOT hedging. "We believe we will pay the dividend" IS hedging.
    Direct factual statements about past results are NOT hedging.
    
    Expressions of excitement, confidence, or enthusiasm are NOT hedging:
    - "We're really excited about X" is NOT hedging
    - "The future of Apple is very bright" is NOT hedging  
    - "Our product pipeline has amazing innovations in store" is NOT hedging
    Direct positive assertions, even about the future, are NOT hedging unless 
    they contain explicit uncertainty markers. Confidence about the future is NOT the same as 
    uncertainty about the future.

    Sentences reporting figures or statistics using words like "estimated," "approximately," or "around" ARE hedging -- the speaker is deliberately qualifying the precision of the claim.

    Sentences:
{formatted_sentences}

    Return ONLY a comma separated list of 1s and 0s, one per sentence, in order.
    NO spaces in between, NO explanation, nothing else.
    Example output: 1,0,1,1,0"""

    return prompt


async def hedging_labeller(
    sentences_df,
    semaphore=None,
    model="claude-haiku-4-5-20251001",
):
    load_dotenv()
    if semaphore is None:
        semaphore = asyncio.Semaphore(10)
    if not isinstance(sentences_df, pd.DataFrame):
        raise TypeError("sentences_df must be a pandas DataFrame")
    if "sentence" not in sentences_df.columns:
        raise ValueError("sentences_df must include a 'sentence' column")

    if len(sentences_df) > 400:
        midpoint = len(sentences_df) // 2
        first_half = sentences_df.iloc[:midpoint].copy()
        second_half = sentences_df.iloc[midpoint:].copy()

        first_labeled = await hedging_labeller(
            first_half,
            semaphore=semaphore,
            model=model,
        )
        second_labeled = await hedging_labeller(
            second_half,
            semaphore=semaphore,
            model=model,
        )

        return pd.concat([first_labeled, second_labeled])

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    sentences_with_labels = sentences_df.copy()
    sentences_with_labels["isHedge"] = np.nan
    sentence_values = sentences_with_labels["sentence"].tolist()

    # Create batches of max 10 sentences
    batch_size = 10
    batches = []
    for start_idx in range(0, len(sentence_values), batch_size):
        end_idx = start_idx + batch_size
        batch_indices = sentences_with_labels.index[start_idx:end_idx].tolist()
        batch_sentences = sentence_values[start_idx:end_idx]
        batches.append((batch_indices, batch_sentences))

    max_retries = 3
    retry_delay_seconds = 1.0

    async def classify_batch(batch_indices, batch_sentences):
        # Filter out NaN values but keep track of original positions
        batch_with_positions = [
            (idx, sentence)
            for idx, sentence in zip(batch_indices, batch_sentences)
            if pd.notna(sentence)
        ]
        
        if not batch_with_positions:
            return batch_indices, [np.nan] * len(batch_sentences)

        non_nan_batch = [str(sentence) for _, sentence in batch_with_positions]

        for attempt in range(max_retries + 1):
            try:
                async with semaphore:
                    response = await client.messages.create(
                        model=model,
                        max_tokens=50,
                        messages=[{"role": "user", "content": get_hedging_on_sentence(non_nan_batch)}],
                    )
                response_text = response.content[0].text.strip()

                # Parse comma-separated response (e.g., "1,0,0,1")
                labels_str = response_text.split(',')
                labels = []
                for label in labels_str:
                    cleaned_label = label.strip().strip('"').strip("'")
                    labels.append(int(cleaned_label) if cleaned_label.isdigit() else np.nan)

                if len(labels) != len(non_nan_batch):
                    raise ValueError(
                        f"Label count mismatch: expected {len(non_nan_batch)}, got {len(labels)}"
                    )

                # Map labels back to original batch with NaN in correct positions
                result = [np.nan] * len(batch_sentences)
                index_lookup = {idx: pos for pos, idx in enumerate(batch_indices)}
                for label_idx, (orig_idx, _) in enumerate(batch_with_positions):
                    result[index_lookup[orig_idx]] = labels[label_idx]
                return batch_indices, result
            except Exception as exc:
                if attempt < max_retries:
                    delay = retry_delay_seconds * (2 ** attempt)
                    logging.warning(
                        "Batch labelling failed (attempt %s/%s). Retrying in %.1fs. Error: %s",
                        attempt + 1,
                        max_retries + 1,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)
                    continue

                logging.error(
                    "Batch labelling failed after %s attempts. Returning NaNs for this batch. Error: %s",
                    max_retries + 1,
                    exc,
                )
                return batch_indices, [np.nan] * len(batch_sentences)

    # Process batches
    tasks = [
        asyncio.create_task(classify_batch(batch_indices, batch_sentences))
        for batch_indices, batch_sentences in batches
    ]

    progress = tqdm(total=len(tasks), desc="Labelling hedging sentences", unit="batch")
    try:
        for task in asyncio.as_completed(tasks):
            batch_indices, batch_labels = await task
            sentences_with_labels.loc[batch_indices, "isHedge"] = batch_labels
            progress.update(1)
    finally:
        progress.close()

    return sentences_with_labels

