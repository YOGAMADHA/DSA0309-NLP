"""Finite-state style morphological analyser/generator (Tasks 5-8).

The lexicon (stems + continuation classes) and orthographic rules define ONE surface<->lexical
relation. It is compiled into a surface->analyses table (analysis direction) and `generate`
runs the same relation in the other direction, as in a two-tape transducer.
"""
from collections import defaultdict
from typing import NamedTuple, Optional
from . import lexicon_data as L
from .orthography import inflect

CONTINUATION = {"N": ["+SG", "+PL"], "V": ["+BASE", "+3SG", "+PAST", "+PASTPART", "+PROG"],
                "ADJ": ["+POS", "+COMP", "+SUPER"]}


class Analysis(NamedTuple):
    lemma: str
    pos: str
    feat: str
    derivation: Optional[str] = None

    def __str__(self):
        d = f"  [derived: {self.derivation}]" if self.derivation else ""
        return f"{self.lemma} +{self.pos} {self.feat}{d}"


def _build():
    entries = defaultdict(set)
    deriv = {}
    for w in L.NOUNS:
        entries[w].add("N")
    for w in L.VERBS:
        entries[w].add("V")
    for w in L.ADJECTIVES:
        entries[w].add("ADJ")
    for base, aff, lemma, pos in L.DERIVED:
        entries[lemma].add(pos)
        deriv[(lemma, pos)] = f"{base}{aff if aff.startswith('-') else '+' + aff}"
    table = defaultdict(list)
    for lemma, poses in entries.items():
        for pos in poses:
            for feat in CONTINUATION[pos]:
                surf = inflect(lemma, pos, feat)
                if surf:
                    a = Analysis(lemma, pos, feat, deriv.get((lemma, pos)))
                    if a not in table[surf]:
                        table[surf].append(a)
    return entries, table


ENTRIES, _TABLE = _build()
STEMS = set(ENTRIES) | set(L.ROOTS)


def analyse(surface):
    """surface -> all licensed analyses (ambiguity preserved)."""
    return list(_TABLE.get(surface.lower(), []))


def generate(lemma, pos, feat):
    """lexical -> surface (same relation, reverse direction)."""
    if pos not in ENTRIES.get(lemma, set()):
        return None
    return inflect(lemma, pos, feat)


def generate_from_lexical(s):
    """'treat +V +PAST' -> 'treated'."""
    lemma, pos, feat = s.split()
    return generate(lemma, pos.lstrip("+"), feat)


def all_surface_forms():
    return set(_TABLE)


def lemmas_for(surface):
    return {a.lemma for a in analyse(surface)}


def lexicon_stats():
    return {"stems_incl_roots": len(STEMS), "inflectional_affixes": len(L.INFLECTIONAL_AFFIXES),
            "derivational_affixes": len(L.DERIVATIONAL_AFFIXES), "irregular_verbs": len(L.IRREGULAR_VERB),
            "irregular_plurals": len(L.IRREGULAR_PLURAL), "surface_forms": len(_TABLE)}
