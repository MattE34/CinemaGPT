import streamlit as st
import pandas as pd
import spacy
import nltk

from nlp import entity_extractor
from nlp import intent_classifier
from nlp import sql_generator
from utils import load_data


# Load data
@st.cache_data
def load_data():
    movies = pd.read_csv("data/tmdb_5000_movies.csv")
    return movies

movies = load_data()

st.title("🎬 CineQuery: Ask About Movies")
user_input = st.text_input("Ask me something about movies!", placeholder="e.g. Top 5 thrillers since 2010")

if user_input:
    st.markdown(f"**Your question:** {user_input}")
    
    # NLP processing
    # entities = extract_entities(user_input)
    # intent = classify_intent(user_input)
    
    # Query generation
    # result_df = generate_query(movies, entities, intent)

    # st.dataframe(result_df)
