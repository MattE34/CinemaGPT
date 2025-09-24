# from utils import load_data
from entity_extractor import extract_entities
from intent_classifier import classify_intent
from preprocess import clean_text
import pandas as pd
import json
import re
from collections import defaultdict

# -------------------------------------------------------- #
# ------------------ HELPER FUNCTION(S) ------------------ #
# -------------------------------------------------------- #

def assign_roles_to_people(entities, raw_text):
    # Assigns roles to PERSON entities using the context of nearby role keywords in the raw text
    # For example, if 'Brad Pitt' is near the word 'starring', he will be classified as an ACTOR
    
    # Updates the entities dict in-place to move PERSON entries into their appropriate roles

    if "PERSON" not in entities:
        return entities

    # Define role keywords to look for in proximity
    role_keywords = {
        "DIRECTOR": ["directed", "director", "film by", "films by", "direct"],
        "ACTOR": ["starring", "starred", "star", "acted", "actor", "act", "actress", "cast", "casted", "featuring", "featuring actor", "feature", "with"],
        "WRITER": ["written", "writer", "write", "screenplay", "screenwriter"],
        "PRODUCER": ["produced", "producer", "produce"],
        "COMPOSER": ["scored", "score", "composed", "composer", "compose", "music by"],
        "CINEMATOGRAPHER": ["shot by", "shot", "shoot", "cinematography", "cinematographer"],
    }

    # Normalize text
    text = raw_text.lower()

    # Build a mapping of person name to its location (index) in the string
    person_indices = {}
    for person in entities["PERSON"]:
        idx = text.find(person.lower())
        if idx != -1:
            person_indices[person] = idx

    # Assign people to the closest matching role based on keyword proximity
    role_to_people = defaultdict(list)

    for person, p_idx in person_indices.items():
        closest_role = None
        closest_distance = float("inf")

        for role, keywords in role_keywords.items():
            for kw in keywords:
                k_idx = text.find(kw)
                if k_idx != -1:
                    distance = abs(p_idx - k_idx)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_role = role

        # Assign the person to the closest detected role
        if closest_role:
            role_to_people[closest_role].append(person)

    # Add new role-specific people to the entities dict and remove associated role keywords

    for role, names in role_to_people.items():
        # Remove keyword-only entries if people were assigned
        entities[role] = [
            entry for entry in entities.get(role, []) if entry not in role_keywords[role]
        ] + names

    # for role, names in role_to_people.items():
    #     if role in entities:
    #         entities[role].extend(names)
    #     else:
    #         entities[role] = names

    # Remove them from PERSON so we don’t double-count
    entities["PERSON"] = [
        p for p in entities["PERSON"]
        if all(p not in role_to_people[r] for r in role_to_people)
    ]

    # If all persons were assigned roles, remove empty PERSON key
    if not entities["PERSON"]:
        del entities["PERSON"]

    return entities

# ----------------------------------------------------------------- #
# ------------------ MAIN QUERY BUILDER FUNCTION ------------------ #
# ----------------------------------------------------------------- #

def build_query(intent, entities, tokens):
    # df = load_data.load_movies_()

    # Apply filters per entities
    # Apply sorting
    # Limit results
    
    query = {
        "filters": {},
        "sort_by": None,
        "limit": None,
        "return": "movie",  # default return type
        "type": intent["type"]
    }

    # 1. Apply filters from extracted entities
    for key, value in entities.items():
        key_lower = key.lower()

        if key_lower in {"genre", "language", "date", "production_company"}:
            query["filters"][key_lower] = value

        elif key_lower == "director":
            query["filters"]["director"] = value
        elif key_lower == "producer":
            query["filters"]["producer"] = value
        elif key_lower == "actor":
            query["filters"]["actor"] = value
        elif key_lower == "writer":
            query["filters"]["writer"] = value
        elif key_lower == "composer":
            query["filters"]["composer"] = value
        elif key_lower == "cinematographer":
            query["filters"]["cinematographer"] = value
        elif key_lower == "movie":
            query["filters"]["title"] = value

    # 2. Intent-based query handling
    if intent["type"] == "top_n":
        query["sort_by"] = intent.get("metric", "rating")
        query["limit"] = intent.get("n", 5)

    elif intent["type"] == "list":
        query["limit"] = intent.get("n", -1)  # no limit if not provided

    elif intent["type"] == "quantity":
        query["return"] = intent.get("metric", "rating")

    elif intent["type"] == "question":
        # Possible return values: "director", "actor", "composer", etc.
        if "movie" in entities or "who" in tokens:
            for role in ["director", "writer", "actor", "composer", "cinematographer"]:
                if role.upper() in entities:
                    query["return"] = role
                    break
            else:
                query["return"] = "person"
        elif "date" in entities or "when" in tokens:
            query["return"] = "date"
        else:
            query["return"] = "unknown"

    elif intent["type"] == "unknown":
        query["return"] = "unknown"

    return query

# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    print("\n|---------- TESING ----------|\n")
    # text = "Show me all Paramount French horror films starring by Brad Pitt and directed Mattt Reeves"
    # text = "What romance movies did Christopher Nolan produce and Tom Cruise star in?"
    # text = "What is the average rating for Interstellar?"
    # text = "How long is The Dark Knight?"
    text = "Show me top 10 movies starring Tom Cruise or Robert Pattinson?"
    tokens = clean_text(text)
    intent = classify_intent(tokens)
    print(f"Text: {text}")
    print(f"Tokens: {tokens}")
    print(f"Intent: {dict(intent)}\n")
    entities = extract_entities(text)
    entities = assign_roles_to_people(entities,text)
    print("Entities:")
    for label, items in entities.items():
        print(f"{label}: {items}")
    query = build_query(intent,entities,tokens)
    print(f"\nQuery: {query}")