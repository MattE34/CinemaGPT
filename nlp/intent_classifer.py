import re
from collections import defaultdict
from preprocess import clean_text

# ---------------------------------------------------------------------- #
# ------------------ MAPPING KEYWORDS TO INTENT TYPES ------------------ #
# ---------------------------------------------------------------------- #

# ----- Rankings ----- #
RANK_KEYWORDS = {"top", "best", "most", "greatest", "highest"}

# ----- Metrics ----- #
METRIC_KEYWORDS = {
    "rating": ["rated", "rating", "score"],
    "popularity": ["popular", "popularity", "famous"],
    "revenue": ["grossing", "revenue", "earned", "box office"],
    "vote_count": ["voted", "votes"]
}

# ----- Numbers ----- #
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

# ------------------------------------------------------- #
# ------------------ UTILITY FUNCTIONS ------------------ #
# ------------------------------------------------------- #

# Extract numeric value (top 5, top 10) and default to 5 if not listed
def extract_top_n(tokens):
    pass

# Detect metric to sort by (rating, popularity, earnings)
def detect_metric(tokens):
    pass

# ------------------------------------------------------------------ #
# ------------------ MAIN CLASSIFICATION FUNCTION ------------------ #
# ------------------------------------------------------------------ #

# From list of prepreocessed tokens, determine intent and key query structure
def classify_intent(tokens):
    pass

# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    print("\n|---------- TESING ----------|\n")
    queries = [
        "top rated japanese films",
        "top 5 films starring Brad Pitt",
        "most popular WB films",
        "films directed by Matt Reeves and shot by Greg Fraiser",
        "sci-fi films composed by hans zimmer",
        "highest grossing action films in 2010"
    ]

    for query in queries:
        tokens = clean_text(query)
        intent = classify_intent(tokens)
        print(f"\nQuery: {query}")
        print(f"Tokens: {tokens}")
        print(f"Intent: {dict(intent)}")