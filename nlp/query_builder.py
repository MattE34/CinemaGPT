from utils.load_data import load_movies_
import pandas as pd
import json

# ----------------------------------------------------------------- #
# ------------------ MAIN QUERY BUILDER FUNCTION ------------------ #
# ----------------------------------------------------------------- #

def build_query(entities, intent):
    df = load_movies_()

    # Apply filters per entities

    # Apply sorting

    # Limit results

# --------------------------------------------- #
# ------------------ TESTING ------------------ #
# --------------------------------------------- #

if __name__ == "__main__":
    pass