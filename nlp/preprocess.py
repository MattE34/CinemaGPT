from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import spacy
import nltk
# nltk.download('punkt_tab')
# nltk.download('stopwords')

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Tokenize the input text (list of individual words)
def tokenize(text):
    tokens = word_tokenize(text)
    return tokens

# Convert all tokens to lowercase
def lowercase(tokens):
    return [t.lower() for t in tokens]

# Remove all punctuation (",", ".", ";", ...) from tokens
def remove_punctuation(tokens):
    return [t for t in tokens if t not in string.punctuation]

# Remove all stopwords ("the", "a", "in", ...) from tokens
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [t for t in tokens if t not in stop_words]

def lemmatize(tokens):
    text = " ".join(tokens)
    doc = nlp(text)
    return [token.lemma_ for token in doc]

def clean_text(text):
    return lemmatize(
        remove_stopwords(
            remove_punctuation(
                lowercase(
                    tokenize(text)))))

#---------- TESTING ----------#
if __name__ == "__main__":
    print("\n\n|---------- TESING ----------|\n\n")

    # raw_text = "NLTK is a powerful library for natural language processing."
    raw_text = "The children were running through the fields while their parents watched."
    # tokens = tokenize(raw_text)
    # print(tokens)
    # tokens = lowercase(tokens)
    # print(tokens)
    # tokens = remove_punctuation(tokens)
    # print(tokens)
    # tokens = remove_stopwords(tokens)
    # print(tokens)
    # tokens = lemmatize(tokens)
    # print(tokens)
    print(raw_text)
    print(clean_text(raw_text))