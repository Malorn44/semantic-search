from .utils import defaultdict, count_dict
from .utils import remove_stop_words, remove_diacritics, remove_nonalphanum

import pickle

import os
current_dir = os.path.dirname(__file__)


with open(os.path.join(current_dir, 'index.pickle'), 'rb') as f:
    index = pickle.load(f)
with open(os.path.join(current_dir, 'page_info.pickle'), 'rb') as f:
    page_info = pickle.load(f)

def get_top_results(results, top):
    results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return results[:top]

def preprocess_search(text):
    text = text.lower()
    return remove_diacritics(remove_nonalphanum(remove_stop_words(text)))

def keyword_search(query, num_results=3):
    query = preprocess_search(query)
    results = defaultdict(count_dict)

    for word in query.split():
        if not word:
            continue

        if word not in index:
            continue

        for page in index[word]['page']:
            if page not in results:
                results[page] = 0
            results[page] +=  index[word]['page'][page] / (page_info[page]['len']*index[word]['density'])
    
    results = get_top_results(results, num_results)
    return [page_info[result[0]] for result in results]
