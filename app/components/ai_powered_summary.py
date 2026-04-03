import os
from typing import cast

import anthropic
import streamlit as st
from dotenv import load_dotenv


def summarise_with_ai():
    hedge_metrics = st.session_state['hedge-metrics']
    topics = st.session_state['topics']

    role_hedges_str = '\n'.join(f'- {a}: {b:.2f}' for a, b in hedge_metrics["role-hedges"])
    top5_topics_str = '\n'.join(f'- {a} = {b}' for a, b in topics)
    prompt = f"""
## CONTEXT
- You are an expert in earnings call analysis with a focus on identifying investment signals for a company. 
- I will give you hedging frequency data separated by executive role and section (presentation vs Q&A section). 
- I will also give you the top 5 most mentioned topics in the earnings call.
- Interpret high hedging as a signal of management uncertainty around guidance. 
- Interpret topic concentration or shifts as signals of strategic focus or risk avoidance. 
- Based only on this data, give me a view — invest, avoid, or watch — with the 2 strongest reasons from the data. 
- If the data is insufficient to form a view, say "Insufficient data to provide a conclusion".
- Do NOT say anything like "As an AI language model..." or "Based on the data...".
- You MUST act speak as if you have the aforementioned role and NOT an AI language model.
- Do NOT write any headers or subheaders. Only body text with your interpretation and conclusion.
- Rather than speaking in full normal sentences, make your points in concise bullet form, with no more than 2 sentences per bullet.
- Each bullet should be in the form "metric. insight from that metric".
- Do NOT use any markdown syntax such as asterisks. ONLY PLAIN TEXT.
- When giving your verdict, write it in the form "Verdict: <your verdict>".
- Do NOT write anything after your verdict. No reasoning or anything.

## HEDGE METRICS (% by section)
- Presentation = {st.session_state['hedge-metrics']['presentation-hedge']:.2f}
- Q&A = {st.session_state['hedge-metrics']['qa-hedge']:.2f}
    
## HEDGE METRICS (by company executive role)
{role_hedges_str}

## MOST MENTIONED TOPICS
### format: <topic name> = <number of sentences mentioned>
{top5_topics_str}
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY is not set.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    with st.spinner("Generating AI summary..."):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[cast(anthropic.types.MessageParam, cast(object, {"role": "user", "content": prompt}))],
        )
    response_text = "".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()
    paragraphs = response_text.split("\n\n") #  Split on double newlines
    styled_text = "".join(f"<p style='font-size:14px;color:black; font-weight: 400;line-height:1.6;margin-bottom:1.25rem'>{p}</p>" for p in paragraphs)
    st.markdown('<h2 style="font-size: 32px; color:black; font-weight: 400;line-height:1.6;">AI SUMMARY</h2>', unsafe_allow_html=True)
    st.markdown(styled_text, unsafe_allow_html=True)
