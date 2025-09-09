from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import spacy

# import nltk

# nltk.download('punkt_tab')
# nltk.download('stopwords')

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Load list of stop words
stop_words = set(stopwords.words('english'))

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
    tokens = tokenize(text)
    tokens = lowercase(tokens)
    tokens = remove_punctuation(tokens)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)
    return tokens

#---------- TESTING ----------#

if __name__ == "__main__":
    print("\n\n|---------- TESING ----------|\n\n")

    # raw_text = "NLTK is a powerful library for natural language processing."
    raw_text = "The children were running through the fields while their parents watched."
    print(raw_text)
    print(clean_text(raw_text))