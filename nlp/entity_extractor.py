import spacy
from collections import defaultdict
import re  # for pattern-based entity extraction (e.g., years)

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# List of genres retrieved in the exploratory data analysis
GENRES = [
    "action", "adventure", "animation", "comedy", "crime", "documentary", "drama", "family", "fantasy", "foreign",
    "history", "horror", "music", "mystery", "romance", "science fiction", "tv movie", "thriller", "war", "western"
]

# Extract different entities (person, genre, title, year, etc.) from the text/tokens
def extract_entities(text):
    pass