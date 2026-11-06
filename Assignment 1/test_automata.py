import random, re
from hospital_nlp.automata import (patient_id_dfa, date_dfa, bp_dfa, icd_dfa, patient_id_nfa,
                                   subset_construction, dfa_to_regex)
from hospital_nlp.thompson import Thompson


def test_dfa_validators_valid_and_invalid():
    assert patient_id_dfa().accepts_string("PT123456")
    assert not patient_id_dfa().accepts_string("PT12345") and not patient_id_dfa().accepts_string("PT12A456")
    assert date_dfa().accepts_string("2026-11-05") and not date_dfa().accepts_string("2026/11/05")
    assert bp_dfa().accepts_string("120/80 mmHg") and not bp_dfa().accepts_string("1/80 mmHg")
    assert icd_dfa().accepts_string("S72.001A") and not icd_dfa().accepts_string("72S.00")


def test_nfa_traces():
    n = patient_id_nfa()
    assert n.accepts_string("PT-123456") and n.accepts_string("PT123456") and n.accepts_string("PT 123456")
    assert not n.accepts_string("PT-12A456")
    assert n.trace("PT-12A456")[-1] == frozenset()           # active set empties after 'A'
    after_T = n.trace("PT")[-1]
    assert after_T == frozenset({"s2", "s3"})                # epsilon closure shows {s2,s3}


def test_subset_construction_and_minimisation_equivalence():
    n = patient_id_nfa(); D = subset_construction(n); M = D.minimise()
    rx = dfa_to_regex(D); th = Thompson(r"PT[- ]?[0-9]{6}")
    rng = random.Random(0)
    for _ in range(1500):
        s = "".join(rng.choice("PT- 0123456789A") for _ in range(rng.randint(0, 11)))
        if rng.random() < .6:
            s = "PT" + rng.choice(["", "-", " "]) + "".join(rng.choice("0123456789") for _ in range(rng.randint(4, 8)))
        ref = n.accepts_string(s)
        assert D.accepts_string(s) == ref and M.accepts_string(s) == ref
        assert bool(re.fullmatch(rx, s)) == ref and th.fullmatch(s) == ref
    assert len(M.states) <= len(D.states)


def test_pumping_lemma_witness_not_regular():
    """Brute-force illustration: no DFA with p states can accept exactly a^n b^n for all n (see README)."""
    p = 5; s = "(" * p + ")" * p
    for y_len in range(1, p + 1):
        for x_len in range(0, p - y_len + 1):
            x, y, z = s[:x_len], s[x_len:x_len + y_len], s[x_len + y_len:]
            pumped = x + z                                  # i = 0
            assert pumped.count("(") != pumped.count(")")   # leaves the language every time
