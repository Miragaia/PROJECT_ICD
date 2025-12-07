# Milestone 3 — Reviews Pipeline

This milestone consolidates an end-to-end pipeline to fetch, preprocess, analyze, and visualize Google reviews for POIs in Aveiro.

Folders
- docs: Documentation and notes
- input: Input data (e.g., pois_aveiro.csv)
- output: Pipeline outputs (CSV, figures)
- notebooks: Jupyter notebooks with the full pipeline

Quickstart
1. Place your pois_aveiro.csv in input/
2. Set environment variable GOOGLE_API_KEY for Google Places API v1
3. Open notebooks/reviews_pipeline.ipynb and run cells sequentially

Notes
- Google Places API often returns at most 5 reviews per place
- Be mindful of quotas and rate limits; the notebook uses small sleeps and basic retries
