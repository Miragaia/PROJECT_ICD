# PROJECT_ICD

## Authors: Miguel Miragaia (108317) & Tomé de Almeida (127986)


Project for the ICD course: data collection and analysis of Points of Interest (POIs) in Aveiro.

This repository contains notebooks, data and helper scripts used to fetch Google Places reviews for POIs, enrich them with NLP analysis (multilingual sentiment via VADER and BERTweet-PT), perform topic modeling (LDA), and visualize results in an interactive Streamlit dashboard.

## Repository layout

- `Milestone_2/` — initial milestone with data, notebooks and API examples
	- `pois_aveiro.csv` — input POIs (OSM-derived)
	- `Reviews_Amenities/` — notebooks and outputs for fetching and processing reviews
	- `API_examples/` — Google Places API usage examples

- `Milestone_3/` — extended analysis with sentiment enrichment, topic modeling, and interactive dashboard
	- `input/` — input data (enriched reviews CSV)
	- `notebooks/` — analysis pipeline notebook
		- `reviews_pipeline.ipynb` — main pipeline: loads reviews, detects language, applies sentiment (VADER + BERTweet-PT), plots exploratory charts
	- `scripts/` — helper scripts
		- `precompute_topics.py` — precompute LDA topics and topic assignments offline for fast dashboard loading
	- `dashboard/` — Streamlit interactive dashboard
		- `app.py` — main dashboard application with multiple map views, charts, and topic analysis
		- `DASHBOARD.md` — detailed dashboard documentation
	- `output/` — generated files
		- `reviews_enriched.csv` — reviews with language, sentiment, rating
		- `topics_{lang}_{n}.json` — precomputed LDA topics (e.g., `topics_en_5.json`)
		- `dom_{lang}_{n}.csv` — topic assignments per review (e.g., `dom_pt_3.csv`)

## Reproducibility: Python virtual environment (root-level)

Create a single virtual environment in the repository root (outside the Milestone folders) to run both the notebooks and the Streamlit dashboard.

Prerequisites
- Python 3.10+ (tested with Python 3.12 on Linux)
- Git

Setup (from repo root)
```bash
python3 -m venv .venv              # create venv in repo root
source .venv/bin/activate          # activate (Linux/macOS)
pip install --upgrade pip
pip install -r requirements.txt    # installs notebooks + dashboard deps
```

Activation reminder
- Linux/macOS: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Deactivate: `deactivate`

Environment variable
```bash
export GOOGLE_API_KEY="YOUR_KEY"
```

Running the notebooks
- Launch Jupyter/Lab using the venv Python so the kernel picks up installed deps:
```bash
python -m pip install notebook jupyterlab  # if not already installed
jupyter lab
```
- Open the target notebook (e.g., `Milestone_3/notebooks/reviews_pipeline.ipynb`) and ensure the kernel points to `.venv`.

Running the Streamlit dashboard
```bash
cd Milestone_3
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501` with interactive visualizations, filters, and maps.

## Milestone 3: New Features & Workflow

### Sentiment Analysis (Multilingual)

- **English reviews**: Analyzed using **VADER** (Valence Aware Dictionary and sEntiment Reasoner)
- **Portuguese reviews**: Analyzed using **BERTweet-PT** (multilingual BERT fine-tuned for Portuguese)
- Both models output sentiment compound scores in [-1, +1] range
- Dashboard includes comparative sentiment distribution charts split by language

### Topic Modeling (LDA)

To avoid live model training in the dashboard, precompute topics and assignments offline:

```bash
cd Milestone_3

# Default: train 3, 5, 7, 10 topics for both EN and PT with 10 passes
python3 scripts/precompute_topics.py

# Custom: specify topic counts, passes, min word frequency, and languages
python3 scripts/precompute_topics.py --topics 3 5 8 --passes 15 --min-word-freq 3
python3 scripts/precompute_topics.py --topics 5 --languages en  # English only
python3 scripts/precompute_topics.py --help  # See all options
```

This generates JSON topic files and CSV assignments in `output/` for the dashboard to load instantly.

### Interactive Dashboard

The Streamlit dashboard (`Milestone_3/dashboard/app.py`) includes:

- **Data Filters**: Language, rating range, place type, place name search
- **KPIs**: Review count, unique places, average rating, % English
- **Charts**: Rating distribution, sentiment comparison (EN vs PT), top places bar chart
- **Topic Analysis Panel**: Explore precomputed LDA topics, view topic distributions, drill into representative reviews
- **Interactive Maps** with 4 view modes:
  - **Markers (Clustered)**: Blue markers with auto-expansion at high zoom (≥16) for individual inspection
  - **Rating Heatmap**: Color gradient by average rating per location (~100m grid aggregation)
  - **Review Density Heatmap**: Color gradient by review concentration
  - **Topic View**: Topic-colored markers with precomputed LDA assignments; respects filters

See [Milestone_3/dashboard/DASHBOARD.md](Milestone_3/dashboard/DASHBOARD.md) for detailed dashboard documentation.

Notes
- Virtualenv lives at `.venv/` in the repo root; safe to delete/recreate.
- Requirements include: pandas, numpy, seaborn, matplotlib, scikit-learn, shapely, nltk, langdetect, requests, wordcloud, vaderSentiment, transformers (for BERTweet-PT), gensim (for LDA), folium/streamlit-folium, streamlit, plotly, and related NLP/geo libs.
- Dashboard data is cached on first load; restart the app to reload from CSV.