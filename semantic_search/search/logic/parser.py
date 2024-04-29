"""
parser.py

Parses html files for all body text
Run this file to update page_info.pickle and index.pickle
"""

# import utils
from utils import count_dict, clean_text, get_lemmas_inflections

# for extracting relevant text blocks from html
from bs4 import BeautifulSoup

# defualt dict
from collections import defaultdict

# for storing the index
import pickle

# fancy time bar
from tqdm import tqdm

# for parsing urls to proper unicode representation
import urllib.parse

# for loading html files
import os
current_dir = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(current_dir, '../data'))

# returns...
# dictionary of word counts
# number of content words in file
# snippet of the page for a description
def parse_html(file_name):
    word_counts = defaultdict(count_dict)
    num_content_words = 0
    
    with open(file_name, mode='r', encoding='utf-8') as page:
        page = page.read()

    # use bs4 to grab text from <p> tags
    soup = BeautifulSoup(page, 'html.parser')
    paragraphs = soup.find_all('p')
    paragraphs = [p.get_text() for p in paragraphs]
    description = ''.join(paragraphs)[:250]
    for paragraph in paragraphs:
        cleaned_text = clean_text(paragraph)
        for word in cleaned_text.split(' '):
            if not word:
                continue

            num_content_words += 1

            word_set = get_lemmas_inflections(word)
            for w in word_set:
                word_counts[w] += 1

    return word_counts, num_content_words, description

if __name__ == "__main__":
    word_counts = {}
    page_info = {}
    total_length = 0

    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]

    # get keyword counts
    for f in tqdm(files):
        if f not in page_info:
            page_info[f] = {
                'len': 0,
                'title': urllib.parse.unquote(os.path.splitext(f)[0].replace('_',' ')),
                'link': 'https://wikipedia.com/wiki/' + os.path.splitext(f)[0],
                'descript': ''
            }

        word_counts[f], page_info[f]['len'], page_info[f]['descript'] = parse_html(os.path.join(data_dir, f))
        total_length += page_info[f]['len']

    # build the reverse index
    index = {}
    for page in word_counts:
        for word in word_counts[page]:
            if word not in index:
                index[word] = {'page': {page: 0}, 'density': 0}
            index[word]['page'][page] = word_counts[page][word]
            index[word]['density'] += word_counts[page][word]
    for word in index:
        index[word]['density'] /= total_length


    with open('index.pickle', 'wb') as f:
        pickle.dump(index, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open('page_info.pickle', 'wb') as f:
        pickle.dump(page_info, f, protocol=pickle.HIGHEST_PROTOCOL)

