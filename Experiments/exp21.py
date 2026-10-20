import nltk

grammar = nltk.CFG.fromstring("""
S -> NP VP
NP -> Det N
VP -> V NP
Det -> 'the'
N -> 'student' | 'book'
V -> 'reads'
""")

sentence = "the student reads the book".split()
parser = nltk.ChartParser(grammar)

for tree in parser.parse(sentence):
    print("Parse tree:")
    print(tree)
    print("Noun phrases:")
    for subtree in tree.subtrees(lambda t: t.label() == "NP"):
        print(" ".join(subtree.leaves()))
