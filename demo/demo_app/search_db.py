from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['civilCrawler']
collection = db['civilResearch']

def search_professors_test(query):
    # Use a simple text search on the 'research_interests' field
    query_regex = {"name": {"$regex": f".*{query}.*", "$options": "i"}}
    matching_professors = list(collection.find(query_regex))
    print(matching_professors)
    print(query)

    return matching_professors

def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    return ' '.join(stemmed_tokens)  # Return as a single string

def search_professors(query):
    # Retrieve all documents from the collection
    all_documents = list(collection.find())

    # Prepare documents
    documents = []
    professors = []

    for doc in all_documents:
        name = doc.get('name', 'Unknown')
        url = doc.get('url', 'No URL provided')
        title_dept = doc.get('title_dept', 'No title_dept provided')
        email = doc.get('email', 'No email provided')
        phone = doc.get('phone', 'No phone provided')
        professors.append((name, url, title_dept, email, phone))

        combined_text = ""

        # Iterate over all fields in the document
        for key, value in doc.items():
            if key not in ['_id', 'url', 'email', 'phone', 'office_location']:  # Exclude non-textual fields
                if isinstance(value, list):  # Handle list fields
                    for item in value:
                        if isinstance(item, dict):
                            # Concatenate all string values in the dictionary
                            combined_text += " ".join([str(v) for v in item.values() if isinstance(v, str)])
                        elif isinstance(item, str):
                            combined_text += " " + item
                elif isinstance(value, str):  # Handle string fields
                    combined_text += " " + value

        processed_text = preprocess_text(combined_text)
        documents.append(processed_text)

    # Create a TfidfVectorizer instance
    vectorizer = TfidfVectorizer()

    # Generate the TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Convert the TF-IDF matrix to a dense format
    dense_tfidf_matrix = tfidf_matrix.todense()

    # Add the processed query and transform it
    processed_query = preprocess_text(query)
    query_vector = vectorizer.transform([processed_query])

    # Compute cosine similarity
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Rank the documents
    document_ranking = sorted(enumerate(cosine_similarities), key=lambda x: x[1], reverse=True)
    print(document_ranking)

    ranked_professors = []

    for rank, (doc_idx, score) in enumerate(document_ranking):
        name, url, title_dept, email, phone = professors[doc_idx]
        ranked_professors.append({'name':name, 'url':url, 'title_dept':title_dept, 'email':email, 'phone':phone, 'score':score})

    print(ranked_professors)

    return ranked_professors
