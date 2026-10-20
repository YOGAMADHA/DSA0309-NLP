from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documents = [
    "Python is a programming language",
    "Machine learning uses Python",
    "Football is a popular sport"
]

query = "Python programming"

vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(documents + [query])

scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

for index, score in ranked:
    print(f"Document {index + 1}: {documents[index]} (Score: {score:.3f})")
