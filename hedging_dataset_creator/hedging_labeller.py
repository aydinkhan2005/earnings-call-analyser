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
    
    Expressions of excitement, confidence, or enthusiasm are NOT hedging:
    - "We're really excited about X" is NOT hedging
    - "The future of Apple is very bright" is NOT hedging  
    - "Our product pipeline has amazing innovations in store" is NOT hedging
    Direct positive assertions, even about the future, are NOT hedging unless 
    they contain explicit uncertainty markers.
    
    Important:
    - Not every modal verb is hedging. "We will pay the dividend"
    is NOT hedging. "We believe we will pay the dividend" IS hedging.
    Direct factual statements about past results are NOT hedging.

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

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    sentences_with_labels = sentences_df.copy()
    sentence_values = sentences_with_labels["sentence"].tolist()

    # Create batches of max 10 sentences
    batch_size = 10
    batches = [sentence_values[i:i+batch_size] for i in range(0, len(sentence_values), batch_size)]

    async def classify_batch(batch):
        # Filter out NaN values but keep track of original positions
        batch_with_positions = [(idx, sentence) for idx, sentence in enumerate(batch) if pd.notna(sentence)]
        
        if not batch_with_positions:
            return [np.nan] * len(batch)
        
        async with semaphore:
            non_nan_batch = [str(sentence) for _, sentence in batch_with_positions]
            response = await client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{"role": "user", "content": get_hedging_on_sentence(non_nan_batch)}],
            )
            response_text = response.content[0].text.strip()
            
            # Parse comma-separated response (e.g., "1,0,0,1")
            labels_str = response_text.split(',')
            labels = [int(label.strip()) if label.strip().isdigit() else np.nan for label in labels_str]
            if len(labels) != len(non_nan_batch):
                logging.warning(f"Label count mismatch: expected {len(non_nan_batch)}, got {len(labels)}. Batch: {non_nan_batch}")
                return [np.nan] * len(batch)

        
        # Map labels back to original batch with NaN in correct positions
        result = [np.nan] * len(batch)
        for label_idx, (orig_idx, _) in enumerate(batch_with_positions):
            if label_idx < len(labels):
                result[orig_idx] = labels[label_idx]
        
        return result

    # Process batches
    tasks = [classify_batch(batch) for batch in batches]
    batch_results = await tqdm.gather(*tasks, desc="Labelling hedging sentences", unit="batch")
    
    # Flatten results
    labels = [label for batch in batch_results for label in batch]

    sentences_with_labels["isHedge"] = labels
    return sentences_with_labels

