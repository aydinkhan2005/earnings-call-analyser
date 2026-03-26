import streamlit as st
import streamlit.components.v1 as components
def render_sidebar():
    html = """
    <style>
    :root {
      --ink: #111;
      --light: #e5e5e5;
      --off: #f7f7f7;
      --mid: #777;
      --red: #e5484d;
      --amber: #f5a524;
      --green: #2ecc71;
    }

    body {
      margin: 0;
      font-family: 'IBM Plex Sans', sans-serif;
    }

    .sidebar {
      border-right: 1px solid var(--light);
      padding: 1.75rem 1.25rem;
      background: var(--off);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow-y: auto;
    }

    /* Logo */
    .logo-row {
      display: flex;
      align-items: center;
      gap: .6rem;
      margin-bottom: 1.75rem;
    }
    .logo-sq {
      width: 20px;
      height: 20px;
      background: var(--red);
    }
    .logo-name {
      font-size: .7rem;
      font-weight: 500;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    /* Company */
    .sb-co-label {
      font-size: .55rem;
      letter-spacing: .13em;
      text-transform: uppercase;
      color: var(--mid);
      margin-bottom: .3rem;
    }
    .sb-co-name {
      font-size: 1rem;
      font-weight: 500;
      margin-bottom: .15rem;
    }
    .sb-co-meta {
      font-size: .65rem;
      color: var(--mid);
      margin-bottom: 1.5rem;
    }

    /* Divider */
    .sb-divider {
      height: 1px;
      background: var(--light);
      margin: 1rem 0;
    }

    /* Score */
    .sb-score-label {
      font-size: .55rem;
      letter-spacing: .13em;
      text-transform: uppercase;
      color: var(--mid);
      margin-bottom: .4rem;
    }
    .sb-score-num {
      font-size: 2.8rem;
      font-weight: 300;
      line-height: 1;
      margin-bottom: .2rem;
    }
    .sb-score-num.high { color: var(--red); }
    .sb-score-num.med { color: var(--amber); }
    .sb-score-num.low { color: var(--green); }

    .sb-verdict {
      font-size: .65rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: .1em;
      margin-bottom: .25rem;
    }
    .sb-verdict.high { color: var(--red); }
    .sb-verdict.med { color: var(--amber); }
    .sb-verdict.low { color: var(--green); }

    .sb-verdict-sub {
      font-size: .63rem;
      color: var(--mid);
      line-height: 1.6;
      margin-bottom: 1.25rem;
    }

    /* Stats */
    .sb-mini-label {
      font-size: .55rem;
      letter-spacing: .13em;
      text-transform: uppercase;
      color: var(--mid);
      margin-bottom: .5rem;
    }
    .sb-stat-row {
      display: flex;
      justify-content: space-between;
      padding: .3rem 0;
      border-bottom: 1px solid var(--light);
    }
    .sb-stat-row:last-child {
      border-bottom: none;
    }
    .sb-stat-k {
      font-size: .65rem;
      color: var(--mid);
    }
    .sb-stat-v {
      font-size: .68rem;
      font-weight: 500;
      color: var(--ink);
    }

    /* Navigation (visual only) */
    .sb-nav {
      margin-top: 1.5rem;
      display: flex;
      flex-direction: column;
    }
    .sb-nav button {
      text-align: left;
      background: none;
      border: none;
      font-size: .73rem;
      color: var(--mid);
      padding: .35rem 0 .35rem .65rem;
      border-left: 2px solid transparent;
    }
    .sb-nav button.active {
      color: var(--ink);
      border-left-color: var(--red);
      font-weight: 500;
    }
    </style>

    <div class="sidebar">
      <div class="logo-row">
        <div class="logo-sq"></div>
        <div class="logo-name">EarningsSense</div>
      </div>

      <div class="sb-co-label">Company</div>
      <div class="sb-co-name">NVIDIA Corporation</div>
      <div class="sb-co-meta">NVDA — Q3 2024<br>Nov 20, 2024</div>

      <div class="sb-divider"></div>

      <div class="sb-score-label">Hedging score</div>
      <div class="sb-score-num med">38<span style="font-size:1.4rem">%</span></div>
      <div class="sb-verdict med">Moderate caution</div>
      <div class="sb-verdict-sub">
        Executives show measured optimism with notable hedging around supply chain and margin outlook.
      </div>

      <div class="sb-divider"></div>

      <div class="sb-mini-label">Call statistics</div>
      <div style="margin-bottom:1rem">
        <div class="sb-stat-row"><span class="sb-stat-k">Total sentences</span><span class="sb-stat-v">284</span></div>
        <div class="sb-stat-row"><span class="sb-stat-k">Hedged</span><span class="sb-stat-v" style="color:var(--red)">108</span></div>
        <div class="sb-stat-row"><span class="sb-stat-k">CEO hedging</span><span class="sb-stat-v">41%</span></div>
        <div class="sb-stat-row"><span class="sb-stat-k">CFO hedging</span><span class="sb-stat-v">52%</span></div>
        <div class="sb-stat-row"><span class="sb-stat-k">Q&A hedging</span><span class="sb-stat-v" style="color:var(--red)">61%</span></div>
        <div class="sb-stat-row"><span class="sb-stat-k">Model confidence</span><span class="sb-stat-v">0.87</span></div>
      </div>

      <div class="sb-nav">
        <button class="active">Overview</button>
        <button>Transcript analysis</button>
        <button>Model features</button>
        <button>Quarter comparison</button>
      </div>
    </div>
    """

    st.title("Earnings Call Analyzer")

    st.markdown(html, unsafe_allow_html=True)