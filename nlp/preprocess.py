from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import spacy
import time

# import nltk

# nltk.download('punkt_tab')
# nltk.download('stopwords')

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Load list of stop words
INTENT_KEYWORDS = {"who", "what", "when", "where", "why", "how", "how many", "number", "count", "all"}
stop_words = set(stopwords.words('english')) - INTENT_KEYWORDS
# stop_words = set(stopwords.words('english'))

#---------- FUNCTIONS ----------#

# Tokenize the input text (list of individual words)
def tokenize(text):
    return word_tokenize(text)

# Convert all tokens to lowercase
def lowercase(tokens):
    return [t.lower() for t in tokens]

# Remove all punctuation (",", ".", ";", ...) from tokens
def remove_punctuation(tokens):
    return [t for t in tokens if t not in string.punctuation]

# Remove all stopwords ("the", "a", "in", ...) from tokens
def remove_stopwords(tokens):
    return [t for t in tokens if t not in stop_words]

# Lemmatize ("children" -> "child", "running" -> "run", "watched" -> "watch") the tokens
def lemmatize(tokens):
    text = " ".join(tokens)
    doc = nlp(text)
    return [token.lemma_ for token in doc]

# Call previous functions to build NLP preprocessing pipeline
def clean_text(text):
    start = time.time()
    print("Preprocessing text...")
    tokens = tokenize(text)
    tokens = lowercase(tokens)
    tokens = remove_punctuation(tokens)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)
    print("Preprocessed text in", round(time.time() - start, 2), "seconds\n")
    return tokens

#---------- TESTING ----------#

if __name__ == "__main__":
    print("\n\n|---------- TESING ----------|\n\n")

    # raw_text = "NLTK is a powerful library for natural language processing."
    # raw_text = "The children were running through the fields while their parents watched."
    # raw_text = "Top sci-fi movies shot by greg fraiser or directed by Christopher Nolan."
    # raw_text = "Show me all French horror films produced by WB or Paramount Pictures or Fox starring Brad Pitt"
    raw_text = "Who directed The Batman and when was The batman released?"
    print(raw_text)
    print(clean_text(raw_text))