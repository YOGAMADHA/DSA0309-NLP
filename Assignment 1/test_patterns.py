import pytest
from hospital_nlp.patterns import PATTERNS, PATTERN_TESTS, validate, recognise_entities
import re


@pytest.mark.parametrize("name", list(PATTERN_TESTS))
def test_positive_and_negative(name):
    pos, neg = PATTERN_TESTS[name]
    for s in pos:
        m = PATTERNS[name].search(s)
        assert m and validate(name, m.group()), f"{name} should match {s!r}"
    for s in neg:
        m = PATTERNS[name].search(s)
        assert not (m and validate(name, m.group())), f"{name} must not match {s!r}"


def test_semantic_validators():
    assert not validate("date", "39/19/2026")
    assert not validate("blood_pressure", "BP 120/800 mmHg")
    assert not validate("age", "Age 450 years")
    assert not validate("temperature", "99.9 C")


def test_greedy_vs_lazy():
    t = "Give 500mg paracetamol and 250mg amoxicillin."
    assert re.search(r"Give.*mg", t).group() == "Give 500mg paracetamol and 250mg"
    assert re.search(r"Give.*?mg", t).group() == "Give 500mg"


def test_precedence_and_grouping():
    assert re.fullmatch(r"(AB|CD)[0-9]{4}", "CD1234")
    assert not re.fullmatch(r"(AB|CD)[0-9]{4}", "ABXYZ")
    assert re.search(r"^AB|CD[0-9]{4}$", "ABXYZ")          # misplaced alternation accepts it


def test_overlap_resolution_frequency_vs_icd():
    kinds = [e[0] for e in recognise_entities("paracetamol 500mg Q8H and S72.001A")]
    assert "frequency" in kinds and "icd_code" in kinds
