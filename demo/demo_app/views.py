from django.shortcuts import render
from .search_db import search_professors

# Create your views here.
def search_view(request):
    return render(request, 'search.html')

def about_view(request):
    return render(request, 'about.html')

def search_civil_research(request):
    query = request.GET.get('query', '')

    professors = search_professors(query)

    return render(request, 'search.html', {'professors': professors, 'query': query})
