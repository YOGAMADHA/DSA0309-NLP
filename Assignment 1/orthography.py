"""Orthographic (spelling) rules applied at morpheme boundaries (Task 8).

Cascade: lexicon lookup -> irregular override -> boundary rules -> surface form.
Each rule is a small function so it can be tested and traced individually.
"""
from .lexicon_data import (IRREGULAR_PLURAL, IRREGULAR_VERB, DOUBLING, ADJ_DOUBLING, ADJ_ER, ADJ_IRREGULAR)

VOWELS = set("aeiou")
SIBILANT_ENDINGS = ("s", "x", "z", "ch", "sh")


def _cy(word):  # consonant + y
    return len(word) > 1 and word.endswith("y") and word[-2] not in VOWELS


def add_s(word):
    """Plural / 3rd-singular: sibilant -es, C+y -> ies, else -s."""
    if word.endswith(SIBILANT_ENDINGS):
        return word + "es"
    if _cy(word):
        return word[:-1] + "ies"
    if word in {"go", "do", "echo", "hero"}:
        return word + "es"
    return word + "s"


def add_ed(word, doubling=False):
    if word.endswith("e"):
        return word + "d"                 # e-deletion (fracture+ed)
    if _cy(word):
        return word[:-1] + "ied"          # y -> i
    if doubling:
        return word + word[-1] + "ed"     # consonant doubling
    return word + "ed"


def add_ing(word, doubling=False):
    if word.endswith("ie"):
        return word[:-2] + "ying"
    if word.endswith(("ee", "oe", "ye")):
        return word + "ing"               # see+ing -> seeing (exception: keep e)
    if word.endswith("e"):
        return word[:-1] + "ing"          # e-deletion
    if doubling:
        return word + word[-1] + "ing"
    return word + "ing"


def add_er(word, suffix, doubling=False):
    if word.endswith("e"):
        return word + suffix[1:]          # large+er -> larger
    if _cy(word):
        return word[:-1] + "i" + suffix
    if doubling:
        return word + word[-1] + suffix
    return word + suffix


def inflect(lemma, pos, feat):
    """Generate a surface form. Returns None if the feature is not licensed."""
    if pos == "N":
        if feat == "+SG":
            return lemma
        if feat == "+PL":
            return IRREGULAR_PLURAL.get(lemma) or add_s(lemma)
    elif pos == "V":
        irr = IRREGULAR_VERB.get(lemma, {})
        dbl = lemma in DOUBLING
        if feat == "+BASE":
            return lemma
        if feat in irr:
            return irr[feat]
        if feat == "+3SG":
            return add_s(lemma)
        if feat in ("+PAST", "+PASTPART"):
            return add_ed(lemma, dbl)
        if feat == "+PROG":
            return add_ing(lemma, dbl)
    elif pos == "ADJ":
        if feat == "+POS":
            return lemma
        if feat in ("+COMP", "+SUPER") and lemma in ADJ_ER:
            if lemma in ADJ_IRREGULAR:
                return ADJ_IRREGULAR[lemma][0 if feat == "+COMP" else 1]
            suf = "er" if feat == "+COMP" else "est"
            return add_er(lemma, suf, lemma in ADJ_DOUBLING)
    return None
