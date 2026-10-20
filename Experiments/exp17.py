from nltk.corpus import wordnet as wn

word = "bank"
synsets = wn.synsets(word)

for syn in synsets[:5]:
    print("Synset:", syn.name())
    print("Meaning:", syn.definition())
    print()
