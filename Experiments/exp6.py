
import random

text = "the cat sleeps the cat eats the dog sleeps"
words = text.split()

bigrams = {}

for i in range(len(words) - 1):
    current = words[i]
    next_word = words[i + 1]

    if current not in bigrams:
        bigrams[current] = []

    bigrams[current].append(next_word)

word = "the"
generated = [word]

for i in range(8):
    if word not in bigrams:
        break
    word = random.choice(bigrams[word])
    generated.append(word)

print("Generated text:")
print(" ".join(generated))
