"""Rewrite-rule normalisation: case, abbreviations, dates, units (Task 3.3-3.5).

Every substitution is logged with its original span so nothing is irreversibly lost.
"""
import re
from datetime import date

ABBREVIATIONS = {
    "BP": "blood pressure", "HR": "heart rate", "RR": "respiratory rate", "Temp": "temperature",
    "SOB": "shortness of breath", "N/V": "nausea and vomiting", "c/o": "complains of", "h/o": "history of",
    "PMH": "past medical history", "DM": "diabetes mellitus", "HTN": "hypertension", "CAD": "coronary artery disease",
    "CVA": "cerebrovascular accident", "MI": "myocardial infarction", "UTI": "urinary tract infection",
    "URI": "upper respiratory infection", "COPD": "chronic obstructive pulmonary disease",
    "CKD": "chronic kidney disease", "AKI": "acute kidney injury", "CBC": "complete blood count",
    "RFT": "renal function test", "LFT": "liver function test", "ECG": "electrocardiogram",
    "MRI": "magnetic resonance imaging", "CT": "computed tomography", "IV": "intravenous", "IM": "intramuscular",
}
# Only expanded when a dose (number + unit) precedes them in the same sentence.
CONTEXT_ABBREVIATIONS = {"OD": "once daily", "BD": "twice daily", "TDS": "three times daily",
                         "QID": "four times daily", "SOS": "when required"}
# Ambiguous abbreviations are deliberately NOT expanded; they are flagged.
AMBIGUOUS = {"MS": ["multiple sclerosis", "mitral stenosis", "morphine sulphate"]}
SAFE_LOWER = {"BP", "HR", "RR", "Temp", "SOB", "N/V", "c/o", "h/o", "PMH", "HTN"}

_PID = re.compile(r"\b(?:PT|MRN)[- ]?[0-9]{6,10}\b")
_DOSE_BEFORE = re.compile(r"[0-9]\s?(?:mg|mcg|g|mL)\b[^.|]*$", re.I)


def _abbr_regex():
    keys = sorted(ABBREVIATIONS, key=len, reverse=True)
    forms = set()
    for k in keys:
        forms.add(k)
        if k in SAFE_LOWER:
            forms.add(k.lower())
        forms.add(k.upper() if k not in ("c/o", "h/o") else k)
    alt = "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True))
    return re.compile(rf"(?<![\w/])({alt})(?![\w/])")


_ABBR_RX = _abbr_regex()
_ABBR_LOOKUP = {}
for _k, _v in ABBREVIATIONS.items():
    for _f in {_k, _k.lower(), _k.upper()}:
        if _f == _k or _k in SAFE_LOWER or _f == _k.upper():
            _ABBR_LOOKUP[_f] = _v
_CTX_RX = re.compile(r"(?<![\w/])(OD|BD|TDS|QID|SOS)(?![\w/])")
_DATE_RX = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
_UNIT_RX = re.compile(r"\b(\d+(?:\.\d+)?)\s?(MG|mg|Mg|MCG|mcg|G|g|ML|mL|Ml)\b")
_DUR_RX = re.compile(r"\bx\s*(\d+\s?(?:hours?|days?|weeks?|months?|years?))\b", re.I)


def canonical_date(s, locale="dmy"):
    """05/11/2026 -> 2026-11-05 only when the locale is known. Returns None if invalid/unknown."""
    m = _DATE_RX.fullmatch(s)
    if not m or locale not in ("dmy", "mdy"):
        return None
    a, b, y = map(int, m.groups())
    d, mo = (a, b) if locale == "dmy" else (b, a)
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def canonical_unit(value, unit, convert_g=False):
    """Return (value, unit, metadata). Unit case is fixed; g->mg only if convert_g (original kept)."""
    u = {"mg": "mg", "mcg": "mcg", "g": "g", "ml": "mL"}[unit.lower()]
    meta = {"original": f"{value} {unit}"}
    if convert_g and u == "g":
        v = float(value) * 1000
        return (f"{v:g}", "mg", meta)
    return (value, u, meta)


def normalise(text, locale="dmy", convert_g=False):
    """Return (normalised_text, log). Patient IDs are protected from case folding."""
    log = []
    protected = {}

    def protect(m):
        key = f"\x00{len(protected)}\x00"
        protected[key] = m.group()
        return key
    text = _PID.sub(protect, text)

    def fix_date(m):
        iso = canonical_date(m.group(), locale)
        if iso:
            log.append(("date", m.group(), iso))
            return iso
        return m.group()
    text = _DATE_RX.sub(fix_date, text)

    def fix_unit(m):
        v, u, meta = canonical_unit(m.group(1), m.group(2), convert_g)
        new = f"{v} {u}"
        log.append(("unit", m.group(), new))
        return new
    text = _UNIT_RX.sub(fix_unit, text)

    text = _DUR_RX.sub(lambda m: (log.append(("duration", m.group(), m.group(1))), "duration=" + m.group(1))[1], text)

    def expand(m):
        full = _ABBR_LOOKUP.get(m.group(1))
        if full:
            log.append(("abbrev", m.group(1), full))
            return full
        return m.group()
    text = _ABBR_RX.sub(expand, text)

    def expand_ctx(m):
        if _DOSE_BEFORE.search(text[:m.start()]):
            full = CONTEXT_ABBREVIATIONS[m.group(1)]
            log.append(("abbrev-context", m.group(1), full))
            return full
        return m.group()
    text = _CTX_RX.sub(expand_ctx, text)

    for amb, senses in AMBIGUOUS.items():
        if re.search(rf"(?<![\w/]){amb}(?![\w/])", text):
            log.append(("ambiguous-abbrev", amb, "/".join(senses)))

    text = text.lower().replace("mmhg", "mmHg").replace(" ml", " mL")
    for key, orig in protected.items():
        text = text.replace(key, orig)
    return text, log
