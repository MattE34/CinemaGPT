from pathlib import Path
import pandas as pd
import ast

# Robustly locate the project root so relative imports work no matter where you run from
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

_MOVIE_JSON_LIST_COLS = ["genres", "keywords", "production_companies", "spoken_languages"]
_CREDIT_JSON_LIST_COLS = ["cast", "crew"]

def _safe_parse(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or x == "":
        return []
    try:
        return ast.literal_eval(x)
    except Exception:
        return []

def _ensure_list(v):
    return v if isinstance(v, list) else []

def load_movies_():
    """
    Returns a single DataFrame with movies merged to credits and all JSON-like list columns parsed.
    Columns guaranteed:
      - id (int), title (str), rating (float), vote_count (float), popularity (float), revenue (float)
      - genres (list[dict]), keywords (list[dict]), production_companies (list[dict]), spoken_languages (list[dict])
      - cast (list[dict]), crew (list[dict])
    """
    movies = pd.read_csv(DATA_DIR / "tmdb_5000_movies.csv")
    credits = pd.read_csv(DATA_DIR / "tmdb_5000_credits.csv")

    # Parse JSON-like columns on each table BEFORE merging to avoid edge-cases
    for col in _MOVIE_JSON_LIST_COLS:
        movies[col] = movies[col].apply(_safe_parse)

    for col in _CREDIT_JSON_LIST_COLS:
        credits[col] = credits[col].apply(_safe_parse)

    # Merge (left join keeps all movies)
    df = movies.merge(credits, left_on="id", right_on="movie_id", how="left")

    # Canonicalize columns
    df["title"] = df["title_x"].fillna(df.get("title_y"))
    for col in ["title_x", "title_y", "movie_id"]:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Add normalized numeric columns used for sorting
    df["rating"] = pd.to_numeric(df.get("vote_average"), errors="coerce")
    df["vote_count"] = pd.to_numeric(df.get("vote_count"), errors="coerce")
    df["popularity"] = pd.to_numeric(df.get("popularity"), errors="coerce")
    df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce")

    # Make sure list columns are always lists (no NaNs)
    for col in _MOVIE_JSON_LIST_COLS + _CREDIT_JSON_LIST_COLS:
        df[col] = df[col].apply(_ensure_list)

    return df