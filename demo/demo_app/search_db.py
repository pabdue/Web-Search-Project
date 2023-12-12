from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['civilCrawler']
collection = db['civilResearch']

def search_professors(query):
    # Use a simple text search on the 'research_interests' field
    query_regex = {"name": {"$regex": f".*{query}.*", "$options": "i"}}
    matching_professors = list(collection.find(query_regex))
    print(matching_professors)
    print(query)

    return matching_professors

'''
# Extract text data for vectorization
corpus = []

for professor in professors:
    research_interests = professor.get('research_interests', [])
    if research_interests:
        research_interest = research_interests[0].get('Research Interest', '')
        corpus.append(research_interest)
    else:
        corpus.append('')  # Add an empty string if 'research_interests' key is not present


# Vectorize the text data
vectorizer = TfidfVectorizer(norm='l2')
X = vectorizer.fit_transform(corpus)

def search_professors(query, page=1):
    # Vectorize the user's query
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity
    cosine_similarities = linear_kernel(query_vector, X).flatten()

    # Sort professors by similarity in descending order
    professor_indices = cosine_similarities.argsort()[::-1]

    # Paginate the results
    paginator = Paginator(professor_indices, 5)
    professors_page = paginator.get_page(page)

    # Get the relevant professors
    relevant_professors = [professors[i] for i in professors_page]

    return relevant_professors

'''
