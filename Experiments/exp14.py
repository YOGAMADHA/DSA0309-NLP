import nltk

grammar = nltk.CFG.fromstring("""
S -> SingularNP SingularV
S -> PluralNP PluralV
SingularNP -> 'he' | 'she'
PluralNP -> 'they' | 'we'
SingularV -> 'runs' | 'eats'
PluralV -> 'run' | 'eat'
""")

parser = nltk.ChartParser(grammar)

sentences = [
    "he runs",
    "they run",
    "he run",
    "they runs"
]

for sentence in sentences:
    valid = list(parser.parse(sentence.split()))
    print(sentence, ":", "Correct" if valid else "Incorrect")
