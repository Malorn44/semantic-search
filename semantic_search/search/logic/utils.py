# for removing diacritics
import unicodedata

# for converting numbers to word representations
from num2words import num2words

# for generating lemmas and inflections
from lemminflect import getAllLemmas, getAllInflections

# stopword list
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

import re
from collections import defaultdict

# default value for a dictionary meant to count element occurences
def count_dict():
    return 0

def print_sorted_word_counts(word_count_dict, top=None):
    # Sort the dictionary by counts in descending order
    sorted_word_counts = sorted(word_count_dict.items(), key=lambda item: item[1], reverse=True)
    
    if not top:
        top = len(sorted_word_counts)
        
    # Print the sorted word counts
    for word, count in sorted_word_counts[:top]:
        print(f"{word}: {count}")

def get_lemmas_inflections(word):
    if word.isnumeric():
        try:
            return set(
                num2words(word).replace('-',' ').split().append(word)
            )
        except: # probably encountered VULGAR FRACTION
            return set([word])
    lemmas = {
        lemma for lemma_list in
        getAllLemmas(word).values()
        for lemma in lemma_list
    }
    inflections = {
        inflection for inflection_list in
        getAllInflections(word).values()
        for inflection in inflection_list
    }
    inflections.add(word)
    return lemmas.union(inflections)

def remove_nonalphanum(text):
    return re.sub(r'[^\w\s-]+','',text).replace('-', ' ')

def remove_citations(text):
    return re.sub(r'\[(\d+|[a-z])\]', ' ', text)

def remove_diacritics(text):
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn')

def remove_stop_words(text):
    return ' '.join(w for w in text.split() if w and w not in frozenset(stopwords.words('english')))

def clean_text(text):
    text = text.lower()
    return remove_diacritics(remove_nonalphanum(remove_citations(remove_stop_words(text))))
