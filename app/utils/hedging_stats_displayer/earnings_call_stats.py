import streamlit.components.v1 as components
def get_stats(transcript_data):
    """
    - Uses a Logistic Regression classifier to classify each sentence
    of corporate executives as hedging (1) or not (0).
    - This is displayed as the hedging frequency separated by CFO and CEO.
    - Most flagged topic MAY also be implemented

    @param transcript_data: Parsed transcript as a JSON object held in memory
    @return Dictionary of key pieces of data
    """
    return "72%"
def render_metrics(score, title="Hedging Score", color="orange", font_size="72px"):
    html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda&family=Noto+Sans&display=swap" rel="stylesheet">
    <style>
    .typography-box {{
        background-color: #f9f9fb;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #e6e6e6;
        display: inline-block;
        opacity: 0;
        transform: translateY(12px);
        animation: fadeIn 0.8s ease-out forwards;
    }}
    .typography-box h3 {{
        margin: 0 0 8px 0;
        font-family: 'Noto Sans', serif;
        font-weight: 600;
    }}
    .typography-box p.large-number {{
        color: {color};
        font-size: {font_size} !important;
        font-family: 'Bodoni Moda', sans-serif;
        margin: 0;
    }}
    @keyframes fadeIn {{
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    </style>
    <div class="typography-box">
        <h3>{title}</h3>
        <p class="large-number">{score}</p>
    </div>
    """
    components.html(html, height=250)