"""Noise-tolerant front end for Task 12: OCR repair, line-break repair, weighted edit distance,
diacritic folding and character n-gram language identification.
All corrections are returned WITH a confidence and the original text so an audit trail is kept.
"""
import math
import re
import unicodedata
from collections import Counter
from . import morphology as morph

OCR_SUB_COST = {("O", "0"): .2, ("o", "0"): .2, ("I", "1"): .2, ("l", "1"): .2, ("l", "I"): .2,
                ("S", "5"): .3, ("B", "8"): .3, ("Z", "2"): .3, ("0", "O"): .2, ("1", "I"): .2, ("1", "l"): .2}
MULTI = {("rn", "m"): .3, ("m", "rn"): .3, ("cl", "d"): .4, ("vv", "w"): .3}


def strip_diacritics(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def weighted_edit_distance(a, b):
    """Levenshtein with cheap OCR-confusion substitutions and 2<->1 multi-char confusions."""
    n, m = len(a), len(b)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): D[i][0] = float(i)
    for j in range(1, m + 1): D[0][j] = float(j)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = 0.0 if a[i-1] == b[j-1] else OCR_SUB_COST.get((a[i-1], b[j-1]), 1.0)
            best = min(D[i-1][j] + 1, D[i][j-1] + 1, D[i-1][j-1] + sub)
            if i >= 2 and (a[i-2:i], b[j-1]) in MULTI:
                best = min(best, D[i-2][j-1] + MULTI[(a[i-2:i], b[j-1])])
            if j >= 2 and (a[i-1], b[j-2:j]) in MULTI:
                best = min(best, D[i-1][j-2] + MULTI[(a[i-1], b[j-2:j])])
            D[i][j] = best
    return D[n][m]


# ---- language identification (character trigrams) ----
VOCAB_EXTRA = {"paracetamol", "amoxicillin", "ibuprofen", "metformin", "amlodipine", "atorvastatin", "aspirin",
               "omeprazole", "ceftriaxone", "morphine", "diclofenac", "pantoprazole", "insulin", "femur"}

TAMIL_ROMAN = """ku irundhuchu kuduthen kudutheen vali kaichal thalai vayiru irukku illa enna nalla sapadu thanni
marundhu saptaen saappittaen mathirai kaalai ippo innum romba konjam naal vandhuchu aayiduchu paaru solrean
pannunga seri aama venum theriyum vandhen poren kudu kudunga irundhathu aachu pochu vandhuduchu sollunga
kaaichal thalaivali vayithu vali""".split()


class LanguageID:
    def __init__(self):
        self.models = {"en": self._profile(list(morph.all_surface_forms()) + list(VOCAB_EXTRA)), "ta-rom": self._profile(TAMIL_ROMAN)}

    @staticmethod
    def _grams(w):
        w = f"^{w.lower()}$"
        return [w[i:i+3] for i in range(len(w) - 2)]

    def _profile(self, words):
        c = Counter(g for w in words for g in self._grams(w))
        return c, sum(c.values()), len(c) + 1

    def score(self, word, lang):
        c, tot, V = self.models[lang]
        gs = self._grams(word)
        return sum(math.log((c[g] + 1) / (tot + V)) for g in gs) / max(len(gs), 1)

    def coverage(self, word, lang):
        gs = self._grams(word)
        c = self.models[lang][0]
        return sum(1 for g in gs if g in c) / max(len(gs), 1)

    def identify(self, token):
        """Returns (label, confidence). Labels: en, ta-rom, num, mixed, unk."""
        if not re.search(r"[A-Za-z]", token):
            return "num", 1.0
        if re.search(r"[0-9]", token):
            return "mixed", 1.0
        t = token.lower()
        if t in morph._TABLE or t in VOCAB_EXTRA:
            return "en", 1.0
        if t in TAMIL_ROMAN:
            return "ta-rom", 1.0
        cov = {l: self.coverage(t, l) for l in self.models}
        best = max(cov, key=lambda l: (cov[l], self.score(t, l)))
        other = min(cov.values())
        return (best, round(cov[best], 2)) if cov[best] >= 0.6 and cov[best] - other >= 0.15 else ("unk", round(cov[best], 2))


# ---- cleanup stages ----
_NUM = r"[0-9OoIl]*[0-9][0-9OoIl]*"
_FIX = str.maketrans({"O": "0", "o": "0", "I": "1", "l": "1"})


def vocab():
    return set(morph.all_surface_forms()) | VOCAB_EXTRA | {w for w in TAMIL_ROMAN}


def repair_linebreaks(text, voc=None):
    """Join 'Dis-\\ncharge' / 'irun-dhuchu' when the joined word is known and the hyphenated one is not."""
    voc = voc or vocab()

    def join(m):
        a, b = m.group(1), m.group(3)
        joined = (a + b).lower()
        if m.group(2).startswith("-\n") or m.group(2).startswith("- ") or (joined in voc and f"{a}-{b}".lower() not in voc):
            if joined in voc or m.group(2).startswith("-\n"):
                return a + b
        return m.group()
    return re.sub(r"([A-Za-z]+)(-\n|- |-)([A-Za-z]+)", join, text)


def repair_numbers(text):
    """Context-restricted OCR digit repair; returns (text, [(orig, fixed, confidence)])."""
    log = []

    def fx(group_fn, conf):
        def inner(m):
            new = group_fn(m)
            if new != m.group():
                log.append((m.group(), new, conf))
            return new
        return inner
    t = re.sub(r"\b(PT|MRN|pt)([- ]?)([0-9OoIlSB]{6,10})(\??)",
               fx(lambda m: ("PT" if m.group(1) in ("pt", "PT") else m.group(1)) + (m.group(2) or "-")
                  + m.group(3).translate(_FIX).replace("S", "5").replace("B", "8"), 0.8), text)
    t = re.sub(r"\b(\d{1,2}[/-])([0-9OoIl]{1,2})([/-])((?:19|20)[0-9OoIl]{2})\b",
               fx(lambda m: m.group(1) + m.group(2).translate(_FIX) + m.group(3) + m.group(4).translate(_FIX), 0.9), t)
    t = re.sub(r"\b(" + _NUM + r")\s?/\s?(" + _NUM + r")(\s?mmHg)\b",
               fx(lambda m: m.group(1).translate(_FIX) + "/" + m.group(2).translate(_FIX) + m.group(3), 0.9), t)
    t = re.sub(r"\b(" + _NUM + r"(?:\.[0-9OoIl]+)?)(\s?(?:mg|mcg|g|mL|mmol/L|g/dL|mg/dL|IU/L|°?[CF]|years?|days?|weeks?|hours?|months?))\b",
               fx(lambda m: m.group(1).translate(_FIX) + m.group(2), 0.85), t)
    return t, log


def correct_tokens(text, voc=None, max_cost=0.45):
    """Dictionary correction for OOV alphabetic tokens (len>=6) using weighted edit distance."""
    voc = voc or vocab()
    vl = [v for v in voc if len(v) >= 5]
    log = []

    def fix(m):
        w = m.group()
        lw = w.lower()
        if len(w) < 6 or lw in voc or not w.isalpha():
            return w
        cands = sorted(((weighted_edit_distance(lw, v), v) for v in vl if abs(len(v) - len(lw)) <= 2))[:2]
        if cands and cands[0][0] <= max_cost and (len(cands) == 1 or cands[1][0] - cands[0][0] > 0.2):
            log.append((w, cands[0][1], round(1 - cands[0][0], 2)))
            return cands[0][1]
        return w
    return re.sub(r"[A-Za-z]+", fix, text), log


def clean(text):
    """Full front end. Returns dict(cleaned, corrections, original)."""
    voc = vocab()
    t = strip_diacritics(text)
    t = repair_linebreaks(t, voc)
    t, nlog = repair_numbers(t)
    t, wlog = correct_tokens(t, voc)
    return {"original": text, "cleaned": t,
            "corrections": [("number",) + x for x in nlog] + [("word",) + x for x in wlog]}
