"""End-to-end pipeline (Task 1.5 / Task 10 / Task 12 hybrid design) and the search index."""
import time
from collections import defaultdict
from . import morphology as morph
from . import noise
from .normalise import normalise
from .patterns import recognise_entities
from .porter_wrap import porter_stem
from .tokenizer import tokenize

_LID = None


def lid():
    global _LID
    if _LID is None:
        _LID = noise.LanguageID()
    return _LID


def analyse_token(tok, use_lid=False):
    """FST analysis first; Porter only as a low-confidence fallback for unanalysed English-like tokens."""
    low = tok.lower()
    a = morph.analyse(low)
    lang = None
    if use_lid:
        lang, _ = lid().identify(tok)
    if a:
        return {"token": tok, "lang": lang or "en", "analyses": [str(x) for x in a],
                "lemmas": sorted({x.lemma for x in a}), "source": "fst", "confidence": 1.0}
    if lang in ("ta-rom", "num", "mixed", "unk") or not low.isalpha():
        return {"token": tok, "lang": lang, "analyses": [], "lemmas": [low], "source": "none", "confidence": 0.3}
    return {"token": tok, "lang": lang or "en", "analyses": [], "lemmas": ["stem:" + porter_stem(low)],
            "source": "porter-fallback", "confidence": 0.5}


def process_record(text, noisy=False, locale="dmy", timings=None):
    """Run every stage; returns a dict keeping original text + corrections for auditability."""
    tm = timings if timings is not None else {}

    def timed(name, fn, *a, **k):
        t0 = time.perf_counter()
        r = fn(*a, **k)
        tm[name] = tm.get(name, 0.0) + time.perf_counter() - t0
        return r
    corrections = []
    cleaned = text
    if noisy:
        c = timed("input_cleaning", noise.clean, text)
        cleaned, corrections = c["cleaned"], c["corrections"]
    entities = timed("entity_recognition", recognise_entities, cleaned)
    normalised, nlog = timed("normalisation", normalise, cleaned, locale)
    tokens = timed("tokenisation", tokenize, cleaned)
    analyses = timed("fst_analysis", lambda: [analyse_token(t, use_lid=noisy) for t in tokens])
    return {"original": text, "cleaned": cleaned, "corrections": corrections, "entities": entities,
            "normalised": normalised, "normalisation_log": nlog, "tokens": tokens, "analyses": analyses}


class SearchIndex:
    """Inverted index over surface / lemma / porter-stem terms with confidence-aware ranking."""

    def __init__(self):
        self.surface, self.lemma, self.stem = defaultdict(set), defaultdict(set), defaultdict(set)
        self.docs = set()

    def add(self, doc_id, analyses):
        self.docs.add(doc_id)
        for a in analyses:
            self.surface[a["token"].lower()].add(doc_id)
            for l in a["lemmas"]:
                self.lemma[l].add(doc_id)
            if a["token"].isalpha():
                self.stem[porter_stem(a["token"])].add(doc_id)

    def search(self, query, mode="fst"):
        """mode: none | porter | fst. Returns {doc_id: score}."""
        scores = defaultdict(float)
        for tok in tokenize(query):
            low = tok.lower()
            if mode == "none":
                for d in self.surface.get(low, ()):
                    scores[d] += 1.0
            elif mode == "porter":
                for d in self.stem.get(porter_stem(low), ()):
                    scores[d] += 1.0
            else:
                a = analyse_token(tok)
                for l in a["lemmas"]:
                    for d in self.lemma.get(l, ()):
                        scores[d] += 0.8 if a["source"] == "fst" else 0.4
                for d in self.surface.get(low, ()):
                    scores[d] += 0.2       # exact surface match ranks above lemma-only match
        return dict(sorted(scores.items(), key=lambda x: -x[1]))
