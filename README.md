# Semantic Search
I made this search engine using Python and Django. It allows you to search Wikipedia pages for Academy Award-winning films using both keyword search and semantic search. Clicking on the search results will take you to the corresponding Wikipedia article.

## How To Run
Make sure you are using Python 3.8 or higher.<br>
**Note:** I only tested this on WSL and Ubuntu. I know that MinGW has an issue with scikit, which is a dependency.

Install the required packages using 
```
pip install -r requirements.txt
```

Navigate to the `semantic_search` directory (the one that contains `manage.py`) and type
```
python manage.py runserver
```
It may take a few minutes to download the LLM I use and to set up packages for the first time. Afterward, it should start within a couple of seconds. After running, click the link in the terminal or go to your browser and type `localhost:8000` in the address bar. You can use the toggle slider to toggle between semantic search and keyword search.


## Project Discussion
This was my first time building a search engine. I enjoyed learning about best practices for creating a search engine and the tradeoffs of different implementations. I started by building a reverse index to perform keyword search. I will go into the pros and cons that I have found of keyword search and semantic search below and discuss alternatives. After implementing keyword search, I decided to implement semantic search. Semantic search works by creating sentence embeddings using an LLM (such as BERT) and performing a similarity score (such as cosine similarity) with the query embedding. It performed, on average, better than keyword search at providing relevant results.

### Keyword Search
For keyword search, I used keyword density scores (KDS). I implemented this from scratch using a simple algorithm. If I re-implemented it, I would use [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) (or BM25F, given the domain) and an existing library to achieve increased performance. Still, it was good to experience building it from scratch. I used the following keyword density calculation:
```
KDS (single page) = (keyword frequency in page) / (total content length of page * KDS (all pages))
KDS (all pages) = (keyword frequency in all pages) / (total content length of all pages)
```
To get the total score for a query, we calculate the KDS for all keywords in the query and sum them together. The most relevant page using this method is the one that has the highest KDS.

In addition to indexing keywords in articles, I also indexed the lemmas and inflections of each keyword using the library [lemminflect](https://lemminflect.readthedocs.io/en/latest/). Using this, pages with different inflections or lemmas of the query will also show up in the results, as they are likely also relevant. Running on my machine, including all of the pre-processing and cleaning of the text, it takes about 4 minutes to generate the reverse index.

#### Pros
- It's fast and understandable. If a result comes up, you know the result contained some words in your query.
- It works well at finding pages with uncommon words or searching for names.
#### Cons
- It doesn't understand context or word meanings; searching for meaning often results in poor search results.

### Semantic Search
Semantic Search uses an LLM to generate sentence embeddings and performs a cosine similarity with the query embedding. I used [sbert](https://sbert.net/) models to generate my embeddings. I trialed three models trained on semantic search and selected the one that provided the best results for this domain.

- **multi-qa-MiniLM-L6-cos-v1:** A small 80mb that provided good performance. It took about 2 minutes to generate all embeddings.
- **msmarco-bert-base-dot-v5:** A larger 420mb model that had worse performance and took about 4 minutes to generate all embeddings.
- **multi-qa-mpnet-base-dot-v1:** A larger 420mb model that had the best performance. It took about 4.5 minutes to generate all embeddings.

I decided to use **multi-qa-mpnet-base-dot-v1** as I thought the performance improvements were worth the larger model and longer upfront computation time. The model is trained on dot products, but I found better search results using cosine similarity. I used the `Sentence-Transformers` library and `Torch` to generate the embeddings and calculate the cosine similarity scores. Since the pages I needed to embed were often larger than the context size for BERT (512 tokens), I chunked the text into 512-word chunks with a 50-word overlap. The word overlap helps maintain context. I then performed mean pooling of the embedding vectors. It took about 6 minutes to load and pre-process the html files and generate the embeddings.

#### Pros
- It provides better results on average than Keyword Search.
- It's can understand context and meaning to provide relevant results even if there is no keyword match.
#### Cons
- It performs poorly when tasked with searching for uncommon words or names.

### Hybrid Search
I want to take this section to discuss the hybrid search model briefly. While implementing both Keyword and Semantic Search, I noticed the benefits and shortcomings of both approaches. I started researching a hybrid approach, sometimes called "Keyword-Aware Semantic Search". This approach uses dense embedding vectors (used for Semantic Search) and sparse vectors (used for Keyword Search). The scores of both methods are combined to produce a hybrid score. Hybrid Search has been shown to perform better than what Keyword and Semantic search can do alone. I have yet to implement this, but I would like to explore this in the future. One of the most popular libraries for implementing Hybrid Search is [langchain](https://github.com/langchain-ai/langchain). I also wanted to link to [this medium](https://medium.com/@nadikapoudel16/advanced-rag-implementation-using-hybrid-search-reranking-with-zephyr-alpha-llm-4340b55fef22) article I found.

## Files

Most of my code is in five files located in `semantic_search/search/logic/`

- **utils.py:** Utility functions used mainly by `parser.py` and `search.py`
- **keyword_search.py:** Code for performing Keyword Search
- **parser.py:** This code is not used by the web app but can be run to re-generate the reverse index used by `search.py`
- **semantic_search.py:** Code for performing Semantic Search
- **embedder.py:** This code is not used by the web app but can be run to re-generate the embedding vectors used by `semantic_search.py`

Additionally, `views.py` handles requests, `templates/search/index.html` has my HTML code, and `static/search/*` has my CSS and JS code.


