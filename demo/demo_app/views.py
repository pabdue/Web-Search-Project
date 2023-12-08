from django.shortcuts import render
from .models import CivilResearch

# Create your views here.
def search_view(request):
    return render(request, 'search.html')

def about_view(request):
    return render(request, 'about.html')

def search_civil_research(request):
    query = request.GET.get('query', '')

    if query:
        # Use the correct field name from your model for filtering
        results = CivilResearch.objects.filter(research_interests__icontains=query)
    else:
        results = []

    return render(request, 'search.html', {'results': results, 'query': query})