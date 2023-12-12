from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["civilCrawler"]
collection = db["civilResearch"]

# Function to preprocess text
def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    return ' '.join(stemmed_tokens)  # Return as a single string

# Prepare documents
documents = []
doc_ids = []
professors = [] 

for doc in collection.find():
    doc_id = str(doc['_id'])
    doc_ids.append(doc_id)

    name = doc.get('name', 'Unknown')
    url = doc.get('url', 'No URL provided')
    professors.append((name, url))
    
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

# Get feature names to match indices
feature_names = vectorizer.get_feature_names()

# Add a query and transform it
query = "Understanding Public Sentiment toward I-710 Corridor Project from Social Media Based on Natural Language Processing"
processed_query = preprocess_text(query)
query_vector = vectorizer.transform([processed_query])

# Compute cosine similarity
cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

# Rank the documents
document_ranking = sorted(enumerate(cosine_similarities), key=lambda x: x[1], reverse=True)

# Display the ranking
for rank, (doc_idx, score) in enumerate(document_ranking):
    name, url = professors[doc_idx]
    print(f"Rank {rank + 1}: Document {doc_idx + 1} (Score: {score}) - {name}, Homepage: {url}")