import json
import pandas as pd
import streamlit as st

# --- Import your NLP pipeline pieces ---
from utils.load_data import load_movies_
from nlp.preprocess import clean_text
from nlp.entity_extractor import extract_entities
from nlp.intent_classifier import classify_intent
from nlp.query_builder import assign_roles_to_people, build_query, execute_query
import nlp.query_builder as qb  # so we can patch load_movies_ to the cached version

# ----------------------
# Page & Theme
# ----------------------
st.set_page_config(
    page_title="CinemaGPT",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Global CSS for dark UI + green titles
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        background-color: #121212 !important; /* dark grey */
    }
    .block-container { max-width: 760px; padding-top: 3rem; padding-bottom: 4rem; }
    h1.cinemagpt-title {
        text-align: center;
        color: #22c55e;           /* green */
        margin-bottom: 0.25rem;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    p.cinemagpt-subtitle {
        text-align: center;
        color: #16a34a;           /* darker green */
        margin-top: 0rem;
        margin-bottom: 1.5rem;
        font-size: 1.05rem;
    }
    .stTextInput > div > div > input {
        background-color: #1e1e1e !important;
        color: #e5e7eb !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background-color: #22c55e !important;
        color: #0b0f0c !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 700 !important;
    }
    .stButton > button:hover {
        background-color: #16a34a !important;
    }
    .result-card {
        background-color: #1a1a1a;
        padding: 1rem 1.1rem;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        margin-bottom: 0.6rem;
    }
    .result-title {
        color: #e5e7eb;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .result-meta {
        color: #9ca3af;
        font-size: 0.95rem;
        word-break: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<h1 class="cinemagpt-title">CinemaGPT</h1>', unsafe_allow_html=True)
st.markdown('<p class="cinemagpt-subtitle">Search all things movies!</p>', unsafe_allow_html=True)

# ----------------------
# Data (cached) + patch query_builder to use the cached dataframe
# ----------------------
@st.cache_data(show_spinner=False)
def cached_movies():
    return load_movies_()

# Monkey-patch the query builder to use our cached loader
qb.load_movies_ = cached_movies

# ----------------------
# UI: Form (Enter key submits) + Button
# ----------------------
with st.form(key="query_form", clear_on_submit=False):
    user_input = st.text_input(
        label="",
        placeholder="search movies",
        help="Try: Who directed The Dark Knight Rises • Top 5 horror movies starring Tom Cruise",
    )
    submitted = st.form_submit_button("Search")  # pressing Enter also submits the form

# Optional: a small advanced/debug panel (collapsed by default)
with st.expander("Advanced (debug)", expanded=False):
    st.caption("Inspect how your query is parsed. Helpful for debugging entity extraction and intent classification.")
    st.caption("No personal data is stored; this pane only shows the current query run.")

# ----------------------
# Helpers
# ----------------------
def render_results(result, query):
    """Pretty print results from execute_query based on their type/shape."""
    # Direct answers or error strings
    if isinstance(result, str):
        msg = result.strip().lower()
        if msg.startswith("no ") or "couldn't understand" in msg:
            st.error(result)
            return
        label = query.get("return", "result").title()
        st.markdown(
            f'<div class="result-card">'
            f'<div class="result-title">{label}</div>'
            f'<div class="result-meta">{result}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    # Empty list
    if isinstance(result, list) and len(result) == 0:
        st.warning("No results. Try rephrasing or broadening your query.")
        return

    # List of strings -> movie titles
    if isinstance(result, list) and all(isinstance(x, str) for x in result):
        df = pd.DataFrame({"Movie": result})
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    # List of dicts -> structured answers (e.g., title -> people/date)
    if isinstance(result, list) and all(isinstance(x, dict) for x in result):
        df = pd.DataFrame(result)
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    # Fallback (unknown structure)
    st.write(result)

# ----------------------
# Run pipeline
# ----------------------
if submitted:
    try:
        text = (user_input or "").strip()
        if not text:
            st.info("Type a query above to begin.")
        else:
            # Pipeline: preprocess → intent → entities → role assignment → query → execute
            tokens = clean_text(text)
            intent = classify_intent(tokens)
            entities = extract_entities(text)
            entities = assign_roles_to_people(entities, text)
            query = build_query(intent, entities, tokens)

            # Show debug info
            with st.expander("Advanced (debug)", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Intent**")
                    st.code(json.dumps(intent, indent=2), language="json")
                    st.write("**Entities**")
                    st.json(entities)
                with col2:
                    st.write("**Query**")
                    st.json(query)

            # Execute & render
            result = execute_query(query)

            # Handle unknown/unsupported intent explicitly
            if intent.get("type") == "unknown":
                st.warning(
                    "Sorry, I couldn't understand that. "
                    "Try phrasing it differently (e.g., 'Top 5 action movies since 2010')."
                )
            else:
                render_results(result, query)

    except Exception as e:
        st.error("Something went wrong while processing your request.")
        st.exception(e)
