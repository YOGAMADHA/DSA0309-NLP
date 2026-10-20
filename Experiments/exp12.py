grammar = {
    "S": [["NP", "VP"]],
    "NP": [["Det", "N"]],
    "VP": [["V", "NP"]],
    "Det": [["the"]],
    "N": [["cat"], ["mouse"]],
    "V": [["chased"]]
}

def earley(words):
    n = len(words)
    chart = [set() for _ in range(n + 1)]
    chart[0].add(("S'", ("S",), 0, 0))

    for i in range(n + 1):
        changed = True
        while changed:
            changed = False
            for state in list(chart[i]):
                lhs, rhs, dot, start = state

                if dot < len(rhs) and rhs[dot] in grammar:
                    for rule in grammar[rhs[dot]]:
                        new = (rhs[dot], tuple(rule), 0, i)
                        if new not in chart[i]:
                            chart[i].add(new)
                            changed = True

                elif dot < len(rhs) and i < n and rhs[dot] == words[i]:
                    chart[i + 1].add((lhs, rhs, dot + 1, start))

                elif dot == len(rhs):
                    for old in list(chart[start]):
                        a, b, d, st = old
                        if d < len(b) and b[d] == lhs:
                            new = (a, b, d + 1, st)
                            if new not in chart[i]:
                                chart[i].add(new)
                                changed = True

    return ("S'", ("S",), 1, 0) in chart[n]

sentence = "the cat chased the mouse".split()
print("Accepted" if earley(sentence) else "Rejected")
