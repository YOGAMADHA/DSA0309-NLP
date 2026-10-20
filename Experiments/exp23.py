import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

text = """
Python is a programming language.
Python is used for machine learning.
Machine learning helps computers learn from data.
"""

sentences = sent_tokenize(text)
vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(sentences)

scores = []
for i in range(len(sentences) - 1):
    score = cosine_similarity(matrix[i], matrix[i + 1])[0][0]
    scores.append(score)

average = sum(scores) / len(scores) if scores else 0

print("Average coherence score:", round(average, 3))
print("Coherence:", "High" if average >= 0.2 else "Low")
