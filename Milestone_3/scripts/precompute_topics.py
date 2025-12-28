import os
import json
import argparse
from pathlib import Path

import pandas as pd
from gensim import corpora
from gensim.models import LdaMulticore

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"
ENRICHED_CSV = OUTPUT_DIR / "reviews_enriched.csv"

def prepare_texts(df_lang: pd.DataFrame) -> list:
    texts = [str(x).split() for x in df_lang["text_processed"].fillna("").tolist()]
    return [[t for t in doc if t] for doc in texts]

def train_lda(texts, num_topics, passes, min_word_freq):
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=min_word_freq, no_above=0.7, keep_n=1000)
    corpus = [dictionary.doc2bow(text) for text in texts]
    if not corpus:
        return None, None
    lda = LdaMulticore(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        passes=passes,
        workers=1,
        per_word_topics=True,
        minimum_probability=0.0,
    )
    return lda, dictionary

def topics_to_df(lda_model, n_words=10) -> pd.DataFrame:
    rows = []
    for tid, tw in lda_model.print_topics(num_words=n_words):
        parts = [p.split("*") for p in tw.split(" + ")]
        words = [w.strip('"') for _, w in parts]
        rows.append({"topic_id": tid, "top_words": ", ".join(words)})
    return pd.DataFrame(rows)

def dominant_topics_df(texts, lda_model, dictionary) -> pd.DataFrame:
    dom = []
    for i, text in enumerate(texts):
        bow = dictionary.doc2bow(text)
        if not bow:
            dom.append({"row_idx": i, "topic_id": None, "topic_prob": 0.0})
            continue
        topics = lda_model.get_document_topics(bow)
        if topics:
            tmax = max(topics, key=lambda x: x[1])
            dom.append({"row_idx": i, "topic_id": tmax[0], "topic_prob": float(tmax[1])})
        else:
            dom.append({"row_idx": i, "topic_id": None, "topic_prob": 0.0})
    return pd.DataFrame(dom)

def main():
    parser = argparse.ArgumentParser(description="Precompute LDA topics for reviews dashboard")
    parser.add_argument("--topics", nargs="+", type=int, default=[3, 5, 7, 10],
                        help="Number of topics to train (can specify multiple, e.g., --topics 3 5 7)")
    parser.add_argument("--passes", type=int, default=10,
                        help="Number of LDA passes (default: 10)")
    parser.add_argument("--min-word-freq", type=int, default=2,
                        help="Minimum word frequency to include in dictionary (default: 2)")
    parser.add_argument("--languages", nargs="+", choices=["en", "pt"], default=["en", "pt"],
                        help="Languages to process (default: en pt)")
    args = parser.parse_args()

    if not ENRICHED_CSV.exists():
        print(f"Missing enriched CSV: {ENRICHED_CSV}")
        return
    df = pd.read_csv(ENRICHED_CSV, low_memory=False)

    lang_map = {"en": "English", "pt": "Portuguese"}
    
    for lang_code in args.languages:
        lang_name = lang_map[lang_code]
        df_lang = df[df["lang"].eq(lang_code)].copy()
        if df_lang.empty or len(df_lang) < 5:
            print(f"Skipping {lang_name}: insufficient reviews ({len(df_lang)})")
            continue

        texts = prepare_texts(df_lang)
        if len(texts) < 5 or all(len(t) == 0 for t in texts):
            print(f"Skipping {lang_name}: insufficient tokens")
            continue

        for num_topics in args.topics:
            print(f"\nTraining LDA for {lang_name} ({num_topics} topics, {args.passes} passes, {len(texts)} reviews)...")
            lda, dictionary = train_lda(texts, num_topics, args.passes, args.min_word_freq)
            if lda is None:
                print(f"Failed to train LDA for {lang_name} with {num_topics} topics")
                continue

            # Save topics JSON
            topics_df = topics_to_df(lda, 10)
            topics_path = OUTPUT_DIR / f"topics_{lang_code}_{num_topics}.json"
            topics_df.to_json(topics_path, orient="records")
            print(f"✓ Saved topics -> {topics_path}")

            # Save dominant topics CSV with review context
            dom_df = dominant_topics_df(texts, lda, dictionary)
            # attach review context columns for easy display
            keep_cols = [
                "place_name", "rating", "review_text", "publish_time",
            ]
            for c in keep_cols:
                if c in df_lang.columns:
                    dom_df[c] = df_lang[c].values
            dom_path = OUTPUT_DIR / f"dom_{lang_code}_{num_topics}.csv"
            dom_df.to_csv(dom_path, index=False)
            print(f"✓ Saved assignments -> {dom_path}")
    
    print("\n" + "="*60)
    print("Precomputation complete!")
    print("="*60)

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()
