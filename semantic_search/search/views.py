from django.shortcuts import render
from .logic.keyword_search import keyword_search
from .logic.semantic_search import semantic_search

def index(request):
    query = request.GET.get('query', '')
    num_results = int(request.GET.get('num_results', '3'))
    using_semantic_search = request.GET.get('semantic','off')

    # Call semantic search or keyword search
    if using_semantic_search == 'on':
        results = semantic_search(query,num_results)
    else:
        results = keyword_search(query,num_results)
    return render(request, 'search/index.html', {'results': results})
