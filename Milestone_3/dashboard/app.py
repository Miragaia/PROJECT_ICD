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
from pathlib import Path

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

# ---------- Topic Analysis (Precomputed) ----------
st.markdown("### Topic Analysis (Precomputed)")

OUTPUT_DIR = BASE_DIR / "output"

def available_topic_counts(lang_code: str) -> list:
    counts = []
    for p in OUTPUT_DIR.glob(f"topics_{lang_code}_*.json"):
        try:
            n = int(p.stem.split("_")[-1])
            counts.append(n)
        except Exception:
            pass
    return sorted(set(counts))

def load_topics(lang_code: str, n_topics: int) -> pd.DataFrame:
    path = OUTPUT_DIR / f"topics_{lang_code}_{n_topics}.json"
    if not path.exists():
        return pd.DataFrame()
    try:
        dfj = pd.read_json(path)
        return dfj
    except Exception:
        return pd.DataFrame()

def load_assignments(lang_code: str, n_topics: int) -> pd.DataFrame:
    path = OUTPUT_DIR / f"dom_{lang_code}_{n_topics}.csv"
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

col_t1, col_t2, col_t3 = st.columns(3)
language_t = col_t1.selectbox("Language", ["English", "Portuguese"])
lang_code_t = "en" if language_t == "English" else "pt"
avail = available_topic_counts(lang_code_t)
if not avail:
    st.info("No precomputed topics found. Run the precompute script to generate files.")
else:
    num_topics_t = col_t2.selectbox("Topics (precomputed)", avail)
    top_k_reviews_t = col_t3.slider("Top reviews", 1, 20, 8, 1)

    df_topics_t = load_topics(lang_code_t, num_topics_t)
    dom_df_t = load_assignments(lang_code_t, num_topics_t)

    if df_topics_t.empty or dom_df_t.empty:
        st.info("Missing topics or assignments for the selected configuration.")
    else:
        # Topic distribution
        t_counts = dom_df_t["topic_id"].value_counts().sort_index()
        fig_t = px.bar(
            x=t_counts.index,
            y=t_counts.values,
            labels={"x": "Topic ID", "y": "# Reviews"},
            title=f"Topic Distribution ({language_t})",
        )
        st.plotly_chart(fig_t, use_container_width=True)

        # Topic details & review drill-down
        st.markdown("**Topic details & reviews**")
        topic_options = sorted(df_topics_t["topic_id"].tolist()) if "topic_id" in df_topics_t.columns else []
        if topic_options:
            selected_tid = st.selectbox("Select topic", topic_options)
            tw_row = df_topics_t[df_topics_t["topic_id"].eq(selected_tid)].iloc[0]
            st.markdown(f"**Top words (Topic {selected_tid}):**")
            if "top_words" in df_topics_t.columns:
                st.write(tw_row["top_words"])  # comma-separated string
            else:
                st.write(", ".join(tw_row.get("words", [])))

            st.markdown("**Representative reviews:**")
            reps = dom_df_t[dom_df_t["topic_id"].eq(selected_tid)].sort_values("topic_prob", ascending=False).head(top_k_reviews_t)
            if reps.empty:
                st.info("No reviews mapped to this topic.")
            else:
                cols = ["place_name", "rating", "review_text", "publish_time", "topic_prob"]
                safe_cols = [c for c in cols if c in dom_df_t.columns]
                st.dataframe(reps[safe_cols], use_container_width=True)
        else:
            st.info("No topics identified.")

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
