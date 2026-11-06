"""Regex tokeniser with true maximal-munch selection (Task 3)."""
import re

UNITS = r"(?:mg|mcg|g|mL|mmHg|kg|cm)"
ALTERNATIVES = [
    ("abbrev", r"[A-Za-z]+(?:\.[A-Za-z]+)+\.?"),                       # i.v.
    ("hyphen", r"[A-Za-z]+(?:-[A-Za-z]+)+"),                           # post-operative
    ("value_unit", r"[0-9]+(?:\.[0-9]+)?\s?" + UNITS + r"(?![A-Za-z])"),  # 500mg, 500 mg
    ("ratio", r"[0-9]+(?:/[0-9]+)+"),                                  # 120/80
    ("word", r"[A-Za-z]+(?:'[A-Za-z]+)?"),                             # words / contractions
    ("number", r"[0-9]+(?:\.[0-9]+)?"),
]
_COMPILED = [(n, re.compile(p)) for n, p in ALTERNATIVES]
_SKIP = re.compile(r"\s+")


def tokenize_spans(text):
    """At each position try every alternative and keep the LONGEST match (maximal munch)."""
    pos, out = 0, []
    while pos < len(text):
        m = _SKIP.match(text, pos)
        if m:
            pos = m.end()
            continue
        best = None
        for name, rx in _COMPILED:
            m = rx.match(text, pos)
            if m and (best is None or m.end() > best[2]):
                best = (name, m.start(), m.end())
        if best is None:                       # single punctuation char kept as its own token
            out.append(("punct", pos, pos + 1, text[pos]))
            pos += 1
        else:
            out.append((best[0], best[1], best[2], text[best[1]:best[2]]))
            pos = best[2]
    return out


def tokenize(text, keep_punct=False):
    return [t[3] for t in tokenize_spans(text) if keep_punct or t[0] != "punct"]
