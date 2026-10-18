
import nltk
from nltk import RegexpTagger

patterns = [
    (r'I|you|he|she|we|they', 'PRON'),
    (r'.*ing$', 'VERB'),
    (r'.*ed$', 'VERB'),
    (r'.*ly$', 'ADV'),
    (r'.*s$', 'NOUN'),
    (r'.*', 'NOUN')
]

tagger = RegexpTagger(patterns)

text = "I enjoy playing games"
words = nltk.wordpunct_tokenize(text)

print(tagger.tag(words))
