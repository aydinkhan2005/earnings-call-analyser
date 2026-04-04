<h1> ▌EARNINGSSENSE — Analysing Executive Speech</h1>
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
<h2>Process From User Input To Output</h2>
<br>
<div align="center"><img src="inference_pipeline.drawio.svg"/></div>
<br>
<div align="center">
  <table>
    <tr>
      <td>🟨 Dashboard UI & Output</td>
      <td>🟪 Data / NLP</td>
      <td>🟦 ML models</td>
    </tr>
  </table>
</div>
<h2>Training the Classifiers</h2>
<p>Training the Logistic Regression models required two labelled datasets.</p>
<ul>
  <li>Dataset 1 was for training the hedging model. This was a <b>binary classification</b> problem where 1 would denote hedging and 0 otherwise.</li>
  <li>Dataset 2 was for training the topic classification model. This was a <b>multi class classifiaction</b>problem ranging from topic 1 through to topic 11.</li>
</ul>
<h3>The problem</h3>
<ul>
  <li>No pre-labelled dataset existed for our purposes so we had to create one by splitting our 57000 (approx.) sentences worth of transcript data into a train and test set.</li>
  <li>Each sentence was then labelled (0-1 for hedging, 1-11 for topic) by <b>Claude Haiku</b> via the <b>Anthropic API</b>.</li>
</ul>
<h3>The API costs</h3>
<ul>
  <li>The <b>brute force sequential method</b> of sending one API request at a time yielded a proecssing time of <b>approximatley 8 minutes per transcript</b>.</li>
  <li>Applied to all transcripts available, this would have taken an approximate <b>25 hours</b> and around <b>$30</b> to label the entire dataset with binary hedging labels alone.</li>
</ul>
<h3>Solution to the API costs</h3>
<ul>
  <li>We sent each API request, asking Claude to label 10 sentences at a time rather than one.</li>
  <li>Using <code>asyncio</code>, we were able to send about <b>10 concurrent requests</b>.</li>
  <li>As a result, we reduced the binary labelling time <b>from 8 minutes to about 5-7 seconds</b> per transcript.</li>
  <li>Total binary labelling for the entire set of 171 transcripts took only <b>3 hours</b> compared to the <b>estimated 25 hours</b> before.</li>
  <li>Total labelling costs for creating the hedged sentences dataset took <b>$4.24</b>, a significant decrease from the estimated <b>$30</b>.</li>
</ul>
<p>This same concurrency and batching system was used for creating the topic dataset but slightly more costly due to the multi-class labels.</p>
<h2>Data Sources</h2>
Earnings call transcripts sourced from Earnings Calls Transcripts - NASDAQ - 2016-2020 on Kaggle.
Originally from Thomson Reuters. See data/LICENSE for full license details.
