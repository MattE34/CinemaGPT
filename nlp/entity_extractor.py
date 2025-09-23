import os
import time
import spacy
from spacy.pipeline import EntityRuler
from spacy.matcher import PhraseMatcher
from collections import defaultdict
import re
import pandas as pd
import json
# import preprocess # for testing purposes

# ---------------------------------------------------- #
# ------------------ LOADING ASSETS ------------------ #
# ---------------------------------------------------- #

# # Load SpaCy English model and EntityExtractor
# nlp = spacy.load("en_core_web_sm")
# ruler = nlp.add_pipe("entity_ruler", before="ner")

# # Load prebuilt pipeline (saved locally)
# nlp = spacy.load("nlp_with_entities")

# ----- Global cache for nlp ----- #
_nlp = None
  
def get_nlp():
    # global _nlp
    # if _nlp is None:
    #     print("Loading NLP pipeline with entities...")
    #     _nlp = spacy.load("nlp_with_entities")  # takes ~90s the first time
    #     print("NLP pipeline loaded.")
    # return _nlp
    global _nlp
    if _nlp is None:
        start = time.time()
        print("Loading minimal NLP pipeline with EntityRuler only...")
        _nlp = spacy.blank("en")
        ruler = _nlp.add_pipe("entity_ruler")
        with open("entity_patterns.jsonl", "r", encoding="utf8") as f:
            loaded_patterns = [json.loads(line.strip()) for line in f]
        ruler.add_patterns(loaded_patterns)
        print("NLP pipelined loaded in", round(time.time() - start, 2), "seconds\n")
    return _nlp

# # ----- Load datasets ----- #
# movies = pd.read_csv("../data/tmdb_5000_movies.csv")
# credits = pd.read_csv("../data/tmdb_5000_credits.csv")

# --------------------------------------------------------- #
# ------------------ EXTRACTING ENTITIES ------------------ #
# --------------------------------------------------------- #

# ----- List of language codes to full names (e.g., 'en' → 'english') ----- #
LANGUAGE_MAP = {
    'en': 'english',
    'fr': 'french',
    'de': 'german',
    'es': 'spanish',
    'ja': 'japanese',
    'zh': 'chinese',
    'ko': 'korean',
    'hi': 'hindi',
    'ru': 'russian',
    'it': 'italian',
    'pt': 'portuguese',
    'ar': 'arabic',
    'tr': 'turkish',
    'nl': 'dutch',
    # add more if needed
}
# languages = set(LANGUAGE_MAP.values())

# ----- List of genres retrieved in the exploratory data analysis ----- #
# added multiple versions of certain genres
GENRES = [
    "action", "adventure", "animation", "animated", "comedy", "comedies", "crime", "documentary", "documentaries", "drama", "dramas",
    "dramatic", "family", "fantasy", "foreign", "history", "historical", "horror", "music", "mystery", "romance", "romantic",
    "science fiction", "science-fiction", "sci fi", "sci-fi", "tv movie", "thriller", "war", "western", "westerns"
]

# # ----- Utility: Clean & Prepare ----- #
# def clean_title(title):
#     return title.lower().strip()

# # ----- Extract all unique movie titles ----- #
# movie_titles = set(clean_title(title) for title in movies['title'].unique())
# STOP_MOVIE_TOKENS = {"show me", "list", "find", "give me", "i want", "tell me"}

# # ----- Extract production companies ----- #
# production_companies = set()
# for row in movies['production_companies']:
#     try:
#         companies = json.loads(row.replace("'", "\""))  # some rows may use single quotes
#         for company in companies:
#             name = company['name'].lower().strip()
#             production_companies.add(name)
#     except Exception:
#         continue
# # add additional synonyms
# production_companies.update({"fox", "wb", "warner bros"})

# # ----- Extract all known persons and their roles ----- #
# crew_members = json.loads(credits.to_json(orient='records'))
# cast_members = json.loads(credits.to_json(orient='records'))
# people_set = set()
# directors, actors, writers, producers, composers, cinematographers = set(), set(), set(), set(), set(), set()

# # ----- Crew members ----- #
# for row in crew_members:
#     try:
#         crew = json.loads(row['crew']) if isinstance(row['crew'], str) else row['crew']
#         for member in crew:
#             name = member['name'].lower()
#             job = member['job'].lower()
#             people_set.add(name)
#             if job == "director":
#                 directors.add(name)
#             elif job in ["writer", "screenplay"]:
#                 writers.add(name)
#             elif job == "producer":
#                 producers.add(name)
#             elif job in ["original music composer", "composer"]:
#                 composers.add(name)
#             elif job in ["director of photography", "cinematographer"]:
#                 cinematographers.add(name)
#     except Exception:
#         continue

# # ----- Cast members ----- #
# for row in cast_members:
#     try:
#         cast = json.loads(row['cast']) if isinstance(row['cast'], str) else row['cast']
#         for actor in cast:
#             name = actor['name'].lower()
#             people_set.add(name)
#             actors.add(name)
#     except Exception:
#         continue
    
# ------------------------------------------------------------------- #
# ------------------ BUILDING ENTITYRULER PATTERNS ------------------ #
# ------------------------------------------------------------------- #

patterns = []

# # ----- Languages ----- #
# for lang in languages:
#     patterns.append({"label": "LANGUAGE", "pattern": lang})

# # ----- Movie titles ----- #
# for title in movie_titles:
#     if title in STOP_MOVIE_TOKENS:
#         continue
#     patterns.append({"label": "MOVIE", "pattern": title})

# # ----- Production companies ----- #
# for company in production_companies:
#     patterns.append({"label": "PRODUCTION_COMPANY", "pattern": company})

# # ----- People (generic) ----- #
# for name in people_set:
#     patterns.append({"label": "PERSON", "pattern": name})

# ----- Roles ----- #
ROLE_SYNONYMS = {
"DIRECTOR": ["director", "directed"],
"WRITER": ["writer", "written", "screenwriter"],
"PRODUCER": ["producer", "produced"],
"COMPOSER": ["composer", "composed", "scored", "score"],
"CINEMATOGRAPHER": ["cinematographer", "shot", "shot by"],
"ACTOR": ["actor", "actress", "acted", "cast", "starring", "starred", "featuring", "featuring actor", "with"]
}

# for role, terms in ROLE_SYNONYMS.items():
#     for term in terms:
#         patterns.append({"label": role, "pattern": term})

# # ----- Genres ----- #
# for genre in GENRES:
#     patterns.append({"label": "GENRE", "pattern": genre})

# # ----- Save patterns to disk for reuse (ONLY DO ONCE) ----- #
# with open("entity_patterns.jsonl", "w", encoding="utf8") as f:
#     for pattern in patterns:
#         f.write(json.dumps(pattern) + "\n")

# ----- Add to pipeline ----- #

# # Reading and adding patterns from local json file
# with open("entity_patterns.jsonl", "r", encoding="utf8") as f:
#     loaded_patterns = [json.loads(line.strip()) for line in f]

# ruler.add_patterns(loaded_patterns)
# # ruler.add_patterns(patterns)

# # ----- Save the full pipeline locally (serialize) ----- #
# nlp.to_disk("nlp_with_entities")

# --------------------------------------------------------------- #
# ------------------ EXTRACT ENTITIES FUNCTION ------------------ #
# --------------------------------------------------------------- #

# Extract different entities (person, genre, title, year, etc.) from the tokens
def extract_entities(text):

    nlp = get_nlp()
    doc = nlp(text.lower())
    extracted = defaultdict(list)
    for ent in doc.ents:
        extracted[ent.label_].append(ent.text)
    return extracted

# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    print("\n|---------- TESING ----------|\n")
    # text = "Show me the best science-fiction movies with Brad Pitt from 1999 or 2000 or Avatar or Star Wars, directed by Christopher Nolan and shot by Wally Pfister and scored by Hans Zimmer"
    text = "Show me all French horror films produced by WB or Paramount Pictures or Fox starring Brad Pitt"
    entities = extract_entities(text)
    for label, items in entities.items():
        print(f"{label}: {set(items)}")