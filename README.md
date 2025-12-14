# PROJECT_ICD

## Authors: Miguel Miragaia (108317) & Tomé de Almeida (127986)


Project for the ICD course: data collection and analysis of Points of Interest (POIs) in Aveiro.

This repository contains notebooks, data and helper scripts used to fetch Google Places reviews for POIs, process amenities and run basic NLP analysis (sentiment / topic modeling). The work was produced as part of the Milestone_2 deliverable.
## Repository layout

- `Milestone_2/` — project milestone with data, notebooks and API examples
	- `pois_aveiro.csv` — input POIs (OSM-derived)
	- `Reviews_Amenities/` — notebooks and outputs for fetching and processing reviews

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

Notes
- Virtualenv lives at `.venv/` in the repo root; safe to delete/recreate.
- Requirements include: pandas, numpy, seaborn, matplotlib, scikit-learn, shapely, nltk, langdetect, requests, wordcloud, vaderSentiment, folium/streamlit-folium, streamlit, plotly, and related NLP/geo libs.