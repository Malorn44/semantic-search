"""
embedder.py

Used for generating embeddings
Run this file to update pages.pickle and embeddings.pickle

NOTE: this file was only run on my machine to generate the embeddings and
may not work on your machine if you do not have an available CUDA device
"""

# for generating embeddings
from sentence_transformers import SentenceTransformer
import torch

# for extracting relevant text blocks from html
from bs4 import BeautifulSoup

# for storing the index
import pickle

# fancy time bar
from tqdm import tqdm

# for loading html files
import os
current_dir = os.path.dirname(__file__)
data_dir = os.path.normpath(os.path.join(current_dir, '../data'))

import re


embedder = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

# generates embedding vector for a string of text
def generateDocumentEmbedding(text):
    max_chunk_size = 512 # BERT uses context size of 512 tokens
    overlap_size = 50 # overlap between chunks helps retain context

    words = text.split()

    # Create overlapping chunks
    chunks = []
    for i in range(0, len(words), max_chunk_size - overlap_size):
        chunk_words = words[i:i+max_chunk_size]
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)

    # generate embeddings and return the mean aggregate embeddings
    chunk_embeddings = embedder.encode(chunks, convert_to_tensor=True)
    aggregate_embedding = torch.mean(chunk_embeddings, axis=0)
    return aggregate_embedding

# performs pre-processing on text
def clean(text):
    text = re.sub(r'\[(\d+|[a-z])\]', ' ', text) # remove citations
    text = re.sub(r'\s+', ' ', text) # remove multi spaces
    text = text.replace('\n', '') # remove end line characters
    text = text.strip() # remove leading or ending spaces
    return text

# returns an array of texts
def load_files(files):
    texts = []

    for file in tqdm(files):
        with open(os.path.join(data_dir, file), 'r') as f:
            html_content = f.read()

        # use bs4 to grab text from <p> tags
        soup = BeautifulSoup(html_content, 'html.parser')
        paragraphs = soup.find_all('p')
        paragraph_texts = [p.get_text() for p in paragraphs]
        text = (' '.join(paragraph_texts))
        text = clean(text)
        texts.append(text)

    return texts

if __name__ == "__main__":
    # load files and generate texts
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    texts = load_files(files)

    # prints the device being used
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    # generate embeddings
    embeddings = torch.stack([generateDocumentEmbedding(text) for text in tqdm(texts)])

    # save embeddings and files
    torch.save(embeddings,'embeddings.pickle')
    with open('pages.pickle', 'wb') as f:
        pickle.dump(files, f, protocol=pickle.HIGHEST_PROTOCOL)


