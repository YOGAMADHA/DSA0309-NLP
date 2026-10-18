
import nltk

nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

text = "The little boy plays cricket"

tokens = nltk.word_tokenize(text)
tags = nltk.pos_tag(tokens)

for word, tag in tags:
    print(word, "->", tag)
