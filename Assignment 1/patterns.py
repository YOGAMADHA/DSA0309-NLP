"""Twelve clinical entity recognisers (Task 2) + semantic validators.

Regexes are candidate recognisers; `validate` applies range/calendar checks afterwards.
NOTE: in the PDF the patterns are shown with doubled backslashes; in real Python raw strings a
single backslash is required, which is what is used here.
"""
import re
from datetime import date

PATTERN_SRC = {
    "patient_id": r"\b(?:PT|MRN)[- ]?[0-9]{6,10}\b",
    "date": r"\b(?:[0-3]?[0-9][/-][01]?[0-9][/-](?:19|20)?[0-9]{2}|(?:19|20)[0-9]{2}-[01][0-9]-[0-3][0-9])\b",
    "drug_strength": r"\b[A-Za-z][A-Za-z-]+\s?[0-9]+(?:\.[0-9]+)?\s?(?:mg|mcg|g|mL)\b(?![/A-Za-z])",
    "frequency": r"\b(?:OD|BD|TDS|QID|BID|TID|SOS|Q[0-9]{1,2}H|(?i:once daily|twice daily|every [0-9]{1,2} hours))\b",
    "lab_value": r"\b[A-Za-z][A-Za-z0-9-]*\s*[:=]?\s*[0-9]+(?:\.[0-9]+)?\s?(?:mg/dL|g/dL|mmol/L|IU/L|10\^?[0-9]+/L)",
    "blood_pressure": r"\b(?:BP\s*)?[0-9]{2,3}\s*/\s*[0-9]{2,3}\s?mmHg\b",
    "temperature": r"\b(?:Temp\s*)?(?:(?:3[0-9]|4[0-2])(?:\.[0-9])?\s?°?C|(?:9[0-9]|10[0-9])(?:\.[0-9])?\s?°?F)\b",
    "icd_code": r"\b[A-Z][0-9][A-Z0-9](?:\.[A-Z0-9]{1,4})?\b",
    "ward_bed": r"\bWard\s*[A-Za-z0-9-]+\s*,?\s*Bed\s*[A-Za-z0-9-]+\b",
    "contact": r"(?<![\w-])(?:\+91[- ]?)?[6-9][0-9]{9}(?![\w])",
    "age": r"\b(?:Age\s*[:=]?\s*[0-9]{1,3}(?:\s?(?:years?|yrs?|y/o))?|[0-9]{1,3}\s?(?:y/o|yrs?[- ]old|years?[- ]old))\b",
    "duration": r"\b[0-9]+\s?(?:hours?|days?|weeks?|months?|years?)\b",
}
PATTERNS = {k: re.compile(v) for k, v in PATTERN_SRC.items()}

# Priority for overlap resolution (earlier wins; longer spans are not guaranteed to win otherwise).
PRIORITY = ["patient_id", "date", "blood_pressure", "lab_value", "temperature", "drug_strength", "ward_bed",
            "contact", "age", "frequency", "icd_code", "duration"]

# (must_match, must_not_match) test strings per pattern, used by the unit tests.
PATTERN_TESTS = {
    "patient_id": (["PT-1234567", "MRN 12345678", "PT123456"], ["PT-12A4567", "PT-123"]),
    "date": (["05/11/2026", "2026-11-05", "5-1-26"], ["39/19/2026", "hello"]),
    "drug_strength": (["paracetamol 500mg", "amoxicillin 250 mg"], ["paracetamol five mg", "Hb 12.5 g/dL"]),
    "frequency": (["BD", "once daily", "Q8H", "every 8 hours"], ["dailyish", "ABD"]),
    "lab_value": (["Hb 12.5 g/dL", "Na: 140 mmol/L"], ["Hb twelve g/dL"]),
    "blood_pressure": (["BP 120/80 mmHg", "120/80 mmHg"], ["120/80", "BP 1/2 mmHg"]),
    "temperature": (["Temp 37.2 C", "38°C", "98.6 F"], ["Temp 99.9 C", "cat"]),
    "icd_code": (["S72.001A", "I21.9", "E11"], ["72S.00", "ab"]),
    "ward_bed": (["Ward B2, Bed 14", "Ward 3 Bed A1"], ["Ward, Bed"]),
    "contact": (["9876543210", "+91 9876543210"], ["+91 12345", "1234567890"]),
    "age": (["Age: 45 years", "62 y/o"], ["many years"]),
    "duration": (["3 days", "2 weeks"], ["many days"]),
}


def _valid_date(s):
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = map(int, m.groups())
    else:
        m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", s)
        if not m:
            return False
        d, mo, y = map(int, m.groups())
        y += 2000 if y < 100 else 0
    try:
        date(y, mo, d)
        return True
    except ValueError:
        return False


def validate(name, text):
    """Semantic range checks applied after the regex candidate is found."""
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]
    if name == "date":
        return _valid_date(text)
    if name == "blood_pressure":
        return len(nums) >= 2 and 50 <= nums[0] <= 300 and 20 <= nums[1] <= 200 and nums[0] > nums[1]
    if name == "temperature":
        v = nums[-1]
        return 34 <= v <= 43 if re.search(r"C\b", text) else 93 <= v <= 109
    if name == "age":
        return bool(nums) and 0 <= nums[0] <= 120
    return True


def recognise_entities(text, do_validate=True):
    """Return non-overlapping [(type, start, end, text)] using PRIORITY for conflicts."""
    taken, out = [], []
    for name in PRIORITY:
        for m in PATTERNS[name].finditer(text):
            s, e = m.span()
            if any(s < te and ts < e for ts, te in taken):
                continue
            if do_validate and not validate(name, m.group()):
                continue
            taken.append((s, e))
            out.append((name, s, e, m.group()))
    return sorted(out, key=lambda x: x[1])
