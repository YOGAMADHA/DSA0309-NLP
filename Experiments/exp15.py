import nltk

grammar = nltk.PCFG.fromstring("""
S -> NP VP [1.0]
NP -> Det N [0.8] | 'John' [0.2]
VP -> V NP [0.7] | V [0.3]
Det -> 'the' [1.0]
N -> 'dog' [0.6] | 'cat' [0.4]
V -> 'sees' [1.0]
""")

parser = nltk.ViterbiParser(grammar)
sentence = "John sees the dog".split()

for tree in parser.parse(sentence):
    print(tree)
    print("Probability:", tree.prob())
