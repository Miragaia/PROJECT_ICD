"""Streamlit dashboard for Aveiro POI reviews.
Run with: streamlit run dashboard/app.py (from Milestone_3 directory).
"""
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import plugins

# ---------- Config ----------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "output" / "reviews_enriched.csv"
MAP_ZOOM_DEFAULT = 13

st.set_page_config(page_title="Aveiro POI Reviews", layout="wide")


# ---------- Data ----------
@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"Data file not found: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Coerce numeric fields
    df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")
    df["sentiment_compound"] = pd.to_numeric(df.get("sentiment_compound"), errors="coerce")
    # Drop rows without coordinates or names
    df = df.dropna(subset=["lat", "lon", "place_name"])
    return df


df = load_data(DATA_PATH)

st.title("Aveiro POI Reviews Dashboard")
st.caption("Interactive exploration of Google reviews fetched for OSM POIs in Aveiro.")

if df.empty:
    st.stop()

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")
langs = st.sidebar.multiselect("Language", options=["en", "pt"], default=["en", "pt"])
min_rating, max_rating = st.sidebar.slider("Rating range", 1.0, 5.0, (1.0, 5.0), 0.1)
ptype_opts = sorted([p for p in df["place_primary_type"].dropna().unique()])
ptype_sel = st.sidebar.multiselect("Primary type", options=ptype_opts)
place_query = st.sidebar.text_input("Search place name")

filtered = df[df["lang"].isin(langs)]
filtered = filtered[filtered["rating"].between(min_rating, max_rating)]
if ptype_sel:
    filtered = filtered[filtered["place_primary_type"].isin(ptype_sel)]
if place_query:
    filtered = filtered[filtered["place_name"].str.contains(place_query, case=False, na=False)]

# ---------- KPIs ----------
st.subheader("Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Reviews", len(filtered))
col2.metric("Places", filtered["place_id"].nunique())
col3.metric("Avg rating", round(filtered["rating"].mean(), 2) if len(filtered) else 0)
col4.metric("% English", round(100 * filtered["lang"].eq("en").mean(), 1) if len(filtered) else 0)

if filtered.empty:
    st.info("No data for current filters.")
    st.stop()

# ---------- Charts ----------
st.markdown("### Ratings")
st.plotly_chart(
    px.histogram(filtered, x="rating", color="lang", nbins=20, marginal="box", title="Rating distribution"),
    use_container_width=True,
)

st.markdown("### Sentiment (English & Portuguese)")
f_en = filtered[filtered["lang"].eq("en")].dropna(subset=["sentiment_compound"])
f_pt = filtered[filtered["lang"].eq("pt")].dropna(subset=["sentiment_compound"])

if len(f_en) > 0 or len(f_pt) > 0:
    # Create sentiment comparison
    sentiment_data = []
    if len(f_en) > 0:
        sentiment_data.extend([{"Sentiment": score, "Language": "English"} for score in f_en["sentiment_compound"]])
    if len(f_pt) > 0:
        sentiment_data.extend([{"Sentiment": score, "Language": "Portuguese"} for score in f_pt["sentiment_compound"]])
    
    if sentiment_data:
        sentiment_df = pd.DataFrame(sentiment_data)
        st.plotly_chart(
            px.histogram(
                sentiment_df,
                x="Sentiment",
                color="Language",
                nbins=30,
                title="Sentiment distribution (VADER for English, TextBlob for Portuguese)",
                barmode="overlay"
            ),
            use_container_width=True,
        )
    
    # KPIs for sentiment
    col1, col2 = st.columns(2)
    if len(f_en) > 0:
        en_mean = f_en["sentiment_compound"].mean()
        en_std = f_en["sentiment_compound"].std()
        col1.metric("English Sentiment (avg)", f"{en_mean:.3f} ± {en_std:.3f}")
    if len(f_pt) > 0:
        pt_mean = f_pt["sentiment_compound"].mean()
        pt_std = f_pt["sentiment_compound"].std()
        col2.metric("Portuguese Sentiment (avg)", f"{pt_mean:.3f} ± {pt_std:.3f}")
else:
    st.info("No sentiment data available for current filters.")

st.markdown("### Top places by review count")
top_places = filtered["place_name"].value_counts().nlargest(12).reset_index()
top_places.columns = ["place_name", "n_reviews"]
st.plotly_chart(
    px.bar(top_places, x="n_reviews", y="place_name", orientation="h", title="Top places"),
    use_container_width=True,
)

# ---------- Map ----------
st.markdown("### Map")

# Map view toggle
map_view = st.radio(
    "Map view",
    ["Markers (Clustered)", "Rating Heatmap", "Review Density Heatmap"],
    horizontal=True,
    help="Switch between marker clusters, rating intensity heatmap, or review density heatmap"
)

mean_lat = filtered["lat"].mean()
mean_lon = filtered["lon"].mean()
center = [mean_lat, mean_lon] if pd.notna(mean_lat) and pd.notna(mean_lon) else [40.6405, -8.6538]

m = folium.Map(location=center, zoom_start=MAP_ZOOM_DEFAULT, tiles="cartodbpositron")

if map_view == "Markers (Clustered)":
    marker_cluster = plugins.MarkerCluster()
    marker_cluster.add_to(m)

if map_view == "Markers (Clustered)":
    for _, row in filtered.iterrows():
        popup_parts = [f"<b>{row['place_name']}</b>"]
        if pd.notna(row.get("rating")):
            popup_parts.append(f"Rating: {row['rating']}")
        if pd.notna(row.get("place_primary_type")):
            popup_parts.append(f"Type: {row['place_primary_type']}")
        if pd.notna(row.get("lang")):
            popup_parts.append(f"Lang: {row['lang']}")
        # include short review preview if available
        review_txt: Optional[str] = row.get("review_text") if "review_text" in row else None
        if isinstance(review_txt, str) and review_txt.strip():
            preview = (review_txt[:120] + "…") if len(review_txt) > 120 else review_txt
            popup_parts.append(f"Review: {preview}")
        popup_html = "<br>".join(popup_parts)

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc",
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(marker_cluster)

elif map_view == "Rating Heatmap":
    # Aggregate by place (mean rating per place)
    place_agg = filtered.groupby(["place_id", "place_name"]).agg({
        "lat": "first",
        "lon": "first",
        "rating": "mean"
    }).reset_index()
    
    # Create heatmap data: [lat, lon, weight]
    heat_data = [[row["lat"], row["lon"], row["rating"]] for _, row in place_agg.iterrows()]
    
    if heat_data:
        plugins.HeatMap(
            heat_data,
            min_opacity=0.3,
            max_zoom=18,
            radius=25,
            blur=20,
            gradient={0.0: 'blue', 0.5: 'yellow', 0.75: 'orange', 1.0: 'red'},
            name="Rating Heatmap"
        ).add_to(m)
        
        # Add markers with rating info
        for _, row in place_agg.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=3,
                color="white",
                fill=True,
                fill_color="white",
                fill_opacity=0.6,
                popup=f"<b>{row['place_name']}</b><br>Avg Rating: {row['rating']:.2f}"
            ).add_to(m)

elif map_view == "Review Density Heatmap":
    # All reviews as points (density based on review count)
    heat_data = [[row["lat"], row["lon"]] for _, row in filtered.iterrows()]
    
    if heat_data:
        plugins.HeatMap(
            heat_data,
            min_opacity=0.2,
            max_zoom=18,
            radius=20,
            blur=15,
            gradient={0.0: 'lightblue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'},
            name="Review Density"
        ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

st_folium(m, width=1200, height=550)
