
tagged_words = [
    ("I", "NOUN"),
    ("like", "NOUN"),
    ("cricket", "NOUN")
]

print("Before transformation:")
print(tagged_words)

# Rule: Change "like" to VERB
for i, (word, tag) in enumerate(tagged_words):
    if word == "like" and tag == "NOUN":
        tagged_words[i] = (word, "VERB")

print("After transformation:")
print(tagged_words)
