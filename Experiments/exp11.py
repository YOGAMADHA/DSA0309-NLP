grammar = {
    "S": [["NP", "VP"]],
    "NP": [["Det", "N"]],
    "VP": [["V", "NP"]],
    "Det": [["the"]],
    "N": [["cat"], ["mouse"]],
    "V": [["chased"]]
}

def parse(symbol, words, pos):
    if symbol not in grammar:
        return pos + 1 if pos < len(words) and words[pos] == symbol else None

    for rule in grammar[symbol]:
        current = pos
        for item in rule:
            result = parse(item, words, current)
            if result is None:
                break
            current = result
        else:
            return current
    return None

sentence = "the cat chased the mouse".split()
result = parse("S", sentence, 0)
print("Accepted" if result == len(sentence) else "Rejected")
