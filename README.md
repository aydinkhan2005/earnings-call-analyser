<h1> ▌EARNINGSSENSE — Designed to analyse executive speech</h1>
<span><img src="https://img.shields.io/badge/Anthropic-blue?style=for-the-badge" alt="Anthropic API"> <img src="https://img.shields.io/badge/NLTK-orange?style=for-the-badge" alt="NLTK"> <img src="https://img.shields.io/badge/Streamlit-red?style=for-the-badge" alt="streamlit"> <img src="https://img.shields.io/badge/pytest-yellow?style=for-the-badge" alt="pytest"> <img src="https://img.shields.io/badge/yfinance-darkgreen?style=for-the-badge" alt="yfinance"> <img src="https://img.shields.io/badge/plotly-green?style=for-the-badge" alt="plotly"></span>

<h2>Overview</h2>
<p><strong>EARNINGSSENSE</strong> prompts the user to select:</p>
<ul>
  <li>a company</li>
  <li>a financial year</li>
  <li>a quarter of that financial year</li>
</ul>
<p>The app then presents an analysis of the <b>natural language</b> of the company's executive panel.</p>
<ul>
  <li>It highlights the frequency of hedging for each person, as well as the most common broad topics mentioned</li>
  <li>A stock chart is also shown to give users an idea of how the company is performing in the quarters leading up to the call.</li>
  <li>An <b>AI powered summary</b> where the earnings call analysis is passed as context to <b>Claude Haiku</b> via the Anthropic API.</li>
</ul>
<h2>Example demonstration</h2>
<img src="earnings_call_analyser_dashboard.png">
<p>The dashboard shows the analysis of the earnings call corresponding to the second quarter of the 2020 financial year for the semiconductor company ASML.</p>
<p>The user views:</p>
<ul>
  <li>The exact names and roles of the executive panel members.</li>
  <li>Hedging rate separated by <b>executive member</b> and by <b>call section (presentation vs Q&A)</b>.</li>
  <li>An <b>AI powered summary</b> which gives a recommendation to the user on whether to invest, acting as a financial analyst and earnings call language expert.</li>
  <li>The top 5 most mentioned topics in the earnings call. This gives an idea of what the company is currently focused on.</li>
</ul>
<h2>Data Sources</h2>
Earnings call transcripts sourced from Earnings Calls Transcripts - NASDAQ - 2016-2020 on Kaggle.
Originally from Thomson Reuters. See data/LICENSE for full license details.
