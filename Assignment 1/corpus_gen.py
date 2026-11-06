"""Reproducible synthetic corpus (500 records, >= 25,000 tokens). All identifiers are fictional.

Each record stores gold entities and gold concepts (lemmas inserted by the generator).
"""
import json
import random
from . import morphology as morph
from .tokenizer import tokenize

SEED = 20260611
COUNTS = {"discharge_summary": 150, "prescription": 125, "operation_note": 125, "nursing_observation": 100}
MIN_TOKENS = {"discharge_summary": 90, "prescription": 40, "operation_note": 70, "nursing_observation": 55}

DRUGS = ["paracetamol", "amoxicillin", "ibuprofen", "metformin", "amlodipine", "atorvastatin", "aspirin",
         "omeprazole", "ceftriaxone", "diclofenac", "pantoprazole"]
FREQ = ["OD", "BD", "TDS", "QID", "once daily", "twice daily", "Q8H"]
DX = [("Fracture of femur", "S72.001A"), ("Acute appendicitis", "K35.80"), ("Type 2 diabetes", "E11.9"),
      ("Essential hypertension", "I10"), ("Pneumonia", "J18.9"), ("Chronic kidney disease", "N18.9"),
      ("Acute myocardial infarction", "I21.9"), ("Urinary tract infection", "N39.0")]
PROCS = ["appendectomy", "nephrectomy", "cholecystectomy", "mastectomy", "hysterectomy", "laminectomy", "colectomy"]
SYMPTOMS = ["fever", "cough", "headache", "nausea", "vomiting", "dizziness", "fatigue", "pain", "swelling"]
N_POOL = ["fracture", "lesion", "wound", "incision", "suture", "artery", "vein", "biopsy", "infection", "ulcer",
          "abscess", "tumour", "cyst", "rash", "bruise", "scar", "dressing", "catheter", "drain", "graft",
          "stent", "implant", "splint", "bandage", "specimen", "sample", "kidney", "liver", "lung", "tendon",
          "ligament", "joint", "polyp", "hernia", "stone", "symptom", "complication", "finding", "child", "diagnosis"]
V_POOL = ["treat", "monitor", "examine", "observe", "repair", "remove", "suture", "heal", "bleed", "swell",
          "recover", "improve", "worsen", "irrigate", "drain", "aspirate", "review", "assess", "record",
          "document", "admit", "transfer", "refer", "stop", "undergo", "give", "take", "find", "see"]
A_POOL = ["mild", "severe", "acute", "chronic", "stable", "critical", "benign", "tender", "persistent", "minor"]


def _sentence(rng, concepts):
    def noun():
        n = rng.choice(N_POOL); f = rng.choice(["+SG", "+PL"]); concepts.add(n)
        return morph.generate(n, "N", f)

    def verb(feats):
        v = rng.choice(V_POOL); f = rng.choice(feats); concepts.add(v)
        return morph.generate(v, "V", f)

    def adj():
        a = rng.choice(A_POOL); concepts.add(a); return a
    t = rng.randint(0, 5)
    if t == 0: return f"The {adj()} {noun()} was {verb(['+PASTPART'])}."
    if t == 1: return f"No {noun()} {verb(['+3SG'])} after {noun()}."
    if t == 2: return f"{noun().capitalize()} noted; {verb(['+PROG'])} the {noun()}."
    if t == 3: return f"{noun().capitalize()} and {noun()} were {verb(['+PASTPART'])} by the team."
    if t == 4: return f"Patient {verb(['+PAST'])} well, {adj()} {noun()} {verb(['+PAST'])}."
    return f"The team {verb(['+PAST'])} the {noun()} and {verb(['+BASE'])} the {noun()}."


def _ward(rng):
    return "Ward " + rng.choice("ABCD") + str(rng.randint(1, 9)) + ", Bed " + str(rng.randint(1, 40))


def _date(rng):
    return f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/{rng.choice([2025, 2026])}"


def _entity_block(rng, kind, ents):
    def add(t, s):
        ents.append((t, s)); return s
    pid = add("patient_id", f"PT-{rng.randint(100000, 9999999)}")
    if kind == "discharge_summary":
        dx, icd = rng.choice(DX)
        d1, d2 = add("date", _date(rng)), add("date", _date(rng))
        return (f"{pid} | Admitted {d1} | Discharged {d2}. {add('age', 'Age: ' + str(rng.randint(5, 95)) + ' years')}. "
                f"{add('ward_bed', _ward(rng))}. "
                f"Diagnosis: {dx} ({add('icd_code', icd)}). Patient c/o {rng.choice(SYMPTOMS)} x "
                f"{add('duration', str(rng.randint(1, 14)) + ' days')}. "
                f"{add('blood_pressure', f'BP {rng.randint(100, 160)}/{rng.randint(60, 99)} mmHg')}. "
                f"{add('temperature', f'Temp {rng.randint(36, 39)}.{rng.randint(0, 9)} C')}. "
                f"{add('lab_value', f'Hb {rng.randint(8, 15)}.{rng.randint(0, 9)} g/dL')}. "
                f"Discharged on {add('drug_strength', rng.choice(DRUGS) + ' ' + str(rng.choice([250, 500, 650])) + 'mg')} "
                f"{add('frequency', rng.choice(FREQ))}. Contact {add('contact', str(rng.randint(6, 9)) + ''.join(rng.choice('0123456789') for _ in range(9)))}.")
    if kind == "prescription":
        d1 = add("date", _date(rng))
        lines = [f"Rx {pid} dated {d1}."]
        for _ in range(rng.randint(2, 4)):
            lines.append(f"Tab {add('drug_strength', rng.choice(DRUGS) + ' ' + str(rng.choice([250, 500, 650])) + 'mg')} "
                         f"{add('frequency', rng.choice(FREQ))} for {add('duration', str(rng.randint(2, 10)) + ' days')}.")
        return " ".join(lines)
    if kind == "operation_note":
        d1 = add("date", _date(rng)); dx, icd = rng.choice(DX)
        return (f"{pid} operated {d1}. Procedure: {rng.choice(PROCS)} for {dx} ({add('icd_code', icd)}). "
                f"{add('blood_pressure', f'BP {rng.randint(100, 150)}/{rng.randint(60, 95)} mmHg')} pre-op. "
                f"Post-operative plan: {add('drug_strength', rng.choice(DRUGS) + ' ' + str(rng.choice([500, 650])) + 'mg')} "
                f"{add('frequency', rng.choice(FREQ))}, review in {add('duration', str(rng.randint(1, 4)) + ' weeks')}.")
    return (f"{pid} {add('ward_bed', _ward(rng))}. "
            f"{add('blood_pressure', f'BP {rng.randint(95, 165)}/{rng.randint(55, 100)} mmHg')}. "
            f"{add('temperature', f'Temp {rng.randint(36, 39)}.{rng.randint(0, 9)} C')}. "
            f"{add('lab_value', f'Na {rng.randint(130, 148)} mmol/L')}. c/o {rng.choice(SYMPTOMS)} x "
            f"{add('duration', str(rng.randint(1, 7)) + ' days')}.")


def generate(seed=SEED):
    rng = random.Random(seed)
    records, n = [], 0
    for kind, cnt in COUNTS.items():
        for _ in range(cnt):
            ents, concepts = [], set()
            text = _entity_block(rng, kind, ents)
            while len(tokenize(text)) < MIN_TOKENS[kind] + rng.randint(0, 12):
                text += " " + _sentence(rng, concepts)
            n += 1
            records.append({"id": f"R{n:04d}", "type": kind, "text": text,
                            "gold_entities": ents, "gold_concepts": sorted(concepts)})
    return records


def save(records, path="data/synthetic_corpus.jsonl"):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load(path="data/synthetic_corpus.jsonl"):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def ocr_corrupt(text, rng, digit_rate=0.10, m_rate=0.15, hyph_rate=0.04):
    """Inject OCR-style noise for the Task-12 experiments."""
    out = []
    for w in text.split(" "):
        if any(c.isdigit() for c in w):
            w = "".join({"0": "O", "1": "I"}.get(c, c) if rng.random() < digit_rate else c for c in w)
        elif "m" in w and rng.random() < m_rate:
            i = w.index("m"); w = w[:i] + "rn" + w[i + 1:]
        elif w.isalpha() and len(w) >= 8 and rng.random() < hyph_rate:
            k = rng.randint(3, len(w) - 3); w = w[:k] + "-\n" + w[k:]
        out.append(w)
    return " ".join(out)
