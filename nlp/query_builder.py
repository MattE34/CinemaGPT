from utils.load_data import load_movies_
from nlp.entity_extractor import extract_entities
from nlp.intent_classifier import classify_intent
from nlp.preprocess import clean_text
import pandas as pd
import json
import re
from collections import defaultdict
import time

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

    # --- NEW: cleanup any role entries that contain ONLY keywords (no people) ---
    for role, keywords in role_keywords.items():
        # roles in entities are uppercase here; build_query lowercases keys later
        if role in entities:
            entities[role] = [
                v for v in entities[role]
                if v.lower() not in [kw.lower() for kw in keywords]
            ]
            if not entities[role]:
                del entities[role]

    return entities

# ----------------------------------------------------------------- #
# ------------------ MAIN QUERY BUILDER FUNCTION ------------------ #
# ----------------------------------------------------------------- #

def build_query(intent, entities, tokens):
    start = time.time()
    print("Building query...")
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

    # --- START: question-specific logic (robust who/when handling) ---
    if intent["type"] == "question":
        tokens_set = set(tokens)
        # print(tokens_set)

        # Detect which ROLE the question is asking about
        def any_in(words): return any(w in tokens_set for w in words)

        role_asked = None
        if any_in(["directed", "director", "direct"]):
            role_asked = "director"
        elif any_in(["starring", "starred", "star", "actor", "act", "cast", "with", "featuring", "feature", "acted"]):
            role_asked = "actor"
        elif any_in(["written", "writer", "write", "wrote", "screenplay", "screenwriter"]):
            role_asked = "writer"
        elif any_in(["produced", "producer", "produce"]):
            role_asked = "producer"
        elif any_in(["scored", "score", "composed", "composer", "compose", "music"]):
            role_asked = "composer"
        elif any_in(["cinematography", "cinematographer", "dop", "photography", "shot", "shoot"]):
            role_asked = "cinematographer"

        # print(role_asked)
        if "who" in tokens_set and role_asked:
            # print("WHO AND ROLE ASKED")
            # We’re asking for a person with this role; don’t filter by that role
            query["return"] = role_asked
            for r in ("director", "producer", "actor", "writer", "composer", "cinematographer"):
                if r in query["filters"]:
                    # log or print here if you want to debug
                    # print("REMOVING ROLE KEYWORDS")
                    query["filters"].pop(r)
                # query["filters"].pop(r, None)

        elif "when" in tokens_set:
            # We’re asking for a date; do not restrict by a date value
            query["return"] = "date"
            query["filters"].pop("date", None)

    elif intent["type"] == "top_n":
        query["sort_by"] = intent.get("metric", "rating")
        query["limit"] = intent.get("n", 5)

    elif intent["type"] == "list":
        query["limit"] = intent.get("n", -1)  # no limit if not provided

    elif intent["type"] == "quantity":
        query["return"] = intent.get("metric", "rating")

    # elif intent["type"] == "question":
    #     # Possible return values: "director", "actor", "composer", etc.
    #     if "movie" in entities or "who" in tokens:
    #         for role in ["director", "writer", "actor", "composer", "cinematographer"]:
    #             if role.upper() in entities:
    #                 query["return"] = role
    #                 break
    #         else:
    #             query["return"] = "person"
    #     elif "date" in entities or "when" in tokens:
    #         query["return"] = "date"
    #     else:
    #         query["return"] = "unknown"

    elif intent["type"] == "unknown":
        query["return"] = "unknown"

    print("Built query in", round(time.time() - start, 2), "seconds\n")
    return query

# ------------------------------------------------------------ #
# ------------------ EXECUTE QUERY FUNCTION ------------------ #
# ------------------------------------------------------------ #

def match_dict_list(column, key, values):
    return column.apply(lambda items: any(v.lower() in str(item.get(key, "")).lower() for item in items for v in values))

def execute_query(query):
    start = time.time()
    print("Executing query...")
    df = load_movies_()
    
    filters = query.get("filters", {})
    sort_by = query.get("sort_by")
    limit = query.get("limit", -1)
    return_type = query.get("return", "movie")
    intent_type = query.get("type", "list")

    # ===============================
    # Apply Filters
    # ===============================
    for key, values in filters.items():
        key = key.lower()
        values = [v.lower() for v in values]

        if key == "actor":
            df = df[match_dict_list(df["cast"], "name", values)]
        elif key == "director":
            df = df[df["crew"].apply(lambda crew: any(
                member.get("job", "").lower() == "director" and
                any(v in member.get("name", "").lower() for v in values)
                for member in crew
            ))]
        elif key == "producer":
            df = df[df["crew"].apply(lambda crew: any(
                member.get("job", "").lower() == "producer" and
                any(v in member.get("name", "").lower() for v in values)
                for member in crew
            ))]
        elif key == "composer":
            df = df[df["crew"].apply(lambda crew: any(
                "compos" in member.get("job", "").lower() and
                any(v in member.get("name", "").lower() for v in values)
                for member in crew
            ))]
        elif key == "cinematographer":
            df = df[df["crew"].apply(lambda crew: any(
                "cinematograph" in member.get("job", "").lower() or
                "director of photography" in member.get("job", "").lower()
                and any(v in member.get("name", "").lower() for v in values)
                for member in crew
            ))]
        elif key == "genre":
            df = df[match_dict_list(df["genres"], "name", values)]
        elif key == "production_company":
            df = df[match_dict_list(df["production_companies"], "name", values)]
        elif key == "language":
            df = df[match_dict_list(df["spoken_languages"], "name", values)]
        elif key == "title":
            df = df[df["title"].str.lower().isin(values)]
        else:
            continue  # Unrecognized filters

    # for key, values in filters.items():
    #     if key not in df.columns:
    #         continue
        
    #     # If column is a list (stored as string), match any of the provided values
    #     if df[key].dtype == object and df[key].str.startswith("[").any():
    #         df = df[df[key].apply(lambda x: any(val.lower() in str(x).lower() for val in values))]
    #     else:
    #         df = df[df[key].str.lower().isin([v.lower() for v in values])]

    # ===============================
    # Sorting Logic
    # ===============================
    if sort_by:
        ascending = False if sort_by in ["rating", "vote_count", "popularity", "revenue"] else True
        if sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=ascending)

    # ===============================
    # Limit Results
    # ===============================
    if isinstance(limit, int) and limit > 0:
        df = df.head(limit)

    # ===============================
    # Return Type Logic
    # ===============================
    print("Executed query in", round(time.time() - start, 2), "seconds\n")

    # --- NEW: question answering for who/when ---
    if intent_type == "question":
        if len(df) == 0:
            return "No matching movies found."

        if return_type in {"director", "writer", "producer", "composer", "cinematographer"}:
            role_map = {
                # use exact job titles found in TMDB 5000
                "director": {"director"},  # (do NOT include "art director" or "director of photography")
                "writer": {"writer", "screenplay", "story"},
                "producer": {"producer", "executive producer", "co-producer", "associate producer", "line producer"},
                "composer": {"original music composer", "composer"},  # keep it tight to avoid "music editor"
                "cinematographer": {"director of photography", "cinematographer"},
            }

            # jobs = set(j.lower() for j in role_map[return_type])

            # If a specific title was given, you’ll usually get 1 row – return the name directly
            def people_for_role(row, role):
                    jobs = role_map[role]
                    names = []
                    for m in row.get("crew", []) or []:
                        job = (m.get("job") or "").strip().lower()
                        if job in jobs:  # <-- exact match only
                            nm = m.get("name")
                            if nm:
                                names.append(nm)
                    # de-dupe preserving order
                    seen, out = set(), []
                    for n in names:
                        if n not in seen:
                            out.append(n)
                            seen.add(n)
                    return out
                
                # names = []
                # for m in row.get("crew", []) or []:
                #     job = (m.get("job") or "").lower()
                #     if any(k in job for k in jobs):
                #         nm = m.get("name")
                #         if nm:
                #             names.append(nm)
                # # de-dupe preserving order
                # seen = set()
                # out = []
                # for n in names:
                #     if n not in seen:
                #         out.append(n)
                #         seen.add(n)
                # return out


            if len(df) == 1:
                names = people_for_role(df.iloc[0], return_type)
                return ", ".join(names) if names else f"No {return_type} listed."

            return [
                {"title": row["title"], return_type: people_for_role(row, return_type)}
                for _, row in df.iterrows()
            ]
        
            # if len(df) == 1:
            #     names = people_for_role(df.iloc[0])
            #     return ", ".join(names) if names else f"No {return_type} listed."

            # # Multiple titles matched: return a compact mapping
            # return [
            #     {"title": row["title"], return_type: people_for_role(row)}
            #     for _, row in df.iterrows()
            # ]

        elif return_type == "actor":
            # For “who starred in …?” give top-billed cast
            def top_billed(row, k=3):
                cast = (row.get("cast") or [])
                cast_sorted = sorted(
                    [m for m in cast if isinstance(m, dict)],
                    key=lambda e: e.get("order", 999)
                )
                names = [m.get("name") for m in cast_sorted[:k] if m.get("name")]
                return names

            if len(df) == 1:
                names = top_billed(df.iloc[0])
                return ", ".join(names) if names else "No cast listed."
            return [
                {"title": row["title"], "actors": top_billed(row)}
                for _, row in df.iterrows()
            ]

        elif return_type == "date":
            # “When was <movie> released?”
            if len(df) == 1:
                rd = df.iloc[0].get("release_date")
                return str(rd) if pd.notnull(rd) else "Unknown release date."
            return [
                {"title": row["title"], "release_date": row.get("release_date")}
                for _, row in df.iterrows()
            ]

        # Fallback
        return "I parsed a question but couldn’t determine what to return."
    
    if return_type == "movie":
        return df["title"].tolist()
    
    elif return_type in ["rating", "runtime", "revenue", "budget"]:
        if len(df) == 0:
            return f"No movies matched the query."
        
        # Single movie case
        if len(df) == 1:
            row = df.iloc[0]
            return f"{row['title']} has a {return_type} of {row[return_type]}"
        
        # Multiple movies – return average or summary
        avg = round(df[return_type].astype(float).mean(), 2)
        return f"The average {return_type} for these movies is {avg}"

    elif intent_type == "question":
        return f"Here's what I found: {df['title'].tolist()}" if len(df) else "No matching movies found."

    elif intent_type == "unknown":
        return "Sorry, I couldn't understand your request. Please rephrase."

    else:
        return df["title"].tolist()


# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    print("\n|---------- TESING ----------|\n")
    # text = "Show me all Paramount French horror films starring by Brad Pitt and directed Mattt Reeves"
    # text = "What romance movies did Christopher Nolan produce and Tom Cruise star in?"
    # text = "What is the average rating for Interstellar?"
    # text = "How long is The Dark Knight?"
    # text = "Show me top 10 movies starring Tom Cruise or Robert Pattinson?"

    # queries = [
    #     "Show me all Paramount French horror films starring by Brad Pitt and directed Mattt Reeves",
    #     "What romance movies did Christopher Nolan produce and Tom Cruise star in?",
    #     "What is the average rating for Interstellar?",
    #     "How long is The Dark Knight?",
    #     "Show me top 10 movies starring Tom Cruise or Robert Pattinson?"
    # ]
    # for text in queries:
    #     tokens = clean_text(text)
    #     intent = classify_intent(tokens)
    #     entities = extract_entities(text)
    #     entities = assign_roles_to_people(entities,text)
    #     query = build_query(intent,entities,tokens)
    #     print(f"\nText: {text}")
    #     print(f"Query: {query}")

    # tokens = clean_text(text)
    # intent = classify_intent(tokens)
    # print(f"Text: {text}")
    # print(f"Tokens: {tokens}")
    # print(f"Intent: {dict(intent)}\n")
    # entities = extract_entities(text)
    # entities = assign_roles_to_people(entities,text)
    # print("Entities:")
    # for label, items in entities.items():
    #     print(f"{label}: {items}")
    # query = build_query(intent,entities,tokens)
    # print(f"\nQuery: {query}")

    # text = "Top 5 horror movies starring Tom Cruise"
    # text = "Top films starring Tom Cruise"
    # text = "Who directed The Dark Knight Rises"
    text = "Who shot The Dark Knight Rises"
    # text = "What is the average rating for The Dark Knight Rises"
    # text = "list movies directed by christopher nolan"
    # text = "when was the dark knight rises released?"
    tokens = clean_text(text)
    intent = classify_intent(tokens)
    entities = extract_entities(text)
    entities = assign_roles_to_people(entities,text)
    query = build_query(intent,entities,tokens)
    result = execute_query(query)
    print(f"\nText: {text}")
    print(f"Query: {query}")
    print(f"Results: {result}")

