from sentence_transformers import SentenceTransformer, util
import torch

import pickle

import os
current_dir = os.path.dirname(__file__)

embedder = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

# Load embeddings depending on what device is available (cpu / gpu)
embedding_path = os.path.join(current_dir, 'embeddings.pickle')
if (torch.cuda.is_available()):
    embeddings = torch.load(embedding_path)
else:
    embeddings = torch.load(embedding_path, map_location=torch.device('cpu'))

# Load files and page_info to be returned as the search results
with open(os.path.join(current_dir, 'pages.pickle'), 'rb') as f:
    pages = pickle.load(f)
with open(os.path.join(current_dir, 'page_info.pickle'), 'rb') as f:
    page_info = pickle.load(f)

# Return top_k results using cosine similarity
def semantic_search(query, num_results=3):
    top_k = min(num_results, embeddings.shape[0])
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)
    return [page_info[pages[i]] for i in top_results[1]]