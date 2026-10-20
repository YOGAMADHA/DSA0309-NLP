import nltk

grammar = nltk.CFG.fromstring("""
S -> NP VP
NP -> Det N
VP -> V NP
Det -> 'the'
N -> 'cat' | 'mouse'
V -> 'chased'
""")

sentence = "the cat chased the mouse".split()
parser = nltk.ChartParser(grammar)

for tree in parser.parse(sentence):
    print(tree)
    tree.pretty_print()
