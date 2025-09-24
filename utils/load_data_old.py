import pandas as pd
import ast

def parse_column(df, col):
    try:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    except:
        df[col] = [[] for _ in range(len(df))]
    return df

def load_movies_():
    # Load CSV files
    movies = pd.read_csv('data/tmdb_5000_movies.csv')
    credits = pd.read_csv('data/tmdb_5000_credits.csv')
    # movies = pd.read_csv('../data/tmdb_5000_movies.csv')
    # credits = pd.read_csv('../data/tmdb_5000_credits.csv')

    # # Merge dataframes
    # movies = movies.merge(credits, left_on='id', right_on='movie_id', how='left')

    # Rename columns for clarity
    movies.rename(columns={'vote_average': 'rating', 'title_x': 'title'}, inplace=True)

    # Drop duplicate columns
    movies.drop('title_y', axis=1, inplace=True)
    movies.drop('movie_id', axis=1, inplace=True)

    # return movies

    df = pd.merge(movies, credits, on="id")

    for col in ["genres", "cast", "crew", "production_companies", "spoken_languages"]:
        df = parse_column(df, col)

    return df