
tag_probabilities = {
    "I": {"PRON": 0.95, "NOUN": 0.05},
    "like": {"VERB": 0.80, "ADJ": 0.20},
    "dogs": {"NOUN": 0.90, "VERB": 0.10},
    "run": {"VERB": 0.70, "NOUN": 0.30}
}

text = "I like dogs"
words = text.split()

for word in words:
    if word in tag_probabilities:
        tag = max(tag_probabilities[word],
                  key=tag_probabilities[word].get)
    else:
        tag = "UNKNOWN"

    print(word, "->", tag)
