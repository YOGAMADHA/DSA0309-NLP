"""Thin wrapper around NLTK's reference Porter stemmer (Task 9)."""
from nltk.stem import PorterStemmer

_stemmer = PorterStemmer()


def porter_stem(word):
    return _stemmer.stem(word.lower())


def measure(word):
    """Porter measure m in [C](VC)^m[V] (simplified y handling)."""
    w = word.lower()
    pattern = ""
    for i, ch in enumerate(w):
        is_v = ch in "aeiou" or (ch == "y" and i > 0 and pattern and pattern[-1] == "C")
        pattern += "V" if is_v else "C"
    collapsed = ""
    for ch in pattern:
        if not collapsed or collapsed[-1] != ch:
            collapsed += ch
    return collapsed.count("VC"), collapsed
