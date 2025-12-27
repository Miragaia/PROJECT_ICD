# Aveiro POI Reviews Dashboard

## Overview

The **Aveiro POI Reviews Dashboard** is an interactive web application built with **Streamlit** that enables exploratory analysis of Google reviews collected for Points of Interest (POIs) in Aveiro. The dashboard visualizes ratings, sentiment, top places, and geographic locations on an interactive map powered by Leaflet.

**Built with:**
- Streamlit (UI framework)
- Plotly (interactive charts)
- Folium/Leaflet (interactive map)
- Pandas (data handling)

---

## Features

### 1. **Data Filters (Sidebar)**

Fine-tune the displayed data using the left sidebar:

- **Language**: Select English (en), Portuguese (pt), or both
- **Rating range**: Slider to filter reviews by star rating (1.0–5.0)
- **Primary type**: Checkboxes to filter by place category (restaurant, cafe, museum, etc.)
- **Search place name**: Text input to search by place name (case-insensitive partial match)

All filters are interactive; charts, KPIs, and map update in real time.

### 2. **Key Performance Indicators (KPIs)**

Four metrics displayed at the top summarize the filtered dataset:

- **Reviews**: Total count of reviews matching current filters
- **Places**: Number of unique places (place_id) in the filtered set
- **Avg rating**: Mean star rating (1–5 scale)
- **% English**: Percentage of reviews in English language

### 3. **Rating Distribution Chart**

**Type**: Histogram with marginal box plot

**Shows:**
- Distribution of star ratings (1–5) split by language (color-coded)
- Number of bins = 20
- Kernel density estimate (KDE) overlay for smooth distribution visualization

**Insights:**
- Identify rating concentration (e.g., 4–5 stars vs. lower ratings)
- Compare EN vs. PT rating patterns

### 4. **Sentiment Distribution (English only)**

**Type**: Histogram

**Shows:**
- VADER sentiment compound scores for English reviews only
- Score range: [-1 (negative), 0 (neutral), +1 (positive)]
- Number of bins = 30

**Behavior:**
- Displays only when English reviews are present in filtered data
- Automatically hidden if filter excludes English or no EN data matches

**Note:** Portuguese sentiment requires a separate sentiment model; currently VADER (English-tuned) is used.

### 5. **Top Places by Review Count**

**Type**: Horizontal bar chart

**Shows:**
- Top 12 places ranked by number of reviews
- Sorted in descending order
- Interactive hover for exact counts

**Use cases:**
- Identify most-reviewed POIs
- Focus analysis on high-visibility places

### 6. **Interactive Map with Heatmap Layers**

**Type**: Leaflet map with multiple view modes

**View Modes (Radio Selection):**

1. **Markers (Clustered)** - Default view
   - Blue circle markers with clustering for dense areas
   - Click markers for detailed popups
   - Popups show: place name, rating, type, language, review preview

2. **Rating Heatmap** - Quality intensity view
   - Color gradient based on average rating per place
   - Gradient: Blue (low) → Yellow → Orange → Red (high)
   - Small white markers show place locations
   - Popup shows average rating per place
   - Aggregates multiple reviews per place

3. **Review Density Heatmap** - Activity intensity view
   - Color gradient based on review count/concentration
   - Gradient: Light Blue → Cyan → Lime → Yellow → Red
   - Shows where most reviews are concentrated
   - Helps identify high-activity zones

**Common Features:**
- **Center**: Dynamically centers on the mean latitude/longitude of filtered places
- **Zoom**: Default zoom level 13 (neighborhood-level detail)
- **Base tiles**: CartoDB Positron (clean, light aesthetic)
- **Layer control**: Toggle between different map layers
- **Responsive**: Adapts to filter changes in real-time

**Heatmap Parameters:**
- Radius: 20-25 pixels
- Blur: 15-20 pixels for smooth gradients
- Min opacity: 0.2-0.3
- Max zoom: 18 (preserves heatmap at high zoom levels)

**Use Cases:**
- **Markers**: Explore individual places and read reviews
- **Rating Heatmap**: Identify areas with high-quality establishments
- **Density Heatmap**: Find popular/frequently-reviewed zones

---

## Data Source

The dashboard reads from:

```
../output/reviews_enriched.csv
```

**Required columns:**
- `lat`, `lon`: Geographic coordinates
- `place_name`: Place identifier
- `place_id`: Unique place ID (for deduplication)
- `rating`: Star rating (1–5)
- `lang`: Detected language (en, pt, or null)
- `sentiment_compound`: VADER sentiment score (English only; NaN for PT)
- `place_primary_type`: Place category
- `review_text`: Original review text (for preview)

**Data freshness:** All data is cached on first load; restart the app to reload.

---

## Installation & Running

### Prerequisites

- Python 3.10+
- Virtual environment activated (see repo `README.md`)
- Dependencies installed: `pip install -r requirements.txt`

### Launch the dashboard

From the repo root:

```bash
cd Milestone_3
streamlit run dashboard/app.py
```

Streamlit will output a local URL (typically `http://localhost:8501`); open it in your web browser.

### Stopping the dashboard

Press `Ctrl+C` in the terminal running Streamlit.

---

## Usage Examples

### Example 1: Compare English vs. Portuguese reviews

1. Open the sidebar filters
2. Select only "en" in the Language filter
3. View rating distribution and sentiment for English speakers
4. Repeat with "pt" to see Portuguese patterns

### Example 2: Find the most-reviewed restaurants

1. Set **Primary type** = "restaurant"
2. Observe the "Top places by review count" chart
3. Click a marker on the map to inspect a specific restaurant

### Example 3: Filter highly-rated places

1. Set **Rating range** to 4.0–5.0
2. See only places with high ratings
3. Check the map and top places chart for 4–5 star establishments

### Example 4: Explore a specific place

1. Type a place name in **Search place name** (e.g., "Biblioteca")
2. All charts and the map update to show only that place
3. Use the map popup to read individual reviews

### Example 5: Identify high-quality zones (Rating Heatmap)

1. Switch map view to "Rating Heatmap"
2. Look for red/orange zones (high average ratings)
3. Zoom in to see specific places in those areas
4. Compare with density heatmap to find high-quality + popular zones

### Example 6: Find review hotspots (Density Heatmap)

1. Switch to "Review Density Heatmap"
2. Identify red/yellow zones with high review concentration
3. These indicate tourist/commercial hotspots
4. Cross-reference with rating heatmap to assess quality

---

## Technical Details

### Architecture

```
dashboard/
├── app.py                 # Main Streamlit application
├── DASHBOARD.md           # This file
└── (other assets if added)
```

### Key functions

| Function | Purpose |
|----------|---------|
| `load_data()` | Load and preprocess enriched CSV; cache for performance |
| `@st.cache_data` | Streamlit caching decorator (avoid reloads on interaction) |
| `st.multiselect()`, `st.slider()`, `st.text_input()` | Filter widgets |
| `px.histogram()`, `px.bar()` | Plotly charts |
| `folium.Map()`, `folium.CircleMarker()` | Leaflet map elements |
| `st_folium()` | Render Folium map in Streamlit |

### Performance notes

- **Data loading**: CSV is cached; restart app to reload.
- **Chart rendering**: Plotly charts are interactive and responsive.
- **Map rendering**: Marker clustering scales to 1000+ markers efficiently.
- **Filter responsiveness**: All updates are near-instantaneous.

---

## Limitations & Future Enhancements

### Current limitations

1. **Portuguese sentiment**: VADER is English-only. A Portuguese model (e.g., PT-BERT, SentiLex) would enable PT sentiment visualization.
2. **Temporal analysis**: No date-range filter; all reviews are aggregated over time.
3. **Place details**: Popup shows basic info; more detailed place profiles could be added.
4. **Statistical tests**: No significance tests or confidence intervals for comparative analysis.

### Suggested enhancements

1. **Time series**: Add publish date filter and trend charts
2. **Keyword analysis**: Display TF-IDF keywords per place or language
3. **Export**: Add CSV/PDF export of filtered results
4. **Custom map layers**: Toggle between satellite, street, and other tile sets
5. **Advanced search**: Regex or fuzzy matching for place names
6. **Multi-language sentiment**: Integrate Portuguese sentiment model
7. **Mobile optimization**: Responsive design for phones/tablets
8. **Sentiment heatmap**: Add heatmap layer colored by average sentiment (EN only)
9. **Comparative analysis**: Side-by-side comparison of two places/zones
10. **Route planning**: Connect high-rated places for tourism routes

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Data file not found" | Ensure `reviews_enriched.csv` is at `../output/reviews_enriched.csv` relative to `app.py` |
| Empty charts/map | Check filters; they may be excluding all data. Reset to default filters. |
| Slow map rendering | Reduce number of places using filters; large datasets (1000+ markers) may lag. |
| Streamlit not found | Activate venv and reinstall: `pip install streamlit streamlit-folium` |
| Port 8501 already in use | Run with `streamlit run app.py --server.port 8502` (or another port) |

---

## Credits & Attribution

- **Data source**: Google Places API v1 (Nearby Search)
- **Framework**: Streamlit, Plotly, Folium
- **Analysis pipeline**: `Milestone_3/notebooks/reviews_pipeline.ipynb`

---

## Contact & Support

For issues or questions about the dashboard, refer to the main repository `README.md` or contact the project authors.

---

*Last updated: December 15, 2025*

---

## Precomputed Topic Analysis (LDA)

To avoid training LDA models live in the app, precompute topics and assignments first.

From the repo root:

```bash
# Default: train 3, 5, 7, 10 topics for both EN and PT with 10 passes
python3 Milestone_3/scripts/precompute_topics.py

# Custom: specify topic counts, passes, min word frequency, and languages
python3 Milestone_3/scripts/precompute_topics.py --topics 3 5 8 --passes 15 --min-word-freq 3
python3 Milestone_3/scripts/precompute_topics.py --topics 5 --languages en  # English only
python3 Milestone_3/scripts/precompute_topics.py --help  # See all options
```

**CLI Options:**
- `--topics`: Number of topics (can specify multiple, e.g., `3 5 7 10`)
- `--passes`: LDA training passes (default: 10, higher = better quality but slower)
- `--min-word-freq`: Minimum word frequency in dictionary (default: 2)
- `--languages`: Languages to process: `en`, `pt`, or both (default: `en pt`)

This generates:

- `Milestone_3/output/topics_{lang}_{n}.json`: top words per topic
- `Milestone_3/output/dom_{lang}_{n}.csv`: dominant topic assignment per review with context

Then run the dashboard and use the "Topic Analysis (Precomputed)" section to explore topics and representative reviews instantly. The dropdown will show all available precomputed topic counts.
