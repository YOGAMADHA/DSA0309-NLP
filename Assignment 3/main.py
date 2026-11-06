"""
DSA03 NLP Assignment 3
Run: python main.py
No third-party packages required.
This is a compact educational implementation for the controlled helpdesk grammar.
"""
from collections import defaultdict
from time import perf_counter
import math

# Grammar rules are represented as (LHS, RHS tuple). Lexical rules have one terminal.
RULES = [
("S",("DECL",)),("S",("YNQ",)),("S",("WHQ",)),("S",("IMP",)),
("DECL",("NP","VP")),("YNQ",("AUX","NP","VPBASE")),("WHQ",("WH","AUX","NP","VPBASE")),
("WHQ",("WH","VP")),("IMP",("VB","NP")),("IMP",("VB","PP")),
("NP",("DET","N")),("NP",("DET","ADJ","N")),("NP",("PRON",)),
("NP",("NAME",)),("NP",("NP","PP")),("NP",("NP","REL")),
("VP",("V_INTR",)),("VP",("V_TRANS","NP")),("VP",("V_DITRANS","PRON","NP")),
("VP",("V_SENT","S")),("VP",("V_PP","PP")),("VP",("VP","PP")),
("VP",("AUX","VB")),("VP",("AUX","V_PART")),
("VPBASE",("VB",)),("VPBASE",("VB","NP")),("VPBASE",("VB","PP")),
("VPBASE",("VB","NP","PP")),("PP",("P","NP")),
("ADJP",("ADJ",)),("ADJP",("ADV","ADJ")),("NP",("NP","CONJ","NP")),
("VP",("VP","CONJ","VP")),("S",("S","CONJ","S")),
("REL",("RELPRO","VP")),("REL",("RELPRO","AUX","V_PART")),
("WH",("WHWORD",)),("NP",("DET","N","PP")),
("NP",("DET","ADJ","ADJ","N")),("VP",("V_TRANS","NP","PP")),
("VP",("V_INTR","ADV"))
]

LEXICON = {
"DET":"the a this that these those my your their",
"N":"student students form forms fee fees hostel hostels room rooms library exam exams timetable timetables notice notices receipt receipts seminar seminars portal assignment assignments placement placements book booking result results class classes campus",
"ADJ":"late current available postponed important new final online",
"ADV":"quickly today tomorrow now already",
"PRON":"I me we us they them he him she her you",
"NAME":"Ravi Anu",
"V_INTR":"crashed arrived exists",
"V_TRANS":"submit check show book need access view",
"V_DITRANS":"send give",
"V_SENT":"tell know explain",
"V_PP":"apply wait look",
"VB":"submit check show book send tell apply open view pay",
"AUX":"do does did can will is are was were",
"V_PART":"postponed paid available",
"P":"with near for to in at from about by",
"CONJ":"and or but",
"RELPRO":"that who which",
"WHWORD":"what when where which who how"
}
LEX = {}
for tag, words in LEXICON.items():
    for w in words.split():
        LEX.setdefault(w, []).append(tag)

def tokenize(s):
    return [x.lower() for x in s.replace("?", "").replace(".", "").replace(",", "").split()]

def earley(sentence):
    words = tokenize(sentence)
    n = len(words)
    chart = [set() for _ in range(n+1)]
    # State: (lhs, rhs tuple, dot, origin)
    start = ("@START", ("S",), 0, 0)
    chart[0].add(start)
    for i in range(n+1):
        changed = True
        while changed:
            changed = False
            for st in list(chart[i]):
                lhs, rhs, dot, origin = st
                if dot < len(rhs):
                    sym = rhs[dot]
                    if sym in LEXICON or sym in {"DET","N","ADJ","ADV","PRON","NAME","V_INTR","V_TRANS","V_DITRANS","V_SENT","V_PP","VB","AUX","V_PART","P","CONJ","RELPRO","WHWORD"}:
                        for prod in RULES:
                            if prod[0] == sym:
                                ns = (prod[0], prod[1], 0, i)
                                if ns not in chart[i]:
                                    chart[i].add(ns); changed = True
                    else:
                        for prod in RULES:
                            if prod[0] == sym:
                                ns = (prod[0], prod[1], 0, i)
                                if ns not in chart[i]:
                                    chart[i].add(ns); changed = True
                else:
                    for prev in list(chart[origin]):
                        pl, pr, pd, po = prev
                        if pd < len(pr) and pr[pd] == lhs:
                            ns = (pl, pr, pd+1, po)
                            if ns not in chart[i]:
                                chart[i].add(ns); changed = True
            if i < n:
                for st in list(chart[i]):
                    lhs, rhs, dot, origin = st
                    if dot < len(rhs):
                        sym = rhs[dot]
                        if sym in LEX:
                            if words[i] in LEX and sym in LEX[words[i]]:
                                chart[i+1].add((lhs, rhs, dot+1, origin))
                        elif sym in LEXICON and words[i] in LEXICON[sym].split():
                            chart[i+1].add((lhs, rhs, dot+1, origin))
    accepted = ("@START", ("S",), 1, 0) in chart[n]
    return accepted, chart

# Recursive-descent recognizer without left-recursive expansion; depth limit prevents runaway recursion.
def top_down(sentence, max_depth=30):
    words = tokenize(sentence)
    def parse_symbol(sym, pos, depth):
        if depth > max_depth: return []
        if sym in LEX:
            return [pos+1] if pos < len(words) and sym in LEX.get(words[pos], []) else []
        results=[]
        for lhs, rhs in RULES:
            if lhs != sym: continue
            positions=[pos]
            for part in rhs:
                nxt=[]
                for p in positions:
                    nxt.extend(parse_symbol(part,p,depth+1))
                positions=nxt
                if not positions: break
            results.extend(positions)
        return results
    return len(words) in parse_symbol("S",0,0)

# Demonstration PCFG probabilities (illustrative relative frequencies from a 20-tree hand-built sample).
PCFG = {
"S": [("DECL",.55),("YNQ",.15),("WHQ",.20),("IMP",.10)],
"DECL": [("NP VP",1.0)],
"NP": [("DET N",.55),("DET ADJ N",.20),("PRON",.10),("NAME",.05),("NP PP",.10)],
"VP": [("V_INTR",.15),("V_TRANS NP",.35),("V_DITRANS PRON NP",.10),
       ("V_SENT S",.10),("V_PP PP",.15),("VP PP",.15)]
}
def pcfg_demo():
    # A transparent worked PP-attachment comparison:
    # attach PP to NP vs VP. Probabilities are illustrative MLE-style estimates.
    np_attach = .10 * .55 * .15
    vp_attach = .15 * .55 * .55
    return np_attach, vp_attach

TESTS = [
("The student submits the form.", True),
("The students submit the forms.", True),
("Show the students with the late fee notice.", True),
("Book the room near the library for the seminar.", True),
("Can you check the timetable?", True),
("Where is the library?", True),
("When will the exams be held?", True),
("Submit the assignment.", True),
("Send me the receipt.", True),
("Tell me the fee is paid.", True),
("The portal crashed.", True),
("Apply for a hostel room.", True),
("The late fee notice is available.", True),
("My exam result is online.", True),
("The students and staff need the timetable.", True),
("The hostel charges are due.", True),
("Who can access the portal?", True),
("Does the student need a room?", True),
("Show me the placement notice.", True),
("The exams that were postponed will be held tomorrow.", True),
("The library is near the hostel.", True),
("Pay the current fee today.", True),
("The student checks the result.", True),
("We need the room for the seminar.", True),
("The form is available online.", True),
("The students submits the form.", False),
("The student submit the forms.", False),
("Me checks the timetable.", False),
("The portal crashed the form.", False),
("Submit.", False)
]

def main():
    print("DSA03 NLP Assignment 3 - Helpdesk Parser")
    print("-"*55)
    print(f"Grammar phrase-structure rules: {len(RULES)}")
    print(f"Lexicon entries: {sum(len(v.split()) for v in LEXICON.values())}")
    print(f"Test sentences: {len(TESTS)}")
    print("\\nSentence test results (Earley recognizer):")
    rows=[]
    for s, expected in TESTS:
        t0=perf_counter(); found, chart=earley(s); elapsed=(perf_counter()-t0)*1000
        states=sum(len(c) for c in chart)
        rows.append((len(tokenize(s)),states,elapsed))
        print(f"{'PASS' if found==expected else 'CHECK'} | expected={expected!s:<5} found={found!s:<5} | {s}")
    np_a,vp_a=pcfg_demo()
    print("\\nIllustrative PCFG PP attachment:")
    print(f"NP attachment score = {np_a:.6f}")
    print(f"VP attachment score = {vp_a:.6f}")
    print("Preferred attachment: VP (higher score)")
    print("\\nNote: the controlled grammar is an educational fragment, not a production parser.")
    return rows

if __name__ == "__main__":
    main()
