# from utils import load_data
from entity_extractor import extract_entities
from intent_classifier import classify_intent
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
        "DIRECTOR": ["directed", "director", "film by"],
        "ACTOR": ["starring", "starred", "acted", "featuring", "featuring actors", "with"],
        "WRITER": ["written", "writer", "screenplay", "screenwriter"],
        "PRODUCER": ["produced", "producer"],
        "COMPOSER": ["scored", "composed", "composer", "music by"],
        "CINEMATOGRAPHER": ["shot by", "cinematography", "cinematographer"],
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

    # Add new role-specific people to the entities dict
    for role, names in role_to_people.items():
        if role in entities:
            entities[role].extend(names)
        else:
            entities[role] = names

    # Remove them from PERSON so we don’t double-count
    entities["PERSON"] = [
        p for p in entities["PERSON"]
        if all(p not in role_to_people[r] for r in role_to_people)
    ]

    return entities

# ----------------------------------------------------------------- #
# ------------------ MAIN QUERY BUILDER FUNCTION ------------------ #
# ----------------------------------------------------------------- #

def build_query(entities, intent):
    # df = load_data.load_movies_()

    # Apply filters per entities

    # Apply sorting

    # Limit results
    pass

# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    text = "Show me all Paramount French horror films starring by Brad Pitt and directed Matt Reeves"
    entities = extract_entities(text)
    entities = assign_roles_to_people(entities,text)
    for label, items in entities.items():
        print(f"{label}: {items}")