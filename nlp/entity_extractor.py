import spacy
from spacy.pipeline import EntityRuler
from collections import defaultdict
import re
import pandas as pd
import json
# import preprocess # for testing purposes

# Load SpaCy English model and EntityExtractor
nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("entity_ruler", before="ner")
# ruler = EntityRuler(nlp, overwrite_ents=True)

# Load datasets
movies = pd.read_csv("../data/tmdb_5000_movies.csv")
credits = pd.read_csv("../data/tmdb_5000_credits.csv")

# List of genres retrieved in the exploratory data analysis
    # added multiple versions of certain genres
GENRES = [
    "action", "adventure", "animation", "animated", "comedy", "crime", "documentary", "drama", "dramatic", "family",
    "fantasy", "foreign", "history", "historical", "horror", "music", "mystery", "romance", "science fiction",
    "science-fiction", "sci fi", "sci-fi", "tv movie", "thriller", "war", "western",
]

# --------------------------
# Utility: Clean & Prepare
# --------------------------
def clean_title(title):
    return title.lower().strip()

# Extract all unique movie titles
movie_titles = set(clean_title(title) for title in movies['title'].unique())

# Extract all known persons and their roles
crew_members = json.loads(credits.to_json(orient='records'))
cast_members = json.loads(credits.to_json(orient='records'))
people_set = set()
directors, actors, writers, producers, composers, cinematographers = set(), set(), set(), set(), set(), set()

for row in crew_members:
    try:
        crew = json.loads(row['crew']) if isinstance(row['crew'], str) else row['crew']
        for member in crew:
            name = member['name'].lower()
            job = member['job'].lower()
            people_set.add(name)
            if job == "director":
                directors.add(name)
            elif job in ["writer", "screenplay"]:
                writers.add(name)
            elif job == "producer":
                producers.add(name)
            elif job in ["original music composer", "composer"]:
                composers.add(name)
            elif job in ["director of photography", "cinematographer"]:
                cinematographers.add(name)
    except Exception:
        continue

for row in cast_members:
    try:
        cast = json.loads(row['cast']) if isinstance(row['cast'], str) else row['cast']
        for actor in cast:
            name = actor['name'].lower()
            people_set.add(name)
            actors.add(name)
    except Exception:
        continue

# --------------------------
# Build EntityRuler Patterns
# --------------------------
patterns = []

# Movie titles
for title in movie_titles:
    patterns.append({"label": "MOVIE", "pattern": title})

# People (generic)
for name in people_set:
    patterns.append({"label": "PERSON", "pattern": name})

# Roles
ROLE_SYNONYMS = {
"DIRECTOR": ["director", "directed"],
"WRITER": ["writer", "written", "screenwriter"],
"PRODUCER": ["producer", "produced"],
"COMPOSER": ["composer", "composed", "scored", "score"],
"CINEMATOGRAPHER": ["cinematographer", "shot", "shot by"],
"ACTOR": ["actor", "acted", "cast", "starring", "featuring", "featuring actor", "with"]
}

for role, terms in ROLE_SYNONYMS.items():
    for term in terms:
        patterns.append({"label": role, "pattern": term})


# Genres
for genre in GENRES:
    patterns.append({"label": "GENRE", "pattern": genre})


# Add to pipeline
ruler.add_patterns(patterns)

# Extract different entities (person, genre, title, year, etc.) from the tokens
def extract_entities(text):
    # text = " ".join(tokens)
    # print(f"CLEANED TEXT:\n{text}")

    # doc = nlp(text)
    # entites = defaultdict(list)

    # # temporary
    # return doc.ents

    doc = nlp(text.lower())
    extracted = defaultdict(list)
    for ent in doc.ents:
        extracted[ent.label_].append(ent.text)
    return extracted

    #---------- TESTING ----------#

if __name__ == "__main__":
    print("\n\n|---------- TESING ----------|\n\n")
    # raw_text = "Show me the best science-fiction movies with Brad Pitt from 1999 or 2000 or Avatar or Star War or After Hours"
    # entities = extract_entities(raw_text)
    # for ent in entities:
    #     print(f"Entity: {ent.text}, Type: {ent.label_}")
    
    text = "Show me the best science-fiction movies with Brad Pitt from 1999 or 2000 or Avatar or Star Wars, directed by Christopher Nolan and shot by Wally Pfister and scored by Hans Zimmer"
    entities = extract_entities(text)
    for label, items in entities.items():
        print(f"{label}: {set(items)}")