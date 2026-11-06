"""DFA / NFA machinery for Task 4: validators, epsilon-NFA, subset construction,
minimisation (Moore partition refinement) and DFA -> regex by state elimination.

Input characters are mapped to symbol classes: a literal (if the machine lists it), 'DIGIT',
'ALPHA' (upper-case letter) or 'OTHER'.
"""
import re
from itertools import product

EPS = ""


def classify(ch, literals):
    if ch in literals:
        return ch
    if ch.isdigit():
        return "DIGIT"
    if ch.isalpha() and ch.isupper():
        return "ALPHA"
    return "OTHER"


class DFA:
    def __init__(self, name, start, accepts, delta, literals):
        self.name, self.start, self.accepts = name, start, set(accepts)
        self.delta, self.literals = dict(delta), set(literals)
        self.states = {start} | self.accepts | {s for s, _ in delta} | set(delta.values())
        self.alphabet = {sym for _, sym in delta} | {"OTHER"}

    def trace(self, s):
        state, path = self.start, [self.start]
        for ch in s:
            state = self.delta.get((state, classify(ch, self.literals)), "DEAD")
            path.append(state)
            if state == "DEAD":
                break
        return path

    def accepts_string(self, s):
        return self.trace(s)[-1] in self.accepts

    def complete(self):
        d = dict(self.delta)
        for st, sym in product(self.states | {"DEAD"}, self.alphabet):
            d.setdefault((st, sym), "DEAD")
        return DFA(self.name, self.start, self.accepts, d, self.literals)

    def minimise(self):
        """Moore partition refinement on the completed, reachable DFA."""
        m = self.complete()
        reach, stack = {m.start}, [m.start]
        while stack:
            s = stack.pop()
            for a in m.alphabet:
                t = m.delta[(s, a)]
                if t not in reach:
                    reach.add(t); stack.append(t)
        part = {s: (s in m.accepts) for s in reach}
        while True:
            sig = {s: (part[s], tuple(part[m.delta[(s, a)]] for a in sorted(m.alphabet))) for s in reach}
            ids = {v: i for i, v in enumerate(sorted(set(sig.values()), key=str))}
            new = {s: ids[sig[s]] for s in reach}
            if len(set(new.values())) == len(set(part.values())):
                part = new
                break
            part = new
        name = lambda s: f"M{part[s]}"
        delta = {(name(s), a): name(m.delta[(s, a)]) for s in reach for a in m.alphabet}
        return DFA(self.name + "-min", name(m.start), {name(s) for s in m.accepts if s in reach}, delta, self.literals)

    def table(self):
        rows = []
        for (s, a), t in sorted(self.delta.items(), key=lambda x: (str(x[0][0]), x[0][1])):
            rows.append(f"{s} --{a}--> {t}")
        return "\n".join(rows)


class NFA:
    def __init__(self, name, start, accepts, delta, literals):
        self.name, self.start, self.accepts = name, start, set(accepts)
        self.delta = {k: set(v) for k, v in delta.items()}
        self.literals = set(literals)
        self.alphabet = {sym for _, sym in delta if sym != EPS} | {"OTHER"}

    def eps_closure(self, states):
        out, stack = set(states), list(states)
        while stack:
            s = stack.pop()
            for t in self.delta.get((s, EPS), ()):
                if t not in out:
                    out.add(t); stack.append(t)
        return frozenset(out)

    def move(self, states, sym):
        return self.eps_closure({t for s in states for t in self.delta.get((s, sym), ())})

    def trace(self, s):
        cur = self.eps_closure({self.start})
        sets = [cur]
        for ch in s:
            cur = self.move(cur, classify(ch, self.literals))
            sets.append(cur)
        return sets

    def accepts_string(self, s):
        return bool(self.trace(s)[-1] & self.accepts)


def subset_construction(nfa):
    """NFA -> DFA. Each DFA state is a frozenset of NFA states (eps-closed)."""
    start = nfa.eps_closure({nfa.start})
    seen, todo, delta = {start}, [start], {}
    while todo:
        S = todo.pop()
        for a in sorted(nfa.alphabet):
            T = nfa.move(S, a)
            delta[(S, a)] = T
            if T not in seen:
                seen.add(T); todo.append(T)
    names = {S: ("{" + ",".join(sorted(map(str, S))) + "}") if S else "DEAD" for S in seen}
    accepts = {names[S] for S in seen if S & nfa.accepts}
    d = {(names[S], a): names[T] for (S, a), T in delta.items() if names[S] != "DEAD" or True}
    return DFA(nfa.name + "-dfa", names[start], accepts, d, nfa.literals)


# ---------- the four required DFA validators ----------
def patient_id_dfa():
    d = {("q0", "P"): "q1", ("q1", "T"): "q2"}
    for i in range(6):
        d[(f"q{2+i}", "DIGIT")] = f"q{3+i}"
    return DFA("patient_id", "q0", {"q8"}, d, {"P", "T"})


def date_dfa():
    d, seq = {}, ["DIGIT"] * 4 + ["-"] + ["DIGIT"] * 2 + ["-"] + ["DIGIT"] * 2
    for i, sym in enumerate(seq):
        d[(f"q{i}", sym)] = f"q{i+1}"
    return DFA("date_ymd", "q0", {"q10"}, d, {"-"})


def bp_dfa():
    d = {("q0", "DIGIT"): "q1", ("q1", "DIGIT"): "q2", ("q2", "DIGIT"): "q3",
         ("q2", "/"): "q4", ("q3", "/"): "q4",
         ("q4", "DIGIT"): "q5", ("q5", "DIGIT"): "q6", ("q6", "DIGIT"): "q7",
         ("q6", " "): "q8", ("q7", " "): "q8", ("q6", "m"): "q9", ("q7", "m"): "q9", ("q8", "m"): "q9",
         ("q9", "m"): "q10", ("q10", "H"): "q11", ("q11", "g"): "q12"}
    return DFA("blood_pressure", "q0", {"q12"}, d, {"/", " ", "m", "H", "g"})


def icd_dfa():
    d = {("q0", "ALPHA"): "q1", ("q1", "DIGIT"): "q2", ("q2", "DIGIT"): "q3", ("q2", "ALPHA"): "q3",
         ("q3", "."): "q4"}
    for i in range(4):
        d[(f"q{4+i}", "DIGIT")] = f"q{5+i}"
        d[(f"q{4+i}", "ALPHA")] = f"q{5+i}"
    return DFA("icd_code", "q0", {"q3", "q5", "q6", "q7", "q8"}, d, {"."})


# ---------- NFA with epsilon transitions: PT, optional '-' or ' ', six digits ----------
def patient_id_nfa():
    d = {("s0", "P"): {"s1"}, ("s1", "T"): {"s2"},
         ("s2", EPS): {"s3"}, ("s2", "-"): {"s3"}, ("s2", " "): {"s3"}}
    for i in range(6):
        d[(f"s{3+i}", "DIGIT")] = {f"s{4+i}"}
    return NFA("patient_id_nfa", "s0", {"s9"}, d, {"P", "T", "-", " "})


# ---------- DFA -> regular expression by state elimination ----------
def _lab(sym):
    return "[0-9]" if sym == "DIGIT" else "[A-Z]" if sym == "ALPHA" else re.escape(sym)


def _alt(a, b):
    if a is None: return b
    if b is None: return a
    return a if a == b else f"(?:{a}|{b})"


def _cat(*xs):
    return None if any(x is None for x in xs) else "".join(xs)


def _star(x):
    return "" if x in (None, "") else f"(?:{x})*"


def dfa_to_regex(dfa):
    """GNFA state elimination: R'ij = Rij | Rik (Rkk)* Rkj. Dead state is dropped."""
    states = [s for s in dfa.states if s != "DEAD"]
    R = {}
    for (s, a), t in dfa.delta.items():
        if t == "DEAD" or s == "DEAD" or a == "OTHER":
            continue
        R[(s, t)] = _alt(R.get((s, t)), _lab(a))
    R[("START", dfa.start)] = ""
    for f in dfa.accepts:
        R[(f, "FINAL")] = ""
    remaining = list(states)
    for k in list(states):
        srcs = [i for i in ["START"] + remaining if i != k and (i, k) in R]
        dsts = [j for j in remaining + ["FINAL"] if j != k and (k, j) in R]
        loop = _star(R.get((k, k)))
        for i in srcs:
            for j in dsts:
                R[(i, j)] = _alt(R.get((i, j)), _cat(R[(i, k)], loop, R[(k, j)]))
        remaining.remove(k)
        R = {key: v for key, v in R.items() if k not in key}
    return R.get(("START", "FINAL"))
