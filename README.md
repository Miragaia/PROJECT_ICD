# PROJECT_ICD

## Authors: Miguel Miragaia (108317) & Tomé de Almeida (127986)


Project for the ICD course: data collection and analysis of Points of Interest (POIs) in Aveiro.

This repository contains notebooks, data and helper scripts used to fetch Google Places reviews for POIs, process amenities and run basic NLP analysis (sentiment / topic modeling). The work was produced as part of the Milestone_2 deliverable.
## Repository layout

- `Milestone_2/` — project milestone with data, notebooks and API examples
	- `pois_aveiro.csv` — input POIs (OSM-derived)
	- `Reviews_Amenities/` — notebooks and outputs for fetching and processing reviews

## Reproducibility & Python virtualenv

We recommend using a Python virtual environment to reproduce the analysis. This repo provides a helper script to create a local venv and install dependencies from a `requirements.txt` file.

Prerequisites

- Python 3.10+ (the code was tested with Python 3.12 on Linux)
- Git

Create and activate the venv (one-step)

1. Create the venv and install Python dependencies (script will create `.venv/`):

```bash
./scripts/create_venv.sh
```

2. Activate the virtual environment:

```bash
source .venv/bin/activate
```

3. Run the notebook and select the venv as the environment

Running the notebooks

Open `Milestone_2/Reviews_Amenities/reviews.ipynb` and follow the top cells to set the `GOOGLE_API_KEY` environment variable (recommended) or export it in your shell before launching Jupyter:

```bash
export GOOGLE_API_KEY="YOUR_KEY"
```