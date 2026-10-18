
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

words = ["playing", "played", "plays", "studies", "connected", "happiness"]

for word in words:
    print(word, "->", stemmer.stem(word))
