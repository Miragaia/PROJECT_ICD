# Milestone 3 — Reviews Pipeline, Sentiment Analysis & Interactive Dashboard

This milestone consolidates an end-to-end pipeline to fetch, preprocess, analyze (sentiment + topic modeling), and visualize Google reviews for POIs in Aveiro.

## Folder Structure

- **docs/** — Documentation and notes (this file)
- **input/** — Input data (enriched reviews CSV)
- **output/** — Pipeline outputs
	- `reviews_enriched.csv` — reviews with language detection and sentiment scores
	- `topics_{lang}_{n}.json` — precomputed LDA topic words (e.g., `topics_en_5.json`, `topics_pt_3.json`)
	- `dom_{lang}_{n}.csv` — topic assignments per review (dominant topic + probability)
- **notebooks/** — Jupyter notebooks with the full pipeline
	- `reviews_pipeline.ipynb` — main analysis notebook: fetch, preprocess, sentiment, visualizations
- **scripts/** — Helper scripts
	- `precompute_topics.py` — train LDA models offline and save precomputed topics/assignments
- **dashboard/** — Interactive Streamlit dashboard
	- `app.py` — main application with filters, charts, maps, and topic analysis
	- `DASHBOARD.md` — detailed dashboard user guide

## Workflow Overview

### 1. Fetch & Preprocess (Notebook: `reviews_pipeline.ipynb`)

- Load POIs from `input/` or upstream data
- Fetch reviews via Google Places API v1 (Nearby Search + Place Details)
- Clean text, detect language (English/Portuguese)
- Output: `output/reviews_enriched.csv`

### 2. Sentiment Analysis (In Notebook)

- **English reviews**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
	- Returns compound score in [-1, +1] range
- **Portuguese reviews**: BERTweet-PT (multilingual BERT fine-tuned for Portuguese)
	- Also returns compound score in [-1, +1]
- Comparison chart: sentiment distribution split by language

### 3. Topic Modeling (Precompute Script: `scripts/precompute_topics.py`)

Train LDA models offline to avoid slow inference in the dashboard:

```bash
# Default: train 3, 5, 7, 10 topics for both EN and PT
python3 scripts/precompute_topics.py

# Custom: specify topics, passes, min-word-freq, languages
python3 scripts/precompute_topics.py --topics 3 5 8 --passes 15 --min-word-freq 3
python3 scripts/precompute_topics.py --topics 5 --languages en  # English only
python3 scripts/precompute_topics.py --help  # View all options
```

Outputs:
- `topics_{lang}_{n}.json` — top words per topic
- `dom_{lang}_{n}.csv` — topic assignment per review with dominant topic ID and probability

### 4. Interactive Dashboard (`dashboard/app.py`)

Run the Streamlit app for interactive exploration:

```bash
cd Milestone_3
streamlit run dashboard/app.py
```

**Features:**
- **Sidebar Filters**: Language, rating range, place type, place name search
- **KPIs**: Review count, unique places, avg rating, % English
- **Charts**: Rating distribution, sentiment comparison (EN vs PT), top places
- **Topic Analysis Panel**: Explore precomputed LDA topics, distributions, representative reviews
- **4 Interactive Map Modes**:
  1. **Markers (Clustered)** — Blue markers that expand at high zoom (≥16)
  2. **Rating Heatmap** — Color gradient by avg rating (~100m grid)
  3. **Review Density Heatmap** — Color gradient by review concentration
  4. **Topic View** — Topic-colored markers with precomputed assignments

See [dashboard/DASHBOARD.md](../dashboard/DASHBOARD.md) for detailed usage guide.

## Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment (see repo root README)
- Google API Key (for data fetching)

### Step 1: Fetch & Enrich Reviews

```bash
# Activate venv
source ../.venv/bin/activate

# Set API key
export GOOGLE_API_KEY="your_key_here"

# Run notebook
jupyter lab
# Open notebooks/reviews_pipeline.ipynb, run all cells
# Output: output/reviews_enriched.csv
```

### Step 2: Precompute Topics (Optional)

```bash
python3 scripts/precompute_topics.py
# Generates: output/topics_*.json, output/dom_*.csv
```

### Step 3: Launch Dashboard

```bash
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

## Technical Notes

- **Google Places API**: Often returns ≤5 reviews per place due to quota limits
- **Rate Limiting**: Notebook uses sleeps and retries to respect API quotas
- **Language Detection**: Uses `langdetect` library; fallback to English if ambiguous
- **Sentiment Models**:
	- VADER: Fast, rule-based, English-optimized
	- BERTweet-PT: Neural, Portuguese-optimized (slower but more accurate)
- **Topic Modeling**: Gensim LDA with configurable passes/min-word-frequency
- **Dashboard Caching**: Data and precomputed topics are cached on first load; restart app to reload

## Limitations & Future Work

- **Temporal analysis**: All reviews aggregated over time; no date-range filtering
- **Live topic training**: Dashboard loads only precomputed topics; live LDA not supported
- **Statistical inference**: No significance tests or confidence intervals
- **Mobile optimization**: Dashboard not yet optimized for mobile devices

## References

- **VADER**: Hutto & Gilbert (2014) — Rule-based sentiment analysis
- **BERTweet-PT**: Multilingual BERT fine-tuned for Portuguese social media text
- **Gensim LDA**: Efficient topic modeling library for Python
- **Streamlit**: Fast web app framework for data science
