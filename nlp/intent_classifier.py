import re
from collections import defaultdict
from preprocess import clean_text

# ---------------------------------------------------------------------- #
# ------------------ MAPPING KEYWORDS TO INTENT TYPES ------------------ #
# ---------------------------------------------------------------------- #

# ----- Rankings ----- #
RANK_KEYWORDS = {"top", "best", "most", "greatest", "great", "highest", "high", "popular", "expensive", "pay", "vote"}

# ----- Metrics ----- #
METRIC_KEYWORDS = {
    "rating": ["rated", "rating", "score", "rate"],
    "popularity": ["popular", "popularity", "famous"],
    "revenue": ["grossing", "gross", "revenue", "earned", "earning", "earn", "box office", "paying", "paid", "pay"],
    "budget": ["expensive", "expense", "cost", "costing"],
    "vote_count": ["voted", "votes", "vote"]
}

# ----- Numbers ----- #
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15
}

# ----- Questions ----- #
QUESTION_KEYWORDS = {"who", "when"}

# ----- Quantities ----- #
QUANTITY_KEYWORDS = {"how", "many", "count", "number", "frequency"}

# ----- Lists ----- #
LIST_KEYWORDS = {
    "what", "list", "show", "all", "give", "fetch", "display", "identify",
    "film", "movie", "direct", "actor", "actress", "produce", "write", "compose", "score"
}

# ------------------------------------------------------- #
# ------------------ UTILITY FUNCTIONS ------------------ #
# ------------------------------------------------------- #

# Extract numeric value (top 5, top 10) and default to 5 if not listed
def extract_top_n(tokens):
    for i, token in enumerate(tokens):
        # number listed before "top" or "top" not listed
        if token.isdigit():
            if int(token) < 1000:
                return int(token)
        elif token in NUMBER_WORDS:
            return NUMBER_WORDS[token]
        # number listed after "top"
        elif token == "top" and i + 1 < len(tokens):
            next_token = tokens[i + 1]
            if next_token.isdigit():
                return int(next_token)
            elif next_token in NUMBER_WORDS:
                return NUMBER_WORDS[next_token]
    return 5  # default

# Extract numeric value (5, 10) and default to -1 (no limit) if not listed
def extract_n(tokens):
    for i, token in enumerate(tokens):
        if token.isdigit():
            if int(token) < 1000:
                return int(token)
        elif token in NUMBER_WORDS:
            return NUMBER_WORDS[token]
    return -1  # default

# Detect metric to sort by (rating, popularity, earnings)
def detect_metric(tokens):
    for metric, keywords in METRIC_KEYWORDS.items():
        if any(token in keywords for token in tokens):
            return metric
    return "rating"  # default

# ------------------------------------------------------------------ #
# ------------------ MAIN CLASSIFICATION FUNCTION ------------------ #
# ------------------------------------------------------------------ #

# From list of prepreocessed tokens, determine intent and key query structure
def classify_intent(tokens):
    intent = defaultdict()

    # 1. Ranking-based query
    if any(token in RANK_KEYWORDS for token in tokens):
        intent["type"] = "top_n"
        intent["n"] = extract_top_n(tokens)
        intent["metric"] = detect_metric(tokens)
    
    # 2. Question query
    elif any(token in QUESTION_KEYWORDS for token in tokens):
        intent["type"] = "question"
    
    # 3. Quantity query
    elif any(token in QUANTITY_KEYWORDS for token in tokens):
        intent["type"] = "quantity"

    # 4. List query
    elif any(token in LIST_KEYWORDS for token in tokens):
        intent["type"] = "list"
        intent["n"] = extract_n(tokens)
        
    # Unrecognizable query
    else:
        print("Don't recognize request")

    return intent

# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    print("\n|---------- TESING ----------|")
    queries = [
        "top rated japanese films",
        "8 top grossing films starring Brad Pitt",
        "most popular WB films",
        "twelve films directed by Matt Reeves and shot by Greg Fraiser",
        "list 3 sci-fi films composed by hans zimmer",
        "highest paid actors in 2010",
        "list the 5 most expensive movies",
        "show me christopher nolan films",
        "list the most voted movies",
        "who directed The Dark Knight?",
        "How many movies did Wes Anderson direct?",
        "21 action movies"
        # testing which words are ignored from preprocessing
        # "list display fetch give show me all identify tell me who what when how many number of count"
    ]

    for query in queries:
        tokens = clean_text(query)
        intent = classify_intent(tokens)
        print(f"\nQuery: {query}")
        print(f"Tokens: {tokens}")
        print(f"Intent: {dict(intent)}")