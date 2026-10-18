
import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet', quiet=True)

lemmatizer = WordNetLemmatizer()

words = ["cars", "playing", "studies", "running", "better"]

for word in words:
    print(word, "->", lemmatizer.lemmatize(word, pos='v'))
