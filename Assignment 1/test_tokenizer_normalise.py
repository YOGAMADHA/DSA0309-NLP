from hospital_nlp.tokenizer import tokenize
from hospital_nlp.normalise import normalise, canonical_date, canonical_unit


def test_maximal_munch():
    assert tokenize("BP 120/80 mmHg") == ["BP", "120/80", "mmHg"]
    assert tokenize("Give 500mg paracetamol") == ["Give", "500mg", "paracetamol"]
    assert tokenize("post-operative review") == ["post-operative", "review"]
    assert tokenize("i.v. fluids started") == ["i.v.", "fluids", "started"]
    assert tokenize("500 mg") == ["500 mg"]


def test_full_record_before_after():
    out, log = normalise("PT-1234567 | 05/11/2026 | c/o fever x 3 days. BP 120/80 mmHg. Rx: PARACETAMOL 500 MG BD.")
    assert "PT-1234567" in out                       # identifier case protected
    assert "2026-11-05" in out and "complains of" in out and "duration=3 days" in out
    assert "blood pressure" in out and "paracetamol 500 mg twice daily" in out
    assert any(k == "abbrev-context" for k, *_ in log)


def test_context_dependent_abbreviation():
    assert "twice daily" not in normalise("BD noted")[0]       # no dose before it -> not expanded


def test_ambiguous_abbreviation_flagged_not_expanded():
    out, log = normalise("history of MS")
    assert "MS" in out.upper() and any(k == "ambiguous-abbrev" for k, *_ in log)


def test_date_and_unit_rules():
    assert canonical_date("05/11/2026", "dmy") == "2026-11-05"
    assert canonical_date("05/11/2026", "mdy") == "2026-05-11"
    assert canonical_date("39/19/2026", "dmy") is None
    assert canonical_date("05/11/2026", "unknown") is None
    assert canonical_unit("0.5", "g", convert_g=True)[:2] == ("500", "mg")
