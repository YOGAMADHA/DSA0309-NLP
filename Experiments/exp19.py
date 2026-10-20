import nltk
from nltk.wsd import lesk

sentence = "I deposited money in the bank".split()
sense = lesk(sentence, "bank", "n")

if sense:
    print("Word:", "bank")
    print("Meaning:", sense.definition())
else:
    print("No meaning found")
