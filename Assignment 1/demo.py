"""Prints the hand-trace style outputs referenced in the report (Tasks 3, 4, 7, 8, 9, 12)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from hospital_nlp import morphology as m, noise
from hospital_nlp.automata import patient_id_nfa, subset_construction, dfa_to_regex, bp_dfa
from hospital_nlp.normalise import normalise
from hospital_nlp.porter_wrap import porter_stem
from hospital_nlp.tokenizer import tokenize

print("== Task 3: tokenisation / normalisation ==")
rec = "PT-1234567 | 05/11/2026 | c/o fever x 3 days. BP 120/80 mmHg. Rx: PARACETAMOL 500 MG BD."
print(tokenize("BP 120/80 mmHg; Give 500mg paracetamol; post-operative; i.v. fluids"))
print(normalise(rec)[0])

print("\n== Task 4: NFA trace, subset construction ==")
n = patient_id_nfa()
for s in ("PT-123456", "PT-12A456"):
    print(s, [sorted(x) for x in n.trace(s)], "ACCEPT" if n.accepts_string(s) else "REJECT")
D = subset_construction(n)
print("DFA states (incl. dead):", len(D.states), "-> minimised:", len(D.minimise().states))
print("DFA->regex:", dfa_to_regex(D))

print("\n== Task 7/8: parse and generate ==")
for w in ("fractures", "treated", "bleeding", "nephrectomies", "treatable", "went", "healing"):
    print(f"{w:15s}", [str(a) for a in m.analyse(w)])
for lex in ("fracture +N +PL", "treat +V +PAST", "bleed +V +PROG", "nephrectomy +N +PL", "admit +V +PAST"):
    print(f"{lex:22s} -> {m.generate_from_lexical(lex)}")

print("\n== Task 9: Porter vs FST lemma ==")
for w in ("fractures", "treated", "lesions", "bleeding", "nephrectomies", "went"):
    print(f"{w:14s} porter={porter_stem(w):12s} fst={sorted(m.lemmas_for(w))}")

print("\n== Task 12: noisy / code-mixed records ==")
for t in ("PT-I234567 05/II/2026 Dis-charge: fractured femur.",
          "patient ku fever irundhuchu, paracetamol 500mg kuduthen.",
          "pt O12345? fever irun-dhuchu; paracetarnol 5OOmg kuduthen."):
    c = noise.clean(t)
    print(t, "\n  ->", c["cleaned"], "\n  corrections:", c["corrections"])
L = noise.LanguageID()
print([(w, L.identify(w)[0]) for w in ("patient", "ku", "irundhuchu", "kuduthen", "paracetamol")])
