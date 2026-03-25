import sys
from pathlib import Path

from utils.company_stock_plotter import plot_stock_data

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent

for p in (str(ROOT_DIR), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)
import streamlit as st
import yfinance as yf
import anthropic
import json
import datetime
import plotly.graph_objects as go
import pandas as pd

from utils.input_reciever import recieve_input

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EARNINGS ANALYSER",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Swiss International Typography & Design System ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@300;400;500;700&display=swap');

/* ── Reset & Root ── */
:root {
  --black:    #0A0A0A;
  --white:    #F5F4F0;
  --red:      #D40000;
  --grey-1:   #1A1A1A;
  --grey-2:   #2E2E2E;
  --grey-3:   #5A5A5A;
  --grey-4:   #9A9A9A;
  --grey-5:   #D0CFC8;
  --accent:   #D40000;
  --mono:     'IBM Plex Mono', monospace;
  --sans:     'IBM Plex Sans', sans-serif;
  --display:  'Bebas Neue', sans-serif;
  --grid:     4px;
}

html, body, [class*="css"] {
  font-family: var(--sans) !important;
  background-color: var(--white) !important;
  color: var(--black) !important;
}

/* ── Streamlit chrome overrides ── */
.stApp { background-color: var(--white) !important; }
section[data-testid="stSidebar"] { background-color: var(--black) !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.stDeployButton { display: none !important; }

/* ── Typography ── */
h1, h2, h3 {
  font-family: var(--display) !important;
  letter-spacing: 0.08em !important;
  color: var(--black) !important;
}
.stMarkdown p, .stText {
  font-family: var(--sans) !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
}

/* ── Header Bar ── */
.header-bar {
  background: var(--black);
  padding: 0 40px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 3px solid var(--red);
  position: sticky;
  top: 0;
  z-index: 999;
}
.header-wordmark {
  font-family: var(--display);
  font-size: 28px;
  letter-spacing: 0.15em;
  color: var(--white);
  margin: 0;
}
.header-tag {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--grey-4);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
.header-rule {
  width: 2px;
  height: 28px;
  background: var(--red);
  margin: 0 20px;
}

/* ── Grid Rule Lines ── */
.rule-h {
  border: none;
  border-top: 1px solid var(--grey-5);
  margin: 0;
}
.rule-h-bold {
  border: none;
  border-top: 2px solid var(--black);
  margin: 0;
}

/* ── Section labels ── */
.section-label {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.25em;
  color: var(--red);
  text-transform: uppercase;
  padding: 8px 0 4px;
  margin: 0;
}
.section-title {
  font-family: var(--display);
  font-size: 42px;
  letter-spacing: 0.06em;
  color: var(--black);
  line-height: 1;
  margin: 0 0 8px;
}
.section-sub {
  font-family: var(--sans);
  font-size: 13px;
  color: var(--grey-3);
  font-weight: 300;
  margin: 0;
}

/* ── Control Panel (selector area) ── */
.control-panel {
  background: var(--black);
  padding: 32px 40px;
}
.control-panel-inner {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 24px;
  align-items: end;
}
.field-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.3em;
  color: var(--grey-4);
  text-transform: uppercase;
  margin-bottom: 6px;
  display: block;
}

/* ── Streamlit widget overrides (dark panel) ── */
.control-panel .stSelectbox label,
.control-panel .stSelectbox > div > div {
  color: var(--white) !important;
  background: var(--grey-1) !important;
  border: 1px solid var(--grey-2) !important;
  border-radius: 0 !important;
  font-family: var(--sans) !important;
}
div[data-baseweb="select"] > div {
  border-radius: 0 !important;
  border-color: var(--grey-3) !important;
}

/* ── Buttons ── */
.stButton > button {
  background: var(--red) !important;
  color: var(--white) !important;
  border: none !important;
  border-radius: 0 !important;
  font-family: var(--mono) !important;
  font-size: 12px !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  padding: 12px 28px !important;
  font-weight: 700 !important;
  width: 100% !important;
  transition: background 0.15s !important;
}
.stButton > button:hover {
  background: #AA0000 !important;
}

/* ── KPI Cards ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--grey-5);
  border: 1px solid var(--grey-5);
  margin-bottom: 1px;
}
.kpi-card {
  background: var(--white);
  padding: 20px 24px;
}
.kpi-label {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.25em;
  color: var(--grey-3);
  text-transform: uppercase;
  margin-bottom: 6px;
}
.kpi-value {
  font-family: var(--display);
  font-size: 36px;
  letter-spacing: 0.03em;
  color: var(--black);
  line-height: 1;
  margin-bottom: 4px;
}
.kpi-value.positive { color: #1A7A3C; }
.kpi-value.negative { color: var(--red); }
.kpi-change {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--grey-3);
}

/* ── Analysis Blocks ── */
.analysis-block {
  padding: 28px 32px;
  border-bottom: 1px solid var(--grey-5);
}
.analysis-block:last-child { border-bottom: none; }
.block-tag {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.25em;
  color: var(--red);
  text-transform: uppercase;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.block-tag::before {
  content: '';
  display: inline-block;
  width: 16px;
  height: 2px;
  background: var(--red);
}
.block-content {
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.75;
  color: var(--black);
  font-weight: 300;
}
.block-heading {
  font-family: var(--display);
  font-size: 22px;
  letter-spacing: 0.05em;
  margin: 0 0 12px;
}

/* ── Sentiment badge ── */
.sentiment-badge {
  display: inline-block;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding: 4px 12px;
  border-radius: 0;
  border: 1.5px solid;
  margin-left: 12px;
  vertical-align: middle;
}
.sent-positive { border-color: #1A7A3C; color: #1A7A3C; }
.sent-neutral  { border-color: var(--grey-3); color: var(--grey-3); }
.sent-negative { border-color: var(--red); color: var(--red); }

/* ── Historical Table ── */
.hist-row {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 1fr 1fr;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid var(--grey-5);
  font-family: var(--sans);
  font-size: 13px;
}
.hist-row:first-child {
  background: var(--black);
  color: var(--white);
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
.hist-row:nth-child(even):not(:first-child) { background: rgba(0,0,0,0.015); }

/* ── Page content wrapper ── */
.page-wrap {
  padding: 40px 40px;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--red) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  border-bottom: 2px solid var(--black) !important;
  gap: 0 !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--mono) !important;
  font-size: 11px !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  padding: 12px 24px !important;
  border: none !important;
  background: transparent !important;
  color: var(--grey-3) !important;
}
.stTabs [aria-selected="true"] {
  background: var(--black) !important;
  color: var(--white) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
  font-family: var(--mono) !important;
  font-size: 11px !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  border-bottom: 1px solid var(--grey-5) !important;
}

/* ── Info box ── */
.info-banner {
  background: var(--black);
  color: var(--white);
  padding: 16px 24px;
  font-family: var(--mono);
  font-size: 12px;
  letter-spacing: 0.05em;
  border-left: 4px solid var(--red);
  margin-bottom: 24px;
}

/* ── Quarter pill ── */
.q-pill {
  display: inline-block;
  background: var(--black);
  color: var(--white);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.15em;
  padding: 3px 8px;
  margin-right: 4px;
}
.q-pill.active {
  background: var(--red);
}

/* ── divider with text ── */
.divider-label {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 32px 0 24px;
}
.divider-label::before,
.divider-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--grey-5);
}
.divider-label span {
  font-family: var(--mono);
  font-size: 9px;
  letter-spacing: 0.3em;
  color: var(--grey-4);
  text-transform: uppercase;
  white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# ── Company Registry ────────────────────────────────────────────────────────
COMPANIES = {
    "Microsoft Corporation":      {"ticker": "MSFT",  "name_short": "MSFT"},
    "Alphabet (Google)":    {"ticker": "GOOGL", "name_short": "GOOGLE"},
    "Amazon.com Inc.":      {"ticker": "AMZN",  "name_short": "AMAZON"},
    "NVIDIA Corporation":         {"ticker": "NVDA",  "name_short": "NVIDIA"},
    "Cisco Systems":                {"ticker": "CSCO",  "name_short": "CISCO"},
    "Advanced Micro Devices":   {"ticker": "AMD", "name_short": "AMD"},
    "Intel Corporation":          {"ticker": "INTC", "name_short": "INTEL"},
    'ASML Holding':        {'ticker': 'ASML', 'name_short': 'ASML'},
    'Micron Technology':         {'ticker': 'MU', 'name_short': 'MICRON'}
}

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
YEARS    = [2016, 2017, 2018, 2019, 2020]

# ── Helpers ─────────────────────────────────────────────────────────────────
def quarter_to_dates(q: str, year: int):
    """Return (start_date, end_date) for a quarter."""
    mapping = {
        "Q1": (f"{year}-01-01",   f"{year}-03-31"),
        "Q2": (f"{year}-04-01",   f"{year}-06-30"),
        "Q3": (f"{year}-07-01",   f"{year}-09-30"),
        "Q4": (f"{year}-10-01",   f"{year}-12-31"),
    }
    return mapping[q]

def prev_quarters(q: str, year: int, n: int = 5):
    """Return list of (quarter, year) going back n periods."""
    qi = QUARTERS.index(q)
    result = []
    for _ in range(n):
        qi -= 1
        if qi < 0:
            qi = 3
            year -= 1
        result.append((QUARTERS[qi], year))
    return result

@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    try:
        end_dt = datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)
        df = yf.download(ticker, start=start, end=end_dt.strftime("%Y-%m-%d"), progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        return df
    except Exception:
        return pd.DataFrame()

def fetch_transcript_via_api(company: str, ticker: str, quarter: str, year: int) -> str:
    """Use Claude to generate a realistic earnings call transcript summary."""
    client = anthropic.Anthropic()
    prompt = f"""You are a financial data assistant. Generate a realistic and detailed earnings call transcript summary for {company} (ticker: {ticker}) for {quarter} {year}.

The transcript summary should include:
1. Opening remarks from the CEO
2. Key financial highlights (revenue, EPS, margins - use realistic approximate figures for that period)
3. Segment performance breakdown
4. Guidance for the next quarter
5. Key Q&A exchanges with analysts

Keep it realistic and consistent with the company's actual business. Format it as a structured transcript excerpt, about 600-800 words."""

    #message = client.messages.create(
    #    model="claude-sonnet-4-20250514",
    #    max_tokens=1200,
    #    messages=[{"role": "user", "content": prompt}]
    #)
    #return message.content[0].text

def analyse_transcript(company: str, ticker: str, quarter: str, year: int, transcript: str) -> dict:
    """Run deep analysis on the transcript using Claude."""
    client = anthropic.Anthropic()

    system = """You are a senior equity research analyst. Analyse earnings call transcripts and return ONLY a JSON object with no markdown, no code fences.
The JSON must have exactly these keys:
- sentiment: one of "Positive", "Neutral", "Negative"
- sentiment_score: integer 1-10 (10 = most positive)
- executive_summary: 2-3 sentence plain-English summary
- revenue_mentioned: string (e.g. "$94.9B" or "Not disclosed")
- eps_mentioned: string (e.g. "$1.46" or "Not disclosed")
- yoy_growth: string (e.g. "+8%" or "Not disclosed")
- key_themes: array of 4-6 short theme strings
- risks: array of 3-4 risk strings
- opportunities: array of 3-4 opportunity strings
- guidance_tone: one of "Raised", "Maintained", "Lowered", "Not given"
- guidance_detail: string (1 sentence)
- analyst_reception: one of "Bullish", "Mixed", "Bearish"
- notable_quote: one memorable direct quote attributed to the CEO (plausible given context)
- competitive_position: 1-2 sentence assessment"""

    prompt = f"""Analyse this {quarter} {year} earnings call transcript for {company} ({ticker}):

{transcript}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def build_price_chart(df: pd.DataFrame, ticker: str, quarter: str, year: int) -> go.Figure:
    fig = go.Figure()

    if df.empty:
        fig.add_annotation(text="No price data available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(family="IBM Plex Mono", size=13, color="#5A5A5A"))
    else:
        close_col = "Close"
        if close_col not in df.columns:
            close_col = [c for c in df.columns if "close" in c.lower()]
            if close_col:
                close_col = close_col[0]
            else:
                close_col = df.columns[1]

        fig.add_trace(go.Scatter(
            x=df["Date"], y=df[close_col],
            mode="lines",
            line=dict(color="#D40000", width=2),
            fill="tozeroy",
            fillcolor="rgba(212,0,0,0.07)",
            name="Close",
        ))
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df[close_col].rolling(5).mean(),
            mode="lines",
            line=dict(color="#0A0A0A", width=1.5, dash="dot"),
            name="5-day MA",
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="#F5F4F0",
        paper_bgcolor="#F5F4F0",
        font=dict(family="IBM Plex Mono", size=11, color="#0A0A0A"),
        xaxis=dict(
            showgrid=True, gridcolor="#D0CFC8", gridwidth=0.5,
            zeroline=False, showline=True, linecolor="#0A0A0A",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#D0CFC8", gridwidth=0.5,
            zeroline=False, showline=True, linecolor="#0A0A0A",
            tickprefix="$", tickfont=dict(size=10),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=10), bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    return fig

def build_sentiment_gauge(score: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        number={"font": {"family": "Bebas Neue", "size": 52, "color": "#0A0A0A"}},
        gauge={
            "axis": {"range": [0, 10], "tickfont": {"family": "IBM Plex Mono", "size": 9}},
            "bar": {"color": "#D40000", "thickness": 0.28},
            "bgcolor": "#D0CFC8",
            "steps": [
                {"range": [0, 4],   "color": "#F5E8E8"},
                {"range": [4, 7],   "color": "#F5F4F0"},
                {"range": [7, 10],  "color": "#E8F5EC"},
            ],
            "threshold": {
                "line": {"color": "#0A0A0A", "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        }
    ))
    fig.update_layout(
        margin=dict(l=16, r=16, t=8, b=8),
        paper_bgcolor="#F5F4F0",
        height=200,
    )
    return fig

def build_multi_quarter_chart(all_data: list) -> go.Figure:
    """Build a combined price chart across multiple quarters."""
    fig = go.Figure()
    colors = ["#D40000", "#0A0A0A", "#5A5A5A", "#9A9A9A", "#D0CFC8", "#1A7A3C"]

    for i, (label, df) in enumerate(all_data):
        if df.empty:
            continue
        close_col = [c for c in df.columns if "close" in str(c).lower()]
        if not close_col:
            continue
        close_col = close_col[0]
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df[close_col],
            mode="lines", name=label,
            line=dict(color=colors[i % len(colors)], width=1.8),
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="#F5F4F0",
        paper_bgcolor="#F5F4F0",
        font=dict(family="IBM Plex Mono", size=11, color="#0A0A0A"),
        xaxis=dict(showgrid=True, gridcolor="#D0CFC8", zeroline=False, linecolor="#0A0A0A"),
        yaxis=dict(showgrid=True, gridcolor="#D0CFC8", zeroline=False, linecolor="#0A0A0A", tickprefix="$"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        hovermode="x unified",
        height=320,
    )
    return fig

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <div style="display:flex;align-items:center;gap:0">
    <p class="header-wordmark">EARNINGS ANALYSER</p>
    <div class="header-rule"></div>
    <span class="header-tag">AI-Powered Transcript Intelligence</span>
  </div>
  <span class="header-tag">▣ SWISS SYSTEM v2.0</span>
</div>
""", unsafe_allow_html=True)

# ── Control Panel ────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])
    with c1:
        st.markdown('<span class="field-label" style="color:#9A9A9A">Company</span>', unsafe_allow_html=True)
        company_sel = st.selectbox("Company", list(COMPANIES.keys()), label_visibility="collapsed")
    with c2:
        st.markdown('<span class="field-label" style="color:#9A9A9A">Quarter</span>', unsafe_allow_html=True)
        quarter_sel = st.selectbox("Quarter", QUARTERS, label_visibility="collapsed")
    with c3:
        st.markdown('<span class="field-label" style="color:#9A9A9A">Year</span>', unsafe_allow_html=True)
        year_sel = st.selectbox("Year", YEARS, label_visibility="collapsed")
    with c4:
        st.markdown('<span class="field-label" style="color:#9A9A9A">&nbsp;</span>', unsafe_allow_html=True)
        run = st.button("▶  ANALYSE", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Main Content ─────────────────────────────────────────────────────────────
if not run:
    st.markdown("""
    <div style="padding:80px 40px;text-align:center">
      <p class="section-label" style="text-align:center">Ready</p>
      <p class="section-title" style="font-size:72px;text-align:center">SELECT A COMPANY<br>TO BEGIN</p>
      <p class="section-sub" style="text-align:center;margin-top:16px">
        Choose a company, quarter, and year above — then press ANALYSE.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Run Analysis ─────────────────────────────────────────────────────────────
ticker      = COMPANIES[company_sel]["ticker"]
name_short  = COMPANIES[company_sel]["name_short"]
start, end  = quarter_to_dates(quarter_sel, year_sel)
prev_qrs    = prev_quarters(quarter_sel, year_sel, n=5)
# take user input and fetch the relevant transcript
with st.spinner(f"Fetching transcript and stock data for {company_sel} {quarter_sel} {year_sel}…"):
    # retrieve the relevant transcript's file path
    transcript_path = recieve_input(ticker, quarter_sel, year_sel)
#
with st.spinner("Running AI analysis…"):
    try:
        from speech_parser.transcript_parser import parse_transcript_to_data
        transcript_data = parse_transcript_to_data(transcript_path)
        print('Parsed transcript into memory')
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()

with st.spinner("Loading stock history…"):
    col1, col2 = st.columns(2)
    with col2:
        plot_stock_data(ticker, year_sel, quarter_sel)
    exit()
    prev_stocks = []
    for pq, py in prev_qrs:
        ps, pe = quarter_to_dates(pq, py)
        pdf = fetch_stock_data(ticker, ps, pe)
        prev_stocks.append((f"{pq} {py}", pdf))
# ── Company Header ────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding:32px 40px 0;display:flex;align-items:flex-end;justify-content:space-between;border-bottom:2px solid #0A0A0A">
  <div>
    <p class="section-label">{ticker}</p>
    <p class="section-title" style="font-size:56px">{name_short}</p>
    <p class="section-sub">{company_sel}</p>
  </div>
  <div style="text-align:right;padding-bottom:8px">
    <span class="q-pill active">{quarter_sel} {year_sel}</span>
    {"".join(f'<span class="q-pill">{q} {y}</span>' for q, y in prev_qrs)}
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
sent_class = {"Positive": "positive", "Neutral": "", "Negative": "negative"}.get(analysis.get("sentiment",""), "")
sent_badge_cls = {"Positive": "sent-positive", "Neutral": "sent-neutral", "Negative": "sent-negative"}.get(analysis.get("sentiment",""), "")

stock_open  = f"${stock_df['Open'].iloc[0]:.2f}"  if not stock_df.empty and "Open"  in stock_df.columns else "N/A"
stock_close = f"${stock_df['Close'].iloc[-1]:.2f}" if not stock_df.empty and "Close" in stock_df.columns else "N/A"

if not stock_df.empty and "Close" in stock_df.columns and len(stock_df) > 1:
    qtr_chg = (stock_df["Close"].iloc[-1] - stock_df["Close"].iloc[0]) / stock_df["Close"].iloc[0] * 100
    qtr_chg_str = f"{qtr_chg:+.1f}%"
    qtr_chg_cls = "positive" if qtr_chg >= 0 else "negative"
else:
    qtr_chg_str = "N/A"
    qtr_chg_cls = ""

st.markdown(f"""
<div class="kpi-grid" style="margin:0;padding:0 40px;background:transparent;gap:0;border:none;display:grid;grid-template-columns:repeat(5,1fr);border-top:none">
  <div class="kpi-card" style="border-right:1px solid #D0CFC8">
    <div class="kpi-label">Sentiment</div>
    <div class="kpi-value {sent_class}" style="font-size:28px">{analysis.get("sentiment","—")}</div>
    <div class="kpi-change">Score {analysis.get("sentiment_score","—")} / 10</div>
  </div>
  <div class="kpi-card" style="border-right:1px solid #D0CFC8">
    <div class="kpi-label">Revenue</div>
    <div class="kpi-value" style="font-size:28px">{analysis.get("revenue_mentioned","—")}</div>
    <div class="kpi-change">YoY {analysis.get("yoy_growth","—")}</div>
  </div>
  <div class="kpi-card" style="border-right:1px solid #D0CFC8">
    <div class="kpi-label">EPS</div>
    <div class="kpi-value" style="font-size:28px">{analysis.get("eps_mentioned","—")}</div>
    <div class="kpi-change">Guidance: {analysis.get("guidance_tone","—")}</div>
  </div>
  <div class="kpi-card" style="border-right:1px solid #D0CFC8">
    <div class="kpi-label">Stock Open → Close</div>
    <div class="kpi-value" style="font-size:24px">{stock_open} → {stock_close}</div>
    <div class="kpi-change">Quarter range</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Qtr. Price Δ</div>
    <div class="kpi-value {qtr_chg_cls}" style="font-size:28px">{qtr_chg_str}</div>
    <div class="kpi-change">Analyst: {analysis.get("analyst_reception","—")}</div>
  </div>
</div>
<div style="border-top:2px solid #0A0A0A;margin:0 0 0 0"></div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  ANALYSIS  ", "  STOCK DATA  ", "  HISTORICAL  "])

# ══ TAB 1 — ANALYSIS ══════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div style="padding:8px 0">', unsafe_allow_html=True)

        # Executive summary
        st.markdown(f"""
        <div class="analysis-block">
          <div class="block-tag">Executive Summary</div>
          <div class="block-heading">
            {quarter_sel} {year_sel} Earnings
            <span class="sentiment-badge {sent_badge_cls}">{analysis.get("sentiment","")}</span>
          </div>
          <div class="block-content">{analysis.get("executive_summary","")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Notable quote
        st.markdown(f"""
        <div class="analysis-block" style="background:#0A0A0A;color:#F5F4F0">
          <div class="block-tag" style="color:#D40000">CEO Quote</div>
          <div style="font-family:'IBM Plex Sans',sans-serif;font-size:18px;font-style:italic;font-weight:300;line-height:1.6;color:#F5F4F0;padding-left:20px;border-left:3px solid #D40000">
            "{analysis.get("notable_quote","")}"
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Guidance
        st.markdown(f"""
        <div class="analysis-block">
          <div class="block-tag">Forward Guidance</div>
          <div class="block-content"><strong style="font-family:'IBM Plex Mono';font-size:11px;letter-spacing:0.1em">{analysis.get("guidance_tone","").upper()}</strong> — {analysis.get("guidance_detail","")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Competitive position
        st.markdown(f"""
        <div class="analysis-block">
          <div class="block-tag">Competitive Position</div>
          <div class="block-content">{analysis.get("competitive_position","")}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div style="padding:24px 0">', unsafe_allow_html=True)

        # Sentiment gauge
        st.markdown('<p class="section-label" style="padding:0">Sentiment Score</p>', unsafe_allow_html=True)
        st.plotly_chart(build_sentiment_gauge(analysis.get("sentiment_score", 5)), use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="rule-h" style="margin:8px 0 20px"></div>', unsafe_allow_html=True)

        # Key themes
        themes = analysis.get("key_themes", [])
        st.markdown('<p class="section-label" style="padding:0">Key Themes</p>', unsafe_allow_html=True)
        for t in themes:
            st.markdown(f'<div style="padding:8px 12px;margin-bottom:4px;background:#F0EFE9;font-family:\'IBM Plex Sans\';font-size:13px;border-left:3px solid #D40000">→ {t}</div>', unsafe_allow_html=True)
        st.markdown('<div class="rule-h" style="margin:16px 0 20px"></div>', unsafe_allow_html=True)

        # Risks & Opportunities
        risks = analysis.get("risks", [])
        opps  = analysis.get("opportunities", [])
        rc, oc = st.columns(2)
        with rc:
            st.markdown('<p class="section-label" style="padding:0">Risks</p>', unsafe_allow_html=True)
            for r in risks:
                st.markdown(f'<div style="padding:6px 10px;margin-bottom:3px;background:#FDE8E8;font-family:\'IBM Plex Sans\';font-size:12px;border-left:2px solid #D40000">▲ {r}</div>', unsafe_allow_html=True)
        with oc:
            st.markdown('<p class="section-label" style="padding:0">Opportunities</p>', unsafe_allow_html=True)
            for o in opps:
                st.markdown(f'<div style="padding:6px 10px;margin-bottom:3px;background:#E8F5EC;font-family:\'IBM Plex Sans\';font-size:12px;border-left:2px solid #1A7A3C">◆ {o}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Raw transcript expander
    with st.expander("  RAW TRANSCRIPT EXCERPT  "):
        st.markdown(f'<div style="font-family:\'IBM Plex Mono\';font-size:12px;line-height:1.8;color:#2E2E2E;white-space:pre-wrap;padding:16px">{transcript}</div>', unsafe_allow_html=True)

# ══ TAB 2 — STOCK DATA ════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <div style="padding:20px 0 12px">
      <p class="section-label">{ticker}</p>
      <p class="section-title" style="font-size:32px">PRICE HISTORY — {quarter_sel} {year_sel}</p>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(build_price_chart(stock_df, ticker, quarter_sel, year_sel),
                    use_container_width=True, config={"displayModeBar": False})

    if not stock_df.empty:
        st.markdown('<div class="rule-h" style="margin:20px 0"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-label">Raw Data</p>', unsafe_allow_html=True)
        display_df = stock_df.copy()
        display_df["Date"] = display_df["Date"].astype(str)
        for col in ["Open", "High", "Low", "Close", "Adj Close"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        if "Volume" in display_df.columns:
            display_df["Volume"] = display_df["Volume"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=280)

# ══ TAB 3 — HISTORICAL ════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div style="padding:20px 0 12px">
      <p class="section-label">{ticker} · Last 6 Quarters</p>
      <p class="section-title" style="font-size:32px">TREND OVERVIEW</p>
    </div>
    """, unsafe_allow_html=True)

    # Combined price chart
    all_chart_data = [(f"{quarter_sel} {year_sel}", stock_df)] + prev_stocks
    st.plotly_chart(build_multi_quarter_chart(all_chart_data), use_container_width=True,
                    config={"displayModeBar": False})

    st.markdown('<div class="rule-h" style="margin:24px 0"></div>', unsafe_allow_html=True)

    # Analyse previous quarters
    st.markdown(f"""
    <div class="divider-label"><span>Previous Quarter Analysis</span></div>
    """, unsafe_allow_html=True)

    # Table header
    st.markdown("""
    <div class="hist-row">
      <span>Quarter</span>
      <span>Sentiment</span>
      <span>Score</span>
      <span>Revenue</span>
      <span>Guidance</span>
    </div>
    """, unsafe_allow_html=True)

    # Current quarter row
    st.markdown(f"""
    <div class="hist-row" style="background:#0A0A0A;color:#F5F4F0">
      <span style="font-family:'IBM Plex Mono';font-size:11px;color:#D40000">{quarter_sel} {year_sel} ★</span>
      <span>{analysis.get("sentiment","—")}</span>
      <span>{analysis.get("sentiment_score","—")}/10</span>
      <span>{analysis.get("revenue_mentioned","—")}</span>
      <span>{analysis.get("guidance_tone","—")}</span>
    </div>
    """, unsafe_allow_html=True)

    for i, (pq, py) in enumerate(prev_qrs):
        with st.spinner(f"Analysing {pq} {py}…"):
            try:
                pt = fetch_transcript_via_api(company_sel, ticker, pq, py)
                pa = analyse_transcript(company_sel, ticker, pq, py, pt)
                row_bg = "#F5F4F0" if i % 2 == 0 else "#EDECE7"
                sent_col = {"Positive": "#1A7A3C", "Neutral": "#5A5A5A", "Negative": "#D40000"}.get(pa.get("sentiment",""), "#0A0A0A")
                st.markdown(f"""
                <div class="hist-row" style="background:{row_bg}">
                  <span style="font-family:'IBM Plex Mono';font-size:11px">{pq} {py}</span>
                  <span style="color:{sent_col};font-weight:500">{pa.get("sentiment","—")}</span>
                  <span>{pa.get("sentiment_score","—")}/10</span>
                  <span>{pa.get("revenue_mentioned","—")}</span>
                  <span>{pa.get("guidance_tone","—")}</span>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"  FULL ANALYSIS — {pq} {py}  "):
                    ec1, ec2 = st.columns([2, 1])
                    with ec1:
                        st.markdown(f'<div class="block-tag">Summary</div><div class="block-content">{pa.get("executive_summary","")}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="margin-top:12px" class="block-tag">Notable Quote</div><div style="font-style:italic;font-size:13px;padding-left:12px;border-left:2px solid #D40000;color:#2E2E2E">"{pa.get("notable_quote","")}"</div>', unsafe_allow_html=True)
                    with ec2:
                        st.markdown('<div class="block-tag">Themes</div>', unsafe_allow_html=True)
                        for t in pa.get("key_themes", []):
                            st.markdown(f'<div style="padding:5px 8px;margin-bottom:3px;background:#F0EFE9;font-size:12px;border-left:2px solid #D40000">→ {t}</div>', unsafe_allow_html=True)
                        # Mini stock chart for this quarter
                        ps_start, ps_end = quarter_to_dates(pq, py)
                        ps_df = prev_stocks[i][1] if i < len(prev_stocks) else pd.DataFrame()
                        if not ps_df.empty:
                            mini_fig = build_price_chart(ps_df, ticker, pq, py)
                            mini_fig.update_layout(height=180, margin=dict(l=0,r=0,t=4,b=0))
                            st.plotly_chart(mini_fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as ex:
                st.markdown(f"""
                <div class="hist-row">
                  <span style="font-family:'IBM Plex Mono';font-size:11px">{pq} {py}</span>
                  <span colspan="4" style="color:#9A9A9A;font-size:12px">Analysis unavailable</span>
                </div>
                """, unsafe_allow_html=True)